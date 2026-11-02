// SPDX-License-Identifier: GPL-3.0-or-later
// Every layout variant on one page, with sample content from
// references/examples/ai-cost-js-carousel.md, so an owner (or you) can see the options in
// a brand's own design before choosing. Use it once per brand, or after changing the
// helpers:
//
// The page uses every layout, which is over use_figma's code limit in one call, so it is
// built in two: this file (covers and data), then figma-gallery-2.js (interiors, evidence,
// opinion, close, accents), which also wraps every frame on the page.
//
//   python3 scripts/figma_bundle.py --brand <pack>/design.md --page 'Galeri layout' \
//     scripts/figma-gallery.js -o g1.js --tail 'return { issues: layoutCheck() };'
//   python3 scripts/figma_bundle.py --brand <pack>/design.md --page 'Galeri layout' --keep-page \
//     scripts/figma-gallery-2.js -o g2.js --tail 'return { frame: GALLERY.frame, issues: layoutCheck() };'
//
// Each cell is drawn in one of the brand's colour schemes (the k-th key of BRAND.schemes,
// wrapping round), so the page shows how the feed varies; figma-gallery-schemes.js shows
// one carousel in every scheme. Image slots (IMG-*, ART-*) stay in the surface colour;
// upload or copy image fills into them, then toneNode(node, 'light' | 'dark') with the
// cell's scheme. The frames are wrapped in one frame, 'galeri', for a single screenshot.

const GALLERY = { cells: [] }, SCHEME_KEYS = Object.keys(BRAND.schemes || { base: 1 });
function cell(label, dark, k) {
  useScheme(SCHEME_KEYS[(k || 0) % SCHEME_KEYS.length]);
  const name = label + ' · ' + SCHEME_NAME, s = slide(GALLERY.cells.length, name, dark);
  GALLERY.cells.push({ name, scheme: SCHEME_NAME, id: s.id }); return s;
}

const SAMPLE_ROWS = [
  ['Hono+htmx', 2.67, '2,67', '8,6', '4,26', '1.370', '18'], ['Astro', 2.76, '2,76', '8,2', '4,13', '1.461', '0'],
  ['Nuxt', 2.82, '2,82', '9,0', '3,85', '1.415', '84'], ['Vanilla', 2.98, '2,98', '10,1', '5,00', '1.492', '7'],
  ['Next.js', 3.14, '3,14', '10,9', '4,99', '1.539', '142'], ['Qwik', 3.27, '3,27', '10,7', '5,64', '1.744', '40'],
  ['TanStack Start', 3.54, '3,54', '10,3', '7,07', '1.697', '118'], ['SolidStart', 3.79, '3,79', '11,2', '7,13', '1.630', '40'],
  ['React Router', 3.81, '3,81', '12,5', '7,58', '1.564', '115'], ['SvelteKit', 4.28, '4,28', '10,8', '8,53', '1.611', '36'],
  ['Gracile+Lit', 4.65, '4,65', '12,1', '9,04', '1.717', '8'], ['Angular', 4.97, '4,97', '17,2', '9,76', '2.009', '93'],
];
const SAMPLE_SERIES = [7620,10730,9460,9859,10069,9161,11084,11738,10942,12715,10161,10153,11356,11367,12826,12078,11529,10363,12142,9591,11410,12809,11431,12226,11032,12929,11518,12423,15095,12302,11747,13729,12051,12352,13489,12654,12633,12373,13108,12883,11551,12032,12792,13390,13286,13452,11454,12748,15086,13681,14770,13261,11749,15069,13764,11224,13137,11812,14115,13973,14378,12288,14595,13565,13871,12492,13161,16203,13052,13242,12402,12954,12115,12142,10034,13568,13805,12289,12910,13229,12468,13963,14395,16267,19671];

