// SPDX-License-Identifier: GPL-3.0-or-later
// Paste this at the top of a use_figma 'code' string, or bundle it with
// scripts/figma_bundle.py. Plain Plugin API JavaScript: no imports, top-level await is fine.
// 1. Replace the BRAND block with the one in the brand pack's design.md.
// 2. Set PAGE, N, REBUILD, and SCHEME (a key of BRAND.schemes; null = BRAND.scheme).
// 3. Build each frame with slide() and the layouts below, choosing variants and the
//    colour scheme as references/design-variety.md says; end with
//    'return { media, issues: layoutCheck() }' (example at the bottom).
//    scripts/figma-gallery.js draws every variant; figma-gallery-schemes.js every scheme.
// It has no backticks or dollar-brace sequences, so it embeds in a JS template literal as is.
//
// Colour:   useScheme, inkOn, accentOn, contrast (text colours are picked by contrast,
//           so every layout reads on every scheme).
// Building blocks: R, E, T, measure, headline (marks: 'hl', 'italic', 'color', 'underline'),
//   body, header, footer, slide, plate, vgrad, duotone, anchorBottom.
// Covers:   coverDark, coverSplit, coverType, coverChart, coverQuote.
// Data:     table, barChart, columnChart, bigStat, versus, dots, statCards.
// Interior: labelledItems, splitPlate, fullBleed, steps, quote.
// Evidence: artefact (style 'plain' | 'window' | 'tilt').
// Opinion:  tipCard, checklist, statement.
// Close:    closeSlide (variant 'dark' | 'light').
// Accents:  decor ('bigIndex' | 'dots' | 'ticks').
// Checks:   layoutCheck (includes overflowCheck and a rhythm note).

// ---- from brands/<brand>/design.md ----
const BRAND = {
  site: 'example.com',
  handle: '@brand',
  logo: { letter: 'B', wordmark: 'Brand' },
  swipe: 'GESER  →',
  end: 'SELESAI',
  sourcesLabel: 'SUMBER',
  scheme: 'utama',
  schemes: {
    utama: { ground: '#FFFFFF', text: '#111111', dark: '#111111', onDark: '#FFFFFF', primary: '#1A3D7C', surface: '#EEF1F5', highlight: '#FFD84D', muted: '#5C6670', mutedDark: '#A7B0B8', rule: '#DDE2E7',
      duotone: { light: ['#EEF1F5', '#1A3D7C'], dark: ['#A7B0B8', '#111111'] } },
  },
  fonts: {
    display: { family: 'Inter', style: 'Bold' }, displayRegular: { family: 'Inter', style: 'Regular' }, displayItalic: { family: 'Inter', style: 'Italic' },
    body: { family: 'Inter', style: 'Regular' }, bodyMedium: { family: 'Inter', style: 'Medium' }, bodyBold: { family: 'Inter', style: 'Bold' },
    label: { family: 'Roboto Mono', style: 'Regular' }, arrow: { family: 'Inter', style: 'Medium' },
  },
};
// ---------------------------------------

const PAGE = '<Item> (<format>)';
const N = 8; // frame count, used by the index label and the progress bar
const REBUILD = true; // true only in the build call: it clears this page so a re-run is safe.
                      // Set false for follow-up calls (duotone, copy fixes) or they wipe the frames.
const SCHEME = null; // one scheme per piece: a key of BRAND.schemes, or null for BRAND.scheme

let page = figma.root.children.find(p => p.name === PAGE);
if (!page) { page = figma.createPage(); page.name = PAGE; }
await figma.setCurrentPageAsync(page);
if (REBUILD) for (const c of [...page.children]) c.remove();

const W = 1080, H = 1350, M = 88, CW = 904;
const hex = h => ({ r: parseInt(h.slice(1, 3), 16) / 255, g: parseInt(h.slice(3, 5), 16) / 255, b: parseInt(h.slice(5, 7), 16) / 255 });
const F = BRAND.fonts;
for (const k in F) await figma.loadFontAsync(F[k]);
const solid = (c, o) => o == null ? { type: 'SOLID', color: c } : { type: 'SOLID', color: c, opacity: o };

// ================= colour =================

// C holds the current scheme's colours as Figma RGB. useScheme(name) switches it; the
// layouts read C when they draw, so a gallery can draw several schemes in one call.
// Older brand packs with a single 'colors' block still work.
const C = {}; let DUO = null, SCHEME_NAME = null;
function useScheme(name) {
  const all = BRAND.schemes || { base: BRAND.colors }, key = name || SCHEME || BRAND.scheme || Object.keys(all)[0];
  const sc = all[key]; if (!sc) throw new Error('unknown scheme: ' + key);
  for (const k in sc) if (k !== 'duotone') C[k] = hex(sc[k]);
  if (!sc.onDark) C.onDark = C.ground;
  const d = sc.duotone || {}; // same fallback pairs as brand_css.py, so both renderers agree
  DUO = { light: d.light || [sc.surface, sc.primary], dark: d.dark || [sc.mutedDark, sc.dark] };
  SCHEME_NAME = key; return key;
}
useScheme();

function lum(c) { const f = v => v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b); }
function contrast(a, b) { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); }
// The neutral (text, onDark, dark, or ground) that reads best on a background: on a dark
// scheme's gold card that is the dark ground, not the light text.
function inkOn(bg) { return [C.text, C.onDark, C.dark, C.ground].reduce((a, b) => contrast(b, bg) > contrast(a, bg) ? b : a); }
// The highlight colour if it stands out on bg (contrast >= min, default 3), else the ink.
function accentOn(bg, min) { return contrast(C.highlight, bg) >= (min || 3) ? C.highlight : inkOn(bg); }
// A ground name ('ground', 'dark', 'primary', 'surface', 'highlight'; true = 'dark',
// 'accent' = 'highlight', 'light' = 'ground') as a colour.
function bgOf(mode) { if (mode === true || mode === 'dark') return C.dark; if (mode === 'accent') return C.highlight; if (mode && C[mode]) return C[mode]; return C.ground; }

// ================= building blocks =================

// Rectangle. c = colour or null (empty fills), o = opacity, rad = corner radius.
function R(p, name, x, y, w, h, c, o, rad) {
  const r = figma.createRectangle(); r.name = name; r.x = Math.round(x); r.y = Math.round(y); r.resize(Math.max(1, Math.round(w)), Math.max(1, Math.round(h)));
  r.fills = c ? [solid(c, o)] : []; if (rad) r.cornerRadius = rad; p.appendChild(r); return r;
}

function E(p, name, x, y, d, c, o) {
  const e = figma.createEllipse(); e.name = name; e.resize(Math.max(1, d), Math.max(1, d)); e.x = Math.round(x); e.y = Math.round(y);
  e.fills = c ? [solid(c, o)] : []; p.appendChild(e); return e;
}

// Text. o: { w (wrap width), lh (% line height), ls (% letter spacing), align, op (opacity), name }.
// Order matters: characters, then textAutoResize HEIGHT, then resize, then position.
// Never pass an empty string: characters='' throws "Required value missing".
function T(p, str, font, size, c, x, y, o) {
  o = o || {}; const t = figma.createText(); t.fontName = font; t.fontSize = size; t.characters = str; t.fills = [solid(c, o.op)];
  if (o.lh) t.lineHeight = { unit: 'PERCENT', value: o.lh }; if (o.ls != null) t.letterSpacing = { unit: 'PERCENT', value: o.ls };
  p.appendChild(t); if (o.w) { t.textAutoResize = 'HEIGHT'; t.resize(o.w, Math.max(t.height, 1)); }
  if (o.align) t.textAlignHorizontal = o.align; t.x = Math.round(x); t.y = Math.round(y); t.name = o.name || str.slice(0, 28); return t;
}

