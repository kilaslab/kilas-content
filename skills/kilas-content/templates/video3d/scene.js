// SPDX-License-Identifier: GPL-3.0-or-later
// 3D explainer scene for a 60 s Reel (three.js r178): one bedroom set at night, the shop's
// chat always on screen, the mascot working on the nightstand below it, three questions that
// each use one prop whose result flies into the chat, morning, and an end card.
// Every word on screen and every time lives in beats.js; the set, props and shots live here.
// render(t) is a pure function of time: stills are ?t=12.5, the render seeks the same code.
// Built for an explainer of a shop's chat assistant (references/examples/reels-3d-explainer.md);
// keep the grammar, swap the story in beats.js and the props below.
import * as THREE from "three";
import { BEATS, T, COPY, MASCOT } from "./beats.js";
import { makeMascot, poseMascot } from "./mascot.js";

const W = 1080, H = 1920, DUR = 60;
// the room and the 3D props; accent* are the brand's colours (design.md)
const C = {
  cream: 0xFAF6EE, sand: 0xEFE3CA, navy: 0x16233A, ink: 0x111827, accent: 0x22A08F, accentDark: 0x14786B,
  accentLight: 0xBFE9DF, white: 0xFFFFFF, amber: 0xF2A541, wood: 0xC98B5A, woodDark: 0x9C6A44, skin: 0xF3C9A6,
  hair: 0x3B2A22, shirt: 0xF4EFE6, blanket: 0x6C7FA6, sheet: 0xF7F1E6, wallNight: 0x22324F, wallDay: 0xF1E6D2,
  floorNight: 0x3A3442, floorDay: 0xD9B98F, kraft: 0xE0BC86, grey: 0xB8B2A6,
};

// ---------- easing and keyframes ----------
const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
const lerp = (a, b, k) => a + (b - a) * k;
const E = {
  lin: (k) => k,
  io: (k) => (k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2),
  sine: (k) => -(Math.cos(Math.PI * k) - 1) / 2,
  out: (k) => 1 - Math.pow(1 - k, 3),
  back: (k) => { const c1 = 1.7, c3 = c1 + 1; return 1 + c3 * Math.pow(k - 1, 3) + c1 * Math.pow(k - 1, 2); },
};
const seg = (t, a, b, ease = E.io) => ease(clamp((t - a) / (b - a)));
// keys: [[time, value(s)], ...] -> eased value at t (numbers or arrays)
function key(t, keys, ease = E.io) {
  if (t <= keys[0][0]) return keys[0][1];
  for (let i = 1; i < keys.length; i++) {
    if (t <= keys[i][0]) {
      const [t0, v0] = keys[i - 1], [t1, v1] = keys[i];
      const k = ease((t - t0) / (t1 - t0));
      return Array.isArray(v0) ? v0.map((v, j) => lerp(v, v1[j], k)) : lerp(v0, v1, k);
    }
  }
  return keys[keys.length - 1][1];
}
// a 0..1 weight that eases in at a and out at b (never jumps)
const hold = (t, a, b, d = 0.35) => seg(t, a, a + d, E.sine) * (1 - seg(t, b - d, b, E.sine));
const hash = (i) => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };

// ---------- renderer, camera, light ----------
const canvas = document.getElementById("gl");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1);
renderer.setSize(W, H, false);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
const cam = new THREE.PerspectiveCamera(30, W / H, 0.1, 200);
const hemi = new THREE.HemisphereLight(0xFFF8EC, 0xC9B79A, 1.2);
scene.add(hemi);
const sun = new THREE.DirectionalLight(0xFFF1DC, 2.0);
sun.position.set(-10, 16, 12);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
Object.assign(sun.shadow.camera, { left: -14, right: 14, top: 14, bottom: -14, near: 1, far: 60 });
sun.shadow.bias = -0.0006;
scene.add(sun);
const lamp = new THREE.PointLight(0xFFC98A, 30, 14, 1.6);
scene.add(lamp);
const glow = new THREE.PointLight(0xBFF5EA, 0, 6, 1.6); // the phone screen lighting the nightstand
scene.add(glow);
const fill = new THREE.DirectionalLight(0xDDE6FF, 1.0); // from the camera side
scene.add(fill); scene.add(fill.target);

// ---------- geometry helpers ----------
const mats = {};
function mat(color, extra = {}) {
  const k = color + JSON.stringify(extra);
  if (!mats[k]) mats[k] = new THREE.MeshStandardMaterial({ color, roughness: 0.7, metalness: 0, ...extra });
  return mats[k];
}
function mesh(geo, color, parent, pos = [0, 0, 0], extra) {
  const m = new THREE.Mesh(geo, extra && extra.isMaterial ? extra : mat(color, extra));
  m.position.set(...pos);
  m.castShadow = true; m.receiveShadow = true;
  parent.add(m);
  return m;
}
function group(parent, pos = [0, 0, 0]) { const g = new THREE.Group(); g.position.set(...pos); parent.add(g); return g; }
// a box with rounded edges; normals point away from the inner box, so the rounding shades smoothly
function rbox(w, h, d, r = 0.15, n = 5) {
  const g = new THREE.BoxGeometry(w, h, d, n, n, n), p = g.attributes.position, nr = g.attributes.normal;
  const hx = w / 2 - r, hy = h / 2 - r, hz = d / 2 - r, v = new THREE.Vector3(), c = new THREE.Vector3();
  for (let i = 0; i < p.count; i++) {
    v.fromBufferAttribute(p, i);
    c.set(clamp(v.x, -hx, hx), clamp(v.y, -hy, hy), clamp(v.z, -hz, hz));
    v.sub(c);
    if (v.lengthSq() < 1e-9) v.set(0, 0, 1);
    v.normalize();
    nr.setXYZ(i, v.x, v.y, v.z);
    v.multiplyScalar(r).add(c);
    p.setXYZ(i, v.x, v.y, v.z);
  }
  return g;
}