// ---- covers ----
{ const s = cell('Cover · coverDark', true, 0);
  coverDark(s, { eyebrow: 'BENCHMARK · NOLAN LAWSON · OKT 2026', number: '60', lines: ['kali agent AI membangun', 'aplikasi yang sama dengan', '12 framework JavaScript.'], body: 'Biaya per build berkisar $2,67 sampai $4,97, padahal skor Lighthouse-nya nyaris sama.' }); }
{ const s = cell('Cover · coverSplit', false, 1);
  coverSplit(s, { eyebrow: 'BENCHMARK · OKT 2026', number: '$4,97', lines: [[['vs ', false], ['$2,67', 'hl'], [' untuk', false]], [['aplikasi yang sama.', false]]], body: 'Agent AI membangun satu aplikasi dengan 12 framework JavaScript. Skor Lighthouse-nya nyaris sama.', credit: 'Foto: <nama> / Unsplash' }); }
{ const s = cell('Cover · coverType (highlight)', false, 0);
  coverType(s, { bg: 'highlight', eyebrow: 'BENCHMARK · OKT 2026', kicker: '12 FRAMEWORK · 60 BUILD', size: 110, lines: [[['Biaya beda ', false], ['86%.', 'underline']], [['Skornya', false]], [['nyaris sama.', 'italic']]], body: 'Satu aplikasi dibangun agent AI dengan 12 framework JavaScript.' }); }
{ const s = cell('Cover · coverType (dark + bigIndex)', true, 2);
  coverType(s, { bg: 'dark', eyebrow: 'BENCHMARK · OKT 2026', size: 110, lines: [[['Framework mana', false]], [['paling ', false], ['murah', 'color']], [['untuk agent AI?', false]]], body: 'Satu aplikasi, 60 build, 12 framework JavaScript.', decor: 'bigIndex', decorText: '12' }); }
{ const s = cell('Cover · coverChart', false, 1);
  coverChart(s, { eyebrow: '#SERI · BIAYA AGENT AI', lines: [[['Hono+htmx paling ', false], ['murah', 'hl']], [['dibangun agent AI.', false]]],
    items: [['Hono+htmx', 2.67], ['Astro', 2.76], ['Nuxt', 2.82], ['Next.js', 3.14], ['SvelteKit', 4.28], ['Angular', 4.97]].map(r => ({ label: r[0], value: r[1], display: '$' + String(r[1]).replace('.', ',') })),
    highlight: [0], primary: [5], source: 'Sumber: Nolan Lawson, median 5 build per framework, 28 Okt 2026' }); }
{ const s = cell('Cover · coverQuote', true, 4);
  coverQuote(s, { eyebrow: 'KUTIPAN · OKT 2026', quote: 'the current crop of MCPs and skills may be doing more harm than good', name: 'Nolan Lawson', role: 'PENULIS BENCHMARK · DUGAAN DI PENUTUP TULISANNYA' }); }