// Width of a string in a given style (temporary node, removed again).
function measure(p, str, font, size, ls) {
  if (!str) return 0; const t = figma.createText(); t.fontName = font; t.fontSize = size; t.characters = str;
  if (ls != null) t.letterSpacing = { unit: 'PERCENT', value: ls }; p.appendChild(t); const w = t.width; t.remove(); return w;
}

// Lines may be plain strings or [[text, mark], ...] arrays; this makes them all arrays.
const asParts = lines => (lines || []).map(l => typeof l === 'string' ? [[l, false]] : l);

// Multi-line headline. lines = [ [ ['Anggap saja ', false], ['pintu air.', 'hl'] ], ... ]
// Marks: true or 'hl' (highlighter behind), 'italic' (display italic), 'color' (accent
// colour), 'underline' (a bar under the words). One mark style per carousel; vary it
// between carousels. The marks adapt to what reads: on light text the highlighter becomes
// accent-coloured text; on a ground the highlighter would vanish into (o.bg), it becomes
// an underline; an accent colour equal to the text becomes italic.
// You choose the line breaks; 84 px fits about 22 characters per line, 72 about 26.
// o: { size = 84, lh = 106, ls, color, accent, bg (the colour behind, for the checks above), font }
// Returns { nodes, bottom } so the next block can stack under it.
function headline(p, lines, x, y, o) {
  o = o || {}; const font = o.font || F.display, size = o.size || 84, lh = o.lh || 106, ls = o.ls != null ? o.ls : -2.5, color = o.color || C.text;
  const lightInk = lum(color) > 0.4, bg = o.bg || (lightInk ? C.dark : C.ground);
  // an accent must differ from the text and read on the ground; none fits: 'color' becomes italic
  const accent = (o.accent ? [o.accent] : lightInk ? [C.highlight, C.primary] : [C.primary, C.highlight]).find(c => contrast(c, color) >= 1.15 && contrast(c, bg) >= 2.5) || null;
  const step = size * lh / 100; const nodes = [];
  asParts(lines).forEach((parts, i) => {
    const ly = y + i * step; let prefix = ''; const ranges = [];
    for (const pr of parts) {
      const s = pr[0]; let mark = pr[1] === true ? 'hl' : pr[1];
      if (mark === 'hl' && lightInk) mark = 'color';
      if (mark === 'hl' && contrast(C.highlight, bg) < 1.25) mark = 'underline';
      if (mark === 'color' && !accent) mark = 'italic';
      if (mark && !o.noMark) {
        if (mark === 'hl' || mark === 'underline') {
          const a = measure(p, prefix, font, size, ls), b = measure(p, prefix + s.replace(/[.,]$/, ''), font, size, ls);
          if (mark === 'hl') R(p, 'highlight', x + a - 10, ly + step * 0.52, b - a + 20, size * 0.38, C.highlight);
          else R(p, 'underline', x + a, ly + step * 0.92, b - a, Math.max(4, size * 0.07), accent && !lightInk ? accent : color);
        } else ranges.push([prefix.length, prefix.length + s.length, mark]);
      }
      prefix += s;
    }
    const t = T(p, prefix, font, size, color, x, ly, { lh, ls, name: 'headline-' + (i + 1) });
    for (const r of ranges) { if (r[2] === 'italic') t.setRangeFontName(r[0], r[1], F.displayItalic); else t.setRangeFills(r[0], r[1], [solid(accent)]); }
    nodes.push(t);
  });
  return { nodes, bottom: Math.round(y + asParts(lines).length * step) };
}

function body(s, str, y, o) {
  o = o || {};
  return T(s, str, o.font || F.body, o.size || 32, o.color || C.text, o.x || M, y, { w: o.w || CW, lh: o.lh || 145, ls: o.ls != null ? o.ls : -0.5, name: o.name || 'body', op: o.op });
}

// Chrome colours (header, footer) for a ground. mode: 'light' (default, the scheme's
// ground), 'dark' (or true; photos too), 'accent' (highlight ground), or a colour key.
function chrome(mode) {
  const bg = bgOf(mode);
  if (bg === C.ground) {
    const cur = contrast(C.highlight, C.primary) < 1.5 ? C.text : C.highlight;
    return { soft: C.muted, softOp: null, rule: C.rule, ruleOp: null, done: C.primary, doneOp: null, rest: C.rule, restOp: null, cur, cue: contrast(C.primary, bg) >= 3 ? C.primary : C.text, ink: C.text };
  }
  const ink = inkOn(bg), softOk = contrast(C.mutedDark, bg) >= 3;
  return { soft: softOk ? C.mutedDark : ink, softOp: softOk ? null : 0.7, rule: ink, ruleOp: 0.2, done: ink, doneOp: 0.6, rest: ink, restOp: 0.18, cur: accentOn(bg, 2), cue: accentOn(bg, 3), ink };
}

// Eyebrow left, "03 / 08" right, hairline under both.
function header(s, left, idx, mode) {
  const k = chrome(mode);
  if (left) T(s, left, F.label, 22, k.soft, M, 70, { ls: 6, op: k.softOp, name: 'eyebrow' });
  T(s, String(idx).padStart(2, '0') + ' / ' + String(N).padStart(2, '0'), F.label, 22, k.soft, M, 70, { w: CW, align: 'RIGHT', ls: 6, op: k.softOp, name: 'index' });
  R(s, 'rule-top', M, 116, CW, 1, k.rule, k.ruleOp);
}

// Site left, swipe cue right, segmented progress bar (done / current / to come).
// The arrow is set in F.arrow, since many mono fonts lack it.
function footer(s, idx, mode) {
  const k = chrome(mode), segW = (CW - (N - 1) * 8) / N;
  for (let i = 0; i < N; i++) {
    const done = i < idx - 1, cur = i === idx - 1;
    R(s, 'progress-' + (i + 1), M + i * (segW + 8), 1262, segW, 6, cur ? k.cur : done ? k.done : k.rest, cur ? null : done ? k.doneOp : k.restOp, 3);
  }
  T(s, BRAND.site, F.label, 22, k.soft, M, 1208, { ls: 4, op: k.softOp, name: 'footer-site' });
  const cueText = idx === N ? BRAND.end : BRAND.swipe;
  const cue = T(s, cueText, F.label, 22, k.cue, M, 1208, { w: CW, align: 'RIGHT', ls: 6, name: 'footer-cue' });
  const a = cueText.indexOf('→'); if (a >= 0) cue.setRangeFontName(a, a + 1, F.arrow);
}

const slides = [], GROUND = {};
function slide(i, name, dark, w, h) {
  const f = figma.createFrame(); f.name = name; f.resize(w || W, h || H); f.x = i * ((w || W) + 120); f.y = 0;
  f.fills = [solid(dark ? C.dark : C.ground)]; f.clipsContent = true; page.appendChild(f); slides.push(f);
  GROUND[f.id] = { ground: C.ground, scheme: SCHEME_NAME }; return f;
}

// Photo plate (rounded, inset) with a credit line under it. Name it IMG-<n>.
// credit is the full line: 'Foto: Name / Unsplash', 'Ilustrasi AI'.
// Crop the photo locally first if its subject is not in the middle: FILL crops the centre.
function plate(s, name, y, h, credit) {
  const r = R(s, name, M, y, CW, h, C.surface, null, 20);
  if (credit) T(s, credit, F.label, 18, C.muted, M, y + h + 12, { ls: 2, name: 'credit' });
  return r;
}

