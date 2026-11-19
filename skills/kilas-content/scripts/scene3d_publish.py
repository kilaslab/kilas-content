#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Check a three.js scene and write the files map that publishes its animatic page.

    python3 scene3d_publish.py <item>/scene <out_dir> [--frames <dir>] [--check-only]

1. Syntax: every scene module is parsed as ESM with `node --check`. A syntax error in one
   module (a duplicate const, say) leaves the page and every still blank with nothing in
   the console, so run this before scene_stills.sh too (--check-only).
2. three.js: the animatic page (storyboard.html) loads three.js and its addons from
   jsDelivr at the revision in lib/three.core.js, so the published page does not carry
   library code. The render page (index.html) keeps lib/ and works offline.
3. Models: artifacts do not serve .bin, so each .gltf is copied to <out_dir> with its
   buffers embedded as base64 data URIs (GLTFLoader reads them); textures stay as files.
4. Writes <out_dir>/files.json: {published path: source} for the Artifact tool's `files`,
   with root = the scene folder and file_path = <scene>/storyboard.html. --frames adds the
   animatic stills as frames/<name>.

Exit 1 on a syntax error, a wrong importmap, or a file over 16 MB.
"""
import argparse, base64, json, os, re, shutil, subprocess, sys, tempfile

SERVED = {".css", ".js", ".mjs", ".json", ".svg", ".png", ".jpg", ".jpeg", ".webp", ".gif",
          ".avif", ".woff", ".woff2", ".ttf", ".otf", ".mp3", ".wav", ".ogg", ".mp4", ".webm", ".txt"}
SKIP_DIRS = {"lib/addons", "node_modules", "frames", "audit"}
SKIP_FILES = {"lib/three.module.js", "lib/three.core.js"}
SKIP_NAMES = {"files.txt"}  # download manifests, at any depth
LIMIT = 16 * 1024 * 1024


def syntax(scene):
    if not shutil.which("node"):
        print("syntax: node not found, skipped (install Node to catch blank-page module errors)")
        return []
    bad = []
    with tempfile.TemporaryDirectory() as tmp:
        for name in sorted(os.listdir(scene)):
            if not name.endswith(".js"):
                continue
            dst = os.path.join(tmp, name[:-3] + ".mjs")
            shutil.copyfile(os.path.join(scene, name), dst)
            r = subprocess.run(["node", "--check", dst], capture_output=True, text=True)
            if r.returncode:
                msg = (r.stderr.strip().splitlines() or ["?"])
                bad.append(f"{name}: " + next((l for l in msg if "Error" in l), msg[-1]))
    for b in bad:
        print("syntax FAIL", b)
    if not bad:
        print("syntax: every module parses")
    return bad


def importmap(scene):
    core = os.path.join(scene, "lib", "three.core.js")
    page = os.path.join(scene, "storyboard.html")
    if not (os.path.exists(core) and os.path.exists(page)):
        return ["no lib/three.core.js or storyboard.html in " + scene]
    m = re.search(r"REVISION\s*=\s*'(\d+)'", open(core, encoding="utf-8", errors="ignore").read(200000))
    rev = m.group(1) if m else "?"
    want = f"https://cdn.jsdelivr.net/npm/three@0.{rev}.0/"
    html = open(page, encoding="utf-8").read()
    mp = re.search(r'<script type="importmap">(.*?)</script>', html, re.S)
    imports = json.loads(mp.group(1)).get("imports", {}) if mp else {}
    ok = imports.get("three", "").startswith(want) and imports.get("./lib/addons/", "").startswith(want)
    if ok:
        print(f"importmap: storyboard.html loads three r{rev} from jsDelivr")
        return []
    line = ('<script type="importmap">{ "imports": { "three": "%sbuild/three.module.js", '
            '"./lib/addons/": "%sexamples/jsm/" } }</script>' % (want, want))
    return [f"storyboard.html importmap must load r{rev} from jsDelivr; use:\n  {line}"]


def embed(src, dst):
    d = json.load(open(src, encoding="utf-8"))
    base = os.path.dirname(src)
    for b in d.get("buffers", []):
        uri = b.get("uri", "")
        if uri and not uri.startswith("data:"):
            raw = open(os.path.join(base, uri), "rb").read()
            if len(raw) != b.get("byteLength", len(raw)):
                raise SystemExit(f"{src}: {uri} is {len(raw)} bytes, glTF says {b['byteLength']}")
            b["uri"] = "data:application/octet-stream;base64," + base64.b64encode(raw).decode()
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    json.dump(d, open(dst, "w", encoding="utf-8"), separators=(",", ":"))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("scene")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--frames", help="folder of animatic stills, published as frames/<name>")
    ap.add_argument("--check-only", action="store_true")
    a = ap.parse_args()
    scene = os.path.abspath(a.scene)
    problems = syntax(scene)
    if a.check_only:
        return 1 if problems else 0
    if not a.out:
        ap.error("out_dir is required unless --check-only")
    problems += importmap(scene)
    out = os.path.abspath(a.out)
    files, total, big = {}, 0, []
    for root, dirs, names in os.walk(scene):
        rel_root = os.path.relpath(root, scene).replace(os.sep, "/")
        rel_root = "" if rel_root == "." else rel_root + "/"
        dirs[:] = sorted(d for d in dirs if not d.startswith(".") and rel_root + d not in SKIP_DIRS)
        for n in sorted(names):
            rel = rel_root + n
            ext = os.path.splitext(n)[1].lower()
            if n.startswith(".") or rel in SKIP_FILES or n in SKIP_NAMES or ext in (".html", ".bin"):
                continue
            src = os.path.join(root, n)
            if ext == ".gltf":
                dst = os.path.join(out, rel)
                embed(src, dst)
                files[rel] = {"from": dst, "contentType": "application/json"}
                src = dst
            elif ext in SERVED:
                files[rel] = src
            else:
                continue
            size = os.path.getsize(src)
            total += size
            if size > LIMIT:
                big.append(f"{rel} is {size / 1e6:.1f} MB (limit 16 MB)")
    if a.frames:
        for n in sorted(os.listdir(a.frames)):
            if os.path.splitext(n)[1].lower() in (".jpg", ".jpeg", ".png", ".webp"):
                src = os.path.abspath(os.path.join(a.frames, n))
                files["frames/" + n] = src
                total += os.path.getsize(src)
    problems += big
    os.makedirs(out, exist_ok=True)
    json.dump(files, open(os.path.join(out, "files.json"), "w", encoding="utf-8"), indent=1)
    for p in problems:
        print("FAIL", p)
    print(f"{len(files)} files, {total / 1e6:.1f} MB -> {os.path.join(out, 'files.json')}")
    print(f"publish: file_path={os.path.join(scene, 'storyboard.html')} root={scene} files=<files.json>")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
