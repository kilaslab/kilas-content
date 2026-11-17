#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Build the HyperFrames project that renders a 3D explainer scene with its voice-over.

  scene3d_video.py <item>/scene <item>/video --vo <vo dir> [--duration 60] [--no-sfx] [--no-music]

Reads VO_STARTS from <scene>/beats.js and the clips vo0.mp3, vo1.mp3, ... from --vo (the
"final" names in vo-manifest.json when vo_elevenlabs.py wrote one). Copies every top-level .js
module (scene.js, beats.js, mascot.js, ...), lib/, img/ and fonts/ into <video>, the clips into <video>/assets/, and writes
<video>/index.html: the stage with style.css inlined, one <audio> per clip at its start with
its measured duration, the scene's build-ready promise, and an empty GSAP timeline that marks
the film's length (the scene draws every frame itself from the hf-seek time). Rebuild after
every change in <scene>; edit the scene, never <video>.

Sound, from beats.js (read with node, so T names and filmTime() work):
  SFX    one <audio> per cue at its film second; the sound is <item>/sfx/<name>.mp3 when that
         file exists, else the kit in sfx_synth.py. A film with no cue stops here unless
         --no-sfx says the owner wants it bare.
  MUSIC  { file, gain, duck, dips }: the bed is trimmed to the film, ducked under the voice with
         a sidechain compressor keyed by the clips at their starts, faded out, one <audio>.
         dips: [[from, to], ...] film seconds (T names work) where the bed goes muffled and a
         little quieter, then opens again over the last 1.5 s: the beat where the story turns
         quiet, so the next one lands. Make the bed with music_elevenlabs.py. A film with VO
         and SFX but no bed read as empty ("masih kerasa sepi"), so a film without MUSIC stops
         here unless --no-music says the owner wants none.
  SPEAK  writes vo-env.js (each clip's loudness, 30 values a second) into <scene> and <video>
         for mouths that move with the voice.
  SYNC   writes <video>/sync.json (word, film second) for reel_qa.py --sync.

Checks before writing: as many starts as clips, no clip overlapping the next, none running
past the duration (DUR in beats.js, else --duration), every sound file found.
Exit codes: 0 written, 1 a check failed, 2 usage.
Then: cd <video> && npx hyperframes check && npx hyperframes render -q delivery --video-bitrate 12M -o ../export/raw.mp4
"""
import argparse, json, math, os, re, shutil, struct, subprocess, sys
from pathlib import Path

GSAP = "https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True).stdout.strip()
    return float(out)


def clips(vo):
    manifest = vo / "vo-manifest.json"
    if manifest.exists():
        names = [m["final"] for m in json.loads(manifest.read_text())]
    else:
        names = sorted((p.name for p in vo.glob("vo*.mp3") if re.fullmatch(r"vo\d+\.mp3", p.name)),
                       key=lambda n: int(re.search(r"\d+", n).group()))
    return [vo / n for n in names]


def beats(scene):
    """beats.js evaluated by node: its exports as JSON, SFX and SYNC already in film seconds."""
    if not shutil.which("node"):
        return None
    mod, run = scene / ".beats-eval.mjs", scene / ".beats-run.mjs"
    mod.write_text((scene / "beats.js").read_text())
    run.write_text("""import * as B from "./.beats-eval.mjs";
const ft = B.filmTime || ((x) => x), at = (v) => (typeof v === "number" ? ft(v) : null);
console.log(JSON.stringify({ DUR: B.DUR ?? null, VO_STARTS: B.VO_STARTS ?? null, MUSIC: B.MUSIC ?? null, SPEAK: B.SPEAK ?? [],
  SFX: (B.SFX ?? []).map((c) => ({ ...c, film: at(c.at) })), SYNC: (B.SYNC ?? []).map((c) => ({ ...c, film: at(c.at) })) }));
""")
    try:
        r = subprocess.run(["node", str(run)], capture_output=True, text=True, timeout=60)
    finally:
        mod.unlink(missing_ok=True); run.unlink(missing_ok=True)
    if r.returncode:
        print(f"beats.js did not load in node: {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else 'no output'}", file=sys.stderr); sys.exit(1)
    return json.loads(r.stdout)


def envelope(path, fps=30):
    """Loudness of a clip, 0..1, fps values a second: RMS per frame against the clip's loud level."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", "12000", "-f", "s16le", "-"], capture_output=True).stdout
    n = len(raw) // 2
    s = struct.unpack(f"<{n}h", raw[: n * 2])
    step = 12000 // fps
    rms = [math.sqrt(sum(v * v for v in s[i:i + step]) / step) for i in range(0, n - step + 1, step)]
    if not rms:
        return []
    top = sorted(rms)[int(len(rms) * 0.92)] or 1
    lv = [min(1.0, v / top) for v in rms]
    lv = [0 if v < 0.12 else v for v in lv]                    # breath and room tone keep the mouth shut
    sm = [max(lv[max(0, i - 1):i + 2]) * 0.5 + lv[i] * 0.5 for i in range(len(lv))]   # no single-frame flaps
    return [round(v, 2) for v in sm]


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("scene"); p.add_argument("video")
    p.add_argument("--vo", required=True, help="folder with vo0.mp3, vo1.mp3, ...")
    p.add_argument("--duration", type=float, default=None, help="film length when beats.js has no DUR (default 60)")
    p.add_argument("--no-sfx", action="store_true", help="build without sound effects: the owner asked for a bare voice-over")
    p.add_argument("--no-music", action="store_true", help="build without a music bed: the owner asked for none")
    a = p.parse_args()
    scene, video, vo = Path(a.scene), Path(a.video), Path(a.vo)
    for f in ("index.html", "scene.js", "beats.js", "style.css"):
        if not (scene / f).exists():
            print(f"missing {scene / f}", file=sys.stderr); sys.exit(2)

    B = beats(scene)
    if B and B["VO_STARTS"] is not None:
        starts = [float(x) for x in B["VO_STARTS"]]
    else:  # no node: the plain list still reads; sound cues need node
        m = re.search(r"VO_STARTS\s*=\s*\[([^\]]*)\]", (scene / "beats.js").read_text())
        if not m:
            print("beats.js has no `export const VO_STARTS = [...]`", file=sys.stderr); sys.exit(1)
        starts = [float(x) for x in m.group(1).split(",") if x.strip()]
        B = B or {"DUR": None, "MUSIC": None, "SPEAK": [], "SFX": [], "SYNC": [], "has": {}}
        print("warning: node not found, so SFX, MUSIC, SPEAK and SYNC in beats.js are not read", file=sys.stderr)
    a.duration = a.duration or B["DUR"] or 60
    item = scene.parent
    cues = [c for c in B["SFX"] if c.get("film") is not None]
    if len(cues) != len(B["SFX"]):
        print("an SFX cue has no numeric `at` (a T name that does not exist?)", file=sys.stderr); sys.exit(1)
    if not cues and not a.no_sfx:
        print("no sound effects: add cues to `export const SFX` in beats.js (templates/video3d/beats.js shows the shape),\n"
              "or pass --no-sfx when the owner wants the voice-over bare", file=sys.stderr); sys.exit(1)
    if not B["MUSIC"] and not a.no_music:
        print("no music bed: make one with music_elevenlabs.py and set `export const MUSIC` in beats.js,\n"
              "or pass --no-music when the owner wants none", file=sys.stderr); sys.exit(1)
    files = clips(vo)
    if len(files) != len(starts):
        print(f"{len(files)} clips in {vo} but {len(starts)} VO_STARTS in beats.js", file=sys.stderr); sys.exit(1)
    timeline, bad = [], False
    for i, (f, s) in enumerate(zip(files, starts)):
        d = duration(f)
        timeline.append((f, s, d))
        print(f"vo{i}  {s:6.2f} -> {s + d:6.2f} s  {f.name}")
        if s + d > a.duration:
            print(f"  ends after {a.duration:g} s", file=sys.stderr); bad = True
        if i + 1 < len(starts) and s + d > starts[i + 1]:
            print(f"  overlaps vo{i + 1} (starts {starts[i + 1]:g} s): move its start or shorten the line", file=sys.stderr); bad = True
    if bad:
        sys.exit(1)

    video.mkdir(parents=True, exist_ok=True)
    (video / "assets").mkdir(exist_ok=True)
    # mouths that move with the voice: the clips' loudness, for the scene and for the render
    env = [envelope(f) if i < len(B["SPEAK"]) and B["SPEAK"][i] else [] for i, (f, _, _) in enumerate(timeline)]
    if any(env) or (scene / "vo-env.js").exists():
        (scene / "vo-env.js").write_text("// Written by scene3d_video.py from the voice-over clips (SPEAK in beats.js); do not edit.\n"
                                         f"export const ENV = {json.dumps({'fps': 30, 'clips': env}, separators=(',', ':'))};\n")
    # sound effects: a file in <item>/sfx wins over the kit
    sfx_lines, made = [], {}
    for i, c in enumerate(sorted(cues, key=lambda c: c["film"])):
        name = c.get("sfx", "")
        if name not in made:
            own = next((q for q in (item / "sfx" / f"{name}.mp3", item / "sfx" / f"{name}.wav") if q.exists()), None)
            if own:
                dst = video / "assets" / f"sfx_{own.name}"; shutil.copy2(own, dst)
            else:
                r = subprocess.run([sys.executable, str(Path(__file__).with_name("sfx_synth.py")), str(video / "assets" / "_kit"), name], capture_output=True, text=True)
                if r.returncode:
                    print(f"SFX '{name}': no {item / 'sfx' / (name + '.mp3')} and {r.stderr.strip()}", file=sys.stderr); sys.exit(1)
                dst = video / "assets" / f"sfx_{name}.mp3"; shutil.move(str(video / "assets" / "_kit" / f"{name}.mp3"), dst)
            made[name] = (dst, duration(dst))
        dst, d = made[name]
        if c["film"] + d > a.duration:
            continue
        sfx_lines.append(f'      <audio id="sfx{i}" class="clip" src="assets/{dst.name}" data-start="{c["film"]:.3f}" data-duration="{d:.3f}" '
                         f'data-track-index="{40 + i}" data-volume="{float(c.get("gain", 0.4)):g}"></audio>')
    shutil.rmtree(video / "assets" / "_kit", ignore_errors=True)
    # music bed, ducked under the voice
    music_line = ""
    if B["MUSIC"]:
        mu = B["MUSIC"]; src = item / mu["file"]
        if not src.exists():
            print(f"MUSIC file not found: {src}", file=sys.stderr); sys.exit(1)
        bed = video / "assets" / "music_bed.mp3"
        ins, keys = ["-stream_loop", "-1", "-i", str(src)], []
        # dips: a low-passed copy of the bed faded in over 0.4 s at each dip's start and out over
        # the 1.5 s before its end (a filter sweep back up into the next beat)
        dips = [(float(x), float(y)) for x, y in (mu.get("dips") or [])]
        w = "+".join(f"clip((t-{x:.3f})/0.4,0,1)*clip(({y:.3f}-t)/1.5,0,1)" for x, y in dips)
        mfilt = (f"[0:a]atrim=0:{a.duration},volume={float(mu.get('gain', 0.5))},asplit=2[mf][ml]",
                 f"[mf]volume='1-min(1,{w})':eval=frame[mfw]",
                 f"[ml]lowpass=f=700,lowpass=f=700,volume='0.8*min(1,{w})':eval=frame[mlw]",
                 "[mfw][mlw]amix=inputs=2:normalize=0[m]") if dips else (f"[0:a]atrim=0:{a.duration},volume={float(mu.get('gain', 0.5))}[m]",)
        for k, (f, s, _) in enumerate(timeline):
            ins += ["-i", str(f)]; keys.append(f"[{k + 1}:a]adelay={int(s * 1000)}:all=1[k{k}]")
        ratio = max(2, min(20, round(10 ** (float(mu.get("duck", 10)) / 20) * 2)))
        graph = ";".join(keys + ["".join(f"[k{k}]" for k in range(len(timeline))) + f"amix=inputs={len(timeline)}:normalize=0[key]",
                                 *mfilt,
                                 f"[m][key]sidechaincompress=threshold=0.02:ratio={ratio}:attack=30:release=450[d]",
                                 f"[d]afade=t=in:d=0.4,afade=t=out:st={a.duration - 1.5}:d=1.5[out]"])
        r = subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", graph, "-map", "[out]", "-t", str(a.duration), "-ar", "48000",
                            "-c:a", "libmp3lame", "-b:a", "192k", str(bed)], capture_output=True, text=True)
        if r.returncode or not bed.exists():
            print(f"music bed failed: {r.stderr.strip()[:400]}", file=sys.stderr); sys.exit(1)
        music_line = (f'      <audio id="music" class="clip" src="assets/{bed.name}" data-start="0" data-duration="{duration(bed):.3f}" '
                      f'data-track-index="5" data-volume="1"></audio>')
    (video / "sync.json").write_text(json.dumps([{"word": c["word"], "clip": c.get("clip"), "film": round(c["film"], 3), "tol": c.get("tol", 0.35)}
                                                 for c in B["SYNC"] if c.get("film") is not None], ensure_ascii=False, indent=1) + "\n")
    # every top-level module the scene imports (scene.js, beats.js, mascot.js, mira.js, ...)
    for f in sorted(scene.glob("*.js")):
        shutil.copy2(f, video / f.name)
    for d in ("lib", "img", "fonts"):
        if (scene / d).is_dir():
            shutil.copytree(scene / d, video / d, dirs_exist_ok=True)
    for f, _, _ in timeline:
        shutil.copy2(f, video / "assets" / f.name)

    css = (scene / "style.css").read_text()
    css = re.sub(r"html,\s*body\s*\{[^}]*\}", "html, body { margin: 0; padding: 0; width: 1080px; height: 1920px; overflow: hidden; }", css, count=1)
    fonts_css = scene / "fonts" / "fonts.css"
    font_head = ""
    if fonts_css.exists():
        css = fonts_css.read_text() + "\n" + css
    else:  # fall back to the dev page's web-font link
        link = re.search(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com[^>]*>', (scene / "index.html").read_text())
        font_head = ("    " + link.group(0) + "\n") if link else ""
    audio = "\n".join(
        f'      <audio id="vo{i}" class="clip" src="assets/{f.name}" data-start="{s:g}" data-duration="{d:.3f}" '
        f'data-track-index="{10 + i}" data-volume="1"></audio>' for i, (f, s, d) in enumerate(timeline))
    audio = "\n".join(x for x in [audio, music_line, *sfx_lines] if x)
    html = f'''<!doctype html>
<!-- Built by scene3d_video.py from {scene}: edit the scene and rebuild, not this file. -->
<html lang="id">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
{font_head}    <style>
{css}
      #root {{ position: relative; width: 1080px; height: 1920px; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{a.duration:g}" data-width="1080" data-height="1920" data-layout-allow-overlap data-layout-allow-overflow>
      <div id="stage">
        <canvas id="gl" width="1080" height="1920"></canvas>
        <div id="ov"></div>
      </div>
{audio}
    </div>
    <script>
      window.__hf = window.__hf || {{}};
      window.__hf.buildReady = window.__hf.buildReady || {{}};
      window.__hf.buildReady["scene"] = new Promise((r) => (window.__sceneReady = r));
    </script>
    <script src="{GSAP}"></script>
    <script>
      // the 3D scene draws itself from hf-seek; this timeline only marks the film's length
      const tl = gsap.timeline({{ paused: true }});
      tl.to({{}}, {{ duration: {a.duration:g} }});
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
    </script>
    <script type="importmap">{{ "imports": {{ "three": "./lib/three.module.js" }} }}</script>
    <script type="module" src="scene.js"></script>
  </body>
</html>
'''
    (video / "index.html").write_text(html)
    if not (video / "hyperframes.json").exists():
        (video / "hyperframes.json").write_text(json.dumps({"paths": {"assets": "assets"}, "media": {"autoProxy": True}}, indent=2) + "\n")
    if not (video / "package.json").exists():
        (video / "package.json").write_text(json.dumps({"name": video.name, "private": True, "type": "module"}, indent=2) + "\n")
    print(f"written {video / 'index.html'} ({len(timeline)} clips, {len(sfx_lines)} sound effects, "
          f"{'a music bed' if music_line else 'no music bed'}, {a.duration:g} s)")
    print(f"next: cd {video} && npx hyperframes check && npx hyperframes render -q delivery --video-bitrate 12M -o ../export/raw.mp4")


if __name__ == "__main__":
    main()