// Vertical dark scrim over a full-bleed photo. stops = [[position 0..1, alpha 0..1], ...].
function vgrad(s, stops, h, name) {
  const g = figma.createRectangle(); g.name = name || 'scrim'; g.resize(s.width, h || s.height);
  g.fills = [{ type: 'GRADIENT_LINEAR', gradientTransform: [[0, 1, 0], [-1, 0, 1]], gradientStops: stops.map(p => ({ position: p[0], color: { r: C.dark.r, g: C.dark.g, b: C.dark.b, a: p[1] } })) }];
  s.appendChild(g); return g;
}

// Move everything drawn since child index 'from' so its bottom sits at bottomY, but never
// above minTop. Build a block at any y, then anchor it.
function anchorBottom(s, from, bottomY, minTop) {
  const made = s.children.slice(from); if (!made.length) return 0;
  const top = Math.min(...made.map(n => n.y)), bot = Math.max(...made.map(n => n.y + n.height));
  let dy = bottomY - bot; if (minTop != null && top + dy < minTop) dy = minTop - top;
  made.forEach(n => { n.y = Math.round(n.y + dy); });
  return top + dy;
}

// Duotone: greyscale the image, then MULTIPLY a highlight colour and LIGHTEN a shadow
// colour, all in the node's fills. Run it in a SEPARATE call after upload_assets has put
// the photo on the node. hi may be 'light' (plates) or 'dark' (full-bleed photos) to use
// the current scheme's pair, or two hex colours. Never on screenshots (ART-*).
// toneNode does the same on a node you hold, and re-tones an image that is already toned.
function toneNode(n, hi, lo, contrastF, exposure) {
  if (typeof hi === 'string' && hi[0] !== '#') { const pair = DUO && DUO[hi]; if (!pair) return false; lo = pair[1]; hi = pair[0]; }
  const imgs = n.fills.filter(f => f.type === 'IMAGE'); if (!imgs.length) return false;
  const old = imgs[imgs.length - 1].filters || {};
  n.fills = [
    Object.assign({}, imgs[imgs.length - 1], { scaleMode: 'FILL', filters: { saturation: -1, contrast: contrastF != null ? contrastF : (old.contrast || 0.2), exposure: exposure != null ? exposure : (old.exposure || 0) } }),
    { type: 'SOLID', color: hex(hi), blendMode: 'MULTIPLY' },
    { type: 'SOLID', color: hex(lo), blendMode: 'LIGHTEN' },
  ];
  return true;
}
async function duotone(id, hi, lo, contrastF, exposure) {
  const n = await figma.getNodeByIdAsync(id);
  return toneNode(n, hi, lo, contrastF, exposure) ? { id, ok: true } : { id, error: 'no image fill yet, or no duotone pair in the scheme' };
}

// ================= covers (slide 1) =================
// Pick by content (references/design-variety.md), and not the variant the previous piece used.

// Dark bookend: full-bleed photo (IMG-1) under a scrim, a big number in the accent,
// headline lines, a body, stacked up from the bottom. For a number with a scene.
// o: { eyebrow, number, lines: ['line', ...], body, img, numberSize }
function coverDark(s, o) {
  s.fills = [solid(C.dark)]; const ink = inkOn(C.dark);
  R(s, o.img || 'IMG-1', 0, 0, s.width, s.height, C.dark);
  vgrad(s, [[0, 0.35], [0.3, 0.5], [0.56, 0.86], [0.75, 0.97], [1, 0.99]]);
  header(s, o.eyebrow, 1, 'dark');
  let y = 1150;
  if (o.body) { const b = body(s, o.body, 0, { color: ink, op: 0.8, w: 840 }); b.y = Math.round(y - b.height); y = b.y - 28; }
  const lines = o.lines || [], step = 70, top = y - lines.length * step;
  lines.forEach((l, i) => T(s, l, F.displayRegular, 64, ink, M, top + i * step, { lh: 110, ls: -1.5, name: 'headline-' + (i + 1) }));
  if (o.number) {
    let ns = o.numberSize || 330;
    const n = T(s, o.number, F.display, ns, accentOn(C.dark), M - 18, 0, { lh: 100, ls: -4, name: 'big-number' });
    if (n.width > CW + 20) { ns = Math.floor(ns * (CW + 20) / n.width); n.fontSize = ns; }
    n.y = Math.round(top - 24 - n.height);
  }
  footer(s, 1, 'dark');
}

// Photo on top, text on the ground below. For a strong photo or illustration that
// should not sit under a scrim. o: { eyebrow, number, lines (parts), body, img, credit, photoH = 700, size = 64 }
function coverSplit(s, o) {
  const ph = o.photoH || 700;
  R(s, o.img || 'IMG-1', 0, 0, s.width, ph, C.surface);
  vgrad(s, [[0, 0.6], [1, 0]], 260, 'scrim-top');
  header(s, o.eyebrow, 1, 'dark');
  if (o.credit) T(s, o.credit, F.label, 16, inkOn(C.dark), M, ph - 38, { w: CW, align: 'RIGHT', ls: 2, op: 0.85, name: 'credit' });
  const from = s.children.length;
  let y = 0;
  if (o.number) { const n = T(s, o.number, F.display, o.numberSize || 200, C.primary, M - 10, y, { lh: 100, ls: -4, name: 'big-number' }); if (n.width > CW) n.fontSize = Math.floor(n.fontSize * CW / n.width); y = n.y + n.height + 10; }
  const h = headline(s, o.lines, M, y, { size: o.size || 64, lh: 108, ls: -1.5 });
  y = h.bottom + 20;
  if (o.body) body(s, o.body, y, { size: 30 });
  anchorBottom(s, from, 1160, ph + 36);
  footer(s, 1);
}

// Type only, on a coloured ground: a claim or a question in very large display type,
// optionally a giant faint number behind it. For an opinion, a paradox, or a story with no
// good image. o: { eyebrow, kicker, lines (parts), body, bg: 'dark'|'primary'|'highlight'|'ground'|'surface', size = 120, decor: 'bigIndex'|false, decorText }
function coverType(s, o) {
  const bgKey = o.bg || 'dark', bg = bgOf(bgKey), ink = inkOn(bg);
  s.fills = [solid(bg)];
  header(s, o.eyebrow, 1, bgKey);
  const from = s.children.length;
  if (o.kicker) T(s, o.kicker, F.label, 26, ink, M, 0, { ls: 6, op: 0.7, name: 'kicker' });
  const marks = s.children.length, size = o.size || 120;
  const h = headline(s, o.lines, M, o.kicker ? 60 : 0, { size, lh: 100, ls: -3, color: ink, bg });
  // at line height 100 an underline touches the next line's capitals: lift it a little
  s.children.slice(marks).forEach(n => { if (n.name === 'underline') n.y = Math.round(n.y - size * 0.06); });
  if (o.body) body(s, o.body, h.bottom + 40, { color: ink, op: 0.85, w: 860 });
  anchorBottom(s, from, 1150, 170);
  if (o.decor) decor(s, o.decor, { bg, text: o.decorText });
  footer(s, 1, bgKey);
}

// A chart as the cover: the finding as the title, sorted bars, the source and n at the
// bottom. For a data series or one survey finding. o: { eyebrow, lines (parts), items, highlight, primary, max, source, size = 72 }
function coverChart(s, o) {
  header(s, o.eyebrow, 1);
  const h = headline(s, o.lines, M, 150, { size: o.size || 72 }), top = h.bottom + 56;
  const rowH = o.rowH || Math.max(56, Math.min(110, Math.floor((1090 - top) / o.items.length)));
  const y = barChart(s, top, { items: o.items, highlight: o.highlight, primary: o.primary, max: o.max, rowH });
  if (o.source) T(s, o.source, F.label, 18, C.muted, M, Math.max(y + 30, 1130), { w: CW, ls: 2, name: 'source' });
  footer(s, 1);
}

