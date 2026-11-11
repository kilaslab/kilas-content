#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Voice-over for a Reel: one ElevenLabs clip per beat, from the `vo:` lines of copy.md.

  vo_elevenlabs.py <item>/copy.md <outdir> [--voice ID] [--speed 1.05] [--model ID] [--only 2,4]
  vo_elevenlabs.py --verify <outdir or audio/video file> [<item>/copy.md] [--words words.json]

Model: eleven_multilingual_v2 by default. For a script in another language with English
acronyms in it (AI, API), use --model eleven_v3: in Indonesian sentences v2 read "API" as the
word "api" and "AI" with Indonesian letters, v3 read both with English letter names (measured,
Nov 2026). v3 takes no previous/next text, so each clip is its own take.

Generate: each non-empty `vo:` line becomes <outdir>/vo<N>.mp3 (raw from ElevenLabs) and,
when ffmpeg is present and --speed is not 1, <outdir>/vo<N>-x<speed>.mp3. Neighbouring lines
go along as previous_text/next_text so the clips sound like one take. Prints each clip's
duration: put each one on the timeline as its own <audio> with that duration.

Verify: transcribes the clips (or one rendered file) with ElevenLabs speech-to-text and
prints the transcript beside the script, flagging words that differ, in order. With --words,
it also saves every word with its start and end time (seconds from the start of the file):
time each character reaction 0-3 frames before its word. Catch misreadings
here ("QRIS" heard as "queries"); write acronyms and numbers the way they are said.

The key comes from ELEVENLABS_API_KEY or a .env file in the working directory; it is never
printed. Needs the key permissions text_to_speech (and speech_to_text for --verify).
Exit codes: 0 ok, 2 usage, 3 key missing or lacks a permission, 1 other failure.
"""
import argparse, difflib, json, os, re, shutil, subprocess, sys, tempfile, unicodedata, urllib.request, urllib.error, uuid
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


def call(req, tries=3):
    # eleven_v3 can take minutes for a long line and sometimes stalls: wait longer, then retry
    for n in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")[:300]
            if e.code in (429, 500, 502, 503) and n + 1 < tries:
                print(f"ElevenLabs HTTP {e.code}, retrying", file=sys.stderr)
                continue
            print(f"ElevenLabs HTTP {e.code}: {body}", file=sys.stderr)
            sys.exit(3 if e.code in (401, 403) else 1)
        except (TimeoutError, OSError) as e:
            if n + 1 == tries:
                print(f"ElevenLabs request failed after {tries} tries: {e}", file=sys.stderr)
                sys.exit(1)
            print(f"ElevenLabs request timed out ({e}), retrying", file=sys.stderr)


def vo_lines(copy_md):
    return [m.strip() for m in re.findall(r"^vo:(.*)$", Path(copy_md).read_text(), re.M) if m.strip()]


def duration(path):
    if not shutil.which("ffprobe"):
        return None
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True).stdout.strip()
    return float(out) if out else None


V3PLUS = re.compile(r"eleven_v[3-9]")


def generate(args):
    lines = vo_lines(args.copy)
    if not lines:
        print("no vo: lines in " + args.copy, file=sys.stderr)
        sys.exit(2)
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    only = {int(n) for n in args.only.split(",")} if args.only else None
    if only is None:
        for old in out.glob("vo*.mp3"):  # clips from an earlier, longer script would pollute --verify
            old.unlink()
    if args.speed != 1 and not shutil.which("ffmpeg"):
        print(f"warning: ffmpeg not found, speed {args.speed} not applied; clips stay at 1.0", file=sys.stderr)
    k = key()
    made = []
    manifest = out / "vo-manifest.json"
    if only is not None and manifest.exists():
        made = json.loads(manifest.read_text())
    for i, text in enumerate(lines):
        if only is not None and i not in only:
            continue
        body = {"text": text, "model_id": args.model}
        if not V3PLUS.match(args.model):
            # v3 and later take neither these settings nor previous/next text (request stitching)
            body["voice_settings"] = {"stability": 0.45, "similarity_boost": 0.8, "style": 0.3, "use_speaker_boost": True}
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
        made = [m for m in made if m.get("file") != raw.name] + [{"file": raw.name, "final": final.name, "seconds": d, "text": text}]
        print(f"{final}\t{d:.3f}s\t{text}" if d else f"{final}\t{text}")
    made.sort(key=lambda m: int(re.match(r"vo(\d+)", m["file"]).group(1)))
    manifest.write_text(json.dumps(made, indent=1, ensure_ascii=False))


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
    return json.loads(call(req))


def words(s):
    s = unicodedata.normalize("NFKC", s.lower())
    return re.findall(r"[a-z0-9]+", s)


def verify(args):
    k = key()
    target = Path(args.target)
    if target.is_dir():
        manifest = target / "vo-manifest.json"
        if manifest.exists():
            files = [target / m["file"] for m in json.loads(manifest.read_text())]
        else:
            files = sorted((f for f in target.glob("vo*.mp3") if "-x" not in f.stem), key=lambda p: (len(p.stem), p.stem))
    else:
        files = [target]
    results = [stt(f, k) for f in files]
    heard = " ".join(r.get("text", "") for r in results)
    if args.words:
        if len(files) != 1:
            print("--words needs one file (the rendered film or the full VO track), not a folder of clips", file=sys.stderr)
        else:
            ws = [{"word": w.get("text"), "start": w.get("start"), "end": w.get("end")}
                  for w in results[0].get("words", []) if w.get("type", "word") == "word"]
            Path(args.words).write_text(json.dumps(ws, indent=1, ensure_ascii=False))
            print(f"WORDS  {len(ws)} words with times -> {args.words}")
    print("HEARD:  " + heard)
    if args.copy:
        script = " ".join(vo_lines(args.copy))
        print("SCRIPT: " + script)
        a, b = words(script), words(heard)
        diffs = [(op, " ".join(a[i1:i2]), " ".join(b[j1:j2]))
                 for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes() if op != "equal"]
        if diffs:
            for op, want, got in diffs:
                print(f"DIFF   {op:7} script: '{want}'  heard: '{got}'")
            print("Check each, in order: a spoken spelling (kris, titik i-d) is fine; a wrong, missing,")
            print("or reordered word means rewrite the vo: line and regenerate.")
        else:
            print("OK     the transcript matches the script word for word, in order")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verify", metavar="TARGET", help="outdir with vo*.mp3, or a rendered audio/video file")
    p.add_argument("copy", nargs="?", help="<item>/copy.md")
    p.add_argument("outdir", nargs="?")
    p.add_argument("--voice", default=DEFAULT_VOICE)
    p.add_argument("--model", default="eleven_multilingual_v2")
    p.add_argument("--speed", type=float, default=1.05)
    p.add_argument("--only", help="regenerate only these clip numbers (e.g. 2 or 2,4); the others stay")
    p.add_argument("--words", help="with --verify on one file: save word timings as JSON")
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