// ---------- the room ----------
const room = group(scene);
const floorMat = mat(C.floorNight, { roughness: 0.9 });
const floor = mesh(new THREE.PlaneGeometry(60, 40), 0, room, [0, 0, 0], floorMat);
floor.rotation.x = -Math.PI / 2;
const wallMat = mat(C.wallNight, { roughness: 0.95 });
mesh(new THREE.PlaneGeometry(60, 30), 0, room, [0, 15, -6], wallMat);
// window with the moon (night) or a bright sky (morning)
const win = group(room, [-3.0, 8.6, -5.9]);
mesh(rbox(5.4, 4.4, 0.3, 0.12), C.shirt, win);
const skyMat = new THREE.MeshStandardMaterial({ color: 0x1B2A48, emissive: 0x1B2A48, emissiveIntensity: 0.8, roughness: 1 });
mesh(new THREE.PlaneGeometry(4.8, 3.8), 0, win, [0, 0, 0.17], skyMat);
mesh(new THREE.BoxGeometry(0.16, 3.8, 0.1), C.shirt, win, [0, 0, 0.2]);
const moon = mesh(new THREE.CircleGeometry(0.55, 32), 0, win, [1.3, 0.9, 0.19], new THREE.MeshBasicMaterial({ color: 0xFFF6D8 }));

// bed with its head against the back wall, beside the nightstand; the owner asleep under the blanket
const bed = group(room, [-2.9, 0, -2.6]);
mesh(rbox(4.6, 1.4, 6.6, 0.2), C.woodDark, bed, [0, 0.7, 0]);
mesh(rbox(4.3, 0.8, 6.3, 0.3), C.sheet, bed, [0, 1.7, 0]);
mesh(rbox(4.8, 3.6, 0.5, 0.2), C.woodDark, bed, [0, 1.8, -3.2]);
mesh(rbox(2.6, 0.5, 1.4, 0.24), C.white, bed, [0, 2.35, -2.3]);
const blanket = mesh(rbox(4.4, 0.7, 4.0, 0.3), C.blanket, bed, [0, 2.3, 1.0]);
// the owner: lies on their back at night (head on the pillow), sits up in the morning
const owner = group(bed, [0, 2.2, -0.6]);
const torso = group(owner);
mesh(new THREE.CapsuleGeometry(0.55, 1.0, 8, 16), C.shirt, torso, [0, 0.9, 0]);
const head = group(torso, [0, 2.1, 0]);
mesh(new THREE.SphereGeometry(0.55, 28, 20), C.skin, head);
mesh(new THREE.SphereGeometry(0.57, 28, 20, 0, Math.PI * 2, 0, Math.PI / 2.1), C.hair, head, [0, 0.04, -0.03]);
mesh(new THREE.SphereGeometry(0.28, 20, 14), C.hair, head, [0, 0.5, -0.32]);
const eyesClosed = [-0.19, 0.19].map((x) => mesh(new THREE.TorusGeometry(0.07, 0.022, 6, 12, Math.PI), C.ink, head, [x, 0.02, 0.53]));
const eyesOpen = [-0.19, 0.19].map((x) => mesh(new THREE.SphereGeometry(0.065, 12, 8), C.ink, head, [x, 0.04, 0.52]));
const rArmL = group(torso, [-0.6, 1.5, 0]), rArmR = group(torso, [0.6, 1.5, 0]);
mesh(new THREE.CapsuleGeometry(0.17, 0.8, 6, 12), C.shirt, rArmL, [0, -0.5, 0]);
mesh(new THREE.CapsuleGeometry(0.17, 0.8, 6, 12), C.shirt, rArmR, [0, -0.5, 0]);

// nightstand on the right, where the mascot works
const NS = [2.6, 0, -4.2];         // nightstand base, against the back wall
const TOP = 3.0;                    // its top surface
const ns = group(room, NS);
mesh(rbox(4.6, TOP, 3.4, 0.18), C.wood, ns, [0, TOP / 2, 0]);
mesh(rbox(4.0, 0.9, 0.1, 0.05), C.woodDark, ns, [0, TOP * 0.55, 1.7]);
mesh(new THREE.SphereGeometry(0.12, 12, 8), C.sand, ns, [0, TOP * 0.55, 1.78]);
// lamp at the back right
const lampG = group(ns, [1.7, TOP, -1.0]);
mesh(new THREE.CylinderGeometry(0.35, 0.45, 0.2, 20), C.ink, lampG, [0, 0.1, 0]);
mesh(new THREE.CylinderGeometry(0.06, 0.06, 1.3, 10), C.ink, lampG, [0, 0.8, 0]);
const shadeMat = new THREE.MeshStandardMaterial({ color: 0xF7E7C8, emissive: 0xFFC98A, emissiveIntensity: 0.6, roughness: 0.8, side: THREE.DoubleSide });
mesh(new THREE.CylinderGeometry(0.45, 0.75, 0.8, 24, 1, true), 0, lampG, [0, 1.6, 0], shadeMat);
lamp.position.set(NS[0] + 1.2, TOP + 2.2, NS[2] + 0.6);
// the shop's phone on a small stand at the back left of the top
const phone3 = group(ns, [-1.95, TOP, -1.2]);
mesh(rbox(0.9, 0.2, 0.6, 0.06), C.ink, phone3, [0, 0.1, 0.1]);
const ph = group(phone3, [0, 0.95, 0]);
ph.rotation.x = -0.18;
mesh(rbox(0.9, 1.7, 0.1, 0.08), C.ink, ph);
const screenMat = new THREE.MeshStandardMaterial({ color: 0x0E1726, emissive: 0xBFF5EA, emissiveIntensity: 0, roughness: 0.4 });
mesh(new THREE.PlaneGeometry(0.78, 1.55), 0, ph, [0, 0, 0.056], screenMat);
glow.position.set(NS[0] - 1.8, TOP + 1.2, NS[2] + 0.2);
const WS = (lx, ly, lz) => [NS[0] + lx, NS[1] + ly, NS[2] + lz]; // nightstand-local -> world