// A quote as the cover, with an optional round portrait (IMG-1, only with the person's
// consent or an official press photo). o: { eyebrow, quote, name, role, img, size = 72 }
function coverQuote(s, o) {
  s.fills = [solid(C.dark)]; const ink = inkOn(C.dark);
  header(s, o.eyebrow, 1, 'dark');
  const from = s.children.length;
  T(s, '“', F.displayItalic, 240, accentOn(C.dark), M - 12, -150, { lh: 100, name: 'quote-mark' });
  const q = T(s, o.quote, F.displayItalic, o.size || 72, ink, M, 0, { w: CW, lh: 110, ls: -1.5, name: 'quote' });
  const ay = q.y + q.height + 48, px = o.img ? M + 148 : M;
  if (o.img) R(s, o.img, M, ay, 120, 120, C.surface, null, 60);
  T(s, o.name, F.bodyBold, 30, ink, px, ay + 18, { name: 'quote-name' });
  if (o.role) T(s, o.role, F.label, 18, chrome('dark').soft, px, ay + 64, { ls: 4, w: CW - (px - M), op: chrome('dark').softOp, name: 'quote-role' });
  const made = s.children.slice(from), hgt = Math.max(...made.map(n => n.y + n.height)) - Math.min(...made.map(n => n.y));
  anchorBottom(s, from, Math.min(1150, 660 + hgt / 2), 160);
  footer(s, 1, 'dark');
}

// ================= data =================

// Comparison table: the data slide worth saving when the source has three or more metrics
// for the same items. o: {
//   head: { name: 'FRAMEWORK', values: ['BIAYA $', 'MENIT', 'TOKEN', 'BARIS', 'JS'] },
//   rows: [{ name: 'Hono+htmx', values: ['2,67', '8,6', '4,26', '1.370', '18'], bar: 2.67, barColor: 'highlight', strong: true }, ...],
//   barMax, best: [row index of the best value per value column, or -1], note, rowH: 52, nameW: 210, barW: 120 }
// Rows are drawn in the order given (sort them first). The bar, when rows have 'bar',
// sits before the first value column, which its header covers. barColor is a colour key.
// best marks the best value of each column (highlighter, or accent text on light ink).
function table(s, y, o) {
  const rowH = o.rowH || 52, nameW = o.nameW || 210, hasBar = o.rows.some(r => r.bar != null), barW = hasBar ? (o.barW || 120) : 0;
  const nameX = M + 44, barX = nameX + nameW + 8, start = hasBar ? barX + barW + 12 : nameX + nameW + 8, lightInk = lum(C.text) > 0.4;
  const nv = o.rows[0].values.length, colW = (M + CW - start) / nv;
  const RE = []; for (let j = 0; j < nv; j++) RE.push(Math.round(start + (j + 1) * colW));
  // a header wider than its column (TERPOTONG, PERINTAH beside each other) drops to 16 px, no tracking
  const hdr = (str, x, w, align) => { const fits = measure(s, str, F.label, 18, 4) <= w - 8;
    return T(s, str, F.label, fits ? 18 : 16, C.muted, x, y + (fits ? 0 : 1), { w, align, ls: fits ? 4 : 0, name: 'th-' + str }); };
  hdr('#', M, 36, 'LEFT'); hdr(o.head.name, nameX, nameW, 'LEFT');
  o.head.values.forEach((h, j) => { if (j === 0 && hasBar) hdr(h, barX, barW + colW, 'LEFT'); else hdr(h, RE[j] - colW, colW, 'RIGHT'); });
  R(s, 'th-rule', M, y + 34, CW, 2, C.text);
  const y0 = y + 38, max = o.barMax || Math.max(...o.rows.map(r => r.bar || 0));
  o.rows.forEach((r, i) => {
    const ry = y0 + i * rowH;
    T(s, String(i + 1).padStart(2, '0'), F.label, 20, C.muted, M, ry + 15, { name: 'rank-' + (i + 1) });
    T(s, r.name, r.strong ? F.bodyBold : F.bodyMedium, 25, C.text, nameX, ry + 11, { ls: -0.5, name: 'name-' + r.name });
    if (r.bar != null) R(s, 'bar-' + r.name, barX, ry + 18, Math.max(4, barW * r.bar / max), 16, C[r.barColor] || C.mutedDark, null, 3);
    r.values.forEach((v, j) => {
      const best = o.best && o.best[j] === i;
      if (best && !lightInk) {
        const tw = measure(s, v, F.label, 24, 0), w = tw + 16;
        R(s, 'best-' + (j + 1), Math.min(RE[j] - tw - 8, M + CW - w), ry + 27, w, 17, C.highlight);
      }
      T(s, v, F.label, 24, best && lightInk ? C.highlight : C.text, RE[j] - colW, ry + 13, { w: colW, align: 'RIGHT', name: 'v' + (j + 1) + '-' + r.name });
    });
    if (i < o.rows.length - 1) R(s, 'row-rule', M, ry + rowH - 1, CW, 1, C.rule);
  });
  let bottom = y0 + o.rows.length * rowH;
  if (o.note) { const n = T(s, o.note, F.body, 20, C.muted, M, bottom + 14, { w: CW, lh: 140, name: 'table-note' }); bottom = n.y + n.height; }
  return Math.round(bottom);
}

// Horizontal bars from zero, in the order given. items: [{ label, value, display }].
// highlight / primary: indices drawn in those colours (the rest mutedDark).
// ref: { value, label } adds a dashed line (an old record, an average).
function barChart(s, y, o) {
  const rowH = o.rowH || 64, labelW = o.labelW || 230, valW = 130;
  const x0 = M + labelW + 16, span = CW - labelW - 16 - valW;
  const max = o.max || Math.max(...o.items.map(i => i.value), o.ref ? o.ref.value : 0);
  o.items.forEach((it, i) => {
    const ry = y + i * rowH, hl = (o.highlight || []).includes(i), pr = (o.primary || []).includes(i);
    T(s, it.label, hl || pr ? F.bodyBold : F.bodyMedium, 26, C.text, M, ry + (rowH - 34) / 2, { w: labelW, name: 'bar-label-' + (i + 1) });
    const bw = Math.max(4, span * it.value / max);
    R(s, 'bar-' + (i + 1), x0, ry + (rowH - 30) / 2, bw, 30, hl ? C.highlight : pr ? C.primary : C.mutedDark, null, 4);
    T(s, it.display || String(it.value), F.label, 24, C.text, x0 + bw + 12, ry + (rowH - 30) / 2 + 1, { name: 'bar-value-' + (i + 1) });
  });
  const bottom = y + o.items.length * rowH;
  R(s, 'bar-baseline', x0 - 2, y - 6, 2, bottom - y + 12, C.text);
  if (o.ref) {
    const rx = x0 + span * o.ref.value / max;
    for (let d = y - 26; d < bottom + 6; d += 14) R(s, 'ref-dash', rx, d, 2, 8, C.text, 0.55);
    if (o.ref.label) T(s, o.ref.label, F.label, 16, C.muted, rx + 8, y - 30, { ls: 2, name: 'ref-label' });
  }
  return Math.round(bottom);
}

