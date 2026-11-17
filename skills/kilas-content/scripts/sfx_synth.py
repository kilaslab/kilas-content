#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Short sound effects made with ffmpeg alone: no key, no download, the same every run.

  sfx_synth.py <out dir> [names...]      (no names: the whole kit)
  sfx_synth.py content/items/<item>/sfx pop whoosh thump

The kit, each a mono 48 kHz MP3 peaking near -3 dBFS (set the level per cue with `gain`):
  pop     a message bubble landing             tick    a button press
  whoosh  a card flying, a camera move         thump   a parcel dropping, a stamp landing
  ding    paid, done, a success                buzz    a phone vibrating on wood
  rise    something popping up or out          paper   a page turning, a receipt printing
A film that needs a sound outside the kit (a door, a crowd) takes a file instead: put
<name>.mp3 in <item>/sfx/ and name it in beats.js SFX; scene3d_video.py prefers a file there
over the kit. Exit codes: 0 written, 1 ffmpeg failed, 2 usage or an unknown name.
"""
import re, shutil, subprocess, sys
from pathlib import Path

KIT = {
    "pop": "aevalsrc='sin(2*PI*(900*t-2800*t*t))*exp(-38*t)':d=0.14:s=48000",
    "tick": "aevalsrc='sin(2*PI*2100*t)*exp(-95*t)':d=0.06:s=48000",
    "whoosh": "anoisesrc=d=0.5:c=pink:a=0.9:r=48000,bandpass=f=1100:width_type=h:w=1400,afade=t=in:d=0.22,afade=t=out:st=0.22:d=0.28",
    "thump": "aevalsrc='sin(2*PI*(120*t-130*t*t))*exp(-13*t)':d=0.32:s=48000,lowpass=f=400",
    "ding": "aevalsrc='(0.6*sin(2*PI*1318.5*t)+0.4*sin(2*PI*1975.5*t))*exp(-6*t)':d=0.8:s=48000",
    "buzz": "aevalsrc='sin(2*PI*155*t)*gt(sin(2*PI*27*t)\\,0)*exp(-1.6*t)':d=0.6:s=48000,lowpass=f=900",
    "rise": "aevalsrc='sin(2*PI*(420*t+1150*t*t))*(1-exp(-30*t))':d=0.34:s=48000,afade=t=out:st=0.2:d=0.14",
    "paper": "anoisesrc=d=0.26:c=white:a=0.8:r=48000,highpass=f=2600,afade=t=in:d=0.03,afade=t=out:st=0.06:d=0.2",
}


def make(name, out):
    f, raw = Path(out) / f"{name}.mp3", Path(out) / f".{name}.wav"
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", KIT[name], "-ac", "1", "-ar", "48000", str(raw)], capture_output=True, text=True)
    if r.returncode or not raw.exists():
        print(f"ffmpeg failed on {name}: {r.stderr.strip()[:300]}", file=sys.stderr); sys.exit(1)
    # bring the peak to -3 dBFS, whatever the recipe gave
    m = re.search(r"max_volume: (-?[\d.]+) dB", subprocess.run(["ffmpeg", "-hide_banner", "-i", str(raw), "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr)
    gain = -3.0 - float(m.group(1)) if m else 0.0
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", f"volume={gain:.2f}dB", "-c:a", "libmp3lame", "-b:a", "128k", str(f)], capture_output=True, text=True)
    raw.unlink(missing_ok=True)
    if r.returncode or not f.exists() or f.stat().st_size < 200:
        print(f"ffmpeg failed on {name}: {r.stderr.strip()[:300]}", file=sys.stderr); sys.exit(1)
    return f


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__); sys.exit(2)
    if not shutil.which("ffmpeg"):
        print("ffmpeg not found (brew install ffmpeg)", file=sys.stderr); sys.exit(1)
    names = sys.argv[2:] or list(KIT)
    bad = [n for n in names if n not in KIT]
    if bad:
        print(f"not in the kit: {', '.join(bad)} (kit: {', '.join(KIT)})", file=sys.stderr); sys.exit(2)
    Path(sys.argv[1]).mkdir(parents=True, exist_ok=True)
    for n in names:
        print(make(n, sys.argv[1]))


if __name__ == "__main__":
    main()
