// SPDX-License-Identifier: GPL-3.0-or-later
// Part 2 of the layout gallery (see figma-gallery.js): interiors, evidence, opinion,
// close, and accents, then the wrap of every frame on the page. Bundle with --keep-page.

const GALLERY = { cells: [] }, SCHEME_KEYS = Object.keys(BRAND.schemes || { base: 1 });
function cell(label, dark, k) {
  useScheme(SCHEME_KEYS[(k || 0) % SCHEME_KEYS.length]);
  const name = label + ' · ' + SCHEME_NAME, s = slide(GALLERY.cells.length, name, dark);
  GALLERY.cells.push({ name, scheme: SCHEME_NAME, id: s.id }); return s;
}

const SAMPLE_SERIES = [7620,10730,9460,9859,10069,9161,11084,11738,10942,12715,10161,10153,11356,11367,12826,12078,11529,10363,12142,9591,11410,12809,11431,12226,11032,12929,11518,12423,15095,12302,11747,13729,12051,12352,13489,12654,12633,12373,13108,12883,11551,12032,12792,13390,13286,13452,11454,12748,15086,13681,14770,13261,11749,15069,13764,11224,13137,11812,14115,13973,14378,12288,14595,13565,13871,12492,13161,16203,13052,13242,12402,12954,12115,12142,10034,13568,13805,12289,12910,13229,12468,13963,14395,16267,19671];


// ---- interior ----
{ const s = cell('Interior · plate + labelledItems', false, 1); header(s, 'PENYEBAB', 4);
  const h = headline(s, [[['Jalan baru membuat', false]], [['agent ', false], ['membuka peta.', 'hl']]], M, 150);
  plate(s, 'IMG-4', h.bottom + 28, 290, 'Foto: <nama> / Unsplash');
  labelledItems(s, h.bottom + 28 + 290 + 60, [['SVELTEKIT · $4,28', 'Kemungkinan terlalu baru untuk data latih Opus 5.5. Agent membaca panduan migrasinya di setiap build.'], ['GRACILE+LIT · $4,65', 'Agent kurang mengenalnya, lalu meng-clone repo atau membaca source di node_modules.'], ['ANGULAR · $4,97', 'Tampaknya karena kodenya paling besar: 2.009 baris.']]);
  footer(s, 4); }
{ const s = cell('Interior · splitPlate + quote', false, 3); header(s, 'KONTEKS', 2);
  const h = headline(s, [[['Anggap saja ', false], ['argo taksi.', 'italic']]], M, 150);
  const y = splitPlate(s, h.bottom + 40, { img: 'IMG-2', h: 520, credit: 'Foto: <nama> / Unsplash', label: 'TUJUAN SAMA', text: 'Nolan Lawson memberi Opus 5.5 aplikasi Pokédex yang sama, plus test yang wajib lulus. Hanya framework-nya yang diganti. Argonya mencatat dolar, menit, token, dan baris kode.' });
  quote(s, y + 44, '“the code size ultimately impacts the number of tokens”', 'NOLAN LAWSON · OKT 2026');
  footer(s, 2); }
{ const s = cell('Interior · fullBleed', true, 2);
  fullBleed(s, { idx: 6, eyebrow: 'SISI LAIN', img: 'IMG-6', lines: [[['Argo ', false], ['jalan lagi', 'hl']], [['di setiap revisi.', false]]], body: 'Biaya build dibayar sekali. Ukuran kode ikut menentukan token di setiap revisi berikutnya, dan JavaScript-nya dikirim ke setiap pengunjung.', credit: 'Foto: <nama> / Unsplash' }); }
{ const s = cell('Interior · steps', false, 4); header(s, 'CARA MENGUKUR', 7);
  const h = headline(s, [[['Tiga langkah sebelum', false]], [['pindah ', false], ['framework.', 'hl']]], M, 150);
  const b = body(s, 'Klaim "lebih cocok untuk agent" bisa diuji dengan biaya beberapa build.', h.bottom + 22);
  steps(s, b.y + b.height + 50, [['Tulis satu tugas yang sama', 'Spesifikasi dan test yang wajib lulus, untuk setiap kandidat.'], ['Bangun minimal 3 kali per framework', 'Hasil agent acak; satu build hanyalah anekdot.'], ['Bandingkan angkanya', 'Biaya, waktu, baris kode, dan JavaScript yang dikirim ke pengguna.'], ['Putuskan, lalu catat alasannya', 'Supaya keputusan berikutnya punya pembanding.']], { gap: 44 });
  footer(s, 7); }

