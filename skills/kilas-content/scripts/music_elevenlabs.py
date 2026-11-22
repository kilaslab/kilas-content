#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Music bed for a Reel: an instrumental ElevenLabs track cut to the film's beats.

  music_elevenlabs.py plan "<brief>" --length 60 --out <item>/music/plan.json        (free)
  music_elevenlabs.py compose <item>/music/plan.json [--length 60]                    (paid)
  music_elevenlabs.py shape <item>/music/bed.mp3 --cuts 4.8,22,44,52,56.5

A Reel with VO and SFX but no bed read as empty to the owner ("masih kerasa sepi", Nov 2026).

plan: ElevenLabs drafts a composition plan from the brief (genre, instruments, tempo, mood;
no credits). Rewrite its sections by hand so each one is a stretch of the film between two
beat borders, with its duration_ms, before composing: a start on the downbeat under the hook,
the groove under the beats, a thinner bar where the story turns quiet, a lift into the payoff,
and a clean ending hit on the end card, never a fade. Keep "lines" empty (instrumental) and
put vocals, choir, and a busy lead in the negative styles: the bed sits under a voice.

compose: turns plan.json into bed.mp3 beside it, with bed.json (the plan, model, date, and
the source line for credits). The sections' durations must add up to --length (±0.5 s).
This call uses the account's credits: compose once the plan reads right, not to explore.

shape: prints the bed's loudness every half second with the cut marks, so you can see the
quiet bar and the ending land where the film needs them before mixing (`beats.js` MUSIC:
{ file: "music/bed.mp3", gain, duck }; scene3d_video.py ducks it under the voice).

The key comes from ELEVENLABS_API_KEY or a .env file in the working directory; it is never
printed. Exit codes: 0 ok, 2 usage or a plan that does not fit, 3 key missing or lacks the
music permission, 1 other failure.
"""
import argparse, datetime, json, os, re, shutil, subprocess, sys, urllib.request, urllib.error
from pathlib import Path

API = "https://api.elevenlabs.io/v1"
MODEL = "music_v1"


def key():
    k = os.environ.get("ELEVENLABS_API_KEY")
    env = Path(".env")
    if not k and env.exists():
        for line in env.read_text().splitlines():
            if line.startswith("ELEVENLABS_API_KEY="):
                k = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not k:
        print("ELEVENLABS_API_KEY not set (env or .env)", file=sys.stderr)
        sys.exit(3)
    return k


def post(path, body, tries=3):
    req = urllib.request.Request(f"{API}{path}", data=json.dumps(body).encode(), method="POST",
                                 headers={"xi-api-key": key(), "Content-Type": "application/json"})
    for n in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:400]
            if e.code in (429, 500, 502, 503) and n + 1 < tries:
                print(f"ElevenLabs HTTP {e.code}, retrying", file=sys.stderr)
                continue
            print(f"ElevenLabs HTTP {e.code}: {msg}", file=sys.stderr)
            sys.exit(3 if e.code in (401, 403) else 1)
        except (TimeoutError, OSError) as e:
            if n + 1 == tries:
                print(f"ElevenLabs request failed after {tries} tries: {e}", file=sys.stderr)
                sys.exit(1)
            print(f"ElevenLabs request timed out ({e}), retrying", file=sys.stderr)


def duration(path):
    if not shutil.which("ffprobe"):
        return None
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True).stdout.strip()
    return float(out) if out else None


def plan(args):
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(post("/music/plan", {"prompt": args.brief, "music_length_ms": int(args.length * 1000), "model_id": MODEL}))
    p = json.loads(out.read_text())
    for s in p.get("sections", []):
        print(f"  {s['duration_ms'] / 1000:5.1f} s  {s['section_name']}")
    print(f"written {out}: now set the sections to the film's beat borders, then compose")


def compose(args):
    src = Path(args.plan)
    p = json.loads(src.read_text())
    secs = p.get("sections") or []
    total = sum(s.get("duration_ms", 0) for s in secs) / 1000
    if not secs or abs(total - args.length) > 0.5:
        print(f"plan sections add up to {total:g} s, the film is {args.length:g} s: fix duration_ms first", file=sys.stderr)
        sys.exit(2)
    if any(s.get("lines") for s in secs) and not args.vocals:
        print("plan has lyric lines: a bed under a voice-over stays instrumental (or pass --vocals)", file=sys.stderr)
        sys.exit(2)
    bed = src.with_name("bed.mp3")
    bed.write_bytes(post("/music?output_format=mp3_44100_128", {"composition_plan": p, "model_id": MODEL}))
    d = duration(bed)
    rec = {"file": bed.name, "model": MODEL, "made": datetime.date.today().isoformat(), "seconds": d,
           "source": "ElevenLabs Music (music_v1), generated for this film", "plan": p}
    src.with_name("bed.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False))
    print(f"written {bed} ({d:.2f} s)" if d else f"written {bed}")


def shape(args):
    if not shutil.which("ffmpeg"):
        print("shape needs ffmpeg", file=sys.stderr)
        sys.exit(1)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", args.bed, "-af", "ebur128=peak=none", "-f", "null", "-"],
                       capture_output=True, text=True)
    pts = [(float(t), float(m)) for t, m in re.findall(r"t:\s*([\d.]+).*?M:\s*(-?[\d.]+)", r.stderr)]
    cuts = [float(c) for c in args.cuts.split(",")] if args.cuts else []
    step, mark, nxt = 0.5, 0, 0.0
    for t, m in pts:
        if t + 1e-6 < nxt:
            continue
        nxt = t + step
        cut = ""
        while mark < len(cuts) and cuts[mark] <= t:
            cut = f"  <- {cuts[mark]:g} s"; mark += 1
        bar = "#" * max(0, int((m + 40) / 1.5))
        print(f"{t:6.1f} s {m:6.1f} LUFS  {bar}{cut}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("plan"); a.add_argument("brief"); a.add_argument("--length", type=float, required=True); a.add_argument("--out", required=True)
    c = sub.add_parser("compose"); c.add_argument("plan"); c.add_argument("--length", type=float, default=60.0)
    c.add_argument("--vocals", action="store_true", help="allow lyric lines (a bed under a VO never needs them)")
    s = sub.add_parser("shape"); s.add_argument("bed"); s.add_argument("--cuts", default="")
    args = p.parse_args()
    {"plan": plan, "compose": compose, "shape": shape}[args.cmd](args)


if __name__ == "__main__":
    main()
