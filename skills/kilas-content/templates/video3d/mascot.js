// SPDX-License-Identifier: GPL-3.0-or-later
// A soft 3D mascot rig for Reels explainers (three.js): a round matte-clay body, a puffy face
// panel drawn on a canvas (speech-bubble outline by default) with oval eyes and a mouth, short
// arms with an elbow and mitten hands (thumb, three fingers), two boots, an optional bubble tail
// on the body, and two acting props (a "?" bubble and three check badges).
// Match it to the brand's own mascot renders: change MASCOT in beats.js (colours, tails), the
// face outline in bubblePath(), or the proportions below. Every pose and face value is a weight
// the caller eases over time, so nothing jumps from one frame to the next.
import * as THREE from "three";

// colours and parts; override any of them with makeMascot(parent, { ... })
const DEFAULTS = {
  body: 0x45B3A5,            // matte clay body, arms, legs
  boots: 0x349F92,           // the feet, one step darker
  ink: "#0E5751",            // eyes and mouth
  tongue: "#7FCFC1",
  badge: "#2B9487",          // "?" mark and check badges
  groove: "rgba(9,60,54,0.42)", // soft shadow around the face panel
  bodyTail: true,            // a speech-bubble tail on the body, lower right, pointing out
};

const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
const lerp = (a, b, k) => a + (b - a) * k;
const sm = (k) => { k = clamp(k); return k * k * (3 - 2 * k); };

function clay(color) {
  return new THREE.MeshStandardMaterial({ color, roughness: 0.62, metalness: 0 });
}
function part(geo, material, parent, pos = [0, 0, 0], scale) {
  const m = new THREE.Mesh(geo, material);
  m.position.set(...pos);
  if (scale) m.scale.set(...scale);
  m.castShadow = true; m.receiveShadow = true;
  parent.add(m);
  return m;
}
function joint(parent, pos = [0, 0, 0]) { const g = new THREE.Group(); g.position.set(...pos); parent.add(g); return g; }

// ---------- the face ----------
// The bubble outline in canvas pixels (512 x 512): an ellipse with a tail at the lower right.
function bubblePath(g, s = 1, ox = 0, oy = 0) {
  const P = (x, y) => [ox + 256 + (x - 256) * s, oy + 240 + (y - 240) * s];
  g.beginPath();
  g.ellipse(...P(256, 240), 212 * s, 184 * s, 0, 0, Math.PI * 2);
  g.moveTo(...P(330, 378)); g.quadraticCurveTo(...P(374, 418), ...P(418, 424)); g.quadraticCurveTo(...P(398, 392), ...P(400, 350));
  g.closePath();
}

