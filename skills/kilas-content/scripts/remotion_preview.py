#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Build a self-contained HTML storyboard & animatic preview from a Remotion Reel
BEFORE running a full MP4 render (references/motion-video.md section 2f).

  remotion_preview.py --project <dir> --composition <id> --manifest <beats.json> --out <preview.html>
                      [--stills-dir <dir>] [--skip-render] [--embed]

Manifest JSON schema:
{
  "title": "Episode 01 — Rahasia Babilonia",
  "series": "Jejak Sejarah Islam",
  "fps": 30,
  "durationSec": 55,
  "composition": "Episode01-RahasiaBabilonia",
  "itemDir": "content/items/2026-11-22-rahasia-babilonia",
  "racikan": { "Preset": "motion-doc", "Engine": "Remotion", ... },
  "hookNotes": ["Why this hook wins over the previous draft..."],
  "beats": [
    {
      "id": "b1",
      "scene": "01 · The Hook",
      "startSec": 0.0,
      "endSec": 5.0,
      "onscreen": "KENAPA DUA MALAIKAT DIKAITKAN DENGAN SIHIR?",
      "vo": "Bagaimana mungkin dua malaikat dikaitkan dengan sihir di Babilonia?",
      "action": "Cracked clay monolith slams in at frame 0 with golden diagonal fissure.",
      "sampleTimes": [0.4, 2.5, 4.4]
    }
  ]
}

Stills are rendered via `npx remotion render <composition> <stills-dir> --frames=<csv> --image-format=png`
(fast — seconds instead of a full MP4 render) so the owner can scrub, read every beat and VO line,
check 360px phone readability, and request revisions before any full MP4 render starts.
"""
import argparse
import base64
import html
import json
import os
import subprocess
import sys
from pathlib import Path


def collect_samples(manifest):
    fps = int(manifest.get("fps", 30))
    dur = float(manifest.get("durationSec", 60))
    max_frame = max(0, int(round(dur * fps)) - 1)
    beats = manifest.get("beats", [])

    samples = []
    seen_frames = set()
    for b_idx, beat in enumerate(beats):
        times = beat.get("sampleTimes")
        if not times:
            s = float(beat["startSec"])
            e = float(beat["endSec"])
            mid = s + (e - s) * 0.55
            times = [s + min(0.8, (e - s) * 0.25), mid] if (e - s) >= 5.0 else [mid]
        for t in times:
            t_f = max(0.0, min(dur - 0.05, float(t)))
            frame = min(max_frame, max(0, int(round(t_f * fps))))
            if frame in seen_frames:
                continue
            seen_frames.add(frame)
            samples.append(
                {
                    "timeSec": round(frame / fps, 2),
                    "frame": frame,
                    "beatIndex": b_idx,
                    "scene": beat.get("scene", ""),
                    "onscreen": beat.get("onscreen", ""),
                }
            )
    samples.sort(key=lambda x: x["frame"])
    return samples, fps, dur


def render_stills(project_dir, composition, stills_dir, frames):
    stills_path = Path(stills_dir)
    stills_path.mkdir(parents=True, exist_ok=True)
    frames_csv = ",".join(str(f) for f in frames)
    cmd = [
        "npx",
        "remotion",
        "render",
        composition,
        str(stills_path),
        f"--frames={frames_csv}",
        "--image-format=png",
    ]
    print(f"Rendering {len(frames)} preview stills from {composition}...")
    res = subprocess.run(cmd, cwd=str(project_dir))
    if res.returncode != 0:
        print(f"remotion_preview: render failed with code {res.returncode}", file=sys.stderr)
        sys.exit(res.returncode)


def find_still_file(stills_dir, frame):
    stills_path = Path(stills_dir)
    for width in (4, 5, 3, 2, 1):
        cand = stills_path / f"element-{frame:0{width}d}.png"
        if cand.exists():
            return cand
    matches = sorted(stills_path.glob(f"*{frame}*.png"))
    return matches[0] if matches else None


def image_src(img_path, out_html, embed):
    if embed:
        data = base64.b64encode(Path(img_path).read_bytes()).decode("ascii")
        return f"data:image/png;base64,{data}"
    return os.path.relpath(Path(img_path).resolve(), Path(out_html).resolve().parent).replace(os.sep, "/")


def build_html(manifest, samples, stills_dir, out_html, embed):
    title = manifest.get("title", "Remotion Reel Preview")
    series = manifest.get("series", "")
    fps = int(manifest.get("fps", 30))
    dur = float(manifest.get("durationSec", 60))
    comp = manifest.get("composition", "")
    item_dir = manifest.get("itemDir", "<item>")
    racikan = manifest.get("racikan", {})
    hook_notes = manifest.get("hookNotes", [])
    beats = manifest.get("beats", [])

    enriched_samples = []
    missing = []
    for s in samples:
        fpath = find_still_file(stills_dir, s["frame"])
        if not fpath:
            missing.append(s["frame"])
            continue
        enriched_samples.append({**s, "src": image_src(fpath, out_html, embed)})

    if missing:
        print(f"remotion_preview: missing rendered frames: {missing}", file=sys.stderr)
        sys.exit(1)

    full_vo = "\n\n".join(b.get("vo", "").strip() for b in beats if b.get("vo", "").strip())

    racikan_rows = "".join(
        f"<tr><th>{html.escape(str(k))}</th><td>{html.escape(str(v))}</td></tr>"
        for k, v in racikan.items()
    )
    hook_list = "".join(f"<li>{html.escape(str(n))}</li>" for n in hook_notes)

    payload = json.dumps(
        {
            "title": title,
            "fps": fps,
            "durationSec": dur,
            "beats": beats,
            "samples": enriched_samples,
            "fullVo": full_vo,
        },
        ensure_ascii=False,
    )

    return f"""<!doctype html>