// ---------- props, one per question ----------
// 1. the shop's notes: a navy binder that opens, pages flip
const nb = group(ns, [1.45, TOP, 0.55]);
mesh(rbox(1.5, 0.12, 1.9, 0.04), C.shirt, nb, [0, 0.06, 0]);
mesh(rbox(1.4, 0.2, 1.8, 0.03), C.sheet, nb, [0, 0.2, 0]);
const cover = group(nb, [-0.75, 0.32, 0]);            // hinge on the left edge
mesh(rbox(1.5, 0.08, 1.9, 0.03), C.shirt, cover, [0.75, 0, 0]);
mesh(new THREE.PlaneGeometry(0.9, 0.3), C.navy, cover, [0.75, 0.045, 0]).rotation.x = -Math.PI / 2;
const pages = [0, 1, 2, 3, 4].map(() => {
  const g = group(nb, [-0.7, 0.31, 0]);
  const p = mesh(new THREE.PlaneGeometry(1.36, 1.74), 0, g, [0.68, 0, 0], mat(C.white, { side: THREE.DoubleSide }));
  p.rotation.x = -Math.PI / 2;
  return g;
});
// 2. the courier tool: an amber box with an antenna, a scale plate, and a parcel
const ku = group(ns, [1.25, TOP, 0.35]);
mesh(rbox(1.7, 0.9, 1.3, 0.12), C.amber, ku, [0, 0.45, 0]);
const kuScreen = new THREE.MeshStandardMaterial({ color: 0x0E1726, emissive: 0xBFF5EA, emissiveIntensity: 0.25, roughness: 0.4 });
mesh(new THREE.PlaneGeometry(1.1, 0.5), 0, ku, [0, 0.5, 0.66], kuScreen);
mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.9, 8), C.ink, ku, [0.6, 1.3, -0.3]);
const tip = mesh(new THREE.SphereGeometry(0.11, 12, 8), C.accent, ku, [0.6, 1.78, -0.3]);
mesh(new THREE.CylinderGeometry(0.62, 0.62, 0.08, 28), C.grey, ku, [-1.45, 0.04, 0.1]);
const parcel = mesh(rbox(0.8, 0.6, 0.8, 0.06), C.kraft, ku, [-1.45, 0.38, 0.1]);
// 3. the payment terminal: a dark box with a screen, a button, and a receipt that prints out
const pay = group(ns, [1.1, TOP, 0.4]);
mesh(rbox(1.4, 0.7, 1.6, 0.14), 0xA7AFBC, pay, [0, 0.35, 0]);
const payScreen = new THREE.MeshStandardMaterial({ color: 0x0E1726, emissive: 0xBFF5EA, emissiveIntensity: 0.3, roughness: 0.4 });
const ps = mesh(new THREE.PlaneGeometry(1.0, 0.6), 0, pay, [0, 0.71, -0.2], payScreen); ps.rotation.x = -Math.PI / 2;
const btn = mesh(new THREE.CylinderGeometry(0.16, 0.16, 0.08, 20), C.accent, pay, [0.35, 0.72, 0.45]);
const paper = group(pay, [0, 0.55, 0.8]);
const paperM = mesh(new THREE.PlaneGeometry(0.9, 1), 0, paper, [0, 0, 0.5], mat(C.white, { side: THREE.DoubleSide }));
paperM.rotation.x = -Math.PI / 2 + 0.25;

// ---------- the mascot ----------
const mascot = makeMascot(scene, MASCOT);
const MS = 0.7; // its size on the nightstand
// where it stands, in nightstand-local coordinates; its root sits on the top
const SPOT = { phone: [-1.95, -0.6], out: [-1.6, 0.4], work: [-1.25, 0.95], wide: [-0.6, 0.9] };

// ---------- camera shots: [position xyz, target xyz] ----------
const top3 = (x, y, z) => [NS[0] + x, TOP + y, NS[2] + z];
const SHOT = {
  wide: [[3.2, 11.5, 17.5], [-1.0, 2.6, -3.6]],
  stand: [[NS[0] + 0.8, TOP + 4.5, NS[2] + 15], top3(-0.6, 1.0, 0)],
  work: [[NS[0] - 0.1, TOP + 3.6, NS[2] + 18], top3(-0.1, 2.5, 0)],
  workL: [[NS[0] - 0.7, TOP + 3.4, NS[2] + 17], top3(-0.3, 2.4, 0)],
  workR: [[NS[0] + 0.5, TOP + 3.8, NS[2] + 17.5], top3(0.1, 2.5, 0)],
  morning: [[1.6, 10.2, 20.5], [-0.3, 3.5, -3.8]],
  morning2: [[1.2, 9.0, 16.5], [-0.3, 3.6, -3.8]],
  cta: [[NS[0] - 0.6, TOP + 2.0, NS[2] + 15], top3(-0.6, 3.0, 0)],
};
// closer shots for the mascot's reactions and for each tool; the target sits above it so it lands
// under the chat panel. aim(target, distance, lift) -> [position, target]
const aim = ([x, y, z], d, lift) => [[x + 0.1, y + lift, z + d], [x, y, z]];
Object.assign(SHOT, {
  cuOut: aim([NS[0] - 1.6, TOP + 2.45, NS[2] + 0.4], 13, 0.8),   // just out of the phone (sst)
  cuMascot: aim([NS[0] - 1.25, TOP + 2.45, NS[2] + 0.95], 13, 0.8), // at its work spot
  cuBook: aim([NS[0] + 0.1, TOP + 2.6, NS[2] + 0.8], 15, 0.9),    // the mascot and the binder
  cuBook2: aim([NS[0] + 0.1, TOP + 2.55, NS[2] + 0.8], 13.6, 0.85), // a slow push while the note is read
  cuKurir: aim([NS[0] - 0.1, TOP + 2.7, NS[2] + 0.7], 15.5, 0.9), // the mascot, the courier box and the parcel
});
// camera keys, timed from beats.js T: a push-in on each reaction, a framing per tool
const CAMK = [
  [0, SHOT.wide], [T.povOut + 0.4, SHOT.wide], [T.mascotOut - 0.1, SHOT.stand], [T.shh[0] - 0.2, SHOT.cuOut], [T.shh[1] - 0.2, SHOT.cuOut], [T.chatIn + 0.1, SHOT.work],
  [T.hl1 + 0.5, SHOT.work], [T.nbOpen + 0.2, SHOT.cuBook], [T.fly1 - 0.1, SHOT.cuBook2], [T.r1 + 0.2, SHOT.cuMascot], [T.m2 - 0.4, SHOT.cuMascot],
  [T.q2[0] + 0.4, SHOT.cuMascot], [T.nbOut + 0.2, SHOT.cuMascot], [T.parcel, SHOT.cuKurir], [T.fly2, SHOT.cuKurir], [T.r2 + 0.3, SHOT.cuMascot], [T.m3 - 1.2, SHOT.cuMascot],
  [T.m3 - 0.2, SHOT.work], [T.r3 + 0.9, SHOT.workL], [T.stamp - 0.3, SHOT.work], [T.notaOut - 0.2, SHOT.cuMascot], [T.morning - 0.2, SHOT.cuMascot],
  [T.dash + 0.1, SHOT.morning], [T.cta - 0.3, SHOT.morning2], [T.cta + 1.1, SHOT.cta], [DUR, SHOT.cta],
].map(([t, s]) => [t, [...s[0], ...s[1]]]);