// Face state -> canvas. f: { blink, look:[dx,dy], surprise, joy, open, frown, o }
function faceTexture(o) {
  const c = document.createElement("canvas"); c.width = c.height = 512;
  const g = c.getContext("2d"), tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 4;
  let last = "";
  const INK = o.ink;
  const draw = (f) => {
    const k = [f.blink, f.look[0], f.look[1], f.surprise, f.joy, f.open, f.frown, f.o].map((v) => v.toFixed(2)).join();
    if (k === last) return; last = k;
    g.clearRect(0, 0, 512, 512);
    // face: white with a soft cool shade toward the edge, so the puff reads even head-on
    const grd = g.createRadialGradient(236, 200, 40, 256, 240, 230);
    grd.addColorStop(0, "#FFFFFF"); grd.addColorStop(0.75, "#F7F4F1"); grd.addColorStop(1, "#E4E7E5");
    g.fillStyle = grd; bubblePath(g); g.fill();

    // eyes: dark skin ovals with a catchlight; joy turns them into ^ arcs, surprise widens them
    const ex = f.look[0] * 22, ey = f.look[1] * 16, big = 1 + 0.22 * f.surprise;
    const open = clamp(f.blink * (1 - f.joy));
    for (const x of [188, 324]) {
      const cx = x + ex, cy = 206 + ey;
      if (open > 0.04) {
        g.fillStyle = INK;
        g.beginPath(); g.ellipse(cx, cy, 28 * big, 42 * big * open, 0, 0, Math.PI * 2); g.fill();
        if (open > 0.5) {
          g.fillStyle = "rgba(255,255,255,0.6)";
          g.beginPath(); g.ellipse(cx - 9 * big, cy - 16 * big * open, 8 * big, 11 * big * open, -0.4, 0, Math.PI * 2); g.fill();
        }
      }
      if (f.joy > 0.04) {
        g.strokeStyle = INK; g.lineWidth = 15; g.lineCap = "round"; g.globalAlpha = clamp(f.joy * 1.4);
        g.beginPath(); g.arc(cx, cy + 14, 28, Math.PI * 1.12, Math.PI * 1.88); g.stroke();
        g.globalAlpha = 1;
      }
    }

    // mouth: a smile that can open into a D, flatten into a frown, or round into a small "o"
    const mx = 256 + f.look[0] * 10, my = 286 + f.look[1] * 8;
    g.fillStyle = INK; g.strokeStyle = INK; g.lineCap = "round"; g.lineJoin = "round";
    if (f.o > 0.3) {
      const r = 14 + 10 * f.o;
      g.beginPath(); g.ellipse(mx, my + 4, r * 0.8, r, 0, 0, Math.PI * 2); g.fill();
    } else if (f.open > 0.15) {
      const w = 64, h = 26 + 38 * f.open;
      g.beginPath(); g.moveTo(mx - w, my - 6); g.quadraticCurveTo(mx, my + 2, mx + w, my - 6);
      g.quadraticCurveTo(mx + w * 0.9, my + h, mx, my + h); g.quadraticCurveTo(mx - w * 0.9, my + h, mx - w, my - 6); g.fill();
      g.fillStyle = o.tongue;
      g.beginPath(); g.ellipse(mx + 4, my + h - 12, 26, 12 * f.open + 4, 0, Math.PI, Math.PI * 2, true); g.fill();
    } else {
      const curve = lerp(1, -0.8, f.frown);           // 1 smile .. -0.8 frown
      g.lineWidth = 20;
      g.beginPath(); g.moveTo(mx - 50, my - 4 * curve); g.quadraticCurveTo(mx, my + 48 * curve, mx + 50, my - 4 * curve); g.stroke();
    }
    tex.needsUpdate = true;
  };
  return { tex, draw };
}

// a soft mask of the bubble (blurred), sampled to puff the face patch toward its middle
function bubbleMask() {
  const c = document.createElement("canvas"); c.width = c.height = 128;
  const g = c.getContext("2d");
  g.scale(0.25, 0.25); g.fillStyle = "#fff"; bubblePath(g); g.fill();
  const b = document.createElement("canvas"); b.width = b.height = 128;
  const h = b.getContext("2d"); h.filter = "blur(7px)"; h.drawImage(c, 0, 0);
  const d = h.getImageData(0, 0, 128, 128).data;
  return (u, v) => { // u, v in 0..1, v up
    const x = clamp(Math.round(u * 127), 0, 127), y = clamp(Math.round((1 - v) * 127), 0, 127);
    return d[(y * 128 + x) * 4] / 255;
  };
}
// a dark soft ring just outside the bubble: the groove where the puffy face meets the body
function rimTexture(o) {
  const c = document.createElement("canvas"); c.width = c.height = 512;
  const g = c.getContext("2d");
  g.filter = "blur(10px)"; g.fillStyle = o.groove; bubblePath(g, 1.045, 0, 5); g.fill();
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}

// sprites beside the head: a "?" bubble (confused) and three check badges (success)
function spriteTex(drawFn) {
  const c = document.createElement("canvas"); c.width = c.height = 256;
  drawFn(c.getContext("2d"));
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}
const QTEX = (o) => spriteTex((g) => {
  g.fillStyle = "#FFFFFF"; g.shadowColor = "rgba(0,0,0,0.25)"; g.shadowBlur = 14; g.shadowOffsetY = 6;
  g.beginPath(); g.ellipse(128, 112, 100, 88, 0, 0, Math.PI * 2);
  g.moveTo(186, 180); g.quadraticCurveTo(208, 232, 226, 240); g.quadraticCurveTo(168, 230, 144, 196); g.fill(); // tail toward the mascot
  g.shadowColor = "transparent"; g.fillStyle = o.badge;
  g.font = "900 130px Inter, Arial, sans-serif"; g.textAlign = "center"; g.textBaseline = "middle"; g.fillText("?", 128, 118);
});
const CTEX = (o) => spriteTex((g) => {
  g.fillStyle = o.badge; g.beginPath(); g.arc(128, 128, 110, 0, Math.PI * 2); g.fill();
  g.strokeStyle = "#FFFFFF"; g.lineWidth = 26; g.lineCap = "round"; g.lineJoin = "round";
  g.beginPath(); g.moveTo(78, 132); g.lineTo(112, 166); g.lineTo(180, 94); g.stroke();
});

