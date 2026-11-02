#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Check a month plan (content/plan/YYYY-MM.md) against the brand pack.

    python3 scripts/check_plan.py content/plan/2026-11.md --brand brands/<brand>/brand.md

Reads the first markdown table that has a date column (Tanggal or Date). Columns are
matched by name in Indonesian or English: Tanggal/Date, Jam/Time, Pilar/Pillar,
Seri/Series, Format, Kanal/Channel, Judul kerja/Working title, Sumber/Source, Status.

Fails on: bad dates, dates outside the plan's month, unknown status, unknown format,
pillars or series not in the brand pack. Warns on: pillar shares more than 15 points off
the brand pack, reactive share off target, more pieces on a day than "max per day",
rows without a source. Prints a summary either way.
"""
import argparse
import collections
import datetime as dt
import os
import re
import sys

ALIASES = {
    "date": {"tanggal", "date"}, "time": {"jam", "time"}, "pillar": {"pilar", "pillar"},
    "series": {"seri", "series"}, "format": {"format"}, "channel": {"kanal", "channel", "channels"},
    "title": {"judul kerja", "working title", "judul", "title"}, "source": {"sumber", "source"},
    "status": {"status"},
}
STATUSES = {"ide", "riset", "draf", "desain", "review", "terjadwal", "terbit", "batal",
            "idea", "research", "draft", "design", "scheduled", "published", "dropped"}
FORMATS = {
    "carousel": "carousel", "single": "single", "reels": "reels", "tiktok": "reels", "shorts": "reels",
    "video": "reels", "x": "x", "thread": "thread", "x-thread": "thread", "linkedin": "linkedin",
    "document": "document", "linkedin-doc": "document", "threads": "threads", "long": "long",
    "blog": "long", "notes": "long", "newsletter": "long", "article": "long",
}
EMPTY = {"", "-", "—"}


def tables(text):
    rows, out = [], []
    for line in text.splitlines():
        if line.strip().startswith("|"):
            rows.append([c.strip() for c in line.strip().strip("|").split("|")])
        elif rows:
            out.append(rows)
            rows = []
    if rows:
        out.append(rows)
    return [t for t in out if len(t) >= 2]


def clean(name):
    return re.sub(r"\s*\((proposed|usulan)[^)]*\)", "", name, flags=re.I).strip().lower()


def section(text, title):
    m = re.search(rf"^## {re.escape(title)}\s*$(.*?)(?=^## |\Z)", text, flags=re.M | re.S)
    return m.group(1) if m else ""


def brand_pack(path):
    text = open(path, encoding="utf-8").read()
    pillars, series, cadence = {}, set(), {}
    for t in tables(section(text, "Pillars")):
        head = [h.lower() for h in t[0]]
        si = next((i for i, h in enumerate(head) if h.startswith("share")), None)
        for r in t[2:]:
            m = re.search(r"(\d+(?:[.,]\d+)?)\s*%", r[si]) if si is not None and si < len(r) else None
            pillars[clean(r[0])] = float(m.group(1).replace(",", ".")) if m else None
    for t in tables(section(text, "Series")):
        for r in t[2:]:
            series.add(clean(r[0]))
    for line in section(text, "Cadence").splitlines():
        m = re.match(r"\s*-\s*([a-z ]+):\s*(\d+)", line, flags=re.I)
        if m:
            cadence[m.group(1).strip().lower()] = int(m.group(2))
    return pillars, series, cadence


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan")
    ap.add_argument("--brand")
    ap.add_argument("--month", help="YYYY-MM; default from the file name")
    a = ap.parse_args()

    text = open(a.plan, encoding="utf-8").read()
    month = a.month or (re.search(r"(\d{4}-\d{2})", os.path.basename(a.plan)) or [None, None])[1]
    table = None
    for t in tables(text):
        head = [h.lower() for h in t[0]]
        if any(h in ALIASES["date"] for h in head):
            table = t
            break
    if not table:
        print("FAIL: no table with a Tanggal/Date column")
        return 1
    head = [h.lower() for h in table[0]]
    col = {k: next((i for i, h in enumerate(head) if h in v), None) for k, v in ALIASES.items()}
    rows = [r + [""] * (len(head) - len(r)) for r in table[2:]]
    get = lambda r, k: r[col[k]].strip() if col[k] is not None else ""

    pillars, series, cadence = brand_pack(a.brand) if a.brand else ({}, set(), {})
    fails, warns = [], []
    per_day, per_pillar, per_status, per_format = (collections.Counter() for _ in range(4))
    reactive = 0
    for n, r in enumerate(rows, 1):
        d = get(r, "date")
        try:
            day = dt.date.fromisoformat(d)
            if month and d[:7] != month:
                fails.append(f"row {n}: {d} is outside {month}")
            per_day[d] += 1
        except ValueError:
            fails.append(f"row {n}: date '{d}' is not YYYY-MM-DD")
        st = get(r, "status").lower()
        per_status[st] += 1
        if st not in STATUSES:
            fails.append(f"row {n}: status '{st}' (use ide, riset, draf, desain, review, terjadwal, terbit, batal)")
        fm = get(r, "format").lower()
        if fm not in FORMATS:
            fails.append(f"row {n}: format '{fm}' (use {', '.join(sorted(set(FORMATS.values())))})")
        per_format[FORMATS.get(fm, fm)] += 1
        p = clean(get(r, "pillar"))
        per_pillar[p] += 1
        if pillars and p not in pillars:
            fails.append(f"row {n}: pillar '{get(r, 'pillar')}' is not in the brand pack")
        s = clean(get(r, "series"))
        if series and s not in EMPTY and s not in series:
            fails.append(f"row {n}: series '{get(r, 'series')}' is not in the brand pack")
        src = get(r, "source").lower()
        if src in EMPTY:
            warns.append(f"row {n}: no source (use a URL, a file, 'evergreen', or 'reaktif')")
        if src in ("reaktif", "reactive"):
            reactive += 1

    total = len(rows)
    maxday = cadence.get("max per day")
    if maxday:
        for d, c in sorted(per_day.items()):
            if c > maxday:
                warns.append(f"{d}: {c} pieces (brand max per day {maxday})")
    if pillars and total:
        for p, target in pillars.items():
            if target is None:
                continue
            share = 100 * per_pillar.get(p, 0) / total
            if abs(share - target) > 15:
                warns.append(f"pillar '{p}': {share:.0f}% of rows vs {target:.0f}% target")
    target_reactive = cadence.get("reactive share")
    if target_reactive is not None and total:
        share = 100 * reactive / total
        if abs(share - target_reactive) > 15:
            warns.append(f"reactive slots: {share:.0f}% vs {target_reactive}% target")

    print(f"{total} rows" + (f" for {month}" if month else ""))
    print("pillars:", ", ".join(f"{k} {v}" for k, v in per_pillar.most_common()))
    print("formats:", ", ".join(f"{k} {v}" for k, v in per_format.most_common()))
    print("status:", ", ".join(f"{k} {v}" for k, v in per_status.most_common()))
    print(f"reactive: {reactive}")
    for w in warns:
        print("warn:", w)
    for f in fails:
        print("FAIL:", f)
    print("\nFAIL found." if fails else "\nNo hard failures.")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