// Vertical bars for a series (versions, months), from zero, with axis labels in a left
// gutter, a dashed reference line, and the highlighted bars labelled.
// o: { values: [..], h = 420, highlight: [indices] (default the last), ref: { value, label }, first, last, fmt }
function columnChart(s, y, o) {
  const h = o.h || 420, gut = 78, x0 = M + gut, w = CW - gut, n = o.values.length;
  const raw = Math.max(...o.values, o.ref ? o.ref.value : 0) * 1.05 || 1, p10 = Math.pow(10, Math.floor(Math.log10(raw)));
  const max = o.max || [1, 2, 2.5, 5, 10].map(m => m * p10).find(v => v >= raw);
  const fmt = o.fmt || (v => String(Math.round(v)).replace(/\B(?=(\d{3})+(?!\d))/g, '.'));
  for (const f of [0, 0.5, 1]) { const gy = y + h - h * f; R(s, 'grid', x0, gy, w, 1, C.rule); T(s, fmt(max * f), F.label, 16, C.muted, M, gy - 10, { w: gut - 12, align: 'RIGHT', name: 'axis' }); }
  const gap = n > 40 ? 2 : 6, bw = (w - gap * (n - 1)) / n, hl = o.highlight || [n - 1];
  o.values.forEach((v, i) => { const bh = Math.max(2, h * v / max); R(s, 'col-' + (i + 1), x0 + i * (bw + gap), y + h - bh, Math.max(1, bw), bh, hl.includes(i) ? C.primary : C.mutedDark); });
  R(s, 'col-baseline', x0, y + h, w, 2, C.text);
  if (o.ref) {
    const ry = y + h - h * o.ref.value / max;
    for (let x = x0; x < x0 + w; x += 14) R(s, 'ref-dash', x, ry, Math.min(8, x0 + w - x), 2, C.text, 0.55);
    if (o.ref.label) T(s, o.ref.label, F.label, 16, C.muted, x0 + 8, ry - 26, { ls: 2, name: 'ref-label' });
  }
  hl.forEach(i => {
    const v = o.values[i], cx = x0 + i * (bw + gap) + bw / 2, tx = Math.min(Math.max(cx - 80, x0), M + CW - 160);
    T(s, fmt(v), F.label, 22, C.primary, tx, y + h - h * v / max - 34, { w: 160, align: 'CENTER', name: 'col-value' });
  });
  let bottom = y + h + 2;
  if (o.first) T(s, o.first, F.label, 16, C.muted, x0, bottom + 10, { name: 'x-first' });
  if (o.last) T(s, o.last, F.label, 16, C.muted, x0, bottom + 10, { w, align: 'RIGHT', name: 'x-last' });
  if (o.first || o.last) bottom += 36;
  return Math.round(bottom);
}

// One number the slide is about, with a label and optional comparison bars.
// o: { value: '86%', label, compare: [{ name, value, display, color: 'highlight'|'primary' }], size = 260, compareRowH = 76 }
function bigStat(s, y, o) {
  const n = T(s, o.value, F.display, o.size || 260, C.primary, M - 10, y, { lh: 100, ls: -4, name: 'big-stat' });
  if (n.width > CW + 20) n.fontSize = Math.floor(n.fontSize * (CW + 20) / n.width);
  let b = n.y + n.height + 8;
  if (o.label) { const l = body(s, o.label, b, { size: 34, name: 'big-stat-label' }); b = l.y + l.height; }
  if (o.compare) {
    const idx = c => o.compare.map((x, i) => x.color === c ? i : -1).filter(i => i >= 0);
    b = barChart(s, b + 48, { items: o.compare.map(c => ({ label: c.name, value: c.value, display: c.display })), highlight: idx('highlight'), primary: idx('primary'), rowH: o.compareRowH || 76 });
  }
  return Math.round(b);
}

// Two sides head to head, with a disc between them. The second side sits on the primary
// colour. o: { left: { kicker, big, label }, right: { ... }, h = 400, size (of the numbers), mid = 'vs' }
function versus(s, y, o) {
  const h = o.h || 400, half = (CW - 40) / 2, bs = o.size || (h >= 400 ? 128 : 96);
  [o.left, o.right].forEach((c, i) => {
    const x = M + i * (half + 40), fill = i === 1 ? C.primary : C.surface, ink = inkOn(fill);
    R(s, 'versus-' + (i + 1), x, y, half, h, fill, null, 20);
    if (c.kicker) T(s, c.kicker, F.label, 18, ink, x + 32, y + 30, { ls: 4, op: 0.7, name: 'versus-kicker' });
    const big = T(s, c.big, F.display, bs, i === 1 ? accentOn(fill) : (contrast(C.primary, fill) >= 3 ? C.primary : ink), x + 30, y + 64, { lh: 100, ls: -3, name: 'versus-big' });
    if (big.width > half - 60) big.fontSize = Math.floor(bs * (half - 60) / big.width);
    if (c.label) T(s, c.label, F.body, 26, ink, x + 32, y + 64 + big.height + 24, { w: half - 64, lh: 135, name: 'versus-label' });
  });
  const cx = M + half + 20, cy = y + h / 2;
  E(s, 'versus-mid', cx - 36, cy - 36, 72, C.highlight);
  T(s, o.mid || 'vs', F.bodyBold, 26, inkOn(C.highlight), cx - 36, cy - 17, { w: 72, align: 'CENTER', name: 'versus-mid-label' });
  return y + h;
}

// A percentage as 100 dots: a 20 × 5 strip by default, or a square with cols: 10 and a
// width (640 fills a slide under a two-line headline). o: { pct, label, color: 'primary'|'highlight', cols = 20, width = CW }
function dots(s, y, o) {
  const cols = o.cols || 20, rows = Math.ceil(100 / cols), gap = 12, d = ((o.width || CW) - gap * (cols - 1)) / cols, filled = Math.round(o.pct);
  for (let i = 0; i < cols * rows; i++) E(s, 'dot', M + (i % cols) * (d + gap), y + Math.floor(i / cols) * (d + gap), d, i < filled ? (C[o.color] || C.primary) : C.rule);
  let b = y + rows * (d + gap) - gap;
  if (o.label) { const l = body(s, o.label, b + 24, { size: 28, color: C.muted, name: 'dots-label' }); b = l.y + l.height; }
  return Math.round(b);
}

// Two or three numbers the reader compares at a glance, on surface cards.
// cards: [{ kicker: 'BARIS KODE', big: '1.370', who: 'Hono+htmx', vs: 'vs 2.009 baris di Angular' }].
function statCards(s, y, cards, o) {
  o = o || {}; const gap = 20, n = cards.length, cw = (CW - gap * (n - 1)) / n, ch = o.h || 262;
  cards.forEach((c, i) => {
    const x = Math.round(M + i * (cw + gap));
    R(s, 'card-' + (i + 1), x, y, cw, ch, C.surface, null, 20);
    if (c.kicker) T(s, c.kicker, F.label, 18, C.muted, x + 32, y + 30, { ls: 4, name: 'card-kicker-' + (i + 1) });
    const big = T(s, c.big, F.display, n > 2 ? 64 : 88, C.primary, x + 30, y + 58, { ls: -2.5, lh: 100, name: 'card-num-' + (i + 1) });
    if (big.width > cw - 60) big.fontSize = Math.floor(big.fontSize * (cw - 60) / big.width);
    if (c.who) T(s, c.who, F.bodyBold, 26, C.text, x + 32, y + 164, { name: 'card-who-' + (i + 1) });
    if (c.vs) T(s, c.vs, F.body, 24, C.muted, x + 32, y + 204, { w: cw - 64, name: 'card-vs-' + (i + 1) });
  });
  return y + ch;
}

// ================= interior =================

// Labelled items (causes, reasons): a label, text in the body, a hairline between.
// list: [['SVELTEKIT · $4,28', 'text'], ...].
function labelledItems(s, y, list, o) {
  o = o || {};
  list.forEach((it, i) => {
    if (i) R(s, 'item-rule', M, y - 16, CW, 1, C.rule);
    T(s, it[0], F.label, 20, C.primary, M, y, { ls: 4, name: 'item-label-' + (i + 1) });
    const t = body(s, it[1], y + 32, { size: o.size || 30, name: 'item-' + (i + 1) });
    y = Math.round(t.y + t.height + 32);
  });
  return y - 32;
}

