#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Check a piece's copy.md for AI tells, language slips, weak structure, and limits.

Copy changes after a build are slow, so the draft is checked while it is still text.
The input is a markdown file with one `## ` section per slide, post, scene, or section;
`>` lines (source notes), `<!-- -->` comments, and builder keys (chart:, photos:, ...)
are ignored.

    python3 scripts/lint_copy.py copy.md
    python3 scripts/lint_copy.py copy.md --format x --brand brands/<brand>/brand.md
    python3 scripts/lint_copy.py copy.md --lang en --format linkedin

--format  carousel (default), single, x, threads, linkedin, reels, long
--lang    auto (default), id, en
--brand   a brand pack's brand.md; its "## Banned phrases" bullets become hard failures
--brief   the item's brief.md (default: brief.md next to copy.md); its "Verbs:" line
          is the metaphor the headlines should carry
--x-premium  allow X long posts (25,000 characters) instead of 280

Besides the per-line rules it checks, for carousels and single posts: the cover's
length and caveats, the metaphor across interior headlines, and runs of short
sentences. It ends with the headline-only read (writing-craft.md section 5).

Exit code 1 when a hard rule fails. Warnings are for a human to judge: a regex cannot
tell a forced triad from a real list of three.
"""
import argparse
import os
import re
import sys

COMMON_HARD = [
    (r"—|(?<!\d)–|–(?!\d)|\s--\s", "dash as connector (use a period, comma, or colon; en dash only in number ranges)"),
    (r"!", "exclamation mark"),
    (r"\b(game[- ]changer|revolusioner|revolutionary|unlock|seamless|delve)\b", "stock buzzword"),
]
HARD = {
    "id": [
        (r"\bbukan\s+(hanya|sekadar|cuma|semata)?\b[^.?!]*\b(tapi|tetapi|melainkan|namun)\b", "contrast reveal 'bukan X, tapi Y': state Y directly"),
        (r"\bbukan\s+(hanya|sekadar|cuma|semata)\b[^.?!]*,\s*(ini|inilah|ada juga|justru)\b", "contrast reveal 'bukan cuma X, ini Y': state Y directly"),
        (r"\b(not just|not only|it's not|isn't just)\b", "English contrast reveal"),
        (r"\b(tanpa\s+\w+[^.?!]*){2,}", "negation list 'tanpa X, tanpa Y': say what does happen"),
        (r"\b(yang mana|di mana)\b", "'yang mana'/'di mana' as a relative connector: split the sentence"),
        (r"\b(hal ini dikarenakan|dikarenakan oleh|dapat dilakukan dengan cara|dalam rangka untuk|terdapat sebuah|pada saat ini|memberikan penjelasan|melakukan (pengecekan|penambahan|perubahan|perbaikan))\b", "calque or heavy nominalisation"),
        (r"^(hasilnya|jawabannya|intinya|kuncinya|faktanya|masalahnya|bagian terbaiknya|plot twist-?nya)\s*[:?]", "colon reveal / self-answered question"),
        (r"\b(di era (digital|modern|serba)|mari kita|tanpa basa-basi|wajib tahu|menjadi tonggak|momen penting|lanskap)\b", "stock phrase"),
        (r"\b(setuju\?|gimana menurutmu\?|tag temanmu|baca (lagi|ulang) kalimat|let that sink in)", "engagement bait"),
        (r"\d,\d{3}\b", "English thousands separator: Indonesian uses 19.671"),
    ],
    "en": [
        (r"\b(it's not|it is not|this isn't|this is not)\b[^.?!]*[,;]\s*(it's|it is|this is)\b", "contrast reveal 'it's not X, it's Y': state Y directly"),
        (r"\bnot (just|only)\b[^.?!]*\bbut\b", "contrast reveal 'not just X but Y'"),
        (r"(\bno \w+[.,]\s*){3,}", "negation list 'No X. No Y. No Z.'"),
        (r"^(the result|the answer|the catch|the kicker|here's the thing|the truth)\s*[:?]", "colon reveal / self-answered question"),
        (r"\b(in today's (fast-paced|digital) world|let's dive in|pivotal moment|landscape|testament to)\b", "stock phrase"),
        (r"\b(agree\?|thoughts\?|tag a friend|save this for later|let that sink in)", "engagement bait"),
    ],
}
WARN = {
    "id": [
        (r"[^,.;:]{2,40},\s[^,.;:]{2,40},\s(dan|atau|serta)\s\w+", "list of three: keep only if the meaning has three parts"),
        (r"^(itu|inilah|ini) (yang|dia)\b.{0,40}\.$", "one-line closer restating the point"),
        (r"\b(sangat|benar-benar|sungguh)\b", "intensifier: show it with a fact instead"),
        (r"\b(luar biasa|menakjubkan|fantastis|epik)\b", "hype word"),
        (r"\b(cek \d+ hal|yuk,? (kenali|simak|cari tahu)|siapa bilang|masih bingung|jangan buru-buru|tahukah kamu|ini rahasia|rahasia di balik)\b", "stock opener of media carousels: lead with the fact"),
        (r"\bUS\$", "'US$': write $ or the Rupiah amount"),
        (r"\b(runs?|run-nya)\b", "'run' in Indonesian copy: write build, percobaan, or putaran"),
        (r"\bapps?\b", "'app' in Indonesian copy: write aplikasi"),
    ],
    "en": [
        (r"[^,.;:]{2,40},\s[^,.;:]{2,40},\s(and|or)\s\w+", "list of three: keep only if the meaning has three parts"),
        (r"^(and that|that's why|this is why)\b.{0,50}\.$", "one-line closer restating the point"),
        (r"\b(very|really|truly|incredibly)\b", "intensifier: show it with a fact instead"),
        (r"\b(amazing|incredible|stunning|unforgettable|epic)\b", "hype word"),
        (r"\b\d{1,3}\.\d{3}\b", "Indonesian thousands separator in English copy (use 19,671)"),
    ],
}
# Method limits that belong in the data note, the opinion slide, or the caption, not on
# the cover (writing-craft.md section 7b).
COVER_CAVEAT = {
    "id": r"\b(bukan (uang|tagihan)|tagihan sebenarnya|yang dikutip|median|rata-rata|sampel|hanya satu (aplikasi|sampel|akun)|n ?= ?\d)",
    "en": r"\b(median|not (the )?actual|sample (size|of)|only one (app|sample)|list price|n ?= ?\d)",
}
# Keys that hold notes for the builder, not text the audience sees.
META_KEYS = {"chart", "sources", "photos", "credit", "credits", "note", "image", "shot", "asset", "visual"}
# Only these are keys (framed formats and reels); any other "Word: ..." line is copy, so
# "Hasilnya: ..." is still checked as a colon reveal. X, Threads, LinkedIn, and long-form
# copy has no keys at all.
KNOWN_KEYS = {"eyebrow", "number", "headline", "body", "sub", "stat", "statlabel", "label", "quote",
              "attribution", "tip", "tiplabel", "cta", "post", "aside", "kicker", "lede", "source",
              "onscreen", "text", "vo", "voiceover", "voice", "index"} | META_KEYS
NUMBERED_KEY = re.compile(r"^(item|card|stat|row|step)\d+(label)?$")
KEYED_FORMATS = {"carousel", "single", "reels"}
# new_item.py formats that lint as another format
ALIASES = {"thread": "x", "document": "linkedin"}
# Keys on the cover that do not count toward its word budget.
COVER_FREE_KEYS = {"eyebrow", "label", "index"}
# Keys whose text is headline text, in order.
HEADLINE_KEYS = ("number", "headline")
WORDS_PER_FRAME = {"carousel": 45, "single": 45}
CHARS_PER_SECTION = {"x": 280, "threads": 500}
COVER_WORDS = 30
ID_MARKERS = r"\b(yang|dan|di|untuk|ini|dengan|tidak|dari|ke|adalah|dalam)\b"
EN_MARKERS = r"\b(the|and|of|to|is|with|that|for|in|it|this)\b"


def sections(text: str, keyed: bool = True):
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    current, lines = None, []
    for raw in text.splitlines():
        if raw.startswith("## "):
            if current:
                yield current, lines
            current, lines = raw[3:].strip(), []
        elif current and raw.strip() and not raw.lstrip().startswith(">"):
            m = re.match(r"^\s*([A-Za-z_0-9]+):(\s|$)", raw) if keyed else None
            key = m.group(1).lower() if m else ""
            if key and key not in KNOWN_KEYS and not NUMBERED_KEY.match(key):
                key = ""
            if key in META_KEYS:
                continue
            text_ = raw[m.end():].strip() if key else raw.strip()
            if text_:
                lines.append((key, text_))
    if current:
        yield current, lines


def banned_from_brand(path: str):
    text = open(path, encoding="utf-8").read()
    m = re.search(r"^## Banned phrases\s*$(.*?)(?=^## |\Z)", text, flags=re.M | re.S)
    if not m:
        return []
    out = []
    for line in m.group(1).splitlines():
        s = line.strip()
        if s.startswith("- ") and len(s) > 2:
            out.append(s[2:].strip())
    return out


def metaphor_terms(path: str):
    """The comma-separated words on the brief's 'Verbs:' line, or None."""
    if not path or not os.path.exists(path):
        return None
    found = re.findall(r"verbs(?:/nouns)?\s*:\s*([^\n·]+)", open(path, encoding="utf-8").read(), flags=re.I)
    filled = [f for f in found if f.strip() and "<" not in f]  # skip the template's placeholder
    if not filled:
        return None
    terms = [t.strip(" .;").lower() for t in filled[0].split(",")]
    return [t for t in terms if t]


