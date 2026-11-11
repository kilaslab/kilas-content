// SPDX-License-Identifier: GPL-3.0-or-later
// Everything the 3D explainer says and when, in one place. scene.js reads only this file for
// words and times, so a new story is an edit here plus the props in scene.js.
// Example story: a buyer chats a shop at night, the owner sleeps, the shop's assistant answers
// an exchange question from the shop's notes, a shipping-cost question through a courier API,
// and takes payment through a payment gateway; in the morning the order is paid.
// Text on screen is >= 34 px on the 1080 canvas. Times are seconds.

// Colours live in three places; set all three from the brand pack's design.md: MASCOT here, the
// CSS variables on #stage in style.css (chat, cards, headline accent), and the palette C at the
// top of scene.js (the room and the 3D props).
// The mascot's colours and parts (DEFAULTS in mascot.js); give every key, so none of the
// example's colours stays on a new mascot. Match the brand's own renders.
export const MASCOT = {
  body: 0x45B3A5, boots: 0x349F92, ink: "#0E5751", badge: "#2B9487",
  tongue: "#7FCFC1", groove: "rgba(9,60,54,0.42)", // mouth inside; soft shadow round the face
  bodyTail: true,
};

// When each voice-over clip starts (vo0.mp3, vo1.mp3, ...): scripts/scene3d_video.py reads this.
// Set them after the clips exist, from their word timings (vo_elevenlabs.py --verify --words).
export const VO_STARTS = [0.3, 4.5, 12.2, 25.8, 37.0, 48.8, 55.6];

// Headline band per part: pill, line 1, line 2 (the accent line).
const HEADS = [
  { t0: 0, t1: 4.5, pill: "Jam 23.47 · pembeli chat", l1: "Pembeli chat,", l2: "kamu lagi tidur" },
  { t0: 4.5, t1: 12.1, pill: "Kenalan dulu", l1: "Asisten yang baca,", l2: "asisten yang balas" },
  { t0: 12.1, t1: 25.4, pill: "1 · Catatan tokomu", l1: "Jawab dari", l2: "catatanmu" },
  { t0: 25.4, t1: 36.6, pill: "2 · API kurir", l1: "Ongkir dicek", l2: "langsung" },
  { t0: 36.6, t1: 48.2, pill: "3 · Payment gateway", l1: "Tagihan QRIS,", l2: "langsung lunas" },
  { t0: 48.2, t1: 55.2, pill: "Paginya", l1: "Bangun,", l2: "udah lunas" },
  { t0: 55.2, t1: 60, pill: "", l1: "", l2: "", last: true },
];

export const BEATS = { at: (t) => HEADS.find((b) => t >= b.t0 && t < b.t1) || HEADS[HEADS.length - 1], heads: HEADS };

// Every event sits on a word of the voice-over, and scene.js times everything from these names
// (the camera keys and the mascot's route too), so moving a time here moves everything tied to
// it. Names: notif the chat reaching the shop's phone, m1-m3 buyer messages, r1-r3 replies,
// fly1-fly3 the result card leaving its prop for the chat, nb* the notes binder, kurir* the
// courier box, pay*/press/scan/paid/print/nota/stamp the payment, q2 the "?" moment,
// shh the hush toward the sleeping owner, hl1/hlFaq the matching words lighting up.
export const T = {
  send: 1.1, read: 2.6, povOut: 3.6, notif: 4.3,
  mascotOut: 8.1, shh: [9.0, 10.2], pushIn: 10.3, chatIn: 10.8, typing: 11.4,
  think: [12.4, 14.9], hl1: 14.0, nbIn: 15.2, nbOpen: 16.0, flip: 16.6, faq: 18.8, hlFaq: 20.3, fly1: 22.7, r1: 23.4,
  m2: 25.4, q2: [26.6, 28.9], shake: 27.6, nbOut: 28.4, kurirIn: 28.9, parcel: 29.4, press2: 29.9, kurir: 30.4, roll: 30.9, fly2: 33.0, r2: 33.7,
  m3: 36.6, payIn: 38.2, press: 40.3, fly3: 41.0, r3: 41.7, scan: 43.6, paid: 44.4, print: 44.5, nota: 44.8, stamp: 45.7, notaOut: 46.8,
  morning: 48.2, wake: 49.2, dash: 50.3, nego: 52.8, cta: 55.3,
};

// Shapes scene.js reads: <mark> in m1 and in faq wraps the words that light up when the notes
// match (one <mark> each); rows are [label, value, class?] with class "ok" (done) or "wait";
// the cards are sized for as many rows as the example has; cta is HTML and keeps the logo lockup.
export const COPY = {
  locale: "id-ID", currency: "Rp",
  app: "WhatsApp",
  shop: "Toko Contoh", shopInitial: "T", shopSub: "akun bisnis",
  buyer: "Kak Sari", buyerInitial: "S",
  clock: ["23.47", "23.48", "23.49"],
  // the first question; <mark> wraps the words that light up when the notes match them
  m1plain: "Kak, kalau kekecilan bisa tukar ukuran?",
  m1: 'Kak, kalau kekecilan bisa <mark class="k">tukar ukuran</mark>?',
  r1: "Bisa kak, tukar ukuran maks. 7 hari setelah barang diterima 🙏",
  r1chip: "dari catatan toko",
  m2: "Ongkir ke Medan berapa kak?",
  r2: "Ongkir ke Medan Rp38.000, sampai 2–3 hari ya kak",
  r2chip: "dari API kurir",
  m3: "Oke kak, ambil 1. Bisa QRIS?",
  r3chip: "tagihan dari payment gateway",
  qr: { head: "QRIS", merchant: "TOKO CONTOH", amount: "Rp189.000", expires: "Berlaku 15 menit", paid: "✓ Terbayar" },
  typing: "Asisten sedang mengetik",
  faq: "<b>FAQ toko</b><br><mark>Tukar ukuran</mark>: maks. 7 hari setelah barang diterima.",
  tool2: { title: "API kurir", status: "● tersambung", rows: [["Berat", "1 kg"], ["Tujuan", "Medan"]], price: 38000, eta: "sampai 2–3 hari" },
  receipt: {
    title: "NOTA PEMBAYARAN", sub: "Toko Contoh · 23.52 · via payment gateway",
    lines: [["Gamis hitam L ×1", "151.000"], ["Ongkir Medan", "38.000"]],
    total: ["TOTAL", "Rp189.000"],
    meta: [["Metode", "QRIS"], ["Status", "LUNAS ✓", "ok"]],
  },
  stamp: "LUNAS ✓",
  labels: ["📒 Catatan toko", "🚚 API kurir", "💳 Payment gateway"],
  dash: { title: "Pesanan masuk semalam", rows: [["Gamis hitam L · Rp189.000", "LUNAS ✓", "ok"], ["1 chat minta diskon", "menunggu kamu", "wait"]] },
  zzz: "zzz…",
  sst: "sst…",
  notif: "<b>Kak Sari</b> · Kak, kalau kekecilan bisa tukar…",
  // the end card: the brand's logo lockup (img/logo.svg) only fades in, never moves
  cta: '<div class="lockup"><img src="img/logo.svg" alt=""><span>Brand</span></div><div class="big">Cobain asistennya</div><div class="sub">Asisten chat AI untuk tokomu</div><div class="btn">Coba gratis di brand.id</div>',
};
