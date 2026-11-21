#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""One-command QA for a rendered Reel: the measured half of the critique loop.

  reel_qa.py <film.mp4> [--out DIR] [--hold 0-1.5,29-33] [--quiet 1.5] [--lufs -14]
             [--master OUT.mp4] [--sync sync.json --words words.json]

Checks, each PASS or FAIL, and exits 1 on any FAIL:
  format    1080x1920 (or the --size given), 25-60 fps, an audio stream
  loudness  integrated LUFS within 1 LU of --lufs, true peak <= -1 dBTP
  audio     44.1 or 48 kHz (a loudnorm pass without -ar leaves 96 or 192 kHz, which the apps
            resample their own way)
  sync      with --sync (written by scene3d_video.py from SYNC in beats.js) and --words (from
            vo_elevenlabs.py --verify <film> --words): each picture lands within its tolerance
            before its word, and no more than 0.1 s after it; a cue's word may list the spellings
            the transcriber uses, split by | ("tiga|37")
  frozen    no run of >= 12 frames with almost no change, outside the --hold windows
            (an intended still: the hook frame, the end card); a hold needs a creeping push-in
  dead      no second mid-film whose motion is under --quiet (mean grey difference per frame
            pair at 4 fps), outside the --hold windows
  flash     no single black or white frame (a render glitch), unless it is a deliberate flash
            you list with --hold
