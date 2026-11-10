// SPDX-License-Identifier: GPL-3.0-or-later
// Character rig for Reels animatics and HyperFrames renders (references/motion-video.md).
// Draws into an <svg viewBox="0 0 1080 1920">; every move goes on one paused GSAP timeline,
// so a still is tl.seek(t) and the render is the same code.
//
//   const R = KilasRig.create(svg, { palette });          // drawing helpers
//   const p = R.person(parentG, 300, { phone: true, mug: true });
//   const m = R.mascot(parentG, 700, 190, { color: "#22A08F" });
//   const tl = gsap.timeline({ paused: true });
//   const A = KilasRig.acting(tl, R.motion);               // rot, jitter, face, take, blink, count, finish
//   Brand motion tokens: KilasRig.create(svg, { palette, motion: { take: {...}, squashMax: 0.1 } })
//   A.face(p, 1.0, "big", "o"); A.take(p, 1.0, 0.08); A.rot(p.armR, 150, 2.0, 0.3, "back.out(1.6)");
//   A.finish(); window.__timelines["main"] = tl;           // counters synced on every seek
(function () {
  const NS = "http://www.w3.org/2000/svg";
  function el(parent, tag, attrs, text) {
    const n = document.createElementNS(NS, tag);
    for (const k in attrs) n.setAttribute(k, attrs[k]);
    if (text != null) n.textContent = text;
    parent.appendChild(n);
    return n;
  }
  const DEFAULTS = {
    ink: "#111827", accent: "#14786B", mascot: "#22A08F", skin: "#F3C9A6", skinShade: "#E2AE88",
    hair: "#3B2A22", shirt: "#F4EFE6", shirtLine: "#B9AE9C", desk: "#C98B5A", deskDark: "#A9703F",
    rule: "#E5E0D4", bubble: "#FFFFFF", out: "#DCF8C6", alarm: "#E5484D",
  };

  // Motion language: override from the brand's design.md "Motion" block (motion-video.md 2b).
  const MOTION = {
    dur: { fast: 0.15, base: 0.4, slow: 0.6 },
    ease: { enter: "back.out(1.7)", exit: "power3.in", emphasis: "elastic.out(1,0.5)", move: "power2.inOut" },
    take: { anticipate: 0.08, stretch: 0.14, settle: 0.35 },
    squashMax: 0.12,
  };

  function create(svg, opts) {
    const C = Object.assign({}, DEFAULTS, (opts && opts.palette) || {});
    const motion = mergeMotion((opts && opts.motion) || {});

    // A chat bubble; g._w is its width, for right-aligning: x = rightEdge - g._w / 2.
    // Kinds: in, out, brand (the mascot's answers), bad (a complaint or a wrong reply).
    function bubble(parent, text, kind) {
      const g = el(parent, "g", {});
      const w = Math.round(text.length * 20 + 52); // 34 px text: readable at 360 px wide
      const fill = kind === "brand" ? C.accent : kind === "out" ? C.out : kind === "bad" ? "#FFE9E9" : C.bubble;
      const stroke = kind === "in" ? C.rule : kind === "bad" ? C.alarm : "none";
      el(g, "rect", { x: -w / 2, y: -34, width: w, height: 68, rx: 26, fill, stroke, "stroke-width": 3 });
      el(g, "text", { x: 0, y: 12, "text-anchor": "middle", "font-family": "Inter, system-ui, sans-serif", "font-size": 34, "font-weight": 600,
        fill: kind === "brand" ? "#fff" : kind === "bad" ? C.alarm : C.ink }, text);
      g._w = w;
      return g;
    }

    // A seated person behind a desk; local origin is the desk centre-left, desk top at y 340.
    // Eye states: normal, big, spiral, x, happy. Mouth states: smile, o, wavy, grin.
    function person(parent, x, o) {
      o = o || {};
      const root = el(parent, "g", { transform: `translate(${x},0)` });
      const body = el(root, "g", {});
      el(body, "ellipse", { cx: 0, cy: 318, rx: 108, ry: 92, fill: C.shirt, stroke: C.shirtLine, "stroke-width": 4 });
      el(body, "rect", { x: -16, y: 212, width: 32, height: 30, fill: C.skinShade });
      const head = el(body, "g", {});
      el(head, "circle", { cx: 0, cy: 58, r: 36, fill: C.hair });
      el(head, "circle", { cx: 0, cy: 150, r: 74, fill: C.skin });
      el(head, "path", { d: "M-76,150 C-80,70 80,70 76,150 C60,108 20,96 -6,104 C-30,96 -62,112 -76,150 Z", fill: C.hair });
      [-40, 40].forEach((cx) => el(head, "circle", { cx, cy: 182, r: 12, fill: "#F2A7A0", opacity: 0.55 }));
      const brows = el(head, "g", {});
      el(brows, "path", { d: "M-40,124 L-14,120", stroke: C.hair, "stroke-width": 6, "stroke-linecap": "round" });
      el(brows, "path", { d: "M14,120 L40,124", stroke: C.hair, "stroke-width": 6, "stroke-linecap": "round" });
      const eyes = el(head, "g", {}), E = {};
      E.normal = el(eyes, "g", {});
      [-27, 27].forEach((ex) => el(E.normal, "ellipse", { cx: ex, cy: 152, rx: 8, ry: 11, fill: C.ink }));
      E.big = el(eyes, "g", { opacity: 0 });
      [-28, 28].forEach((ex) => { el(E.big, "circle", { cx: ex, cy: 150, r: 17, fill: "#fff", stroke: C.ink, "stroke-width": 3 }); el(E.big, "circle", { cx: ex, cy: 152, r: 7, fill: C.ink }); });
      E.spiral = el(eyes, "g", { opacity: 0 });
      [-28, 28].forEach((ex) => {
        const s = el(E.spiral, "g", { class: "spin", transform: `translate(${ex},152)` });
        el(s, "path", { d: "M0,0 m-2,0 a2,2 0 1,1 4,0 a5,5 0 1,1 -10,0 a8,8 0 1,1 16,0 a11,11 0 1,1 -22,0", fill: "none", stroke: C.ink, "stroke-width": 3.5 });
      });
      E.x = el(eyes, "g", { opacity: 0 });
      [-28, 28].forEach((ex) => el(E.x, "path", { d: `M${ex - 10},142 l20,20 M${ex + 10},142 l-20,20`, stroke: C.ink, "stroke-width": 5, "stroke-linecap": "round" }));
      E.happy = el(eyes, "g", { opacity: 0 });
      [-27, 27].forEach((ex) => el(E.happy, "path", { d: `M${ex - 11},156 q11,-14 22,0`, fill: "none", stroke: C.ink, "stroke-width": 5, "stroke-linecap": "round" }));
      const lids = [-27, 27].map((ex) => el(head, "rect", { x: ex - 15, y: 136, width: 30, height: 0, fill: C.skin })); // attr height 0..32 = blink/sleep
      const mouths = el(head, "g", {}), M = {};
      M.smile = el(mouths, "path", { d: "M-20,190 Q0,206 20,190", fill: "none", stroke: C.ink, "stroke-width": 5, "stroke-linecap": "round" });
      M.o = el(mouths, "ellipse", { cx: 0, cy: 196, rx: 11, ry: 15, fill: "#7A2E2E", opacity: 0 });
      M.wavy = el(mouths, "path", { d: "M-24,198 q6,-9 12,0 t12,0 t12,0 t12,0", fill: "none", stroke: C.ink, "stroke-width": 5, "stroke-linecap": "round", opacity: 0 });
      M.grin = el(mouths, "path", { d: "M-24,186 Q0,218 24,186 Z", fill: "#7A2E2E", stroke: C.ink, "stroke-width": 4, opacity: 0 });
      const sweat = el(head, "g", { opacity: 0 });
      el(sweat, "path", { d: "M84,110 q12,18 0,26 q-12,-8 0,-26 Z", fill: "#7CC4F0" });
      const stars = el(head, "g", { opacity: 0, transform: "translate(0,70)" });
      [0, 120, 240].forEach((a) => { const r = (a * Math.PI) / 180; el(stars, "text", { x: Math.cos(r) * 90, y: Math.sin(r) * 26, "text-anchor": "middle", "font-size": 34, fill: "#F5B700" }, "★"); });
      el(root, "rect", { x: -300, y: 340, width: 1100, height: 26, rx: 8, fill: C.desk });
      el(root, "rect", { x: -300, y: 366, width: 1100, height: 110, fill: C.deskDark });
      // Arms rotate about the shoulder with the attribute form rotate(a sx 262): see acting().rot.
      function arm(side) {
        const sx = side * 84;
        const g = el(root, "g", { transform: `rotate(0 ${sx} 262)` });
        g._sx = sx;
        el(g, "path", { d: `M${sx},262 L${sx + side * 26},336`, stroke: C.shirtLine, "stroke-width": 40, "stroke-linecap": "round" });
        el(g, "path", { d: `M${sx},262 L${sx + side * 26},336`, stroke: C.shirt, "stroke-width": 32, "stroke-linecap": "round" });
        el(g, "circle", { cx: sx + side * 26, cy: 340, r: 18, fill: C.skin, stroke: C.skinShade, "stroke-width": 3 });
        return g;
      }
      const armL = arm(-1), armR = arm(1);
      if (o.phone) {
        el(armR, "rect", { x: 92, y: 282, width: 38, height: 64, rx: 7, fill: "#0E1A2B" });
        el(armR, "rect", { x: 96, y: 288, width: 30, height: 50, rx: 4, fill: "#9AD8CF" });
      }
      if (o.mug) {
        el(armL, "rect", { x: -128, y: 300, width: 40, height: 44, rx: 8, fill: "#fff", stroke: C.rule, "stroke-width": 3 });
        el(armL, "path", { d: "M-128,312 q-16,0 -16,12 q0,12 16,12", fill: "none", stroke: C.rule, "stroke-width": 5 });
      }
      return { root, body, head, brows, E, M, lids, sweat, stars, armL, armR };
    }

    // A chat-bubble mascot. Keep squash and stretch within ±12 % so it stays on-model.
    function mascot(parent, x, y, o) {
      const color = (o && o.color) || C.mascot;
      const root = el(parent, "g", { transform: `translate(${x},${y}) scale(1)` });
      const body = el(root, "g", {});
      el(body, "path", { d: "M-30,58 L-58,92 L-6,66 Z", fill: color });
      el(body, "circle", { cx: 0, cy: 0, r: 70, fill: color });
      el(body, "ellipse", { cx: 4, cy: -2, rx: 48, ry: 40, fill: "#fff" });
      el(body, "ellipse", { cx: -14, cy: -8, rx: 6, ry: 9, fill: C.ink });
      el(body, "ellipse", { cx: 20, cy: -8, rx: 6, ry: 9, fill: C.ink });
      el(body, "path", { d: "M-10,12 Q4,24 18,12", fill: "none", stroke: C.ink, "stroke-width": 4.5, "stroke-linecap": "round" });
      const armL = el(body, "g", {}); el(armL, "ellipse", { cx: -80, cy: 4, rx: 20, ry: 13, fill: color });
      const armR = el(body, "g", {}); el(armR, "ellipse", { cx: 80, cy: 4, rx: 20, ry: 13, fill: color });
      gsap.set(body, { transformOrigin: "50% 100%" });
      gsap.set(armL, { transformOrigin: "100% 50%" });
      gsap.set(armR, { transformOrigin: "0% 50%" });
      return { root, body, armL, armR };
    }

    return { el, bubble, person, mascot, C, motion };
  }

  function mergeMotion(m) {
    return {
      dur: Object.assign({}, MOTION.dur, m.dur || {}),
      ease: Object.assign({}, MOTION.ease, m.ease || {}),
      take: Object.assign({}, MOTION.take, m.take || {}),
      squashMax: m.squashMax != null ? m.squashMax : MOTION.squashMax,
    };
  }

  function acting(tl, motionTokens) {
    const M = mergeMotion(motionTokens || {});
    const counters = [];
    const A = {
      // Rotate an arm about its shoulder (attribute form; GSAP's svgOrigin is global and drifts in nested groups).
      rot(arm, a, t, d, ease) { tl.to(arm, { attr: { transform: `rotate(${a} ${arm._sx} 262)` }, duration: d != null ? d : M.dur.fast, ease: ease || M.ease.move }, t); },
      // Typing, buzzing, waving: alternate between two angles n times, ending on a0.
      jitter(arm, a0, a1, t, step, n) { for (let i = 0; i < n; i++) A.rot(arm, i % 2 ? a0 : a1, t + i * step, step, "none"); A.rot(arm, a0, t + n * step, step, "none"); },
      // Swap eye and mouth states at t (pair with take()).
      face(p, t, eyes, mouth) {
        Object.keys(p.E).forEach((k) => tl.set(p.E[k], { opacity: k === eyes ? 1 : 0 }, t));
        Object.keys(p.M).forEach((k) => tl.set(p.M[k], { opacity: k === mouth ? 1 : 0 }, t));
      },
      // A take: anticipation squash, stretch with a small rise, elastic settle. amt 0.05-0.1.
      take(p, t, amt) {
        amt = Math.min(amt, M.squashMax); // never squash past the brand's limit
        const T = M.take;
        tl.to(p.head, { scaleY: 1 - amt, scaleX: 1 + amt * 0.6, transformOrigin: "50% 100%", duration: T.anticipate, ease: "power2.in" }, t - T.anticipate);
        tl.to(p.head, { scaleY: 1 + amt * 1.2, scaleX: 1 - amt * 0.5, y: -90 * amt, transformOrigin: "50% 100%", duration: T.stretch, ease: "power3.out" }, t);
        tl.to(p.head, { scaleY: 1, scaleX: 1, y: 0, transformOrigin: "50% 100%", duration: T.settle, ease: M.ease.emphasis }, t + T.stretch);
      },
      // Pop a node in (a bubble, a card) with the brand's enter ease; node keeps translate/scale/rotate in its transform attribute.
      pop(node, t, x, y, rot) { tl.to(node, { attr: { transform: `translate(${x},${y}) scale(1) rotate(${rot || 0})` }, duration: M.dur.base, ease: M.ease.enter }, t); },
      // A blink over 4 frames (half, shut, shut, half); add one on every expression swap, and one every 0.5-2.3 s.
      blink(p, t) {
        const f = 1 / 30;
        [[0, 16], [f, 32], [3 * f, 16], [4 * f, 0]].forEach(([dt, h]) => tl.set(p.lids, { attr: { height: h } }, t + dt));
      },
      // ---- camera: wrap the whole scene in one top-level <g> and pass it here ----
      // The camera is almost never dead still: every hold creeps in (0.15-0.35 % a frame), moves glide
      // with an ease in and out over 18-40 frames, impacts kick with a shake that flips every frame.
      camera(g) { A._cam = g; A._camS = 1; gsap.set(g, { svgOrigin: "540 960" }); return g; },
      creep(t0, t1, perFrame) {
        const frames = Math.max(1, Math.round((t1 - t0) * 30));
        A._camS = A._camS * (1 + (perFrame != null ? perFrame : 0.0025) * frames);
        tl.to(A._cam, { scale: A._camS, svgOrigin: "540 960", duration: t1 - t0, ease: "none" }, t0);
      },
      glide(t, to, frames) {
        if (to.scale) A._camS = to.scale;
        tl.to(A._cam, Object.assign({ svgOrigin: "540 960", duration: (frames || 24) / 30, ease: "sine.inOut" }, to), t);
      },
      kick(t, px) {
        const f = 1 / 30, amp = px || 10;
        for (let i = 0; i < 7; i++) tl.set(A._cam, { y: (i % 2 ? -1 : 1) * amp * (1 - i / 7) }, t + i * f);
        tl.set(A._cam, { y: 0 }, t + 7 * f);
      },
      // A number on screen as a pure function of time: keys [[t, value], ...], eased between keys.
      count(textEl, keys, suffix) { counters.push([textEl, keys, suffix || ""]); },
      // Call once after the last tween: keeps counters right in stills, scrubbing and renders.
      finish() {
        const at = (t, keys) => {
          let v = keys[0][1];
          for (let i = 1; i < keys.length; i++) {
            const [t0, v0] = keys[i - 1], [t1, v1] = keys[i];
            if (t >= t1) v = v1; else { if (t > t0) { const q = (t - t0) / (t1 - t0); v = v0 + (v1 - v0) * (1 - (1 - q) * (1 - q)); } break; }
          }
          return Math.round(v);
        };
        const sync = () => counters.forEach(([n, k, s]) => (n.textContent = at(tl.time(), k) + s));
        tl.eventCallback("onUpdate", sync);
        const seek = tl.seek.bind(tl);
        tl.seek = (t) => { seek(t, false); sync(); return tl; };
        sync();
        return tl;
      },
    };
    return A;
  }

  window.KilasRig = { create, acting, MOTION };
})();