// Image beside text. o: { img, credit, side: 'left'|'right', imgW = 420, h = 420, label, text, size = 30 }
function splitPlate(s, y, o) {
  const iw = o.imgW || 420, h = o.h || 420, left = (o.side || 'left') === 'left';
  const ix = left ? M : M + CW - iw, tx = left ? M + iw + 36 : M, tw = CW - iw - 36;
  R(s, o.img, ix, y, iw, h, C.surface, null, 20);
  if (o.credit) T(s, o.credit, F.label, 16, C.muted, ix, y + h + 10, { w: iw, ls: 2, name: 'credit' });
  let ty = y;
  if (o.label) { T(s, o.label, F.label, 20, C.primary, tx, ty, { ls: 4, w: tw, name: 'split-label' }); ty += 40; }
  const t = body(s, o.text, ty, { x: tx, w: tw, size: o.size || 30, name: 'split-text' });
  return Math.round(Math.max(y + h + (o.credit ? 34 : 0), t.y + t.height));
}

// An interior slide on a full-bleed photo under a scrim: the turn, or the one slide that
// should feel different. o: { idx, eyebrow, img, lines (parts), body, credit, size = 84 }
function fullBleed(s, o) {
  s.fills = [solid(C.dark)]; const ink = inkOn(C.dark);
  R(s, o.img || 'IMG-' + o.idx, 0, 0, s.width, s.height, C.dark);
  vgrad(s, [[0, 0.45], [0.35, 0.62], [0.6, 0.88], [1, 0.97]]);
  header(s, o.eyebrow, o.idx, 'dark');
  if (o.credit) T(s, o.credit, F.label, 16, chrome('dark').soft, M, 1162, { ls: 2, op: chrome('dark').softOp, name: 'credit' });
  const from = s.children.length;
  const h = headline(s, o.lines, M, 0, { size: o.size || 84, color: ink, bg: C.dark });
  if (o.body) body(s, o.body, h.bottom + 26, { color: ink, op: 0.85 });
  anchorBottom(s, from, o.credit ? 1136 : 1150, 170);
  footer(s, o.idx, 'dark');
}

// Numbered steps with a connector line. list: [[title, text], ...]
function steps(s, y, list, o) {
  o = o || {}; const r = 64, gap = o.gap || 36;
  list.forEach((it, i) => {
    E(s, 'step-' + (i + 1), M, y, r, C.primary);
    T(s, String(i + 1).padStart(2, '0'), F.label, 24, inkOn(C.primary), M, y + 18, { w: r, align: 'CENTER', name: 'step-n-' + (i + 1) });
    const t1 = T(s, it[0], F.bodyBold, 30, C.text, M + r + 28, y + 2, { w: CW - r - 28, lh: 130, name: 'step-title-' + (i + 1) });
    let b = t1.y + t1.height;
    if (it[1]) { const t2 = body(s, it[1], b + 6, { x: M + r + 28, w: CW - r - 28, size: 26, color: C.muted, name: 'step-text-' + (i + 1) }); b = t2.y + t2.height; }
    const next = Math.max(b, y + r) + gap;
    if (i < list.length - 1) R(s, 'step-line', M + r / 2 - 1, y + r + 6, 2, next - (y + r) - 12, C.rule);
    y = next;
  });
  return y - gap;
}

// A short quote in the display italic with a bar and an attribution line.
function quote(s, y, text, attribution, o) {
  o = o || {};
  const bar = R(s, 'quote-bar', M, y + 6, 4, 40, C.primary);
  const q = T(s, text, F.displayItalic, o.size || 40, C.text, M + 28, y, { w: CW - 28, lh: 118, ls: -1, name: 'quote' });
  bar.resize(4, Math.max(20, Math.round(q.height - 10)));
  let bottom = q.y + q.height;
  if (attribution) { const a = T(s, attribution, F.label, 18, C.muted, M + 28, bottom + 12, { ls: 4, name: 'attribution' }); bottom = a.y + a.height; }
  return Math.round(bottom);
}

// ================= evidence =================

// A screenshot as evidence (ART-<n>), scaled to the content width, in colour, with a label
// above (what the columns mean, if you cropped the header off), a credit below, and
// highlighter marks over the rows or phrase that prove the claim. The marks are MULTIPLY
// rectangles on top: they read as a highlighter and leave the image untouched.
// o: { name: 'ART-5', w, h (the image's pixel size), label, credit, url,
//      style: 'plain' | 'window' (a browser bar with the real URL) | 'tilt' (rotated, with a shadow),
//      marks: [[y0, y1], ...] for whole rows, or [{ x0, x1, y0, y1 }, ...] for a phrase,
//      all in image pixels (scripts/artefact_marks.py finds them) }.
// Crop the image locally to the part that proves the claim; aim for 300–450 px tall here.
function artefact(s, y, o) {
  if (o.label) { T(s, o.label, F.label, 18, C.muted, M, y, { ls: 4, name: 'artefact-label' }); y += 34; }
  const style = o.style || 'plain', tilt = style === 'tilt', bar = style === 'window' ? 44 : 0;
  const bw = tilt ? CW - 24 : CW, k = bw / o.w, h = Math.round(o.h * k);
  const box = figma.createFrame(); box.name = 'artefact-' + o.name; box.resize(bw, h + bar); box.x = M + (tilt ? 12 : 0); box.y = y;
  box.fills = [solid(C.surface)]; box.cornerRadius = 12; box.clipsContent = true; box.strokes = [solid(C.rule)]; box.strokeWeight = 1; s.appendChild(box);
  if (bar) {
    R(box, 'window-bar', 0, 0, bw, bar, C.surface);
    [0, 1, 2].forEach(i => E(box, 'window-dot', 20 + i * 20, 16, 12, i === 0 ? C.highlight : C.rule));
    if (o.url) T(box, o.url, F.label, 16, C.muted, 96, 13, { name: 'window-url' });
  }
  R(box, o.name, 0, bar, bw, h, C.surface);
  // a MULTIPLY mark needs a colour that shows on white and keeps black text readable
  const markC = [C.highlight, C.ground, C.surface].find(c => lum(c) > 0.2 && lum(c) < 0.85) || C.highlight;
  for (const m of o.marks || []) {
    const row = Array.isArray(m), b = row ? { x0: 0, x1: o.w, y0: m[0], y1: m[1] } : m, pad = row ? 0 : 4;
    const x = Math.max(1, b.x0 * k - pad), w = Math.min(bw - 1 - x, (b.x1 - b.x0) * k + 2 * pad);
    const r = R(box, 'mark', x, bar + b.y0 * k, w, (b.y1 - b.y0) * k, markC); r.blendMode = 'MULTIPLY';
  }
  if (tilt) {
    box.rotation = o.angle || -1.5;
    box.effects = [{ type: 'DROP_SHADOW', color: { r: 0, g: 0, b: 0, a: 0.18 }, offset: { x: 0, y: 14 }, radius: 36, spread: 0, visible: true, blendMode: 'NORMAL' }];
  }
  let bottom = y + h + bar + (tilt ? 34 : 0);
  if (o.credit) { const c = T(s, o.credit, F.label, 18, C.muted, M, bottom + 12, { ls: 2, w: CW, name: 'credit' }); bottom = c.y + c.height; }
  return Math.round(bottom);
}

// ================= opinion =================

// The action on a primary card. It must pass "who, with what, when" (writing-craft 8).
function tipCard(s, y, label, text) {
  const card = R(s, 'tip-card', M, y, CW, 200, C.primary, null, 20), ink = inkOn(C.primary);
  T(s, label, F.label, 20, accentOn(C.primary), M + 44, y + 40, { ls: 4, name: 'tip-label' });
  const t = T(s, text, F.bodyMedium, 34, ink, M + 44, y + 80, { w: CW - 88, lh: 135, ls: -0.5, name: 'tip' });
  card.resize(CW, Math.round(t.y + t.height + 40 - y));
  return y + card.height;
}