<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- Generated by kilas-content/scripts/remotion_preview.py — Owner Animatic Preview BEFORE final MP4 render -->
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} · Preview Animatic</title>
<style>
  :root {{
    --bg: #0c1117;
    --panel: #131b24;
    --panel-alt: #18232f;
    --ink: #ece7dd;
    --muted: #9aa7b4;
    --gold: #c9ad80;
    --gold-dim: rgba(174, 145, 102, 0.34);
    --line: rgba(213, 197, 168, 0.14);
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--bg);
    color: var(--ink);
    font: 15px/1.55 -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif;
  }}
  .wrap {{ max-width: 1180px; margin: 0 auto; padding: 28px 20px 72px; }}
  .badge {{
    display: inline-block;
    font: 700 11px/1 ui-monospace, SFMono-Regular, Menlo, monospace;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--gold);
    border: 1px solid var(--gold-dim);
    background: rgba(174, 145, 102, 0.1);
    padding: 6px 10px;
    border-radius: 4px;
  }}
  header h1 {{ margin: 12px 0 4px; font-size: 28px; letter-spacing: 0.01em; }}
  header p {{ margin: 0; color: var(--muted); }}
  .gate-banner {{
    margin-top: 18px;
    padding: 14px 18px;
    background: rgba(174, 145, 102, 0.08);
    border-left: 3px solid var(--gold);
    border-radius: 6px;
    font-size: 14px;
  }}
  .gate-banner code {{
    display: inline-block;
    margin-top: 6px;
    padding: 4px 8px;
    background: rgba(0, 0, 0, 0.35);
    border-radius: 4px;
    color: var(--gold);
    font-size: 12px;
  }}
  .top-grid {{
    display: grid;
    grid-template-columns: 380px 1fr;
    gap: 28px;
    margin-top: 26px;
    align-items: start;
  }}
  @media (max-width: 900px) {{ .top-grid {{ grid-template-columns: 1fr; }} }}
  .phone-card {{
    position: sticky;
    top: 16px;
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 16px;
  }}
  .phone-stage {{
    width: 100%;
    max-width: 348px;
    margin: 0 auto;
    aspect-ratio: 9 / 16;
    background: #000;
    border-radius: 12px;
    overflow: hidden;
    position: relative;
    border: 1px solid var(--gold-dim);
  }}
  .phone-stage img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }}
  .phone-hud {{
    position: absolute;
    top: 10px;
    left: 10px;
    right: 10px;
    display: flex;
    justify-content: space-between;
    pointer-events: none;
  }}
  .hud-pill {{
    background: rgba(9, 13, 18, 0.82);
    border: 1px solid var(--gold-dim);
    color: var(--gold);
    padding: 4px 8px;
    border-radius: 4px;
    font: 600 11px/1.2 ui-monospace, SFMono-Regular, Menlo, monospace;
  }}
  .ctl {{
    display: flex;
    gap: 8px;
    align-items: center;
    margin-top: 12px;
  }}
  .ctl button, .btn {{
    cursor: pointer;
    font: 600 13px/1 inherit;
    padding: 9px 13px;
    border-radius: 8px;
    border: 1px solid var(--gold-dim);
    background: var(--panel-alt);
    color: var(--ink);
  }}
  .ctl button:hover, .btn:hover {{ background: rgba(174, 145, 102, 0.2); }}
  .ctl input[type="range"] {{ flex: 1; accent-color: var(--gold); }}
  .ctl output {{
    font: 600 12px/1 ui-monospace, SFMono-Regular, Menlo, monospace;
    color: var(--gold);
    min-width: 58px;
    text-align: right;
  }}
  .now-box {{
    margin-top: 12px;
    padding: 10px 12px;
    border-radius: 8px;
    background: rgba(0, 0, 0, 0.28);
    border: 1px solid var(--line);
    font-size: 13px;
  }}
  .now-box strong {{ color: var(--gold); display: block; margin-bottom: 3px; }}
  .card {{
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 20px;
  }}
  .card-head {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
  }}
  .card h2 {{ margin: 0; font-size: 17px; color: var(--gold); letter-spacing: 0.02em; }}
  .racikan-tbl, .beat-tbl {{ width: 100%; border-collapse: collapse; font-size: 13.5px; }}
  .racikan-tbl th {{
    text-align: left;
    color: var(--muted);
    padding: 6px 10px 6px 0;
    width: 150px;
    border-bottom: 1px solid var(--line);
  }}
  .racikan-tbl td {{ padding: 6px 0; border-bottom: 1px solid var(--line); }}
  .hook-notes {{ margin: 12px 0 0; padding-left: 18px; color: var(--muted); font-size: 13.5px; }}
  .hook-notes li {{ margin-bottom: 4px; }}
  .beat-tbl th {{
    text-align: left;
    color: var(--muted);
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 8px 10px;
    border-bottom: 1px solid var(--gold-dim);
  }}
  .beat-tbl td {{
    padding: 10px;
    vertical-align: top;
    border-bottom: 1px solid var(--line);
  }}
  .beat-tbl tbody tr {{ cursor: pointer; transition: background 120ms ease; }}
  .beat-tbl tbody tr:hover {{ background: rgba(255, 255, 255, 0.03); }}
  .beat-tbl tbody tr.active {{ background: rgba(174, 145, 102, 0.14); }}
  .mono {{ font: 600 12px/1.4 ui-monospace, SFMono-Regular, Menlo, monospace; color: var(--gold); white-space: nowrap; }}
  .onscreen {{ font-weight: 700; color: var(--ink); }}
  .action-note {{ font-size: 12.5px; color: var(--muted); margin-top: 4px; }}
  .stills-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 12px;
  }}
  .still-item {{
    margin: 0;
    cursor: pointer;
    border-radius: 10px;
    padding: 6px;
    background: var(--panel-alt);
    border: 1.5px solid transparent;
  }}
  .still-item.active {{ border-color: var(--gold); background: rgba(174, 145, 102, 0.14); }}
  .still-item img {{
    width: 100%;
    aspect-ratio: 9 / 16;
    object-fit: cover;
    border-radius: 6px;
    display: block;
    background: #000;
  }}
  .still-item figcaption {{
    margin-top: 6px;
    font: 600 11.5px/1.3 ui-monospace, SFMono-Regular, Menlo, monospace;
    color: var(--muted);
    display: flex;
    justify-content: space-between;
  }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <span class="badge">PRE-RENDER ANIMATIC PREVIEW · REMOTION</span>
    <h1>{html.escape(title)}</h1>
    <p>{html.escape(series)} · {dur:.0f} detik · {fps} FPS · 1080×1920 (9:16) · Composition: <strong>{html.escape(comp)}</strong></p>
    <div class="gate-banner">
      <strong>Gate Animatic (belum dirender ke MP4 penuh):</strong> Cek hook, ritme dramatis, akurasi visual, keterbacaan di lebar HP (348 px), dan naskah VO di bawah. Setelah disetujui, jalankan gate lalu render penuh:<br>
      <code>python3 &lt;skill&gt;/scripts/gate.py {html.escape(item_dir)} pass animatic --by owner --quote "ok lanjut render"</code>
    </div>
  </header>

  <section class="top-grid">
    <div class="phone-card">
      <div class="phone-stage">
        <img id="stageImg" alt="Preview frame">
        <div class="phone-hud">
          <span class="hud-pill" id="hudScene">Scene</span>
          <span class="hud-pill" id="hudTime">0.0s · f0</span>
        </div>
      </div>
      <div class="ctl">
        <button id="prevBtn" type="button" title="Frame sebelumnya">◀</button>
        <button id="playBtn" type="button">Putar</button>
        <button id="nextBtn" type="button" title="Frame berikutnya">▶</button>
        <input id="scrub" type="range" min="0" max="0" step="1" value="0" aria-label="Pilih still">
        <output id="counter">1/1</output>
      </div>
      <div class="now-box">
        <strong id="nowScene"></strong>
        <div id="nowVo"></div>
      </div>
    </div>

    <div>
      {f'''<div class="card">
        <div class="card-head"><h2>Racikan &amp; Catatan Hook</h2></div>
        <table class="racikan-tbl">{racikan_rows}</table>
        {f'<ul class="hook-notes">{hook_list}</ul>' if hook_list else ''}
      </div>''' if (racikan_rows or hook_list) else ''}

      <div class="card">
        <div class="card-head">
          <h2>Beat Map &amp; Naskah Voice-Over</h2>
          <button id="copyVoBtn" class="btn" type="button">Salin Naskah VO</button>
        </div>
        <div style="overflow-x:auto;">
          <table class="beat-tbl">
            <thead>
              <tr><th>Waktu</th><th>Di Layar &amp; Aksi Visual</th><th>Voice-Over</th></tr>
            </thead>
            <tbody id="beatsBody"></tbody>
          </table>
        </div>
      </div>
    </div>
  </section>

  <section class="card" style="margin-top: 24px;">
    <div class="card-head">
      <h2>Still Sepanjang Film (Klik untuk inspeksi di layar HP)</h2>
      <span class="mono" id="stillSummary"></span>
    </div>
    <div class="stills-grid" id="stillsGrid"></div>
  </section>
</div>

<script>
const DATA = {payload};
const stageImg = document.getElementById("stageImg");
const hudScene = document.getElementById("hudScene");
const hudTime = document.getElementById("hudTime");
const scrub = document.getElementById("scrub");
const counter = document.getElementById("counter");
const nowScene = document.getElementById("nowScene");
const nowVo = document.getElementById("nowVo");
const playBtn = document.getElementById("playBtn");
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");
const beatsBody = document.getElementById("beatsBody");
const stillsGrid = document.getElementById("stillsGrid");
const stillSummary = document.getElementById("stillSummary");
const copyVoBtn = document.getElementById("copyVoBtn");

let idx = 0;
let timer = null;

scrub.max = Math.max(0, DATA.samples.length - 1);
stillSummary.textContent = DATA.samples.length + " stills · 0.0s – " + DATA.durationSec + "s";

DATA.beats.forEach((b, bIdx) => {{
  const tr = document.createElement("tr");
  tr.dataset.beat = bIdx;
  tr.innerHTML =
    `<td class="mono">${{Number(b.startSec).toFixed(1)}}–${{Number(b.endSec).toFixed(1)}}s<br><span style="color:var(--muted)">${{b.scene || ""}}</span></td>` +
    `<td><div class="onscreen">${{(b.onscreen || "").replace(/</g, "&lt;")}}</div><div class="action-note">${{(b.action || "").replace(/</g, "&lt;")}}</div></td>` +
    `<td>${{(b.vo || "").replace(/</g, "&lt;")}}</td>`;
  tr.addEventListener("click", () => {{
    stop();
    const target = DATA.samples.findIndex((s) => s.beatIndex === bIdx);
    if (target >= 0) show(target);
  }});
  beatsBody.appendChild(tr);
}});

DATA.samples.forEach((s, sIdx) => {{
  const fig = document.createElement("figure");
  fig.className = "still-item";
  fig.dataset.idx = sIdx;
  fig.innerHTML =
    `<img src="${{s.src}}" alt="Frame ${{s.frame}}" loading="lazy">` +
    `<figcaption><span>${{s.timeSec.toFixed(1)}}s</span><span>f${{s.frame}}</span></figcaption>`;
  fig.addEventListener("click", () => {{ stop(); show(sIdx); }});
  stillsGrid.appendChild(fig);
}});

function show(i) {{
  idx = (i + DATA.samples.length) % DATA.samples.length;
  const s = DATA.samples[idx];
  const b = DATA.beats[s.beatIndex] || {{}};
  stageImg.src = s.src;
  hudScene.textContent = s.scene || b.scene || "";
  hudTime.textContent = `${{s.timeSec.toFixed(1)}}s · f${{s.frame}}`;
  scrub.value = idx;
  counter.textContent = `${{idx + 1}}/${{DATA.samples.length}}`;
  nowScene.textContent = `${{b.scene || ""}} (${{Number(b.startSec || 0).toFixed(1)}}–${{Number(b.endSec || 0).toFixed(1)}}s)`;
  nowVo.textContent = b.vo || "(Transisi / jeda visual)";

  document.querySelectorAll("#beatsBody tr").forEach((tr) => {{
    tr.classList.toggle("active", Number(tr.dataset.beat) === s.beatIndex);
  }});
  document.querySelectorAll(".still-item").forEach((el) => {{
    el.classList.toggle("active", Number(el.dataset.idx) === idx);
  }});
}}

function stop() {{
  if (timer) {{ clearInterval(timer); timer = null; }}
  playBtn.textContent = "Putar";
}}

function togglePlay() {{
  if (timer) {{ stop(); return; }}
  playBtn.textContent = "Jeda";
  timer = setInterval(() => show(idx + 1), 2200);
}}

playBtn.addEventListener("click", togglePlay);
prevBtn.addEventListener("click", () => {{ stop(); show(idx - 1); }});
nextBtn.addEventListener("click", () => {{ stop(); show(idx + 1); }});
scrub.addEventListener("input", () => {{ stop(); show(Number(scrub.value)); }});

copyVoBtn.addEventListener("click", async () => {{
  try {{
    await navigator.clipboard.writeText(DATA.fullVo);
    copyVoBtn.textContent = "Tersalin ✓";
    setTimeout(() => (copyVoBtn.textContent = "Salin Naskah VO"), 1800);
  }} catch {{
    prompt("Salin naskah VO:", DATA.fullVo);
  }}
}});

if (DATA.samples.length) show(0);
</script>
</body>
</html>
"""


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--project", default=".", help="Path to Remotion project root")
    p.add_argument("--composition", required=True, help="Remotion composition ID")
    p.add_argument("--manifest", required=True, help="Path to beats manifest JSON")
    p.add_argument("--out", required=True, help="Output preview HTML file path")
    p.add_argument("--stills-dir", default="", help="Directory for rendered PNG stills")
    p.add_argument("--skip-render", action="store_true", help="Reuse existing stills in --stills-dir")
    p.add_argument("--embed", action="store_true", help="Embed stills as base64 data URIs for a single portable HTML file")
    a = p.parse_args()

    manifest = json.loads(Path(a.manifest).read_text(encoding="utf-8"))
    samples, _, _ = collect_samples(manifest)
    if not samples:
        print("remotion_preview: manifest has no beats/samples", file=sys.stderr)
        sys.exit(2)

    stills_dir = a.stills_dir or str(Path(a.out).resolve().parent / "stills")
    if not a.skip_render:
        render_stills(a.project, a.composition, stills_dir, [s["frame"] for s in samples])

    out_path = Path(a.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    html_text = build_html(manifest, samples, stills_dir, out_path, a.embed)
    out_path.write_text(html_text, encoding="utf-8")
    print(f"Wrote {out_path} ({len(samples)} stills, embed={a.embed})")


if __name__ == "__main__":
    main()