export function makeMascot(parent, opts = {}) {
  const o = { ...DEFAULTS, ...opts };
  const skin = clay(o.body), deep = clay(o.boots);
  const root = new THREE.Group(); parent.add(root);
  const hips = joint(root, [0, 0.66, 0]);          // everything above the legs bobs from here
  const body = joint(hips, [0, 1.0, 0]);
  const torso = part(new THREE.SphereGeometry(1, 48, 32), skin, body, [0, 0, 0], [1.04, 0.98, 0.94]);

  // the body's own speech-bubble tail, lower right, pointing out and down (never down like a leg)
  if (o.bodyTail) {
    const tailProfile = [[0.32, 0], [0.3, 0.14], [0.25, 0.3], [0.18, 0.44], [0.12, 0.54], [0.07, 0.6], [0.0, 0.63]]
      .map(([r, y]) => new THREE.Vector2(r, y));
    // on the front, just under the face's own tail, pointing down, right and a little forward
    const tail = part(new THREE.LatheGeometry(tailProfile, 28), skin, body, [0.56, -0.6, 0.36]);
    tail.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), new THREE.Vector3(0.72, -0.66, 0.18).normalize());
    tail.scale.set(0.72, 0.85, 0.55);
  }

  // the face: a patch that follows the body, puffed toward its middle, with a soft groove around it
  const face = faceTexture(o);
  const mask = bubbleMask();
  const FW = 1.78, FH = 1.68, FY = 0.04;
  const onBody = (x, y, lift) => { const u = x / 1.04, v = y / 0.98; return 0.94 * Math.sqrt(Math.max(0, 1 - u * u - v * v)) + lift; };
  const fg = new THREE.PlaneGeometry(FW, FH, 72, 72), fp = fg.attributes.position;
  for (let i = 0; i < fp.count; i++) {
    const x = fp.getX(i), y = fp.getY(i) + FY;
    const puff = 0.085 * sm((mask(x / FW + 0.5, (y - FY) / FH + 0.5) - 0.35) / 0.6);
    fp.setXYZ(i, x, y, onBody(x, y, 0.006 + puff));
  }
  fg.computeVertexNormals();
  const faceMesh = part(fg, new THREE.MeshStandardMaterial({ map: face.tex, roughness: 0.55, transparent: true, alphaTest: 0.5 }), body);
  faceMesh.castShadow = false;
  const rg = new THREE.PlaneGeometry(FW * 1.1, FH * 1.1, 48, 48), rp = rg.attributes.position;
  for (let i = 0; i < rp.count; i++) { const x = rp.getX(i), y = rp.getY(i) + FY; rp.setXYZ(i, x, y, onBody(x, y, 0.003)); }
  const rim = new THREE.Mesh(rg, new THREE.MeshBasicMaterial({ map: rimTexture(o), transparent: true, depthWrite: false }));
  rim.renderOrder = 1; body.add(rim);

  // arms: shoulder -> upper arm -> elbow -> forearm -> hand (palm, thumb, three fingers)
  const arm = (side) => {
    const sh = joint(body, [side * 0.9, -0.2, 0.04]);
    part(new THREE.SphereGeometry(0.21, 20, 14), skin, sh);
    part(new THREE.CapsuleGeometry(0.2, 0.2, 8, 16), skin, sh, [0, -0.17, 0]);
    const el = joint(sh, [0, -0.33, 0]);
    part(new THREE.SphereGeometry(0.19, 20, 14), skin, el);
    part(new THREE.CapsuleGeometry(0.185, 0.16, 8, 16), skin, el, [0, -0.14, 0]);
    const hand = joint(el, [0, -0.32, 0]);
    part(new THREE.SphereGeometry(0.24, 24, 16), skin, hand, [0, -0.02, 0], [1.05, 1.0, 0.82]);
    const thumb = joint(hand, [-side * 0.17, 0.0, 0.07]);
    part(new THREE.CapsuleGeometry(0.085, 0.16, 6, 12), skin, thumb, [0, 0.12, 0]);
    const fingers = [-0.11, 0, 0.11].map((x, i) => {
      const f = joint(hand, [x * side, -0.17, 0.02]);
      part(new THREE.CapsuleGeometry(0.068, 0.11, 6, 12), skin, f, [0, -0.08, 0]);
      return f;
    });
    return { side, sh, el, hand, thumb, fingers };
  };
  const armL = arm(-1), armR = arm(1);

  // legs: hip pivots under the body, boot-like feet pointing forward
  const leg = (side) => {
    const hip = joint(root, [side * 0.4, 0.78, 0]);
    part(new THREE.CapsuleGeometry(0.23, 0.3, 8, 16), skin, hip, [0, -0.32, 0]);
    part(new THREE.SphereGeometry(0.28, 24, 16), deep, hip, [0, -0.66, 0.1], [1.04, 0.66, 1.3]);
    return hip;
  };
  const legL = leg(-1), legR = leg(1);

  const shadow = new THREE.Mesh(new THREE.CircleGeometry(1, 32),
    new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.2, depthWrite: false }));
  shadow.rotation.x = -Math.PI / 2; shadow.position.y = 0.01;
  root.add(shadow);

  const q = new THREE.Sprite(new THREE.SpriteMaterial({ map: QTEX(o), transparent: true, depthWrite: false }));
  q.scale.setScalar(0.001); root.add(q);
  const ctex = CTEX(o);
  const checks = [0, 1, 2].map(() => { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: ctex, transparent: true, depthWrite: false })); s.scale.setScalar(0.001); root.add(s); return s; });

  return { root, hips, body, torso, face, armL, armR, legL, legR, shadow, q, checks };
}

