#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Does the voice-over say an acronym with English letter names? A measured check.

  vo_acronym_check.py <clip.mp3> <words.json> AI API [...]

words.json comes from `vo_elevenlabs.py --verify <clip> --words <json>`. For every word in the
clip that matches one of the acronyms, this prints the second formant (F2) at the start of the word
and a verdict. It works for acronyms that start with A: English says the letter as /eI/
("ei", F2 high, about 1900-2400 Hz for a male voice), Indonesian and most other languages say
/a/ (F2 low, about 1000-1450 Hz). A transcript cannot tell the two apart: "API" read as the
Indonesian word "api" (fire) and "API" said in English both came back as text that looked fine,
or as "Api" (Nov 2026). Listen to the clip as well; the owner's ear decides.

Exit codes: 0 every match sounds English, 1 a match sounds local or unclear, 2 usage.
Pure Python (no numpy): ffmpeg decodes, an LPC spectrum per 30 ms frame finds the formants.
"""
import cmath, json, math, re, subprocess, sys

SR = 10000


def load(path):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"])
    return [int.from_bytes(raw[i:i + 2], "little", signed=True) / 32768.0 for i in range(0, len(raw) - 1, 2)]


def lpc(x, order=12):
    r = [sum(x[i] * x[i + k] for i in range(len(x) - k)) for k in range(order + 1)]
    if r[0] <= 0:
        return None
    a, e = [1.0] + [0.0] * order, r[0]
    for i in range(1, order + 1):
        k = -(r[i] + sum(a[j] * r[i - j] for j in range(1, i))) / e
        a = [a[j] + k * a[i - j] if 0 < j < i else a[j] for j in range(order + 1)]
        a[i] = k
        e *= 1 - k * k
        if e <= 0:
            return None
    return a


def formants(frame):
    """F1, F2 (Hz) from the peaks of the LPC envelope, or None when the frame is unvoiced."""
    f = [frame[0]] + [frame[i] - 0.63 * frame[i - 1] for i in range(1, len(frame))]
    n = len(f)
    f = [v * (0.54 - 0.46 * math.cos(2 * math.pi * i / (n - 1))) for i, v in enumerate(f)]
    a = lpc(f)
    if a is None:
        return None
    freqs = range(150, 3600, 25)
    env = []
    for hz in freqs:
        w = 2 * math.pi * hz / SR
        z = sum(c * cmath.exp(-1j * w * k) for k, c in enumerate(a))
        env.append(-20 * math.log10(abs(z) + 1e-12))
    peaks = [freqs[i] for i in range(1, len(env) - 1) if env[i] > env[i - 1] and env[i] >= env[i + 1]]
    return (peaks[0], peaks[1]) if len(peaks) >= 2 else None


def f2_span(x, start, end, q=0.5):
    """F2 (the q-quantile over voiced frames) between two times in seconds."""
    a, b = int(start * SR), int(end * SR)
    win, hop = int(0.03 * SR), int(0.01 * SR)
    frames = [x[i:i + win] for i in range(a, max(a + 1, b - win), hop)]
    energy = [math.sqrt(sum(v * v for v in fr) / len(fr)) for fr in frames if fr]
    if not energy:
        return None, 0
    gate = 0.35 * max(energy)
    f2 = []
    for fr, e in zip(frames, energy):
        if e >= gate:
            fm = formants(fr)
            if fm and fm[1] > 600:
                f2.append(fm[1])
    f2.sort()
    return (f2[int(q * (len(f2) - 1))] if f2 else None), len(f2)


def main():
    if len(sys.argv) < 4:
        print(__doc__.split("\n\n")[1]); sys.exit(2)
    clip, words, targets = sys.argv[1], json.load(open(sys.argv[2])), {t.upper() for t in sys.argv[3:]}
    x = load(clip)
    bad = found = 0
    for w in words:
        t = re.sub(r"[^A-Za-z]", "", w["word"]).upper()
        if t not in targets:
            continue
        found += 1
        s0, e0 = w["start"], w["end"]
        f2, n = f2_span(x, s0, s0 + 0.35 * (e0 - s0) + 0.03)
        # "AI" in English is /eI.aI/: after the high start the second letter dips to /a/.
        # A voice that says "e-i" stays high all the way (an owner heard that as accented).
        dip = f2_span(x, s0 + 0.4 * (e0 - s0), e0, q=0.25)[0] if t == "AI" else None
        if f2 is None:
            verdict, bad = "no voiced frames: listen", bad + 1
        elif f2 >= 1700 and dip is not None and dip > 1750:
            verdict, bad = f"high start but no /aI/ dip (min F2 {dip:.0f}): listen", bad + 1
        elif f2 >= 1700:
            verdict = "English /eI/" + (f" + /aI/ dip {dip:.0f}" if dip else "")
        elif f2 <= 1500:
            verdict, bad = "local /a/: rewrite or switch model (eleven_v3 read AI/API in English)", bad + 1
        else:
            verdict, bad = "unclear: listen", bad + 1
        print(f"{w['word']:10s} {w['start']:6.2f}-{w['end']:5.2f}s  F2 {f2 or 0:5.0f} Hz ({n} frames)  {verdict}")
    if not found:
        print("none of " + ", ".join(sorted(targets)) + " in the transcript: check the spelling the STT used")
        sys.exit(1)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