// ---- evidence ----
{ const s = cell('Evidence · artefact plain', false, 0); header(s, 'KOMPLIKASI', 5);
  const h = headline(s, [[['Navigasi resmi ', false], ['tidak', 'hl']], [['menjamin', 'hl'], [' argo murah.', false]]], M, 150);
  const b = body(s, 'SvelteKit memakai MCP-nya di 5 dari 5 build dan tetap termahal ketiga. MCP Nuxt tidak pernah dipakai.', h.bottom + 22, { size: 30 });
  const y = artefact(s, b.y + b.height + 30, { name: 'ART-5', w: 1380, h: 570, label: 'TANGKAPAN LAYAR · ALAT RESMI · DIPAKAI AGENT?', credit: 'Tangkapan layar: nolanlawson.com, 28 Okt 2026', marks: [[128, 204], [488, 564]] });
  quote(s, y + 40, '“the current crop of MCPs and skills may be doing more harm than good”', 'NOLAN LAWSON · DUGAAN');
  footer(s, 5); }
{ const s = cell('Evidence · artefact window + tipCard', false, 1); header(s, 'CATATAN BRAND', 7);
  const h = headline(s, [[['Sebelum pindah framework,', false]], [['minta angkanya.', 'hl']]], M, 150, { size: 72 });
  const y = artefact(s, h.bottom + 36, { name: 'ART-7', w: 1740, h: 592, style: 'window', url: 'github.com/nolanlawson/agent-framework-benchmark', credit: 'Tangkapan layar: github.com, 2 Nov 2026', marks: [{ x0: 900, x1: 1435, y0: 437, y1: 467 }] });
  tipCard(s, y + 40, 'BUAT TIM YANG MAU MIGRASI', 'Uji kandidatnya dengan tugas yang sama, minimal 3 build per framework, lalu bandingkan angkanya.');
  footer(s, 7); }
{ const s = cell('Evidence · artefact tilt', false, 2); header(s, 'BUKTI', 5);
  const h = headline(s, [[['MCP Nuxt ', false], ['tidak pernah', 'underline']], [['dipakai agent.', false]]], M, 150);
  const b = body(s, 'Padahal Nuxt yang paling hemat token: 3,85 juta per build, terendah dari 12 framework.', h.bottom + 22);
  const y = artefact(s, b.y + b.height + 50, { name: 'ART-5', w: 1380, h: 570, style: 'tilt', credit: 'Tangkapan layar: nolanlawson.com, 28 Okt 2026', marks: [[128, 204]] });
  quote(s, y + 40, '“For Nuxt, the MCP was never used by the agents.”', 'NOLAN LAWSON · OKT 2026');
  footer(s, 5); }

// ---- opinion ----
{ const s = cell('Opinion · checklist', false, 3); header(s, 'CATATAN BRAND', 7);
  const h = headline(s, [[['Sebelum pindah framework,', false]], [['minta angkanya.', 'color']]], M, 150, { size: 72 });
  const b = body(s, 'Ini satu aplikasi kecil yang mirip Wikipedia. Biaya Angular saja berkisar $3,19 sampai $6,82 antar-build.', h.bottom + 26);
  const y = checklist(s, b.y + b.height + 44, 'CEK SEBELUM MIGRASI', ['Tugas dan test yang sama untuk setiap kandidat.', 'Minimal 3 build per framework.', 'Biaya, baris kode, dan JavaScript dibandingkan berdampingan.', 'Keputusan dan alasannya dicatat.'], { size: 32 });
  T(s, 'Harness-nya terbuka untuk di-fork: github.com/nolanlawson/agent-framework-benchmark', F.label, 18, C.muted, M, y + 24, { w: CW, ls: 2, name: 'note' });
  footer(s, 7); }
{ const s = cell('Opinion · statement (highlight)', false, 4);
  statement(s, { idx: 7, eyebrow: 'CATATAN BRAND', lines: [[['Sebelum pindah', false]], [['framework, ', false], ['minta', 'underline']], [['angkanya.', 'underline']]], body: 'Ini satu aplikasi kecil. Biaya Angular saja berkisar $3,19 sampai $6,82 antar-build.', tip: 'Uji kandidatnya dengan tugas yang sama, minimal 3 build per framework.', decor: 'bigIndex' }); }

// ---- close ----
{ const s = cell('Close · dark', true, 2);
  closeSlide(s, { promise: 'Kabar teknologi seperti ini, lengkap dengan angka dan sumbernya.', cta: 'IKUTI ' + BRAND.handle.toUpperCase(), sources: ['Nolan Lawson, “The AI cost of JavaScript frameworks”, 28 Okt 2026', 'github.com/nolanlawson/agent-framework-benchmark', 'Kurs JISDOR Bank Indonesia, 30 Okt 2026'], credits: 'Ilustrasi AI · Foto Unsplash: <nama> · Tangkapan layar: nolanlawson.com' }); }
{ const s = cell('Close · light', false, 1);
  closeSlide(s, { variant: 'light', promise: 'Kabar teknologi seperti ini, lengkap dengan angka dan sumbernya.', cta: 'IKUTI ' + BRAND.handle.toUpperCase(), sources: ['Nolan Lawson, “The AI cost of JavaScript frameworks”, 28 Okt 2026', 'github.com/nolanlawson/agent-framework-benchmark'], credits: 'Foto Unsplash: <nama> · Tangkapan layar: nolanlawson.com' }); }

// ---- accents ----
{ const s = cell('Accent · decor dots + ticks', false, 3); header(s, 'PENYEBAB', 4);
  decor(s, 'dots');
  const h = headline(s, [[['Patch hasil AI', false]], [['datang ', false], ['tanpa henti.', 'hl']]], M, 150);
  const q = quote(s, h.bottom + 50, '“We are completely overwhelmed, of course.”', 'JAKUB KICINSKI · MAINTAINER JARINGAN LINUX', { size: 56 });
  body(s, 'Di siklus Linux 7.3 ia memperkirakan sepertiga sampai separuh patch net-next tampak seperti perbaikan prioritas rendah buatan AI.', q + 50);
  decor(s, 'ticks', { values: SAMPLE_SERIES.slice(-64) });
  footer(s, 4); }

// ---- wrap every cell on the page in one frame, five per row, with its label ----
{
  const frames = page.children.filter(n => n.type === 'FRAME' && n.name !== 'galeri');
  const cols = 5, cw = W + 80, chh = H + 140;
  const g = figma.createFrame(); g.name = 'galeri'; g.fills = [solid(hex('#E9E9E4'))];
  g.resize(cols * cw + 80, Math.ceil(frames.length / cols) * chh + 80); page.appendChild(g);
  frames.forEach((s, i) => {
    const x = 80 + (i % cols) * cw, y = 80 + Math.floor(i / cols) * chh;
    T(g, s.name, F.label, 40, hex('#111111'), x, y, { name: 'label' });
    g.appendChild(s); s.x = x; s.y = y + 70;
  });
  GALLERY.frame = g.id;
}
