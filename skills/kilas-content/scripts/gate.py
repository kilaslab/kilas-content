#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""The gates of an item, kept in <item>/gates.json so a step cannot be skipped unseen.

  gate.py <item> status
  gate.py <item> pass <gate> [--by NAME] [--quote "the owner's words"] [--evidence FILE]
                             [--scores "hook=8,readability=9,..."] [--self-scored] [--note TEXT]
  gate.py <item> waive <gate> --by owner --quote "the owner's words"
  gate.py <item> require render|post [--platform instagram] [--workspace content]

Gates, in order:
  racikan    the recipe table is in brief.md and the owner saw it (or named the preset)
  partner    the second model reviewed the concept            --evidence partner/round1.md
  overlay    overlay_audit.py passed on the scene             --evidence <dir>/report.md
  animatic   the owner approved the full-length animatic      --by owner --quote "..."
  script     the owner approved the voice-over script         --by owner --quote "..."
  transcript the audio says what the script says              --evidence the --verify output
  reel_qa    reel_qa.py passed on the final MP4               --evidence <film>_qa/report.md
  critique   every critique score is 8 or more                --scores "..." --by <partner> | --self-scored
  go-<platform>  the owner said to post there, for this post  --by owner --quote "..."

A video item (copy.md says `format: reels`, or the item has storyboard.md or an MP4 in export/):
`require render` wants racikan, partner, overlay, animatic, script. `require post` wants those
plus transcript, reel_qa, critique and go-<platform>.
A still item (carousel, single, thread, ...): `require render` has nothing to check, and
`require post` wants partner (carousel only: the partner round before building) and
go-<platform>.
`require post` then prints the lessons of the tools and process areas, and for a video the
Reels already published in the plan, to read before touching the account.
A gate with --evidence passes only if the file exists and, for overlay and reel_qa, holds no
FAIL line; `require` reads the file again and refuses a reel_qa report older than the newest
MP4 in <item>/export. An owner gate needs the owner's own words in --quote. `waive` records
that the owner chose to skip a gate; nothing else skips one.
Exit codes: 0 ok, 1 a gate is missing or stale, 2 usage.
"""
import argparse, datetime as dt, glob, json, os, re, subprocess, sys
from pathlib import Path

ORDER = ["racikan", "partner", "overlay", "animatic", "script", "transcript", "reel_qa", "critique"]
RENDER = ["racikan", "partner", "overlay", "animatic", "script"]
POST = RENDER + ["transcript", "reel_qa", "critique"]
OWNER = {"animatic", "script"}
MACHINE = {"overlay", "reel_qa"}
NEEDS_EVIDENCE = {"partner", "overlay", "transcript", "reel_qa"}


def item_format(item):
    """The format new_item.py wrote in copy.md's header comment, else '' (unknown)."""
    f = Path(item) / "copy.md"
    if f.exists():
        m = re.search(r"<!--\s*format:\s*([a-z-]+)", f.read_text(errors="replace")[:600])
        if m:
            return m.group(1)
    return ""


def is_video(item):
    return (item_format(item) == "reels" or (Path(item) / "storyboard.md").exists()
            or bool(glob.glob(os.path.join(item, "export", "*.mp4"))))


def load(item):
    f = Path(item) / "gates.json"
    return json.loads(f.read_text()) if f.exists() else {"gates": {}}


