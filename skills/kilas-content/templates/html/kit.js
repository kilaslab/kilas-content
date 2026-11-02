// SPDX-License-Identifier: GPL-3.0-or-later
// Slide kit for the HTML renderer (see references/html-render.md). It:
// - gives each <section class="slide"> a ground class from its layout or data-bg
// - adds the header (data-eyebrow, "03 / 08"), the footer, and the progress bar
// - adds scrims over full-bleed photos, the logo and labels on the close slide
// - builds .bars, .columns, .dots, table bars, and screenshot marks from data-* attributes
// - checks the layout (as layoutCheck() in figma-helpers.js) and writes the result to
//   window.__issues and <pre id="kit-issues">, then sets <html data-ready="1">
// URL options: ?only=3 shows slide 3 alone at 0,0 (for screenshots); ?scheme=name
// switches the colour scheme.
(function () {
  const q = new URLSearchParams(location.search);
  if (q.get('scheme')) document.body.dataset.scheme = q.get('scheme');
  const rootCss = getComputedStyle(document.body);
  const pageIssues = [];
  const v = n => { const s = rootCss.getPropertyValue(n).trim(); try { return JSON.parse(s); } catch (e) { return s.replace(/^["']|["']$/g, ''); } };
  const B = { site: v('--brand-site'), handle: v('--brand-handle'), swipe: v('--brand-swipe') || '→', end: v('--brand-end'), sources: v('--brand-sources'), letter: v('--brand-logo-letter'), wordmark: v('--brand-wordmark'), logo: v('--brand-logo-image'), logoDark: v('--brand-logo-image-dark') };
  const known = (v('--brand-schemes') || '').split(/\s+/).filter(Boolean);
  const asked = document.body.dataset.scheme;
  if (asked && known.length && !known.includes(asked)) pageIssues.push({ issue: 'unknown scheme "' + asked + '" (the brand has: ' + known.join(', ') + '); the default was used' });
  const slides = [...document.querySelectorAll('section.slide')];
  const N = +(document.body.dataset.total || slides.length);
  const pad = n => String(n).padStart(2, '0');
  const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
  const fmt = (n, sep) => String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, sep || '.');
  const nice = raw => { const p = Math.pow(10, Math.floor(Math.log10(raw || 1))); return [1, 2, 2.5, 5, 10].map(m => m * p).find(x => x >= raw); };

  function groundOf(s) {
    const map = { dark: 'dark', highlight: 'highlight', accent: 'highlight', primary: 'primary', ground: 'ground', light: 'ground' };
    if (s.dataset.bg) return map[s.dataset.bg] || 'ground';
    if (s.matches('.cover-dark, .full-bleed, .cover-quote, .cover-type')) return 'dark';
    if (s.matches('.close')) return s.matches('.light') ? 'ground' : 'dark';
    if (s.matches('.statement')) return 'highlight';
    return 'ground';
  }

  // ---- structure ----
  slides.forEach((s, i) => {
    const g = groundOf(s), idx = +(s.dataset.index || i + 1);
    s.classList.add('g-' + g); s.dataset.ground = g;
    s.querySelectorAll('.bg').forEach(b => {
      if (b.nextElementSibling && b.nextElementSibling.classList.contains('scrim')) return;
      b.after(el('div', 'scrim' + (s.matches('.close') ? ' close' : s.matches('.full-bleed') ? ' soft' : '')));
    });
    s.querySelectorAll('.top-photo').forEach(t => { if (!t.querySelector('.scrim')) t.append(el('div', 'scrim top')); });
    if (!s.hasAttribute('data-no-chrome')) {
      const hm = s.dataset.head || (s.matches('.cover-split') ? 'dark' : '');
      const head = el('div', 'kit-head' + (hm ? ' g-' + hm : ''));
      const eyebrow = s.dataset.eyebrow || (s.matches('.close') ? (B.wordmark || '').toUpperCase() : '');
      head.append(el('span', '', eyebrow), el('span', '', pad(idx) + ' / ' + pad(N)));
      const foot = el('div', 'kit-foot'), cue = el('span', 'cue'), word = idx === N ? B.end : B.swipe, a = word.indexOf('→');
      if (a >= 0) { cue.append(word.slice(0, a)); cue.append(el('span', 'arrow', '→')); cue.append(word.slice(a + 1)); } else cue.textContent = word;
      foot.append(el('span', 'site', B.site), cue);
      const prog = el('div', 'kit-progress');
      for (let k = 1; k <= N; k++) prog.append(el('i', k < idx ? 'done' : k === idx ? 'cur' : ''));
      s.append(head, el('div', 'kit-rule' + (hm ? ' g-' + hm : '')), foot, prog);
    }
    const logo = s.querySelector('.close .logo, .logo');
    if (logo && !logo.children.length) {
      const src = g === 'ground' ? B.logo : (B.logoDark || B.logo);
      if (src) { const im = el('img', 'logo-img'); im.src = src; im.alt = B.wordmark || ''; logo.append(im); }
      else { if (B.letter) logo.append(el('i', '', B.letter)); if (B.wordmark) logo.append(el('b', '', B.wordmark)); }
    }
    const srcLabel = s.querySelector('.sources .label');
    if (srcLabel && !srcLabel.textContent.trim()) srcLabel.textContent = B.sources;
    s.querySelectorAll('.handle').forEach(h => { if (!h.textContent.trim()) h.textContent = B.handle; });
    s.querySelectorAll('.handle-up').forEach(h => { if (!h.textContent.trim()) h.textContent = B.handle.toUpperCase(); });
  });

  // ---- data builders ----
  document.querySelectorAll('.bars').forEach(bars => {
    const rows = [...bars.querySelectorAll('.bar-row')];
    const max = +bars.dataset.max || Math.max(...rows.map(r => +r.dataset.v || 0), +bars.dataset.ref || 0);
    rows.forEach(r => r.style.setProperty('--v', (+r.dataset.v || 0) / max));
    if (bars.dataset.rowH) bars.style.setProperty('--row', bars.dataset.rowH + 'px');
  });
  document.querySelectorAll('table.data').forEach(t => {
    const cells = [...t.querySelectorAll('td.bar')];
    const max = +t.dataset.max || Math.max(...cells.map(c => +c.dataset.v || 0));
    cells.forEach(c => { if (!c.querySelector('i')) c.append(el('i')); c.style.setProperty('--v', (+c.dataset.v || 0) / max); });
    t.querySelectorAll('td.best').forEach(c => { if (!c.querySelector('span')) { const sp = el('span', '', c.textContent); c.textContent = ''; c.append(sp); } });
  });
  document.querySelectorAll('.columns').forEach(c => {
    const vals = c.dataset.values.split(',').map(Number), ref = +c.dataset.ref || 0, sep = c.dataset.sep;
    const max = +c.dataset.max || nice(Math.max(...vals, ref) * 1.05);
    const hl = c.dataset.hl ? c.dataset.hl.split(',').map(Number) : [vals.length - 1];
    if (c.dataset.h) c.style.setProperty('--h', c.dataset.h + 'px');
    c.style.setProperty('--gap', vals.length > 40 ? '2px' : '6px');
    vals.forEach((x, i) => { const b = el('i', hl.includes(i) ? 'hl' : ''); b.style.setProperty('--v', x / max); c.append(b); });
    [0, .5, 1].forEach(f => { const g = el('div', 'grid'); g.style.bottom = (f * 100) + '%'; c.append(g); const ax = el('div', 'axis', fmt(max * f, sep)); ax.style.bottom = 'calc(' + (f * 100) + '% - 9px)'; c.append(ax); });
    if (ref) { const r = el('div', 'ref'); r.style.bottom = (ref / max * 100) + '%'; if (c.dataset.refLabel) r.append(el('span', '', c.dataset.refLabel)); c.append(r); }
    c._hl = hl; c._vals = vals; c._max = max; c._sep = sep;
    if (c.dataset.first || c.dataset.last) { const x = el('div', 'columns-x'); x.append(el('span', '', c.dataset.first || ''), el('span', '', c.dataset.last || '')); c.after(x); }
  });
  document.querySelectorAll('.dots').forEach(d => {
    const pct = Math.round(+d.dataset.pct || 0), cols = +d.dataset.cols || 20;
    d.style.setProperty('--cols', cols); if (d.dataset.width) d.style.setProperty('--w', d.dataset.width + 'px');
    for (let i = 0; i < 100; i++) d.append(el('i', i < pct ? 'on' : ''));
  });
  document.querySelectorAll('.decor-ticks').forEach(t => {
    let vals = t.dataset.values ? t.dataset.values.split(',').map(Number) : null;
    if (!vals) { let x = +t.dataset.seed || 7; vals = []; for (let i = 0; i < 64; i++) { x = (x * 1103515245 + 12345) % 2147483648; vals.push(x); } }
    const mx = Math.max(...vals), mn = Math.min(...vals);
    vals.forEach(x => { const i = el('i'); i.style.setProperty('--v', (x - mn) / ((mx - mn) || 1)); t.append(i); });
  });
  document.querySelectorAll('figure.artefact.window .frame').forEach(f => {
    if (f.querySelector('.wbar')) return;
    const bar = el('div', 'wbar'); bar.append(el('i'), el('i'), el('i'), el('span', '', f.closest('figure').dataset.url || ''));
    f.prepend(bar);
  });

  // ---- after fonts and images: sizes, then checks ----
  const only = +q.get('only');
  if (only) { document.body.classList.add('only'); slides.forEach((s, i) => { if (i + 1 !== only) s.style.display = 'none'; }); }
  const imgs = [...document.images];
  const loaded = Promise.all(imgs.map(im => im.complete ? 1 : new Promise(r => { im.addEventListener('load', r); im.addEventListener('error', r); })));
  const fonts = document.fonts ? document.fonts.ready : Promise.resolve();
  let done = false;
  const finish = () => {
    if (done) return; done = true;
    document.querySelectorAll('figure.artefact[data-marks]').forEach(fig => {
      const img = fig.querySelector('.frame img'); if (!img || !img.naturalWidth) return;
      const k = img.clientWidth / img.naturalWidth, top = img.offsetTop, frame = fig.querySelector('.frame');
      let marks = []; try { marks = JSON.parse(fig.dataset.marks); } catch (e) {}
      marks.forEach(m => {
        const row = Array.isArray(m), b = row ? { x0: 0, x1: img.naturalWidth, y0: m[0], y1: m[1] } : m, pad = row ? 0 : 4;
        const d = el('div', 'mark');
        d.style.left = Math.max(0, b.x0 * k - pad) + 'px'; d.style.width = ((b.x1 - b.x0) * k + 2 * pad) + 'px';
        d.style.top = (top + b.y0 * k) + 'px'; d.style.height = ((b.y1 - b.y0) * k) + 'px';
        frame.append(d);
      });
    });
    document.querySelectorAll('.bars[data-ref]').forEach(bars => {
      const track = bars.querySelector('.track'); if (!track) return;
      const max = +bars.dataset.max || Math.max(...[...bars.querySelectorAll('.bar-row')].map(r => +r.dataset.v || 0), +bars.dataset.ref);
      const r = el('div', 'ref'); r.style.left = (track.offsetLeft + 2 + (track.clientWidth - 2 - 130) * (+bars.dataset.ref) / max) + 'px';
      if (bars.dataset.refLabel) r.append(el('span', '', bars.dataset.refLabel));
      bars.append(r);
    });
    document.querySelectorAll('.columns').forEach(c => {
      (c._hl || []).forEach(i => { const bar = c.children[i]; if (!bar) return; const lab = el('div', 'val', fmt(c._vals[i], c._sep)); lab.style.left = (bar.offsetLeft + bar.offsetWidth / 2) + 'px'; lab.style.bottom = (c._vals[i] / c._max * 100) + '%'; lab.style.transform = 'translate(-50%, -12px)'; c.append(lab); });
    });
    const issues = pageIssues.concat(check());
    // fonts: a family that did not load renders in the fallback; compare widths against it
    const ctx = document.createElement('canvas').getContext('2d'), probe = 'Hamburgefontsiv 0123 WMQ';
    (v('--brand-fonts') || '').split('|').filter(Boolean).forEach(fam => {
      const same = ['monospace', 'serif'].every(g => { ctx.font = '40px ' + g; const a = ctx.measureText(probe).width; ctx.font = '40px "' + fam + '", ' + g; return ctx.measureText(probe).width === a; });
      if (same) issues.push({ issue: 'font "' + fam + '" did not load (no network, or not on Google Fonts): slides use the fallback; name a substitute in design.md' });
    });
    // images that did not load show as empty plates
    document.querySelectorAll('section.slide img').forEach(im => {
      const s = im.closest('section.slide');
      if (s.style.display === 'none' || (im.complete && im.naturalWidth)) return;
      issues.push({ slide: pad(slides.indexOf(s) + 1), issue: 'image missing: ' + (im.getAttribute('src') || '(no src)') });
      im.style.visibility = 'hidden';
    });
    window.__issues = issues;
    const pre = el('pre'); pre.id = 'kit-issues'; pre.hidden = true; pre.textContent = JSON.stringify(issues); document.body.append(pre);
    document.documentElement.dataset.ready = '1';
  };
  Promise.all([loaded, fonts]).then(() => requestAnimationFrame(() => requestAnimationFrame(finish)));
  setTimeout(finish, 9000);

  function check() {
    const issues = []; let run = 0;
    const chromeSel = '.kit-head, .kit-foot, .kit-progress, .kit-rule, .decor-index, .decor-dots, .decor-ticks, .scrim, #kit-issues';
    slides.forEach((s, i) => {
      if (s.style.display === 'none') return;
      const R = s.getBoundingClientRect(), name = pad(i + 1);
      let maxFont = 0, bottom = 0; const flagged = new Set();
      const w = document.createTreeWalker(s, NodeFilter.SHOW_TEXT);
      while (w.nextNode()) {
        const t = w.currentNode; if (!t.textContent.trim()) continue;
        const pe = t.parentElement; if (pe.closest(chromeSel)) continue;
        maxFont = Math.max(maxFont, parseFloat(getComputedStyle(pe).fontSize) || 0);
        const range = document.createRange(); range.selectNodeContents(t);
        for (const r of range.getClientRects()) {
          const right = r.right - R.left, b = r.bottom - R.top;
          bottom = Math.max(bottom, b);
          if (!flagged.has(pe) && (right > 1080 - 88 + 4 || b > 1200)) { flagged.add(pe); issues.push({ slide: name, text: t.textContent.trim().slice(0, 40), right: Math.round(right), bottom: Math.round(b) }); }
        }
      }
      s.querySelectorAll('.content > *').forEach(n => { bottom = Math.max(bottom, n.getBoundingClientRect().bottom - R.top); });
      const photo = s.querySelector('.bg, .top-photo');
      const plain = s.dataset.ground === 'ground' && !photo;
      run = plain ? run + 1 : 0;
      if (run === 5) issues.push({ slide: name, rhythm: 'five slides in a row on the plain ground: make one a full-bleed, statement, or dark slide' });
      if (i === 0) {
        if (!(photo || s.querySelector('.duo, .bar-row, .columns') || maxFont >= 100)) issues.push({ slide: name, issue: 'cover has no photo, chart, or display type over 100 px' });
        return;
      }
      if (i === slides.length - 1) return;
      if (bottom < 945) issues.push({ slide: name, issue: 'content ends at y=' + Math.round(bottom) + ': enlarge the proof element or the type, or merge this slide' });
      if (maxFont < 64) issues.push({ slide: name, issue: 'largest text is ' + Math.round(maxFont) + ' px: headlines are 72–84' });
    });
    return issues;
  }
})();
