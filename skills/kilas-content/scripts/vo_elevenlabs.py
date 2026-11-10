#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Voice-over for a Reel: one ElevenLabs clip per beat, from the `vo:` lines of copy.md.

  vo_elevenlabs.py <item>/copy.md <outdir> [--voice ID] [--speed 1.05] [--model ID]
  vo_elevenlabs.py --verify <outdir or audio/video file> [<item>/copy.md]

Generate: each non-empty `vo:` line becomes <outdir>/vo<N>.mp3 (raw from ElevenLabs) and,
when ffmpeg is present and --speed is not 1, <outdir>/vo<N>-x<speed>.mp3. Neighbouring lines
go along as previous_text/next_text so the clips sound like one take. Prints each clip's
duration: put each one on the timeline as its own <audio> with that duration.

Verify: transcribes the clips (or one rendered file) with ElevenLabs speech-to-text and
prints the transcript beside the script, flagging words that differ. Catch misreadings
here ("QRIS" heard as "queries"); write acronyms and numbers the way they are said.

The key comes from ELEVENLABS_API_KEY or a .env file in the working directory; it is never
printed. Needs the key permissions text_to_speech (and speech_to_text for --verify).
Exit codes: 0 ok, 2 usage, 3 key missing or lacks a permission, 1 other failure.
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile, unicodedata, urllib.request, urllib.error, uuid
from pathlib import Path

API = "https://api.elevenlabs.io/v1"
DEFAULT_VOICE = "cgSgspJ2msm6clMCkdW9"  # Jessica: young female, conversational; tested in Indonesian


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


def call(req):
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:300]
        print(f"ElevenLabs HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(3 if e.code in (401, 403) else 1)


def vo_lines(copy_md):
    return [m.strip() for m in re.findall(r"^vo:(.*)$", Path(copy_md).read_text(), re.M) if m.strip()]


def duration(path):
    if not shutil.which("ffprobe"):
        return None
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True).stdout.strip()
    return float(out) if out else None


def generate(args):
    lines = vo_lines(args.copy)
    if not lines:
        print("no vo: lines in " + args.copy, file=sys.stderr)
        sys.exit(2)
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    k = key()
    for i, text in enumerate(lines):
        body = {"text": text, "model_id": args.model,
                "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.3, "use_speaker_boost": True}}
        if i:
            body["previous_text"] = lines[i - 1]
        if i + 1 < len(lines):
            body["next_text"] = lines[i + 1]
        req = urllib.request.Request(f"{API}/text-to-speech/{args.voice}?output_format=mp3_44100_128",
                                     data=json.dumps(body).encode(), method="POST",
                                     headers={"xi-api-key": k, "Content-Type": "application/json"})
        raw = out / f"vo{i}.mp3"
        raw.write_bytes(call(req))
        final = raw
        if args.speed != 1 and shutil.which("ffmpeg"):
            final = out / f"vo{i}-x{args.speed:g}.mp3"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-filter:a", f"atempo={args.speed}",
                            "-ar", "44100", "-b:a", "160k", str(final)], check=True)
        d = duration(final)
        print(f"{final}\t{d:.3f}s\t{text}" if d else f"{final}\t{text}")


def stt(path, k):
    wav = Path(tempfile.mkdtemp()) / "a.wav"
    src = path
    if shutil.which("ffmpeg"):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-vn", "-ac", "1", "-ar", "16000", str(wav)], check=True)
        src = wav
    b = uuid.uuid4().hex
    parts = []
    for name, val in (("model_id", "scribe_v1"),):
        parts.append(f'--{b}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{val}\r\n'.encode())
    parts.append(f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="{Path(src).name}"\r\nContent-Type: application/octet-stream\r\n\r\n'.encode()
                 + Path(src).read_bytes() + f"\r\n--{b}--\r\n".encode())
    req = urllib.request.Request(f"{API}/speech-to-text", data=b"".join(parts), method="POST",
                                 headers={"xi-api-key": k, "Content-Type": f"multipart/form-data; boundary={b}"})
    return json.loads(call(req)).get("text", "")


def words(s):
    s = unicodedata.normalize("NFKC", s.lower())
    return re.findall(r"[a-z0-9]+", s)


def verify(args):
    k = key()
    target = Path(args.target)
    files = sorted(target.glob("vo*.mp3"), key=lambda p: (len(p.stem), p.stem)) if target.is_dir() else [target]
    files = [f for f in files if "-x" not in f.stem] if target.is_dir() else files
    heard = " ".join(stt(f, k) for f in files)
    print("HEARD:  " + heard)
    if args.copy:
        script = " ".join(vo_lines(args.copy))
        print("SCRIPT: " + script)
        a, b = words(script), words(heard)
        missing = [w for w in a if w not in b]
        extra = [w for w in b if w not in a]
        if missing or extra:
            print(f"DIFF   not heard: {sorted(set(missing))}  heard instead: {sorted(set(extra))}")
            print("Check each: a spoken spelling (kris, ei-ai) is fine; a wrong word means rewrite and regenerate.")
        else:
            print("OK     every script word was heard")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verify", metavar="TARGET", help="outdir with vo*.mp3, or a rendered audio/video file")
    p.add_argument("copy", nargs="?", help="<item>/copy.md")
    p.add_argument("outdir", nargs="?")
    p.add_argument("--voice", default=DEFAULT_VOICE)
    p.add_argument("--model", default="eleven_multilingual_v2")
    p.add_argument("--speed", type=float, default=1.05)
    args = p.parse_args()
    if args.verify:
        args.target = args.verify
        verify(args)
    elif args.copy and args.outdir:
        generate(args)
    else:
        p.print_usage()
        sys.exit(2)


if __name__ == "__main__":
    main()