// A short list the reader keeps, with boxes, on a surface card. list: ['line', ...]; o: { size = 30 }
function checklist(s, y, label, list, o) {
  o = o || {};
  const card = R(s, 'checklist-card', M, y, CW, 100, C.surface, null, 20);
  let ty = y + 40;
  if (label) { T(s, label, F.label, 20, C.primary, M + 44, ty, { ls: 4, name: 'checklist-label' }); ty += 50; }
  list.forEach((t, i) => {
    const bx = R(s, 'check-' + (i + 1), M + 44, ty + 6, 28, 28, null, null, 6); bx.strokes = [solid(C.primary)]; bx.strokeWeight = 3;
    R(s, 'check-fill-' + (i + 1), M + 51, ty + 13, 14, 14, C.highlight, null, 3);
    const n = body(s, t, ty, { x: M + 96, w: CW - 140, size: o.size || 30, name: 'check-text-' + (i + 1) });
    ty = n.y + n.height + (o.size > 30 ? 30 : 22);
  });
  card.resize(CW, Math.round(ty + 18 - y));
  return y + card.height;
}

// The opinion as a statement on a coloured ground: the carousel's one loud slide.
// o: { idx, eyebrow, lines (parts), body, tip, bg: 'highlight'|'primary'|'dark', size = 96,
//      decor: 'bigIndex' to set a giant faint number in the open top (decorText to choose it) }
function statement(s, o) {
  const bgKey = o.bg || 'highlight', bg = bgOf(bgKey), ink = inkOn(bg);
  s.fills = [solid(bg)];
  header(s, o.eyebrow, o.idx, bgKey);
  const from = s.children.length;
  const h = headline(s, o.lines, M, 0, { size: o.size || 96, lh: 104, ls: -3, color: ink, bg });
  let y = h.bottom + 36;
  if (o.body) { const b = body(s, o.body, y, { color: ink, op: 0.85 }); y = b.y + b.height + 44; }
  if (o.tip) { R(s, 'statement-rule', M, y, 120, 6, ink); T(s, o.tip, F.bodyMedium, 36, ink, M, y + 30, { w: CW, lh: 135, ls: -0.5, name: 'tip' }); }
  anchorBottom(s, from, 1150, 170);
  if (o.decor) decor(s, o.decor, { bg, text: o.decorText || String(o.idx).padStart(2, '0'), at: 'top' });
  footer(s, o.idx, bgKey);
}

// ================= close =================

// Close: the logo lockup from BRAND.logo, the CTA as the headline with the handle in the
// accent colour, the promise, a pill, numbered sources, and every credit. With
// BRAND.logo.image (the brand's own logo file) it draws a 'LOGO' slot instead of the
// letter badge: upload the file to it with scaleMode 'FIT' (logo.imageOnDark on a dark close).
// variant 'dark' (default: photo IMG-<idx> under a scrim) or 'light' (no photo, the scheme's ground).
// o: { idx = N, variant, img, headline = 'Ikuti ' + BRAND.handle, accent = BRAND.handle, promise, cta, sources: [], credits }
function closeSlide(s, o) {
  const idx = o.idx || N, L = BRAND.logo || {}, light = o.variant === 'light', bg = light ? C.ground : C.dark;
  const k = chrome(light ? 'light' : 'dark'), ink = light ? C.text : inkOn(bg);
  const acc = light ? (contrast(C.primary, bg) >= 3 ? C.primary : C.text) : accentOn(bg);
  const pill = light ? C.primary : C.highlight;
  s.fills = [solid(bg)];
  if (!light) { R(s, o.img || 'IMG-' + idx, 0, 0, s.width, s.height, C.dark); vgrad(s, [[0, 0.7], [0.4, 0.86], [0.75, 0.95], [1, 0.98]]); }
  header(s, (L.wordmark || '').toUpperCase(), idx, light ? 'light' : 'dark');
  if (L.image) R(s, 'LOGO', M, 160, 360, 100, null);
  else {
    if (L.letter) { R(s, 'logo-badge', M, 168, 84, 84, C.highlight, null, 22); T(s, L.letter, F.bodyBold, 46, inkOn(C.highlight), M, 183, { w: 84, align: 'CENTER', name: 'logo-letter' }); }
    if (L.wordmark) T(s, L.wordmark, F.bodyMedium, 50, ink, L.letter ? M + 106 : M, 182, { ls: -1, name: 'wordmark' });
  }
  const text = o.headline || ('Ikuti ' + BRAND.handle);
  const hd = T(s, text, F.display, 116, ink, M, 322, { ls: -2.5, lh: 100, name: 'headline' });
  if (hd.width > CW) hd.fontSize = Math.floor(116 * CW / hd.width);
  const accent = o.accent || BRAND.handle, ai = accent ? text.indexOf(accent) : -1;
  if (ai >= 0) hd.setRangeFills(ai, ai + accent.length, [solid(acc)]);
  let y = 604;
  if (o.promise) { const p = body(s, o.promise, 462, { size: 34, color: k.soft, op: k.softOp, w: 820, name: 'promise' }); y = Math.max(604, Math.round(p.y + p.height + 40)); }
  if (o.cta) {
    const w = Math.max(280, Math.round(measure(s, o.cta, F.label, 26, 4) + 100));
    R(s, 'cta', M, y, w, 84, pill, null, 42);
    T(s, o.cta, F.label, 26, inkOn(pill), M, y + 26, { w, align: 'CENTER', ls: 4, name: 'cta-label' });
    y += 148;
  }
  R(s, 'rule-sources', M, y, CW, 1, k.rule, k.ruleOp);
  T(s, BRAND.sourcesLabel || 'SUMBER', F.label, 20, acc, M, y + 24, { ls: 6, name: 'sources-label' });
  y += 66;
  (o.sources || []).forEach((t, i) => {
    T(s, String(i + 1).padStart(2, '0'), F.label, 20, k.soft, M, y + 2, { op: k.softOp, name: 'source-n-' + (i + 1) });
    const n = T(s, t, F.body, 22, ink, M + 52, y, { w: CW - 52, lh: 135, op: 0.82, name: 'source-' + (i + 1) });
    y = Math.round(n.y + n.height + 12);
  });
  if (o.credits) T(s, o.credits, F.label, 18, k.soft, M, y + 22, { w: CW, lh: 140, op: k.softOp, name: 'credits' });
  footer(s, idx, light ? 'light' : 'dark');
}

// ================= accents =================