// ---------- overlay (HTML anchored to the scene) ----------
const ov = document.getElementById("ov");
const els = {};
function div(id, cls, html, parent = ov) { const d = document.createElement("div"); d.className = cls; d.innerHTML = html; d.style.opacity = 0; parent.appendChild(d); els[id] = d; return d; }
const v3 = new THREE.Vector3();
function toScreen(p) { v3.set(...p).project(cam); return [(v3.x + 1) / 2 * W, (1 - v3.y) / 2 * H]; }
let floatT = 0;
function show(id, a, x, y, s = 1) {
  const d = els[id]; d.style.opacity = a; d.style.display = a <= 0.001 ? "none" : "";
  if (y != null && (d.classList.contains("card") || id === "nota" || id === "lunas")) y += 5 * Math.sin(floatT * 1.6);
  if (x != null) { d.style.left = x + "px"; d.style.top = y + "px"; }
  d.style.transform = (d.dataset.anchor === "pin" ? "translate(-50%,-100%) " : "") + `scale(${s})`;
}
function pop(t, a, b, d = 0.4) { const i = seg(t, a, a + d, E.back), o = 1 - seg(t, b - 0.3, b, E.io); return [Math.min(clamp(i * 1.2), o), lerp(0.7, 1, i)]; }

div("band", "band", ""); els.band.setAttribute("data-layout-allow-occlusion", ""); // scrolled-off chat lines sit under it on purpose
div("head", "head", '<span class="pill"></span><div class="h1"><span class="l1"></span><span class="l2"></span></div>');
// POV: the buyer types to the shop
const ck = COPY.clock;
div("pov", "phone", `<div class="scr"><div class="bar"><div class="av">${COPY.shopInitial}</div><div><div class="nm">${COPY.shop}</div><div class="st">${COPY.shopSub}</div></div></div>
  <div class="clock">${ck[0]}</div><div class="msg"><span class="tx"></span><span class="meta">${ck[0]} <span class="tk">✓✓</span></span></div>
  <div class="inp"><span class="ty"></span><span class="caret"></span></div><div class="send"></div><div class="kb">${["qwertyuiop", "asdfghjkl", "zxcvbnm"].map((r) => `<div class="kr">${[...r].map((k) => `<span>${k}</span>`).join("")}</div>`).join("")}</div></div>`);
els.pov.querySelector(".tx").textContent = COPY.m1plain;
div("notif", "notif", `<span class="app">${COPY.app}</span>` + COPY.notif); els.notif.dataset.anchor = "pin";
div("zzz", "zzz", COPY.zzz); els.zzz.dataset.anchor = "pin";
// the shop's chat, always on screen once the mascot opens it; replies sit on the right
const q = COPY.qr;
div("wa", "wa", `<div class="bar"><div class="av">${COPY.buyerInitial}</div><div><div class="nm">${COPY.buyer}</div><div class="st">online</div></div><div class="clk">${ck[0]}</div></div>
  <div class="body"><div class="list" data-layout-allow-occlusion>
    <div class="m in" data-k="m1"><span class="tx">${COPY.m1}</span><span class="meta">${ck[0]}</span></div>
    <div class="m out" data-k="r1">${COPY.r1}<span class="meta">${ck[0]} <i class="tick">✓✓</i></span><span class="chip">${COPY.r1chip}</span></div>
    <div class="m in" data-k="m2">${COPY.m2}<span class="meta">${ck[1]}</span></div>
    <div class="m out" data-k="r2">${COPY.r2}<span class="meta">${ck[1]} <i class="tick">✓✓</i></span><span class="chip">${COPY.r2chip}</span></div>
    <div class="m in" data-k="m3">${COPY.m3}<span class="meta">${ck[2]}</span></div>
    <div class="m out qmsg" data-k="r3"><div class="qr"><div class="qh"><b>${q.head}</b><span>${q.merchant}</span></div><canvas width="37" height="37"></canvas>
      <div class="amt">${q.amount}</div><div class="exp">${q.expires}</div><div class="paidtx">${q.paid}</div><div class="sl"></div></div>
      <span class="meta">${ck[2]} <i class="tick">✓✓</i></span><span class="chip">${COPY.r3chip}</span></div>
    <div class="typing" data-k="typing">${COPY.typing}<span class="dots"><i></i><i></i><i></i></span></div>
  </div></div>`);
const waItems = {}; els.wa.querySelectorAll("[data-k]").forEach((e) => { waItems[e.dataset.k] = e; e.setAttribute("data-layout-allow-occlusion", ""); });
div("faq", "card faq", COPY.faq);
div("qrfly", "qrfly", `<canvas width="37" height="37"></canvas><b>${q.amount}</b>`);
div("sst", "sst", COPY.sst); els.sst.dataset.anchor = "pin";
div("lbl", "lbl", ""); els.lbl.dataset.anchor = "pin";
const k2 = COPY.tool2, rc = COPY.receipt, rows = (list, cls = "ln") => list.map(([a, b, c]) => `<div class="${cls}"><span>${a}</span><span${c ? ` class="${c}"` : ""}>${b}</span></div>`).join("");
div("kurir", "card kurir", `<div class="kt">${k2.title} <span class="on">${k2.status}</span></div>${k2.rows.map(([a, b]) => `<div class="row"><span>${a}</span><b>${b}</b></div>`).join("")}
  <div class="price"><span class="rp"></span></div><div class="eta">${k2.eta}</div>`);
div("nota", "nota", `<div class="in"><div class="tt">${rc.title}</div><div class="sb">${rc.sub}</div>${rows(rc.lines)}
  <div class="rule"></div><div class="ln tot"><span>${rc.total[0]}</span><span>${rc.total[1]}</span></div><div class="rule"></div>${rows(rc.meta)}</div><div class="zz"></div>`);