// ---- data ----
{ const s = cell('Data · table', false, 1); header(s, 'DATA · MEDIAN 5 BUILD PER FRAMEWORK', 3);
  const h = headline(s, [[['Argo Angular ', false], ['86% lebih', 'hl']], [['mahal', 'hl'], [' dari Hono+htmx.', false]]], M, 150, { size: 72 });
  const sub = body(s, 'Hono+htmx $2,67 (sekitar Rp48 ribu) per build. Angular $4,97 (sekitar Rp90 ribu).', h.bottom + 16, { size: 28, color: C.muted });
  table(s, sub.y + sub.height + 28, { head: { name: 'FRAMEWORK', values: ['BIAYA $', 'MENIT', 'TOKEN', 'BARIS', 'JS'] },
    rows: SAMPLE_ROWS.map(r => ({ name: r[0], bar: r[1], values: r.slice(2), barColor: r[0] === 'Angular' ? 'primary' : r[0] === 'Hono+htmx' ? 'highlight' : null, strong: r[0] === 'Angular' || r[0] === 'Hono+htmx' })),
    best: [0, 1, 2, 0, 1], note: 'Biaya = harga API menurut Claude Code, bukan tagihan sebenarnya. Token dalam juta, JS dalam KiB. Stabilo kuning = terbaik di kolomnya.' });
  footer(s, 3); }
{ const s = cell('Data · barChart + ref', false, 2); header(s, 'DATA · BIAYA PER BUILD', 3);
  const h = headline(s, [[['Separuh framework', false]], [['di bawah ', false], ['$3,50.', 'hl']]], M, 150);
  barChart(s, h.bottom + 70, { items: SAMPLE_ROWS.map(r => ({ label: r[0], value: r[1], display: '$' + r[2] })), rowH: 60, highlight: [0], primary: [11], ref: { value: 3.5, label: '$3,50' } });
  footer(s, 3); }
{ const s = cell('Data · columnChart + ref', false, 0); header(s, 'DATA · 85 MERGE WINDOW SEJAK 2011', 3);
  const h = headline(s, [[['Rekor lama dilewati ', false]], [['3.404 commit.', 'hl']]], M, 150);
  columnChart(s, h.bottom + 90, { values: SAMPLE_SERIES, h: 520, ref: { value: 16267, label: 'REKOR LAMA 16.267' }, first: '3.1 · 2011', last: '7.4 · 2026' });
  footer(s, 3); }
{ const s = cell('Data · bigStat', false, 4); header(s, 'DATA', 3);
  const h = headline(s, [[['Argo Angular ', false], ['jauh', 'italic']], [['lebih mahal.', false]]], M, 150);
  bigStat(s, h.bottom + 20, { value: '86%', size: 300, label: 'biaya median Angular di atas Hono+htmx, untuk aplikasi yang sama.', compare: [{ name: 'Angular', value: 4.97, display: '$4,97', color: 'primary' }, { name: 'Hono+htmx', value: 2.67, display: '$2,67', color: 'highlight' }] });
  footer(s, 3); }
{ const s = cell('Data · versus', false, 3); header(s, 'SISI LAIN', 6);
  const h = headline(s, [[['Kode yang ditulis', false]], [['agent ', false], ['ikut dibayar.', 'hl']]], M, 150);
  const y = versus(s, h.bottom + 50, { h: 460, left: { kicker: 'HONO+HTMX', big: '1.370', label: 'baris kode untuk aplikasi yang sama' }, right: { kicker: 'ANGULAR', big: '2.009', label: 'baris kode, 47% lebih banyak' } });
  body(s, 'Setiap revisi berikutnya membaca kode itu lagi, jadi jumlah barisnya ikut menentukan token.', y + 40);
  footer(s, 6); }
{ const s = cell('Data · dots', false, 2); header(s, 'DATA', 6);
  const h = headline(s, [[['Hono+htmx cukup ', false], ['68%', 'hl']], [['dari kode Angular.', false]]], M, 150);
  dots(s, h.bottom + 44, { pct: 68, cols: 10, width: 640, label: '1.370 dari 2.009 baris. Satu titik = 1%.' });
  footer(s, 6); }
{ const s = cell('Data · plate + statCards', false, 0); header(s, 'SISI LAIN', 6);
  plate(s, 'IMG-6', 150, 260, 'Foto: <nama> / Unsplash');
  const h = headline(s, [[['Argo ', false], ['jalan lagi', 'hl']], [['di setiap revisi.', false]]], M, 470);
  const b = body(s, 'Biaya build dibayar sekali. Ukuran kode ikut menentukan token di setiap revisi berikutnya.', h.bottom + 22);
  statCards(s, b.y + b.height + 34, [{ kicker: 'BARIS KODE', big: '1.370', who: 'Hono+htmx', vs: 'vs 2.009 baris di Angular' }, { kicker: 'JAVASCRIPT KE HP', big: '0 KiB', who: 'Astro', vs: 'vs 142 KiB di Next.js' }]);
  footer(s, 6); }