// ---------- poses ----------
// Each arm gesture is a target for shoulder (x forward swing, z lift out), elbow (x bend
// forward, z bend in the frontal plane) and hand (fingers 0 curled .. 1 open, index 0..1 out,
// up 0..1 thumb pointing at the sky). Weights blend them on top of the rest pose.
const REST = { shx: 0, shz: 0.22, elx: -0.15, elz: 0, fingers: 0.45, index: 0, up: 0 };
const GEST = {
  reach: { shx: -1.15, shz: 0.12, elx: -0.35, elz: 0, fingers: 0.9, index: 0, up: 0 },
  wave: { shx: -0.15, shz: 2.35, elx: 0, elz: 0, fingers: 1, index: 0, up: 0 },
  point: { shx: -0.55, shz: 1.2, elx: -0.1, elz: 0, fingers: 0, index: 1, up: 0 },
  thumbs: { shx: -0.55, shz: 0.5, elx: -1.6, elz: 0, fingers: 0, index: 0, up: 1 },
  think: { shx: -0.55, shz: 0.42, elx: -2.35, elz: 0.25, fingers: 0.1, index: 1, up: 0 },
};
const KEYS = Object.keys(REST);
const qa = new THREE.Quaternion(), qb = new THREE.Quaternion(), qw = new THREE.Quaternion();

function poseArm(a, t, w, swing) {
  const p = { ...REST };
  for (const g in GEST) {
    const k = clamp(w[g] || 0);
    if (k > 0) for (const key of KEYS) p[key] = lerp(p[key], GEST[g][key], k);
  }
  const wv = clamp(w.wave || 0);
  // a thumbs-up pumps a little; a pointing hand jabs at what it shows
  const pump = 0.14 * Math.sin(t * 6.5) * clamp(w.thumbs || 0) + 0.08 * Math.sin(t * 5) * clamp(w.point || 0);
  a.sh.rotation.set(p.shx + swing + pump, 0, a.side * (p.shz + 0.04 * Math.sin(t * 2.2 + a.side)));
  // waving swings the forearm in the frontal plane; thinking taps a little
  a.el.rotation.set(p.elx, 0, a.side * (p.elz + wv * 0.42 * Math.sin(t * 9)) + (w.think || 0) * 0.05 * Math.sin(t * 3));
  a.fingers.forEach((f, i) => {
    const isIndex = i === 0;                           // the finger nearest the thumb
    const open = isIndex ? Math.max(p.fingers, p.index) : p.fingers;
    f.scale.set(1, lerp(0.3, isIndex ? 1 + 0.5 * p.index : 1, open), 1);
    f.rotation.x = lerp(1.1, 0, open);                 // curled fingers fold toward the palm
    f.rotation.z = a.side * (i - 1) * 0.18 * p.fingers; // open fingers spread
  });
  // thumb: rests along the palm; for a thumbs-up it points straight up in the world
  qa.setFromEuler(new THREE.Euler(-0.35, 0, a.side * 0.9));
  if (p.up > 0.001) {
    a.thumb.parent.updateWorldMatrix(true, false);
    a.thumb.parent.getWorldQuaternion(qw); qw.invert();
    qb.copy(qw);                                       // world identity -> +y is the sky
    a.thumb.quaternion.copy(qa).slerp(qb, p.up);
    a.thumb.scale.set(1 + 0.35 * p.up, 1 + 0.9 * p.up, 1 + 0.35 * p.up);
  } else { a.thumb.quaternion.copy(qa); a.thumb.scale.setScalar(1); }
}

