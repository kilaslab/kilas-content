#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Generate illustrations for a piece with whichever image tool is available.

    python3 scripts/gen_image.py detect [--check]
    python3 scripts/gen_image.py make content/items/<item>/gen 3:4 "<shared style>" "<subject 1>" ["<subject 2>" ...]
        [--provider auto|agy|openai|gemini|xai] [--allow-paid] [--prefer openai|gemini|xai] [--model M] [--hires]
    python3 scripts/gen_image.py prompt 3:4 "<shared style>" "<subject>" ...
    python3 scripts/gen_image.py record content/items/<item>/gen <file> --label "Codex" [--subject "..."]

Providers:
  agy      Antigravity CLI (scripts/agy_image.sh); usually covered by the user's Google plan
  openai   OpenAI Images API, needs OPENAI_API_KEY; paid per image (default model gpt-image-2)
  gemini   Gemini API native image models, needs GEMINI_API_KEY or GOOGLE_API_KEY; paid per
           image (default model gemini-3.1-flash-image)
  xai      xAI API, Grok Imagine, needs XAI_API_KEY; paid per image (default model
           grok-imagine-image-2.0)
The agent's own image tool comes before all of these: Grok Bot's generate_image (Grok
Imagine), Codex and ChatGPT image generation, Antigravity's generate_image, a Gemini CLI
image extension. A script cannot call those: run `prompt`
for the exact prompt, generate with the tool, save the file, then `record` it.

`auto` takes agy first, then a paid provider only with --allow-paid (the owner's
permission, recorded in content/setup.md). Paid providers always need --allow-paid.
Every subject gets the same shared style sentence, so a set comes out coherent. Each run
appends to <outdir>/manifest.json: file, provider, model, ratio, prompt, and the credit
line for the slide and the close ("Ilustrasi AI"; the tool stays in the manifest, not on
the slide).