def save(item, data):
    (Path(item) / "gates.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def evidence_problem(item, gate, rec):
    ev = rec.get("evidence")
    if not ev:
        return None
    path = Path(ev) if os.path.isabs(ev) else Path(item) / ev
    if not path.exists():
        return f"evidence is gone: {ev}"
    if gate in MACHINE:
        text = path.read_text(errors="replace")
        if re.search(r"^- FAIL", text, re.M):
            return f"{ev} has a FAIL line"
        if not re.search(r"^- PASS", text, re.M):
            return f"{ev} has no PASS line (not a report of that check)"
    if gate == "reel_qa":
        films = glob.glob(str(Path(item) / "export" / "*.mp4"))
        if films and max(os.path.getmtime(f) for f in films) > path.stat().st_mtime + 1:
            return f"{ev} is older than the newest MP4 in export/: run reel_qa.py on the file you will post"
    return None


def scores_problem(rec):
    sc = rec.get("scores") or {}
    if not sc:
        return "no scores recorded"
    low = [f"{k}={v}" for k, v in sc.items() if v < 8]
    return ("below 8: " + ", ".join(low)) if low else None


def state(item, data, gate):
    rec = data["gates"].get(gate)
    if not rec:
        return "missing", "not recorded"
    if rec["status"] == "waived":
        return "waived", f'waived by {rec.get("by")}: "{rec.get("quote")}"'
    prob = evidence_problem(item, gate, rec) or (scores_problem(rec) if gate == "critique" else None)
    if prob:
        return "stale", prob
    bits = [rec.get("at", "")[:10]]
    if rec.get("by"): bits.append("by " + rec["by"])
    if rec.get("quote"): bits.append('"' + rec["quote"] + '"')
    if rec.get("evidence"): bits.append(rec["evidence"])
    if rec.get("scores"): bits.append(", ".join(f"{k} {v}" for k, v in rec["scores"].items()) + (" (self-scored)" if rec.get("self_scored") else ""))
    return "pass", " · ".join(b for b in bits if b)


def published_reels(workspace):
    rows = []
    for f in sorted(glob.glob(os.path.join(workspace, "plan", "*.md"))):
        for line in open(f, encoding="utf-8"):
            cells = [c.strip() for c in line.split("|")]
            if len(cells) > 6 and any(c.lower() in ("reels", "reel") for c in cells) and re.search(r"terbit|published|posted|tayang", cells[-2], re.I):
                rows.append((cells[1], next((c for c in cells if c.startswith("[") or len(c) > 30), cells[-3])[:110], cells[-2][:90]))
    return rows


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("item"); p.add_argument("action", choices=["status", "pass", "waive", "require"])
    p.add_argument("gate", nargs="?")
    p.add_argument("--by", default=""); p.add_argument("--quote", default=""); p.add_argument("--evidence", default="")
    p.add_argument("--scores", default=""); p.add_argument("--self-scored", action="store_true"); p.add_argument("--note", default="")
    p.add_argument("--platform", default=""); p.add_argument("--workspace", default="content")
    a = p.parse_args()
    if not Path(a.item).is_dir():
        print(f"no item folder: {a.item}", file=sys.stderr); sys.exit(2)
    data = load(a.item)

    if a.action == "status":
        base = ORDER if is_video(a.item) else ["partner"]
        names = base + sorted(g for g in data["gates"] if g.startswith("go-"))
        for g in names:
            st, why = state(a.item, data, g)
            print(f"{st.upper():8} {g:11} {why}")
        return

    if a.action in ("pass", "waive"):
        g = a.gate or ""
        if g not in ORDER and not re.fullmatch(r"go-[a-z0-9]+", g):
            print(f"unknown gate '{g}'; one of: {', '.join(ORDER)}, go-<platform>", file=sys.stderr); sys.exit(2)
        rec = {"status": "pass" if a.action == "pass" else "waived", "at": dt.datetime.now().isoformat(timespec="seconds")}
        if a.action == "waive" or g in OWNER or g.startswith("go-"):
            if a.by != "owner" or not a.quote.strip():
                print(f"{g}: needs --by owner --quote \"<the owner's own words>\"", file=sys.stderr); sys.exit(2)
        if a.action == "pass" and g in NEEDS_EVIDENCE and not a.evidence:
            print(f"{g}: needs --evidence <file>", file=sys.stderr); sys.exit(2)
        if a.action == "pass" and g == "critique":
            try:
                rec["scores"] = {k.strip(): float(v) for k, v in (kv.split("=") for kv in a.scores.split(",") if kv.strip())}
            except ValueError:
                print('critique: --scores "hook=8,readability=9,motion=8,variety=8,composition=8,brand=9,sound=8"', file=sys.stderr); sys.exit(2)
            if not a.by and not a.self_scored:
                print("critique: name who scored it with --by <partner>, or pass --self-scored (and say so to the owner)", file=sys.stderr); sys.exit(2)
            rec["self_scored"] = a.self_scored
        for k in ("by", "quote", "note"):
            if getattr(a, k): rec[k] = getattr(a, k)
        if a.evidence:
            ev = Path(a.evidence)
            try:
                rec["evidence"] = str(ev.resolve().relative_to(Path(a.item).resolve()))
            except ValueError:
                rec["evidence"] = str(ev.resolve())
        prob = evidence_problem(a.item, g, rec) or (scores_problem(rec) if g == "critique" and a.action == "pass" else None)
        if prob:
            print(f"{g}: not recorded, {prob}", file=sys.stderr); sys.exit(1)
        data["gates"][g] = rec; save(a.item, data)
        print(f"{rec['status']} {g}")
        return

    stage = a.gate
    if stage not in ("render", "post"):
        print("require render | require post --platform <name>", file=sys.stderr); sys.exit(2)
    video = is_video(a.item)
    if not video:
        fmt = item_format(a.item) or "still"
        if stage == "render":
            print(f"ok: render ({fmt} item: the video gates do not apply)")
            return
        need = ["partner"] if fmt == "carousel" else []
    else:
        need = list(RENDER if stage == "render" else POST)
    if stage == "post":
        if not a.platform:
            print("require post needs --platform (instagram, threads, tiktok, ...): the owner's go is per platform", file=sys.stderr); sys.exit(2)
        need.append("go-" + a.platform.lower())
    bad = []
    for g in need:
        st, why = state(a.item, data, g)
        print(f"{st.upper():8} {g:11} {why}")
        if st in ("missing", "stale"):
            bad.append(g)
    if bad:
        print(f"\nstop: {', '.join(bad)} not passed. Do the step, then `gate.py {a.item} pass <gate> ...`; only the owner waives one.", file=sys.stderr)
        sys.exit(1)
    if stage == "post":
        here = Path(__file__).resolve().parent
        print("\nBefore touching the account, read these (lessons, area tools and process):")
        out = subprocess.run([sys.executable, str(here / "lessons.py"), "rules", a.workspace], capture_output=True, text=True).stdout
        print("\n".join(l for l in out.splitlines() if "[tools]" in l or "[process]" in l) or "  (no lessons file, or none in these areas)")
        if video:
            reels = published_reels(a.workspace)
            print("\nReels already published in the plan (two in a row are never both about the product):")
            print("\n".join(f"  {d}  {t}  [{s}]" for d, t, s in reels[-3:]) or "  (none marked published in the plan)")
        print("\nThen follow references/publishing.md for this platform, step by step.")
    print(f"\nok: {stage}")


if __name__ == "__main__":
    main()