div("lunas", "stamp", COPY.stamp); els.lunas.setAttribute("data-layout-allow-overlap", "");
div("dash", "dash", `<div class="dt">${COPY.dash.title}</div>${COPY.dash.rows.map(([a, b, c]) => `<div class="row"><span>${a}</span><span class="ch ${c}">${b}</span></div>`).join("")}`);
div("cta", "cta", COPY.cta);
// a QR-like matrix with finder patterns, drawn once (seeded)
(() => {
  const cv = els.wa.querySelector(".qr canvas"), x = cv.getContext("2d"), N = 37;
  x.fillStyle = "#fff"; x.fillRect(0, 0, N, N); x.fillStyle = "#111827";
  for (let i = 0; i < N; i++) for (let j = 0; j < N; j++) if (hash(i * 53 + j * 17 + 5) > 0.5) x.fillRect(i, j, 1, 1);
  for (const [a, b] of [[0, 0], [N - 7, 0], [0, N - 7]]) {
    x.fillStyle = "#fff"; x.fillRect(a - (a ? 1 : 0), b - (b ? 1 : 0), 8, 8);
    x.fillStyle = "#111827"; x.fillRect(a, b, 7, 7); x.fillStyle = "#fff"; x.fillRect(a + 1, b + 1, 5, 5); x.fillStyle = "#111827"; x.fillRect(a + 2, b + 2, 3, 3);
  }
  els.qrfly.querySelector("canvas").getContext("2d").drawImage(cv, 0, 0);
})();
const stageEl = document.getElementById("stage");
const hex = (h) => [(h >> 16) & 255, (h >> 8) & 255, h & 255];
const mixC = (a, b, k) => new THREE.Color().setRGB(...hex(a).map((v, i) => lerp(v, hex(b)[i], k) / 255), THREE.SRGBColorSpace);
const mixS = (a, b, k) => `rgb(${hex(a).map((v, i) => Math.round(lerp(v, hex(b)[i], k))).join(",")})`;

// chat messages: [key, time it appears]; the list is bottom-anchored, so new ones push old ones up
const WA = [["m1", T.chatIn], ["r1", T.r1], ["m2", T.m2], ["r2", T.r2], ["m3", T.m3], ["r3", T.r3]];
// the mascot types after each question until its reply lands
const TYPING = [[T.typing, T.r1], [T.m2 + 0.9, T.r2], [T.m3 + 1.2, T.r3]];
// where a result card lands when it flies into the chat (screen px), and its size there
const LAND = [600, 950, 0.45];

// where the mascot stands over time (it walks between spots)
const ROUTE = [[0, SPOT.phone], [T.mascotOut + 0.6, SPOT.out], [T.shh[1], SPOT.out], [T.shh[1] + 1.2, SPOT.work], [T.morning - 0.4, SPOT.work],
  [T.wake + 0.4, SPOT.wide], [DUR, SPOT.wide]];

