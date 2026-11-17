// SPDX-License-Identifier: GPL-3.0-or-later
// Lists every piece of text the overlay shows at this second, for scripts/overlay_audit.py:
// where it sits on the 1080 x 1920 frame, how tall its letters really are after every scale,
// and its colour. Loaded only with ?audit (scene.js). Mark text that is small on purpose (a
// timestamp inside a chat bubble) with data-audit="fine" on it or on a parent; it is then
// measured against the fine-print floor instead of the reading size.
export function audit(root) {
  const stage = root.getBoundingClientRect(), k = 1080 / stage.width;
  const out = [];
  const shown = (el) => {
    let a = 1;
    for (let e = el; e && e !== root.parentElement; e = e.parentElement) {
      const cs = getComputedStyle(e);
      if (cs.display === "none" || cs.visibility === "hidden") return 0;
      a *= parseFloat(cs.opacity);
    }
    return a;
  };
  // the overlay ignores the pointer; hit-testing (what is on top at a point) needs it switched on
  const hit = document.createElement("style"); hit.textContent = "#" + root.id + ", #" + root.id + " * { pointer-events: auto !important; }";
  document.head.appendChild(hit);
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  const seen = new Map();
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    const text = n.nodeValue.replace(/\s+/g, " ").trim();
    if (!text) continue;
    const el = n.parentElement, alpha = shown(el);
    if (alpha < 0.9) continue; // fading in or out: judged once it has arrived
    const r = document.createRange(); r.selectNodeContents(n);
    const rects = [...r.getClientRects()].filter((q) => q.width > 1 && q.height > 1);
    if (!rects.length) continue;
    // text scrolled out of a clipped panel, or wholly off the frame, is not on screen: leave it out
    let cx0 = stage.left, cy0 = stage.top, cx1 = stage.right, cy1 = stage.bottom;
    for (let e = el.parentElement; e && e !== root.parentElement; e = e.parentElement) {
      const s = getComputedStyle(e), q = e.getBoundingClientRect();
      if (s.overflow !== "visible") { cx0 = Math.max(cx0, q.left); cy0 = Math.max(cy0, q.top); cx1 = Math.min(cx1, q.right); cy1 = Math.min(cy1, q.bottom); }
      // a panel that fades its top edge out (a chat list scrolling away): the fade is not reading room
      const mk = s.maskImage || s.webkitMaskImage || "";
      const fade = /^linear-gradient\((transparent|rgba\(0, 0, 0, 0\))/.test(mk) && mk.match(/([\d.]+)px\s*\)\s*$/);
      if (fade) cy0 = Math.max(cy0, q.top + parseFloat(fade[1]) * (q.height / (e.offsetHeight || q.height)));
    }
    const bx0 = Math.min(...rects.map((q) => q.left)), by0 = Math.min(...rects.map((q) => q.top));
    const bx1 = Math.max(...rects.map((q) => q.right)), by1 = Math.max(...rects.map((q) => q.bottom));
    const vis = Math.max(0, Math.min(bx1, cx1) - Math.max(bx0, cx0)) * Math.max(0, Math.min(by1, cy1) - Math.max(by0, cy0)) / ((bx1 - bx0) * (by1 - by0));
    const onStage = Math.min(bx1, stage.right) > Math.max(bx0, stage.left) && Math.min(by1, stage.bottom) > Math.max(by0, stage.top);
    if (!onStage || vis < 0.6) continue;
    // covered by another overlay (a stamp on a receipt, a card over the chat): not readable now, so
    // not judged now. Three points along the text.
    let hid = 0;
    for (const f of [0.25, 0.5, 0.75]) {
      for (const e of document.elementsFromPoint(bx0 + (bx1 - bx0) * f, (by0 + by1) / 2)) {
        if (e === el || el.contains(e) || e.contains(el)) break;
        if (!root.contains(e)) break;
        const s = getComputedStyle(e), bgc = (s.backgroundColor.match(/[\d.]+/g) || []).map(Number);
        const paints = s.backgroundImage !== "none" || (bgc.length && (bgc.length < 4 || bgc[3] > 0.5)) || /^(IMG|CANVAS|svg)$/.test(e.tagName);
        if (paints && shown(e) >= 0.5) { hid++; break; }
      }
    }
    if (hid >= 2) continue;
    const cs = getComputedStyle(el);
    // letters scale with every transform above them: compare a line's drawn height with the
    // height the same line has in layout
    const lh = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.2;
    const scale = el.offsetHeight ? el.getBoundingClientRect().height / el.offsetHeight : 1;
    const x0 = Math.min(...rects.map((q) => q.left)), y0 = Math.min(...rects.map((q) => q.top));
    const x1 = Math.max(...rects.map((q) => q.right)), y1 = Math.max(...rects.map((q) => q.bottom));
    const item = {
      text: text.slice(0, 60), cls: (el.className && el.className.toString()) || el.tagName.toLowerCase(),
      x: (x0 - stage.left) * k, y: (y0 - stage.top) * k, w: (x1 - x0) * k, h: (y1 - y0) * k,
      px: parseFloat(cs.fontSize) * scale * k, weight: parseInt(cs.fontWeight, 10) || 400, color: cs.color, alpha,
      fine: !!el.closest('[data-audit="fine"]'), skip: (el.closest("[data-audit-skip]") || {}).dataset?.auditSkip || "",
      lineHeight: lh * scale * k,
      rects: rects.map((q) => { const l = Math.max(q.left, cx0), tp = Math.max(q.top, cy0), r2 = Math.min(q.right, cx1), b = Math.min(q.bottom, cy1);
        return [(l - stage.left) * k, (tp - stage.top) * k, (r2 - l) * k, (b - tp) * k]; }).filter((q) => q[2] > 2 && q[3] > 2),
    };
    // one entry per element: join its text nodes
    const prev = seen.get(el);
    if (prev) {
      const nx = Math.min(prev.x, item.x), ny = Math.min(prev.y, item.y);
      prev.w = Math.max(prev.x + prev.w, item.x + item.w) - nx; prev.h = Math.max(prev.y + prev.h, item.y + item.h) - ny;
      prev.x = nx; prev.y = ny; prev.text = (prev.text + " " + item.text).slice(0, 60); prev.rects.push(...item.rects);
    } else { seen.set(el, item); out.push(item); }
  }
  const tag = document.createElement("script");
  tag.type = "application/json"; tag.id = "overlay-audit";
  tag.textContent = JSON.stringify(out).replace(/</g, "\\u003c");
  document.body.appendChild(tag);
}