def short_runs(text: str, max_words: int = 6, run: int = 3) -> bool:
    """True when `run` sentences in a row have `max_words` words or fewer."""
    sentences = [s for s in re.split(r"(?<=[.?!])\s+", text) if s.strip()]
    streak = 0
    for s in sentences:
        streak = streak + 1 if len(s.split()) <= max_words else 0
        if streak >= run:
            return True
    return False


def detect_lang(all_text: str) -> str:
    i = len(re.findall(ID_MARKERS, all_text, flags=re.I))
    e = len(re.findall(EN_MARKERS, all_text, flags=re.I))
    return "id" if i >= e else "en"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("copy")
    ap.add_argument("--format", default="carousel", choices=["carousel", "single", "x", "threads", "linkedin", "reels", "long", "thread", "document"])
    ap.add_argument("--lang", default="auto", choices=["auto", "id", "en"])
    ap.add_argument("--brand")
    ap.add_argument("--brief")
    ap.add_argument("--x-premium", action="store_true")
    a = ap.parse_args()
    a.format = ALIASES.get(a.format, a.format)
    if not os.path.exists(a.copy):
        ap.error(f"{a.copy} not found")

    secs = list(sections(open(a.copy, encoding="utf-8").read(), keyed=a.format in KEYED_FORMATS))
    all_text = " ".join(v for _, ls in secs for _, v in ls)
    lang = detect_lang(all_text) if a.lang == "auto" else a.lang
    hard = COMMON_HARD + HARD[lang]
    banned = banned_from_brand(a.brand) if a.brand else []
    hard += [(r"(?<!\w)" + re.escape(p) + r"(?!\w)", f"brand banned phrase '{p}'") for p in banned]
    char_limit = CHARS_PER_SECTION.get(a.format)
    if a.format == "x" and a.x_premium:
        char_limit = 25000
    framed = a.format in ("carousel", "single")
    frames = [i for i, (t, _) in enumerate(secs) if not t.lower().startswith("caption")]

    print(f"lang={lang} format={a.format}" + (f" brand-banned={len(banned)}" if a.brand else ""))
    failed = False
    total_chars = 0
    for idx, (title, lines) in enumerate(secs):
        is_caption = title.lower().startswith("caption")
        is_cover = framed and frames and idx == frames[0]
        words = sum(len(v.split()) for _, v in lines)
        chars = len("\n".join(v for _, v in lines))
        total_chars += 0 if is_caption else chars
        issues = []
        if not lines and not is_caption:
            issues.append(("FAIL", "empty section: write it or delete it", ""))
        elif is_cover and not any(k in HEADLINE_KEYS or not k for k, _ in lines):
            issues.append(("FAIL", "the cover has no headline", ""))
        for key, content in lines:
            for pat, msg in hard:
                if re.search(pat, content, flags=re.I | re.M):
                    issues.append(("FAIL", msg, content))
            for pat, msg in WARN[lang]:
                if re.search(pat, content, flags=re.I | re.M):
                    issues.append(("warn", msg, content))
            if a.format == "reels" and key in ("onscreen", "text") and len(content.split()) > 8:
                issues.append(("warn", "on-screen text over 8 words", content))
            if short_runs(content):
                issues.append(("warn", "three short sentences in a row: join two of them with the relation between them", content))
            if is_cover and re.search(COVER_CAVEAT[lang], content, flags=re.I):
                issues.append(("warn", "caveat or method word on the cover: move it to the data note, opinion slide, or caption (writing-craft 7b)", content))
        if is_cover:
            cover_words = sum(len(v.split()) for k, v in lines if k not in COVER_FREE_KEYS)
            if cover_words > COVER_WORDS:
                issues.append(("warn", f"cover has {cover_words} words, eyebrow excluded (aim for <= {COVER_WORDS})", ""))
        if is_caption:
            if not lines and a.format in ("carousel", "single", "reels"):
                issues.append(("FAIL", "empty caption: write it (formats/specs.md) or delete the section", ""))
            if chars > 2200:
                issues.append(("FAIL", f"caption {chars} characters (Instagram limit 2,200)", ""))
            tags = re.findall(r"(?<!\w)#\w+", " ".join(v for _, v in lines))
            if len(tags) > 5:
                issues.append(("warn", f"{len(tags)} hashtags (Instagram allows 5)", ""))
        elif a.format in WORDS_PER_FRAME and words > WORDS_PER_FRAME[a.format]:
            issues.append(("warn", f"{words} words on one frame (aim for <= {WORDS_PER_FRAME[a.format]})", ""))
        elif char_limit and chars > char_limit:
            issues.append(("FAIL", f"{chars} characters (limit {char_limit})", ""))
        status = "ok" if not issues else f"{len(issues)} issue(s)"
        print(f"## {title}  [{words} words, {chars} chars, {status}]")
        for level, msg, line in issues:
            failed |= level == "FAIL"
            print(f"   {level}: {msg}")
            if line:
                print(f"         > {line[:110]}")
    if a.format == "linkedin" and total_chars > 3000:
        failed = True
        print(f"\nFAIL: {total_chars} characters in total (LinkedIn limit 3,000)")
    if a.format == "reels":
        vo = sum(len(v.split()) for _, ls in secs for k, v in ls if k in ("vo", "voiceover", "voice"))
        if vo:
            print(f"\nvoice-over: {vo} words, about {round(vo / 2.3)} s at 130–150 words per minute")

    if framed:
        heads = []
        for i in frames:
            h = " ".join(v for k, v in secs[i][1] if k in HEADLINE_KEYS)
            heads.append(h)
        if any(heads):
            print("\nHeadline-only read (does it tell the story to a stranger?):")
            print("  " + " ".join(h for h in heads if h))
        interior = [h for h in heads[1:-1] if h]
        brief = a.brief or os.path.join(os.path.dirname(os.path.abspath(a.copy)), "brief.md")
        terms = metaphor_terms(brief)
        if terms is None:
            shown = os.path.relpath(brief) if not os.path.relpath(brief).startswith("..") else brief
            print(f"warn: no 'Verbs:' line in {shown}: write the metaphor family there "
                  "(writing-craft 4), then lint again; metaphor not checked")
        elif interior:
            hits = sum(1 for h in interior if any(t in h.lower() for t in terms))
            note = f"metaphor ({', '.join(terms)}): in {hits} of {len(interior)} interior headlines"
            if hits < 3 and len(interior) >= 4:
                print(f"warn: {note}; carry it in at least 3 (writing-craft 4)")
            else:
                print(note)
    print("\nFAIL found: fix before building." if failed else "\nNo hard failures.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