// ---------- the film ----------
function render(t) {
  t = clamp(t, 0, DUR);
  floatT = t;
  // night -> morning
  const day = seg(t, T.morning, T.morning + 2.0, E.sine);
  hemi.color.copy(mixC(0x6F7FA8, 0xFFF8EC, day)); hemi.groundColor.copy(mixC(0x1A2236, 0xC9B79A, day));
  hemi.intensity = lerp(1.0, 1.25, day);
  sun.color.copy(mixC(0x9DB3E6, 0xFFE9C8, day)); sun.intensity = lerp(0.9, 2.2, day);
  sun.position.set(lerp(-6, -12, day), lerp(14, 16, day), lerp(-2, 12, day));
  lamp.intensity = lerp(32, 0, day); shadeMat.emissiveIntensity = lerp(0.7, 0.05, day);
  wallMat.color.copy(mixC(C.wallNight, C.wallDay, day)); floorMat.color.copy(mixC(C.floorNight, C.floorDay, day));
  skyMat.color.copy(mixC(0x1B2A48, 0xCFE8F7, day)); skyMat.emissive.copy(mixC(0x1B2A48, 0xCFE8F7, day));
  moon.material.opacity = 1 - day; moon.material.transparent = true;
  stageEl.style.background = mixS(0x16233A, 0xFAF6EE, day);
  stageEl.classList.toggle("night", day < 0.5);
  const bandC = mixS(0x16233A, 0xFAF6EE, day);
  els.band.style.opacity = 1;
  els.band.style.background = `linear-gradient(${bandC} 0%, ${bandC} 62%, transparent 100%)`;

  // camera: eased between shots, plus a slow drift so a hold never freezes
  const c = key(t, CAMK, E.sine);
  // a slow push-in and pull-out along the view line, with a sideways drift: holds keep moving
  const dolly = 0.07 * Math.sin(t * 0.23) + 0.035 * Math.sin(t * 0.61 + 2);
  cam.position.set(lerp(c[0], c[3], dolly) + 0.22 * Math.sin(t * 0.37), lerp(c[1], c[4], dolly) + 0.12 * Math.sin(t * 0.53 + 1), lerp(c[2], c[5], dolly));
  cam.lookAt(c[3] + 0.08 * Math.sin(t * 0.29 + 0.5), c[4], c[5]);
  cam.updateMatrixWorld(true);
  fill.position.copy(cam.position); fill.target.position.set(c[3], c[4], c[5]); fill.intensity = lerp(1.1, 0.5, day);

  // the phone wakes when the chat arrives
  const lit = seg(t, T.notif - 0.1, T.notif + 0.3) * (1 - 0.6 * day);
  screenMat.emissiveIntensity = lit * (0.9 + 0.1 * Math.sin(t * 6) * (1 - seg(t, T.notif + 1.7, T.notif + 2.7)));
  glow.intensity = lit * 3;
  ph.position.y = 0.95 + 0.02 * Math.sin(t * 40) * hold(t, T.notif + 0.1, T.notif + 1.3, 0.1); // buzz

  // the owner asleep, breathing; in the morning they sit up and open their eyes
  const up = seg(t, T.wake, T.wake + 1.2, E.io);
  torso.rotation.x = lerp(-Math.PI / 2 + 0.12, -0.12, up);
  torso.rotation.y = 0.5 * up; // she turns to the phone
  torso.position.set(0, lerp(-0.2, 0, up), lerp(0.6, -0.8, up));
  torso.scale.setScalar(1 + 0.02 * Math.sin(t * 1.6) * (1 - up));
  for (const e of eyesClosed) e.visible = up < 0.6;
  for (const e of eyesOpen) e.visible = up >= 0.6;
  rArmL.rotation.z = lerp(0.1, -2.6, hold(t, T.wake + 1.0, T.wake + 2.4, 0.5)); // a morning stretch
  rArmR.rotation.z = lerp(-0.1, 2.6, hold(t, T.wake + 1.0, T.wake + 2.4, 0.5));
  blanket.position.y = 2.3 + 0.03 * Math.sin(t * 1.6) * (1 - up);
  head.rotation.x = 0.12 * Math.sin((t - T.wake) * 2.2) * seg(t, T.wake + 2.4, T.wake + 3.0) + 0.15 * seg(t, T.wake + 2.4, T.wake + 3.0);

  // props: in and out with a soft scale, never popping
  const nbS = hold(t, T.nbIn, T.nbOut + 0.4, 0.5), kuS = hold(t, T.kurirIn, T.m3 + 0.9, 0.5), paS = hold(t, T.payIn, T.morning + 0.2, 0.5);
  nb.scale.setScalar(Math.max(0.001, E.back(nbS) * 1)); nb.visible = nbS > 0.001;
  ku.scale.setScalar(Math.max(0.001, kuS)); ku.visible = kuS > 0.001;
  pay.scale.setScalar(Math.max(0.001, paS)); pay.visible = paS > 0.001;
  cover.rotation.z = Math.PI * 0.96 * seg(t, T.nbOpen, T.nbOpen + 0.8, E.io);
  pages.forEach((g, i) => { g.rotation.z = Math.PI * 0.94 * seg(t, T.flip + i * 0.32, T.flip + i * 0.32 + 0.5, E.io); g.position.y = 0.31 + i * 0.004; });
  parcel.position.y = lerp(1.6, 0.38, seg(t, T.parcel, T.parcel + 0.5, E.out)) + 0.04 * Math.sin(Math.PI * seg(t, T.parcel + 0.5, T.parcel + 0.8));
  tip.material = mat(Math.sin(t * 8) > 0 && t > T.kurir && t < T.roll + 1.6 ? C.accentLight : C.accent);
  kuScreen.emissiveIntensity = 0.25 + 0.5 * hold(t, T.kurir, T.r2);
  btn.position.y = 0.72 - 0.05 * hold(t, T.press + 0.3, T.press + 0.7, 0.12);
  payScreen.emissiveIntensity = 0.3 + 0.6 * hold(t, T.press + 0.5, T.notaOut);
  const pr = seg(t, T.print, T.print + 1.0, E.out);
  paper.scale.set(1, 1, Math.max(0.001, pr)); paper.visible = pr > 0.001 && paS > 0.01;

  // the mascot: pops out of the phone, then acts every beat; every weight is eased, nothing jumps
  const pos = key(t, ROUTE, E.sine), ahead = key(t + 0.25, ROUTE, E.sine);
  const born = seg(t, T.mascotOut, T.mascotOut + 0.6, E.back);
  const arc = Math.sin(Math.PI * seg(t, T.mascotOut, T.mascotOut + 0.6)) * 0.9; // hop out of the screen
  mascot.root.position.set(NS[0] + pos[0], TOP + arc + (1 - born) * 0.9, NS[2] + pos[1]);
  mascot.root.scale.setScalar(Math.max(0.001, MS * born));
  mascot.root.visible = born > 0.01;
  const walk = clamp(Math.hypot(ahead[0] - pos[0], ahead[1] - pos[1]) * 6);
  // turn: toward the sleeping owner (sst), toward the props while working, toward the owner in the morning
  const yaw = key(t, [[0, 0], [T.shh[0], 0], [T.shh[0] + 0.4, -0.85], [T.shh[1] - 0.2, -0.85], [T.shh[1] + 0.3, 0],
    [T.nbIn, 0], [T.nbIn + 0.5, 0.3], [T.r1 + 0.9, 0.3], [T.r1 + 1.6, -0.15], [T.m2, 0], [T.q2[0], 0], [T.q2[0] + 0.4, 0.35], [T.r2, 0.35], [T.r2 + 0.4, 0],
    [T.payIn, 0], [T.payIn + 0.5, 0.3], [T.stamp, 0.3], [T.stamp + 0.4, 0], [T.morning + 0.6, 0], [T.morning + 1.2, -0.5], [T.cta, -0.5], [T.cta + 0.6, 0], [60, 0]], E.sine);
  mascot.root.rotation.y = yaw + 0.12 * Math.sin(t * 0.8) + 0.05 * Math.sin(t * 1.7 + 1);
  mascot.body.rotation.y = Math.sin((t - T.shake) * 14) * 0.2 * hold(t, T.shake, T.shake + 0.9, 0.2); // head shake: the rate is not in the notes
  const H = (a, b, d = 0.3) => hold(t, a, b, d);
  const hopAt = (...ts) => ts.reduce((v, h) => (t >= h && t < h + 0.6 ? seg(t, h, h + 0.6, E.lin) : v), 0);
  const look = key(t, [[0, [0, 0]], [T.mascotOut + 0.6, [0, 0]], [T.shh[0] + 0.2, [-0.9, 0.1]], [T.shh[1], [-0.9, 0.1]], [T.chatIn, [0.5, -0.9]],
    [T.think[0], [0.3, -0.9]], [T.nbIn, [0.7, 0.7]], [T.faq, [0.9, 0.1]], [T.fly1, [0.4, -0.9]], [T.r1 + 1.2, [0, 0]], [T.m2, [0.3, -0.9]],
    [T.q2[0], [0.8, 0.6]], [T.kurirIn, [0.8, 0.5]], [T.fly2, [0.4, -0.9]], [T.r2 + 1.2, [0, 0]], [T.m3, [0.3, -0.9]], [T.payIn, [0.8, 0.5]],
    [T.fly3, [0.4, -0.9]], [T.scan, [0.3, -0.8]], [T.nota, [0.8, 0.2]], [T.stamp + 0.6, [0, 0]], [T.morning + 0.6, [-0.8, -0.1]], [T.cta, [0, 0]], [60, [0, 0]]], E.sine);
  const joyW = Math.max(H(T.r1, T.r1 + 1.6), H(T.r2, T.r2 + 1.6), H(T.stamp, T.morning), 0.6 * H(T.dash, T.nego), 0.5 * H(T.cta + 0.8, 60));
  poseMascot(mascot, t, {
    walk, phase: t * 9,
    hop: hopAt(T.mascotOut + 0.65, T.r1 + 0.1, T.r2 + 0.1, T.stamp, T.cta + 0.8),
    tilt: 0.45 * H(T.think[0], T.think[1]) - 0.4 * H(T.q2[0], T.q2[1]) + 0.25 * H(T.faq + 0.2, T.fly1),
    lean: 0.6 * Math.max(H(T.nbOpen - 0.3, T.flip + 1.0), H(T.press2 - 0.3, T.press2 + 0.8), H(T.press - 1.3, T.press + 0.7)),
    armR: {
      think: Math.max(H(T.shh[0], T.shh[1]), H(T.think[0], T.think[1])),
      reach: Math.max(H(T.nbOpen - 0.3, T.flip + 1.0), H(T.press2 - 0.3, T.press2 + 0.8), H(T.press - 1.3, T.press + 0.7)),
      point: H(T.faq + 0.2, T.fly1 - 0.1),
      thumbs: Math.max(H(T.r1, T.r1 + 1.6), H(T.r2, T.r2 + 1.6), H(T.stamp, T.morning)),
      wave: Math.max(H(T.dash, T.nego, 0.4), H(T.cta + 0.8, 60, 0.4)),
    },
    armL: {
      reach: Math.max(H(T.nbOpen - 0.3, T.flip + 1.0), H(T.press2 - 0.3, T.press2 + 0.8), H(T.press - 0.3, T.press + 0.7)),
      thumbs: H(T.stamp, T.morning),
    },
    face: {
      look,
      surprise: Math.max(H(T.mascotOut, T.mascotOut + 1.0, 0.2), 0.6 * H(T.faq, T.faq + 0.8, 0.2)),
      o: Math.max(H(T.mascotOut, T.mascotOut + 0.9, 0.2), 0.8 * H(T.shh[0] + 0.2, T.shh[1])),
      joy: joyW,
      open: Math.max(0.7 * H(T.faq + 0.2, T.fly1), joyW, 0.6 * H(T.m3, T.m3 + 1.4)),
      frown: Math.max(H(T.q2[0], T.q2[1]), 0.35 * H(T.think[0], T.think[1])),
    },
    question: H(T.q2[0], T.q2[1], 0.25),
    checks: H(T.stamp, T.morning, 0.4),
  });

  // ---------- overlay ----------
  const b = BEATS.at(t), hd = els.head;
  hd.querySelector(".pill").textContent = b.pill;
  hd.querySelector(".pill").style.display = b.pill ? "" : "none";
  hd.querySelector(".l1").textContent = b.l1;
  hd.querySelector(".l2").textContent = b.l2 || "";
  const into = b.t0 === 0 ? 1 : seg(t, b.t0, b.t0 + 0.4, E.out), outo = b.last ? 0 : 1 - seg(t, b.t1 - 0.25, b.t1);
  hd.style.opacity = Math.min(into, outo);
  hd.style.transform = `translateY(${(1 - into) * 24}px)`;

  // POV phone: typing 0-0.95 s, send at 1.1 s, slides away 3.6-4.6 s
  const typed = Math.round(COPY.m1plain.length * lerp(0.3, 1, seg(t, 0, T.send - 0.15, E.lin)));
  const sent = t >= T.send;
  els.pov.querySelector(".ty").textContent = sent ? "" : COPY.m1plain.slice(0, typed);
  const pm = els.pov.querySelector(".msg");
  pm.style.opacity = sent ? 1 : 0; pm.style.transform = `scale(${sent ? lerp(0.85, 1, seg(t, T.send, T.send + 0.3, E.back)) : 0.85})`;
  els.pov.querySelector(".caret").style.opacity = sent || (t % 0.8) > 0.4 ? 0 : 1;
  const tk = els.pov.querySelector(".tk");
  tk.classList.toggle("blue", t >= T.read); // read on the shop's side
  tk.style.display = "inline-block"; tk.style.transform = `scale(${1 + 0.6 * Math.sin(Math.PI * seg(t, T.read, T.read + 0.5, E.lin))})`;
  const out = seg(t, T.povOut, T.povOut + 1.0, E.io);
  // a slow push-in while the message waits, then the phone drops away
  show("pov", 1 - seg(t, T.povOut + 0.8, T.povOut + 1.0), null, null, lerp(1, 0.8, out) * (1 + 0.05 * seg(t, T.send, T.povOut, E.sine)));
  els.pov.style.marginTop = lerp(0, 1500, out) + 8 * Math.sin(t * 2.2) + "px";

  // notification over the 3D phone, zzz over the owner
  const pp = toScreen(WS(-1.95, TOP + 2.2, -1.2));
  const [na, ns2] = pop(t, T.notif, T.mascotOut);
  show("notif", na, clamp(pp[0], 340, 740), Math.max(pp[1] - 120, 700), ns2);
  const rz = toScreen([-2.9, 4.2, -4.6]);
  show("zzz", hold(t, T.notif + 0.5, T.pushIn + 0.4) + hold(t, T.morning - 0.2, T.wake, 0.3), rz[0], rz[1] + 6 * Math.sin(t * 2), 1);

  // the chat: grows out of the 3D phone at 9.4 s, then stays
  const wi = seg(t, T.chatIn, T.chatIn + 0.8, E.io), wo = seg(t, T.morning - 0.3, T.morning + 0.3, E.io);
  show("wa", wi * (1 - seg(t, T.morning + 0.1, T.morning + 0.3)), null, null, lerp(0.25, 1, wi) * lerp(1, 0.12, wo));
  els.wa.style.transformOrigin = `${clamp(pp[0], 100, 980) - 70}px ${pp[1] - 440}px`;
  for (const [k, at] of WA) {
    const e = waItems[k], on = t >= at;
    e.style.display = on ? "" : "none";
    if (on) { const s = seg(t, at, at + 0.35, E.back); e.style.transform = `scale(${lerp(0.8, 1, s)})`; e.style.opacity = clamp(s * 1.4); }
  }
  // the mascot's typing bubble, on the shop's side (right), between each question and its reply
  const ty = TYPING.find(([a, b]) => t >= a && t < b);
  waItems.typing.style.display = ty ? "" : "none";
  if (ty) {
    const s = seg(t, ty[0], ty[0] + 0.3, E.back);
    waItems.typing.style.transform = `scale(${lerp(0.8, 1, s)})`; waItems.typing.style.opacity = clamp(s * 1.4);
    waItems.typing.querySelectorAll(".dots i").forEach((d, i) => (d.style.opacity = 0.35 + 0.65 * Math.max(0, Math.sin(t * 7 - i * 0.9))));
  }
  els.wa.querySelector(".clk").textContent = t >= T.m3 ? ck[2] : t >= T.m2 ? ck[1] : ck[0];
  waItems.m1.querySelector("mark")?.classList.toggle("on", t >= T.hl1 && t < T.r1 + 0.8);
  for (const tk of els.wa.querySelectorAll(".tick")) tk.classList.add("blue");
  const qrEl = waItems.r3.querySelector(".qr"), sk = seg(t, T.scan, T.scan + 1.0, E.io), sl = qrEl.querySelector(".sl");
  sl.style.opacity = sk > 0 && sk < 1 ? 1 : 0; sl.style.top = lerp(90, 330, sk) + "px";
  qrEl.classList.toggle("paid", t >= T.paid);

  // every tool works the same way: its result rises from the prop, then flies up into the chat
  // and turns into the mascot's reply there
  const fly = (id, from, inAt, flyAt, landAt, rest = [430, 1110], s0 = 1) => {
    const i = seg(t, inAt, inAt + 0.6, E.io), f = seg(t, flyAt, landAt, E.io);
    const x = lerp(lerp(from[0] - 100, rest[0], i), LAND[0], f), y = lerp(lerp(from[1] - 60, rest[1], i), LAND[1], f);
    show(id, t < landAt ? i * (1 - seg(t, landAt - 0.2, landAt)) : 0, x, y - 60 * Math.sin(Math.PI * f), lerp(lerp(0.3, s0, i), LAND[2], f));
  };
  // 1. the FAQ page rises out of the binder; "tukar ukuran" lights up in it as in the chat
  fly("faq", toScreen(WS(1.45, TOP + 0.4, 0.55)), T.faq, T.fly1, T.r1, [470, 1100], 0.9);
  els.faq.querySelector("mark")?.classList.toggle("on", t >= T.hlFaq);
  // 2. the courier card: price digits roll, then settle
  fly("kurir", toScreen(WS(0.75, TOP + 1.0, 0.4)), T.kurir, T.fly2, T.r2, [500, 1095], 0.85);
  const rk = seg(t, T.roll, T.roll + 1.4, E.out);
  const money = (n) => COPY.currency + n.toLocaleString(COPY.locale);
  const roll = Math.floor((lerp(k2.price * 0.3, k2.price, rk) + (rk < 0.95 ? hash(Math.floor(t * 20)) * k2.price * 0.6 : 0)) / 1000) * 1000;
  els.kurir.querySelector(".rp").textContent = money(rk < 1 ? roll : k2.price);
  els.kurir.querySelector(".rp").classList.toggle("set", rk >= 1);
  // 3. the QR comes out of the terminal and flies into the chat as the bill
  fly("qrfly", toScreen(WS(1.1, TOP + 0.9, 0.4)), T.press + 0.3, T.fly3, T.r3, [560, 1120], 1);
  // 3. the receipt rises from the terminal, then the LUNAS stamp lands on it
  const np = toScreen(WS(0.75, TOP + 1.0, 1.2));
  const ni = seg(t, T.nota, T.nota + 0.7, E.io), no = seg(t, T.notaOut, T.notaOut + 0.4);
  show("nota", ni * (1 - no), lerp(np[0] - 150, 430, ni), lerp(np[1], 1110, ni), lerp(0.3, 0.84, ni));
  show("lunas", t > T.stamp && t < T.notaOut + 0.4 ? 1 - no : 0, 420, 1450, lerp(2.0, 1, seg(t, T.stamp, T.stamp + 0.35, E.back)));
  // labels pinned to the props
  const lab = t < T.nbOut + 0.2 ? [COPY.labels[0], WS(1.45, TOP + 1.2, 0.55), hold(t, T.nbIn + 0.3, T.faq)]
    : t < T.m3 + 0.9 ? [COPY.labels[1], WS(1.25, TOP + 1.3, 0.4), hold(t, T.kurirIn + 0.3, T.kurir)]
      : [COPY.labels[2], WS(1.1, TOP + 1.4, 0.4), hold(t, T.payIn + 0.3, T.press + 0.2)];
  const lp = toScreen(lab[1]);
  els.lbl.textContent = lab[0];
  show("lbl", lab[2], clamp(lp[0], 260, 820), lp[1], lerp(0.85, 1, lab[2]));

  // "sst…" beside the mascot while it hushes toward the sleeping owner
  const sp = toScreen([mascot.root.position.x - 1.35, mascot.root.position.y + 2.55 * MS, mascot.root.position.z]);
  show("sst", hold(t, T.shh[0] + 0.2, T.shh[1], 0.25), sp[0], sp[1] + 4 * Math.sin(t * 3), 1);
  // morning: the summary the owner wakes up to; the item waiting for them pulses on its word (T.nego)
  const [da, ds] = pop(t, T.dash, T.cta - 0.3, 0.45);
  show("dash", da, 70, 1230 + 6 * Math.sin(t * 1.4), ds);
  els.dash.querySelector(".wait").style.transform = `scale(${1 + 0.1 * Math.max(0, Math.sin((t - T.nego) * 6)) * hold(t, T.nego, T.nego + 2.2, 0.3)})`;
  const ct = seg(t, T.cta, T.cta + 0.6, E.out);
  show("cta", ct, null, null, 1); // the logo never animates: the card only fades in
  const cb = els.cta.querySelector(".btn");
  cb.style.transform = `scale(${1 + 0.04 * Math.max(0, Math.sin((t - T.cta - 1.3) * 3.2)) * seg(t, T.cta + 1.3, T.cta + 1.7)})`;

  renderer.render(scene, cam);
}

// ---------- drive ----------
const qs = new URLSearchParams(location.search);
window.__render = render;
window.__dur = DUR;
if (qs.has("t")) {
  render(parseFloat(qs.get("t")));
  document.title = "ready " + qs.get("t");
}
// HyperFrames seek protocol
window.addEventListener("hf-seek", (e) => render(e.detail.time));
if (window.__sceneReady) document.fonts.ready.then(() => { render(0); window.__sceneReady(); });
