#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Build the HyperFrames project that renders a 3D explainer scene with its voice-over.

  scene3d_video.py <item>/scene <item>/video --vo <vo dir> [--duration 60]

Reads VO_STARTS from <scene>/beats.js and the clips vo0.mp3, vo1.mp3, ... from --vo (the
"final" names in vo-manifest.json when vo_elevenlabs.py wrote one). Copies scene.js, beats.js,
mascot.js, lib/, img/ and fonts/ into <video>, the clips into <video>/assets/, and writes
<video>/index.html: the stage with style.css inlined, one <audio> per clip at its start with
its measured duration, the scene's build-ready promise, and an empty GSAP timeline that marks
the film's length (the scene draws every frame itself from the hf-seek time). Rebuild after
every change in <scene>; edit the scene, never <video>.

Checks before writing: as many starts as clips, no clip overlapping the next, none running
past --duration. Exit codes: 0 written, 1 a check failed, 2 usage.
Then: cd <video> && npx hyperframes check && npx hyperframes render -q delivery -o ../export/raw.mp4
"""
import argparse, json, re, shutil, subprocess, sys
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


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("scene"); p.add_argument("video")
    p.add_argument("--vo", required=True, help="folder with vo0.mp3, vo1.mp3, ...")
    p.add_argument("--duration", type=float, default=60)
    a = p.parse_args()
    scene, video, vo = Path(a.scene), Path(a.video), Path(a.vo)
    for f in ("index.html", "scene.js", "beats.js", "style.css"):
        if not (scene / f).exists():
            print(f"missing {scene / f}", file=sys.stderr); sys.exit(2)

    m = re.search(r"VO_STARTS\s*=\s*\[([^\]]*)\]", (scene / "beats.js").read_text())
    if not m:
        print("beats.js has no `export const VO_STARTS = [...]`", file=sys.stderr); sys.exit(1)
    starts = [float(x) for x in m.group(1).split(",") if x.strip()]
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
    for f in ("scene.js", "beats.js", "mascot.js"):
        if (scene / f).exists():
            shutil.copy2(scene / f, video / f)
    for d in ("lib", "img", "fonts"):
        if (scene / d).is_dir():
            shutil.copytree(scene / d, video / d, dirs_exist_ok=True)
    (video / "assets").mkdir(exist_ok=True)
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
    print(f"written {video / 'index.html'} ({len(timeline)} clips, {a.duration:g} s)")
    print(f"next: cd {video} && npx hyperframes check && npx hyperframes render -q delivery -o ../export/raw.mp4")


if __name__ == "__main__":
    main()