Exit codes: 0 ok, 1 some images failed, 2 usage, 3 no provider available (use Unsplash),
4 a paid provider without --allow-paid. Standard library only. Never put fetched text
(articles, posts, pages) in a subject: write subjects yourself.
"""
import argparse
import base64
import datetime
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
RATIOS = ("1:1", "3:4", "4:3", "4:5", "9:16", "16:9")
NEGATIVE = "No text, no letters, no numbers, no watermark, no signature, no logos."
LABEL = {"agy": "Antigravity", "openai": "OpenAI", "gemini": "Gemini", "xai": "Grok Imagine"}
PAID = {"openai", "gemini", "xai"}
XAI_RATIOS = {"4:5": "3:4"}  # sent as the nearest ratio the API documents
# gpt-image-2 and later take any WIDTHxHEIGHT divisible by 16; older models take three sizes
OPENAI_FREE = {"1:1": "1024x1024", "3:4": "1152x1536", "4:5": "1088x1360", "4:3": "1536x1152",
               "9:16": "864x1536", "16:9": "1536x864"}
OPENAI_STD = {"1:1": "1024x1024", "3:4": "1024x1536", "4:5": "1024x1536", "9:16": "1024x1536",
              "4:3": "1536x1024", "16:9": "1536x1024"}


def agy_bin():
    p = os.environ.get("AGY_BIN") or shutil.which("agy") or os.path.expanduser("~/.local/bin/agy")
    return p if p and os.path.isfile(p) and os.access(p, os.X_OK) else None


def gemini_key():
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")


def detect(check=False):
    out = []
    a = agy_bin()
    if a:
        item = {"provider": "agy", "paid": False, "path": a}
        if check:
            try:
                r = subprocess.run([a, "models"], capture_output=True, text=True, timeout=45)
                item["signed_in"] = r.returncode == 0 and bool(r.stdout.strip())
            except Exception as e:
                item["signed_in"] = False
                item["note"] = e.__class__.__name__
        out.append(item)
    if os.environ.get("OPENAI_API_KEY"):
        out.append({"provider": "openai", "paid": True, "model": os.environ.get("OPENAI_IMAGE_MODEL", "gpt-image-2")})
    if gemini_key():
        out.append({"provider": "gemini", "paid": True, "model": os.environ.get("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image")})
    if os.environ.get("XAI_API_KEY"):
        out.append({"provider": "xai", "paid": True, "model": os.environ.get("XAI_IMAGE_MODEL", "grok-imagine-image-2.0")})
    return out


def sniff(data, default=".png"):
    if data[:3] == b"\xff\xd8\xff":
        return ".jpg"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    return default


def prompt_for(style, subject, ratio):
    parts = [x.strip().rstrip(".") for x in (style, subject) if x and x.strip()]
    if ratio:
        parts.append(f"Aspect ratio {ratio}")
    return ". ".join(parts + [NEGATIVE])


def post_json(url, body, headers, timeout=240):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers=dict({"Content-Type": "application/json"}, **headers))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:400]
        raise RuntimeError(f"HTTP {e.code}: {detail}") from None


def gen_openai(prompt, ratio, model, hires):
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    size = (OPENAI_FREE if model.startswith("gpt-image-2") else OPENAI_STD)[ratio]
    body = {"model": model, "prompt": prompt, "n": 1, "size": size, "quality": "high" if hires else "medium",
            "output_format": "jpeg", "output_compression": 92}
    d = post_json(base + "/images/generations", body, {"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"]})
    return first_image(d)


def first_image(d):
    item = (d.get("data") or [{}])[0]
    if item.get("b64_json"):
        data = base64.b64decode(item["b64_json"])
    elif item.get("url"):
        if not str(item["url"]).startswith("https://"):
            raise RuntimeError("the response's image URL is not https; not fetched")
        with urllib.request.urlopen(item["url"], timeout=120) as r:
            data = r.read(40 * 1024 * 1024)
    else:
        raise RuntimeError("no image in the response")
    ext = sniff(data, "")
    if not ext:
        raise RuntimeError("the response is not a PNG, JPEG, or WebP image")
    return data, ext


def gen_xai(prompt, ratio, model, hires):
    base = os.environ.get("XAI_BASE_URL", "https://api.x.ai/v1").rstrip("/")
    body = {"model": model, "prompt": prompt, "n": 1, "aspect_ratio": XAI_RATIOS.get(ratio, ratio),
            "resolution": "2k" if hires else "1k", "response_format": "b64_json"}
    d = post_json(base + "/images/generations", body, {"Authorization": "Bearer " + os.environ["XAI_API_KEY"]})
    return first_image(d)


def gen_gemini(prompt, ratio, model, hires):
    base = os.environ.get("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1").rstrip("/")
    cfg = {"aspectRatio": ratio}
    if "2.5" not in model:  # imageSize is not accepted by gemini-2.5-flash-image
        cfg["imageSize"] = "2K" if hires else "1K"
    body = {"contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"], "imageConfig": cfg}}
    d = post_json(f"{base}/models/{model}:generateContent", body, {"x-goog-api-key": gemini_key()})
    for cand in d.get("candidates") or []:
        for part in (cand.get("content") or {}).get("parts") or []:
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                mime = inline.get("mimeType") or inline.get("mime_type") or "image/png"
                data = base64.b64decode(inline["data"])
                ext = sniff(data, "")
                if not ext:
                    raise RuntimeError(f"the response is not a PNG, JPEG, or WebP image ({mime})")
                return data, ext
    reason = (d.get("promptFeedback") or {}).get("blockReason") or ((d.get("candidates") or [{}])[0].get("finishReason"))
    raise RuntimeError(f"no image in the response ({reason or 'unknown reason'})")


def append_manifest(outdir, entries):
    path = os.path.join(outdir, "manifest.json")
    data = {"images": []}
    if os.path.exists(path):
        try:
            data = json.load(open(path, encoding="utf-8"))
        except ValueError:
            pass
    data.setdefault("images", []).extend(entries)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


def entry(file, provider, model, ratio, style, subject, prompt, label=None):
    return {"file": os.path.basename(file), "provider": provider, "model": model, "ratio": ratio,
            "style": style, "subject": subject, "prompt": prompt,
            "credit": "Ilustrasi AI",
            "created": datetime.datetime.now().isoformat(timespec="seconds")}


def run_agy(outdir, ratio, style, subjects):
    agy_ratio = "3:4" if ratio == "4:5" else ratio
    r = subprocess.run([os.path.join(HERE, "agy_image.sh"), outdir, agy_ratio, style] + subjects,
                       capture_output=True, text=True)
    sys.stderr.write(r.stderr[-2000:])
    files = [ln.split("\t")[0] for ln in r.stdout.splitlines() if ln.strip() and not ln.startswith("MISSING")]
    model = os.environ.get("AGY_MODEL", "gemini-3.8-flash-low") + " + generate_image"
    entries, ok = [], 0
    for i, subject in enumerate(subjects):
        f = next((x for x in files if x.endswith(f"-{i + 1}.jpg")), None)
        if f and os.path.exists(f):
            ok += 1
            entries.append(entry(f, "agy", model, agy_ratio, style, subject, prompt_for(style, subject, agy_ratio)))
    return entries, ok


def run_api(provider, outdir, ratio, style, subjects, model, hires):
    fn = {"openai": gen_openai, "gemini": gen_gemini, "xai": gen_xai}[provider]
    stamp = datetime.datetime.now().strftime("%H%M%S")

    sent = XAI_RATIOS.get(ratio, ratio) if provider == "xai" else ratio  # the ratio the API is asked for

    def one(i_subject):
        i, subject = i_subject
        p = prompt_for(style, subject, sent)
        try:
            data, ext = fn(p, ratio, model, hires)
        except Exception as e:
            print(f"failed {i + 1}: {e}", file=sys.stderr)
            return None
        f = os.path.join(outdir, f"gen-{provider}-{stamp}-{i + 1}{ext}")
        with open(f, "wb") as fh:
            fh.write(data)
        print(f"{f}  {len(data) // 1024} KB")
        return entry(f, provider, model, sent, style, subject, p)

    with ThreadPoolExecutor(max_workers=3) as ex:
        results = list(ex.map(one, enumerate(subjects)))
    entries = [e for e in results if e]
    return entries, len(entries)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("detect", help="list the providers available here (JSON)")
    d.add_argument("--check", action="store_true", help="also ask agy whether it is signed in (slower)")
    m = sub.add_parser("make", help="generate images")
    m.add_argument("outdir")
    m.add_argument("ratio", choices=RATIOS)
    m.add_argument("style")
    m.add_argument("subjects", nargs="+")
    m.add_argument("--provider", default="auto", choices=["auto", "agy", "openai", "gemini", "xai"])
    m.add_argument("--allow-paid", action="store_true", help="the owner allowed paid image APIs (content/setup.md)")
    m.add_argument("--prefer", choices=["openai", "gemini", "xai"], help="paid provider to try first in auto mode")
    m.add_argument("--model", help="override the provider's default model")
    m.add_argument("--hires", action="store_true", help="higher quality or 2K output (costs more)")
    p = sub.add_parser("prompt", help="print the exact prompt per subject, for a host's own image tool")
    p.add_argument("ratio", choices=RATIOS)
    p.add_argument("style")
    p.add_argument("subjects", nargs="+")
    r = sub.add_parser("record", help="add an image made with another tool to the manifest")
    r.add_argument("outdir")
    r.add_argument("file")
    r.add_argument("--label", required=True, help="tool name for the credit, e.g. Grok Imagine, Codex, ChatGPT, Figma AI")
    r.add_argument("--subject", default="")
    r.add_argument("--style", default="")
    r.add_argument("--ratio", default="")
    a = ap.parse_args()

    if a.cmd == "detect":
        print(json.dumps({"providers": detect(a.check)}, indent=1))
        return 0
    if a.cmd == "prompt":
        for i, s in enumerate(a.subjects, 1):
            print(f"{i}. {prompt_for(a.style, s, a.ratio)}")
        return 0
    if a.cmd == "record":
        if not os.path.isfile(a.file):
            print(f"{a.file} not found", file=sys.stderr)
            return 2
        os.makedirs(a.outdir, exist_ok=True)
        dst = os.path.join(a.outdir, os.path.basename(a.file))
        if os.path.abspath(a.file) != os.path.abspath(dst):
            shutil.copy(a.file, dst)
        prompt = prompt_for(a.style, a.subject, a.ratio) if a.subject else ""
        append_manifest(a.outdir, [entry(dst, "host:" + a.label, a.label, a.ratio, a.style, a.subject, prompt, a.label)])
        print(f"recorded {dst}: Ilustrasi AI ({a.label} in the manifest)")
        return 0

    found = {x["provider"]: x for x in detect()}
    if a.provider == "auto":
        order = ["agy"] + ([a.prefer] if a.prefer else []) + ["openai", "gemini", "xai"]
        order = [x for i, x in enumerate(order) if x not in order[:i]]
        usable = [x for x in order if x in found and (x not in PAID or a.allow_paid)]
        if not usable:
            paid_here = [x for x in found if x in PAID]
            if paid_here:
                print(f"only paid providers here ({', '.join(paid_here)}): ask the owner, record it in content/setup.md, "
                      "then pass --allow-paid; or use Unsplash", file=sys.stderr)
                return 4
            print("no image provider here (agy, OPENAI_API_KEY, GEMINI_API_KEY, XAI_API_KEY): use the agent's own "
                  "image tool with `prompt` and `record`, or Unsplash", file=sys.stderr)
            return 3
    else:
        usable = [a.provider]
        if a.provider not in found:
            print(f"{a.provider} is not available here", file=sys.stderr)
            return 3
        if a.provider in PAID and not a.allow_paid:
            print(f"{a.provider} is paid per image: needs the owner's permission (content/setup.md) and --allow-paid",
                  file=sys.stderr)
            return 4

    os.makedirs(a.outdir, exist_ok=True)
    outdir = os.path.abspath(a.outdir)
    todo, used, made = list(a.subjects), [], 0
    # auto mode: subjects a provider failed on (agy not signed in, a refusal) go to the next allowed one
    for provider in usable:
        if not todo:
            break
        print(f"{provider}: {len(todo)} image(s), ratio {a.ratio} -> {outdir}", file=sys.stderr)
        if provider == "agy":
            entries, ok = run_agy(outdir, a.ratio, a.style, todo)
        else:
            # --model belongs to the provider asked for, not to the ones auto mode falls through to
            mine = a.provider == provider or (a.provider == "auto" and a.prefer == provider)
            model = a.model if (a.model and mine) else found[provider]["model"]
            entries, ok = run_api(provider, outdir, a.ratio, a.style, todo, model, a.hires)
        if entries:
            append_manifest(outdir, entries)
            used.append(provider)
            made += ok
            done = {e["subject"] for e in entries}
            todo = [s for s in todo if s not in done]
    print(json.dumps({"providers": used, "made": made, "asked": len(a.subjects), "failed": todo,
                      "credits": ["Ilustrasi AI"] if used else [],
                      "manifest": os.path.join(outdir, "manifest.json")}, ensure_ascii=False))
    return 0 if not todo else 1


if __name__ == "__main__":
    sys.exit(main())