// Background accents, at most on two slides per carousel, drawn behind the content:
// 'bigIndex' a giant faint number (o.text, default the slide number; o.at 'bottom' or 'top'),
// 'dots' a dot grid in the top right, 'ticks' a strip of thin bars above the footer (pass
// o.values for real data; otherwise a seeded pattern, o.seed). o.bg: the colour behind
// (default the scheme's ground).
function decor(s, kind, o) {
  o = o || {}; const bg = o.bg || C.ground, made = [];
  const faint = bg === C.ground ? [C.surface, null] : [inkOn(bg), 0.08];
  if (kind === 'bigIndex') {
    const t = T(s, o.text || String(slides.indexOf(s) + 1).padStart(2, '0'), F.display, o.size || 560, faint[0], 0, 0, { lh: 100, ls: -6, op: faint[1], name: 'decor-index' });
    t.x = Math.round(s.width - t.width + 40); t.y = Math.round(o.at === 'top' ? 60 : s.height - t.height - 110); made.push(t);
  }
  if (kind === 'dots') {
    for (let r = 0; r < 6; r++) for (let c = 0; c < 10; c++) made.push(E(s, 'decor-dot', s.width - M - 9 * 28 - 8 + c * 28, 150 + r * 28, 8, bg === C.ground ? C.rule : faint[0], bg === C.ground ? null : 0.25));
  }
  if (kind === 'ticks') {
    const v = o.values || seeded(o.seed || 7, 64), mx = Math.max(...v), mn = Math.min(...v), n = v.length, gap = 4, tw = (CW - gap * (n - 1)) / n;
    v.forEach((x, i) => { const th = 6 + 40 * (x - mn) / ((mx - mn) || 1); made.push(R(s, 'decor-tick', M + i * (tw + gap), 1176 - th, Math.max(2, tw), th, i === n - 1 ? C.highlight : (bg === C.ground ? C.rule : faint[0]), i === n - 1 || bg === C.ground ? null : 0.22)); });
  }
  const base = s.children.findIndex(n => n.name === 'scrim') + 1;
  made.forEach((n, i) => s.insertChild(base + i, n));
  return made;
}
function seeded(seed, n) { let x = seed; const out = []; for (let i = 0; i < n; i++) { x = (x * 1103515245 + 12345) % 2147483648; out.push(x / 2147483648); } return out; }

// ================= checks =================

// Text past the right margin or into the footer.
function overflowCheck() {
  const issues = [];
  for (const s of slides) for (const t of s.findAll(n => n.type === 'TEXT' && !/^decor-/.test(n.name))) {
    const bx = t.absoluteBoundingBox, fb = s.absoluteBoundingBox;
    const right = bx.x + bx.width - fb.x, bottom = bx.y + bx.height - fb.y;
    if (right > s.width - M + 4 || (bottom > s.height - 150 && !/footer/.test(t.name))) issues.push({ slide: s.name, name: t.name, right: Math.round(right), bottom: Math.round(bottom) });
  }
  return issues;
}

// Call last and return its result. Adds to overflowCheck: a cover with neither a photo, a
// chart, nor display type over 100 px; an interior slide whose content ends above 70% of
// the height (an empty lower third reads as unfinished on a phone); an interior slide whose
// largest text is under 64 px; and a rhythm note when five or more slides in a row share
// the scheme's plain ground (try fullBleed, statement, or a dark slide).
function layoutCheck() {
  const issues = overflowCheck(), grounds = [];
  slides.forEach((s, i) => {
    const kids = s.children.filter(n => !/^(footer|progress-|scrim|decor-)/.test(n.name) && !(n.width >= s.width && n.height >= s.height));
    const sizes = s.findAll(n => n.type === 'TEXT' && !/^decor-/.test(n.name)).map(t => typeof t.fontSize === 'number' ? t.fontSize : 0);
    const g = (GROUND[s.id] || {}).ground || C.ground, fill = s.fills[0] && s.fills[0].color;
    const plain = fill && Math.abs(fill.r - g.r) + Math.abs(fill.g - g.g) + Math.abs(fill.b - g.b) < 0.02;
    const photo = s.children.some(n => /^IMG-/.test(n.name) && n.width >= s.width && n.height >= s.height * 0.5);
    grounds.push(plain && !photo ? 'plain' : 'other');
    if (i === 0) {
      const ok = photo || s.findAll(n => /^IMG-|^bar-/.test(n.name)).length || Math.max(0, ...sizes) >= 100;
      if (!ok) issues.push({ slide: s.name, issue: 'cover has no photo, chart, or display type over 100 px: use a cover variant' });
      return;
    }
    if (i === slides.length - 1) return;
    const bottom = Math.max(0, ...kids.map(n => n.y + n.height));
    if (bottom < s.height * 0.7) issues.push({ slide: s.name, issue: 'content ends at y=' + Math.round(bottom) + ': enlarge the proof element or the type, or merge this slide (aim for about y=1050–1150)' });
    if (Math.max(0, ...sizes) < 64) issues.push({ slide: s.name, issue: 'largest text is ' + Math.max(0, ...sizes) + ' px: headlines are 72–84' });
  });
  let run = 0;
  grounds.forEach((g, i) => { run = g === 'plain' ? run + 1 : 0; if (run === 5) issues.push({ slide: slides[i].name, rhythm: 'five slides in a row on the plain ground: make one of them a fullBleed, statement, or dark slide' }); });
  return issues;
}

// ================= example: an 8-slide carousel in one call =================
// (from references/examples/ai-cost-js-carousel.md; shortened). Set SCHEME above, or call
// useScheme('gelap') before the first slide.
//
// { const s = slide(0, '01 Cover', true);
//   coverDark(s, { eyebrow: 'BENCHMARK · NOLAN LAWSON · OKT 2026', number: '60',
//     lines: ['kali agent AI membangun', 'aplikasi yang sama dengan', '12 framework JavaScript.'],
//     body: 'Biaya per build berkisar $2,67 sampai $4,97, padahal skor Lighthouse-nya nyaris sama.' }); }
// { const s = slide(1, '02 Konteks', false); header(s, 'KONTEKS', 2);
//   plate(s, 'IMG-2', 150, 400, 'Foto: <name> / Unsplash');
//   const h = headline(s, [[['Anggap saja ', false], ['argo taksi.', 'hl']]], M, 612);
//   body(s, '<body>', h.bottom + 26); footer(s, 2); }
// { const s = slide(2, '03 Data', false); header(s, 'DATA · MEDIAN 5 BUILD', 3);
//   const h = headline(s, [[['Argo Angular ', false], ['86% lebih', 'hl']], [['mahal', 'hl'], [' dari Hono+htmx.', false]]], M, 150, { size: 72 });
//   table(s, h.bottom + 40, { head: {...}, rows: [...], best: [0, 1, 2, 0, 1], note: '<one caveat>' }); footer(s, 3); }
// { const s = slide(4, '05 Komplikasi', false); header(s, 'KOMPLIKASI', 5);
//   const h = headline(s, [...], M, 150); const b = body(s, '<body>', h.bottom + 22, { size: 30 });
//   const y = artefact(s, b.y + b.height + 30, { name: 'ART-5', w: 1380, h: 570, style: 'window', url: 'nolanlawson.com', label: '<columns>', credit: 'Tangkapan layar: <site>, <date>', marks: [[128, 204], [488, 564]] });
//   quote(s, y + 40, '“<quote>”', '<NAME · CONTEXT>'); footer(s, 5); }
// { const s = slide(5, '06 Sisi lain', true);
//   fullBleed(s, { idx: 6, eyebrow: 'SISI LAIN', img: 'IMG-6', lines: [[['Argo ', false], ['jalan lagi', 'hl']], [['di setiap revisi.', false]]], body: '<body>', credit: 'Foto: <name> / Unsplash' }); }
// { const s = slide(6, '07 Catatan', false);
//   statement(s, { idx: 7, eyebrow: 'CATATAN <BRAND>', lines: [[['Sebelum pindah framework, ', false]], [['minta angkanya.', 'underline']]], body: '<why>', tip: '<action>' }); }
// { const s = slide(7, '08 Ikuti', true);
//   closeSlide(s, { promise: '<what this piece just did>', cta: 'IKUTI ' + BRAND.handle.toUpperCase(), sources: [...], credits: '<every credit>' }); }
// const media = {}; for (const s of slides) for (const n of s.findAll(n => /^(IMG|ART)-/.test(n.name))) media[n.name] = n.id;
// return { page: page.id, scheme: SCHEME_NAME, media, issues: layoutCheck() };
// Then, in a second call after upload_assets: duotone(id, 'dark') for full-bleed photos,
// duotone(id, 'light') for plates (the scheme's pairs).