Writes to --out (default: <film>_qa/): contact.png (2 fps, 18 s a page; contact-2.png ... for the
rest), phone.png (1 fps at 360 px wide, 30 s a page; phone-2.png ...),
motion.csv (second, motion), and report.md with the numbers. Look at both sheets after a PASS:
the script measures, it does not judge taste.
--master OUT.mp4 first writes the film at the target loudness and under -1 dBTP (loudnorm, then a
limiter; video copied, audio at 48 kHz)
and checks that file instead: the one step between the render and the post.
Needs ffmpeg/ffprobe and Pillow.
"""
import argparse, csv, json, re, shutil, subprocess, sys, tempfile
from pathlib import Path


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def windows(spec):
    out = []
    for part in (spec or "").split(","):
        if "-" in part:
            a, b = part.split("-", 1)
            out.append((float(a), float(b)))
    return out


def inside(t, wins):
    return any(a <= t <= b for a, b in wins)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("film")
    p.add_argument("--out")
    p.add_argument("--hold", default="", help="intended still windows in seconds, e.g. 0-1.5,29-33")
    p.add_argument("--quiet", type=float, default=1.5, help="motion floor for a dead second")
    p.add_argument("--lufs", type=float, default=-14.0)
    p.add_argument("--size", default="1080x1920")
    p.add_argument("--master", help="write the film here at the target loudness and 48 kHz, then check that file")
    p.add_argument("--sync", help="sync.json from scene3d_video.py"); p.add_argument("--words", help="word timings of the film")
    a = p.parse_args()
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            sys.exit(f"{tool} not found (brew install ffmpeg)")
    try:
        from PIL import Image, ImageChops, ImageStat
    except ImportError:
        sys.exit("Pillow not found (pip install pillow)")
    film = Path(a.film)
    if a.master:
        r = run(["ffmpeg", "-v", "error", "-y", "-i", str(film), "-c:v", "copy", "-af", 
                 # one loudnorm pass can still overshoot after AAC (-0.9 dBTP on a 48 s Reel): a limiter
                 # at -2 dBFS (latency compensated, so the voice stays in sync) keeps the true peak under -1
                 f"loudnorm=I={a.lufs:.0f}:TP=-1.5:LRA=11,alimiter=limit=0.79:level=false:latency=true",
                 "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", a.master])
        if r.returncode or not Path(a.master).exists():
            sys.exit(f"--master failed: {r.stderr.strip()[:300]}")
        film = Path(a.master)
    out = Path(a.out or f"{film.with_suffix('')}_qa")
    out.mkdir(parents=True, exist_ok=True)
    holds = windows(a.hold)
    results = []

    def check(name, ok, detail):
        results.append((name, ok, detail))

    info = json.loads(run(["ffprobe", "-v", "error", "-show_entries",
                           "stream=codec_type,width,height,r_frame_rate,sample_rate,bit_rate:format=duration",
                           "-of", "json", str(film)]).stdout)
    streams = info.get("streams", [])
    v = next((s for s in streams if s.get("codec_type") == "video"), {})
    has_audio = any(s.get("codec_type") == "audio" for s in streams)
    num, den = (v.get("r_frame_rate", "0/1").split("/") + ["1"])[:2]
    fps = float(num) / float(den or 1)
    dur = float(info.get("format", {}).get("duration", 0))
    size = f"{v.get('width')}x{v.get('height')}"
    check("format", size == a.size and 25 <= fps <= 60 and has_audio,
          f"{size}, {fps:.2f} fps, {dur:.2f} s, audio {'yes' if has_audio else 'NO'}")

    au = next((s for s in streams if s.get("codec_type") == "audio"), {})
    if has_audio:
        sr = int(au.get("sample_rate") or 0)
        check("audio", sr in (44100, 48000), f"{sr} Hz" + ("" if sr in (44100, 48000) else "; re-run with --master OUT.mp4 (it writes 48 kHz)"))
    if has_audio:
        ln = run(["ffmpeg", "-hide_banner", "-i", str(film), "-af", "loudnorm=print_format=summary", "-f", "null", "-"]).stderr
        i_m = re.search(r"Input Integrated:\s+(-?[\d.]+)", ln)
        tp_m = re.search(r"Input True Peak:\s+([+-]?[\d.]+)", ln)
        lufs = float(i_m.group(1)) if i_m else float("nan")
        tp = float(tp_m.group(1)) if tp_m else float("nan")
        check("loudness", abs(lufs - a.lufs) <= 1.0 and tp <= -1.0,
              f"{lufs:.1f} LUFS (target {a.lufs:.0f} ±1), true peak {tp:.1f} dBTP (≤ -1); fix: "
              f"reel_qa.py in.mp4 --master out.mp4")

    tmp = Path(tempfile.mkdtemp())
    # full frame rate, tiny grey frames, for frozen runs and flash frames
    run(["ffmpeg", "-v", "error", "-i", str(film), "-vf", "scale=90:160,format=gray", str(tmp / "f%05d.png")])
    frames = sorted(tmp.glob("f*.png"))
    prev, frozen_run, frozen_bad, flashes = None, [], [], []
    for i, f in enumerate(frames):
        im = Image.open(f)
        mean = ImageStat.Stat(im).mean[0]
        t = i / fps
        if (mean < 6 or mean > 249) and not inside(t, holds):
            flashes.append(round(t, 2))
        if prev is not None:
            diff = ImageStat.Stat(ImageChops.difference(im, prev)).mean[0]
            if diff < 0.15:
                frozen_run.append(t)
            else:
                if len(frozen_run) >= 12 and not all(inside(x, holds) for x in frozen_run):
                    frozen_bad.append((round(frozen_run[0], 2), round(frozen_run[-1], 2)))
                frozen_run = []
        prev = im
    if len(frozen_run) >= 12 and not all(inside(x, holds) for x in frozen_run):
        frozen_bad.append((round(frozen_run[0], 2), round(frozen_run[-1], 2)))
    check("frozen", not frozen_bad, f"frozen spans ≥12 f outside holds: {frozen_bad or 'none'}"
          + ("; give every hold a creeping push-in (motion-video.md 2d)" if frozen_bad else ""))
    check("flash", not flashes, f"single black/white frames at: {flashes[:10] or 'none'}")

    # motion per second at 4 fps
    shutil.rmtree(tmp)
    tmp = Path(tempfile.mkdtemp())
    run(["ffmpeg", "-v", "error", "-i", str(film), "-vf", "fps=4,scale=270:-1,format=gray", str(tmp / "m%04d.png")])
    ms = sorted(tmp.glob("m*.png"))
    per = {}
    prev = None
    for i, f in enumerate(ms):
        im = Image.open(f)
        if prev is not None:
            per[int(i / 4)] = per.get(int(i / 4), 0) + ImageStat.Stat(ImageChops.difference(im, prev)).mean[0]
        prev = im
    with open(out / "motion.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["second", "motion"])
        for k in sorted(per):
            w.writerow([k, round(per[k], 2)])
    dead = [k for k in sorted(per) if per[k] < a.quiet and not inside(k + 0.5, holds) and 0 < k < int(dur) - 1]
    check("dead", not dead, f"dead seconds (motion < {a.quiet}): {dead or 'none'}"
          + ("; add a reaction, a push-in, or cut the beat shorter" if dead else ""))
    shutil.rmtree(tmp)

    if a.sync and a.words:
        cues = json.loads(Path(a.sync).read_text()); words = json.loads(Path(a.words).read_text())
        norm = lambda w: re.sub(r"[^\w]", "", w.lower())
        off = []
        for c in cues:
            # "tiga|37": the transcriber writes a number as digits on one run and as words on the next
            alts = {norm(x) for x in c["word"].split("|")}
            hits = [w for w in words if norm(w["word"]) in alts]
            if not hits:
                off.append(f'"{c["word"]}" not in the transcript'); continue
            w = min(hits, key=lambda w: abs(w["start"] - c["film"]))
            d = c["film"] - w["start"]                       # negative: the picture leads the word
            if d < -float(c.get("tol", 0.35)) or d > 0.1:
                off.append(f'"{c["word"]}" said at {w["start"]:.2f} s, picture at {c["film"]:.2f} s ({d:+.2f} s)')
        check("sync", not off, f"{len(cues)} pictures on their words" if not off else "; ".join(off) + "; move the T time or VO_STARTS in beats.js")
    elif a.sync or a.words:
        sys.exit("--sync and --words go together")

    # one sheet holds 36 (contact) or 30 (phone) frames, so a longer film gets more pages:
    # contact.png, contact-2.png, ... and phone.png, phone-2.png, ... A single page cut a 60 s
    # film at 18 s and 36 s, and a partner scored the missing half as "nothing happens" (Nov 2026).
    sheets = []
    for name, vf in (("contact", "fps=2,scale=270:-1,tile=6x6"), ("phone", "fps=1,scale=360:-1,tile=6x5")):
        for old in out.glob(f"{name}*.png"):
            old.unlink()
        run(["ffmpeg", "-v", "error", "-y", "-i", str(film), "-vf", vf, "-start_number", "1", str(out / f"{name}-%d.png")])
        (out / f"{name}-1.png").rename(out / f"{name}.png")
        pages = [f"{name}.png"] + sorted((q.name for q in out.glob(f"{name}-*.png")), key=lambda n: int(n.split("-")[1][:-4]))
        sheets.append(", ".join(pages))

    vbr = int(v.get("bit_rate") or 0) / 1e6
    note = (f"- note video {vbr:.1f} Mbps: the apps re-encode every upload, and a thin source loses fine gradients first; "
            "render with --video-bitrate 12M (hyperframes render)" if 0 < vbr < 8 else "")
    lines = [f"# QA: {film.name}", ""]
    for name, ok, detail in results:
        lines.append(f"- {'PASS' if ok else 'FAIL'} {name}: {detail}")
    if note:
        lines.append(note)
    lines += ["", f"Sheets: {sheets[0]} (2 fps, 18 s a page); {sheets[1]} (1 fps at 360 px, 30 s a page).",
              "Send every page to the critique loop; this report covers only what can be measured.", ""]
    (out / "report.md").write_text("\n".join(lines))
    print("\n".join(lines[2:2 + len(results) + (1 if note else 0)]))
    print(f"report: {out / 'report.md'}")
    sys.exit(0 if all(ok for _, ok, _ in results) else 1)


if __name__ == "__main__":
    main()
