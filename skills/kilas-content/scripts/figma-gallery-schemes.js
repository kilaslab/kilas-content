// SPDX-License-Identifier: GPL-3.0-or-later
// The same six slides in every colour scheme of the brand, one row per scheme, so the owner
// can see what each scheme does to a carousel before a series or a piece picks one.
//
//   use_figma code = figma-helpers.js (the brand's BRAND block, PAGE = 'Galeri skema warna')
//                  + this file
//                  + return { page: page.id, frame: GALLERY_SCHEMES.frame, issues: layoutCheck() };
//
// Image slots: IMG-1 (cover, full-bleed), IMG-2 (plate), ART-5 (screenshot), IMG-8 (close).
// Copy or upload images into them, then toneNode(node, 'dark' | 'light') with the row's
// scheme (GROUND[frame.id].scheme) so each row's photos take that scheme's duotone.

const GALLERY_SCHEMES = { rows: [] }, ROW_KEYS = Object.keys(BRAND.schemes || { base: 1 });
const ROW_BARS = [['Hono+htmx', 2.67], ['Astro', 2.76], ['Nuxt', 2.82], ['Next.js', 3.14], ['SvelteKit', 4.28], ['Angular', 4.97]];

ROW_KEYS.forEach((key, r) => {
  useScheme(key);
  const at = (i, label, dark) => slide(r * 6 + i, key + ' · ' + label, dark);
  { const s = at(0, '01 Cover', true);
    coverDark(s, { eyebrow: 'BENCHMARK · NOLAN LAWSON · OKT 2026', number: '60', lines: ['kali agent AI membangun', 'aplikasi yang sama dengan', '12 framework JavaScript.'], body: 'Biaya per build berkisar $2,67 sampai $4,97, padahal skor Lighthouse-nya nyaris sama.' }); }
  { const s = at(1, '02 Konteks', false); header(s, 'KONTEKS', 2);
    plate(s, 'IMG-2', 150, 400, 'Foto: <nama> / Unsplash');
    const h = headline(s, [[['Anggap saja ', false], ['argo taksi.', 'hl']]], M, 612);
    const b = body(s, 'Nolan Lawson memberi Opus 5.5 tujuan yang sama: aplikasi Pokédex berdata PokéAPI, plus test yang wajib lulus. Hanya framework-nya yang diganti.', h.bottom + 26);
    const ry = Math.round(b.y + b.height + 34);
    R(s, 'rule-stat', M, ry, CW, 1, C.rule);
    T(s, '97–100', F.display, 84, C.primary, M, ry + 22, { ls: -2.5, name: 'stat' });
    T(s, 'skor Performance Lighthouse di 12 framework. Accessibility: 100 semua.', F.body, 26, C.muted, 530, ry + 30, { w: 462, lh: 135, name: 'stat-label' });
    footer(s, 2); }
  { const s = at(2, '03 Data', false); header(s, 'DATA · BIAYA PER BUILD', 3);
    const h = headline(s, [[['Argo Angular ', false], ['86% lebih', 'hl']], [['mahal', 'hl'], [' dari Hono+htmx.', false]]], M, 150, { size: 72 });
    const y = barChart(s, h.bottom + 80, { items: ROW_BARS.map(x => ({ label: x[0], value: x[1], display: '$' + String(x[1]).replace('.', ',') })), rowH: 100, highlight: [0], primary: [5] });
    T(s, 'Median 5 build per framework. Harga API menurut Claude Code, bukan tagihan.', F.body, 20, C.muted, M, y + 24, { w: CW, name: 'note' });
    footer(s, 3); }
  { const s = at(3, '05 Komplikasi', false); header(s, 'KOMPLIKASI', 5);
    const h = headline(s, [[['Navigasi resmi ', false], ['tidak', 'hl']], [['menjamin', 'hl'], [' argo murah.', false]]], M, 150);
    const b = body(s, 'SvelteKit memakai MCP-nya di 5 dari 5 build dan tetap termahal ketiga. MCP Nuxt tidak pernah dipakai.', h.bottom + 22, { size: 30 });
    const y = artefact(s, b.y + b.height + 30, { name: 'ART-5', w: 1380, h: 570, label: 'TANGKAPAN LAYAR · ALAT RESMI · DIPAKAI AGENT?', credit: 'Tangkapan layar: nolanlawson.com, 28 Okt 2026', marks: [[128, 204], [488, 564]] });
    quote(s, y + 40, '“the current crop of MCPs and skills may be doing more harm than good”', 'NOLAN LAWSON · DUGAAN');
    footer(s, 5); }
  { const s = at(4, '07 Catatan', false);
    statement(s, { idx: 7, eyebrow: 'CATATAN BRAND', lines: [[['Sebelum pindah', false]], [['framework, ', false], ['minta', 'underline']], [['angkanya.', 'underline']]], body: 'Ini satu aplikasi kecil. Biaya Angular saja berkisar $3,19 sampai $6,82 antar-build.', tip: 'Uji kandidatnya dengan tugas yang sama, minimal 3 build per framework.', decor: 'bigIndex' }); }
  { const s = at(5, '08 Ikuti', true);
    closeSlide(s, { promise: 'Kabar teknologi seperti ini, lengkap dengan angka dan sumbernya.', cta: 'IKUTI ' + BRAND.handle.toUpperCase(), sources: ['Nolan Lawson, “The AI cost of JavaScript frameworks”, 28 Okt 2026', 'github.com/nolanlawson/agent-framework-benchmark'], credits: 'Ilustrasi AI · Foto Unsplash: <nama> · Tangkapan layar: nolanlawson.com' }); }
  GALLERY_SCHEMES.rows.push(key);
});

// ---- wrap: one row per scheme, its name above the row ----
{
  const cols = 6, cw = W + 80, chh = H + 160;
  const g = figma.createFrame(); g.name = 'galeri-skema'; g.fills = [solid(hex('#E9E9E4'))];
  g.resize(cols * cw + 80, ROW_KEYS.length * chh + 80); page.appendChild(g);
  slides.forEach((s, i) => {
    const r = Math.floor(i / cols), c = i % cols, x = 80 + c * cw, y = 80 + r * chh;
    if (c === 0) T(g, ROW_KEYS[r], F.label, 56, hex('#111111'), x, y, { ls: 4, name: 'row-label' });
    g.appendChild(s); s.x = x; s.y = y + 90;
  });
  GALLERY_SCHEMES.frame = g.id;
}