// poseMascot(mascot, t, s): every field is an eased 0..1 weight unless noted.
//   walk, phase       stepping (phase advances with time)
//   armR / armL       { reach, wave, point, thumbs, think }
//   lean (-1..1)      lean forward (+) / back; tilt (-1..1) head tilt to its left/right
//   hop (0..1)        one hop of joy across its own window
//   face              { look:[dx,dy] -1..1, surprise, joy, open, frown, o }
//   question, checks  the "?" bubble and the three floating check badges
export function poseMascot(m, t, s) {
  const walk = s.walk || 0, ph = s.phase != null ? s.phase : t * 7;
  const swing = Math.sin(ph) * 0.55 * walk;
  m.legL.rotation.x = swing; m.legR.rotation.x = -swing;
  const bob = walk * 0.09 * (1 - Math.cos(2 * ph)) / 2;
  const hop = s.hop ? Math.sin(Math.PI * sm(s.hop)) * 0.55 : 0;
  // squash on take-off and landing, stretch in the air: within +-12 %
  const air = s.hop ? Math.sin(Math.PI * sm(s.hop)) : 0, edge = s.hop ? Math.sin(Math.PI * 2 * sm(s.hop)) : 0;
  const breathe = (1 - walk) * 0.022 * Math.sin(t * 2.2);
  const sq = 1 + breathe + 0.08 * air - 0.06 * Math.abs(edge) * (1 - air);
  m.hips.position.y = 0.66 + bob + hop;
  m.legL.position.y = m.legR.position.y = 0.78 + hop;
  m.body.scale.set(1 / Math.sqrt(sq), sq, 1 / Math.sqrt(sq));
  m.body.rotation.z = walk * 0.06 * Math.sin(ph) + (s.tilt || 0) * 0.16 + 0.025 * Math.sin(t * 1.3);
  m.body.rotation.x = walk * 0.08 + (s.lean || 0) * 0.16;

  poseArm(m.armR, t, s.armR || {}, swing * 0.8);
  poseArm(m.armL, t, s.armL || {}, -swing * 0.8);

  // face: blink every ~2.7 s (eased over 5 frames), plus whatever the moment asks for
  const bt = (t + 0.7) % 2.7, blink = bt < 0.16 ? 1 - Math.sin(Math.PI * bt / 0.16) * 0.9 : 1;
  const f = s.face || {};
  m.face.draw({ blink, look: f.look || [0, 0], surprise: f.surprise || 0, joy: f.joy || 0, open: f.open || 0, frown: f.frown || 0, o: f.o || 0 });

  // the "?" bubble and the check badges sit on the mascot's left, where a layout with the chat
  // panel above keeps the frame free; move them if your layout differs
  const qk = clamp(s.question || 0);
  m.q.scale.setScalar(Math.max(0.001, 1.25 * sm(qk * 1.25)));
  m.q.position.set(-1.5, 2.6 + 0.06 * Math.sin(t * 3), 0.3);
  const ck = clamp(s.checks || 0);
  m.checks.forEach((c, i) => {
    const k = sm(ck * 1.3 - i * 0.15), base = [[-1.55, 2.6], [-1.95, 1.65], [-1.25, 3.3]][i];
    c.scale.setScalar(Math.max(0.001, 0.78 * k));
    c.position.set(base[0] + 0.08 * Math.sin(t * 2 + i), base[1] + 0.12 * Math.sin(t * 2.6 + i * 2), 0.5);
  });

  m.shadow.scale.setScalar(1.08 - (bob + hop) * 0.5);
}
