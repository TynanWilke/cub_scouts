#!/usr/bin/env python3
"""Generate 4 consistent black-and-white coloring-page animals via Poe.

Secret handling: the Poe API key is read from /etc/tw-pa/env inside this
script; it never appears in source or argv.
"""
import json
import os
import re
import sys
import urllib.request

POE_URL = "https://api.poe.com/v1/chat/completions"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")

STYLE = (
    "Black and white coloring page line art of a REAL animal as it looks in nature. "
    "Naturalistic, true-to-life anatomy, proportions and body shape - accurate to the "
    "real species, like a good natural-history field-guide ink drawing. "
    "NOT a cartoon, NOT cute or chibi, no big eyes, no smiling face, no human-like expression. "
    "Full body of a {animal}, centered, plain solid white background. "
    "Clean uniform black outlines of the animal's true silhouette and major body parts "
    "(head, limbs, tail, wings) - and NOTHING else on the body: no shading, no gray fills, "
    "no hatching, no fur or scale texture, no color anywhere. "
    "The body must be large EMPTY blank areas so kids can draw their own patterns on it - "
    "do not draw stripes, spots, scales or any pattern. "
    "No text, no words, no border, no frame, no background scenery, no ground."
)

ANIMALS = {
    "frog": "a frog sitting upright on its haunches with front legs braced, seen from the front",
    "zebra": "a plains zebra standing in full side view",
    "butterfly": "a monarch butterfly with wings spread flat, seen from above",
    "snake": "a snake coiled in loose S-curves with its head raised, seen from the side",
}


def load_key() -> str:
    import subprocess

    # /etc/tw-pa/env is root-owned; try passwordless sudo first, then the
    # 1Password vault (the sanctioned source of truth).
    try:
        out = subprocess.run(
            ["sudo", "-n", "cat", "/etc/tw-pa/env"],
            capture_output=True, text=True, timeout=15,
        )
        text = out.stdout if out.returncode == 0 else ""
    except Exception:
        text = ""
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("POE_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")

    env = dict(os.environ)
    env["XDG_CONFIG_HOME"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".opcfg")
    os.makedirs(env["XDG_CONFIG_HOME"], exist_ok=True)
    out = subprocess.run(
        ["op", "read", "op://Assistant Allowed/poe.com API Key/credential"],
        capture_output=True, text=True, timeout=30, env=env,
    )
    if out.returncode != 0:
        raise RuntimeError(f"could not load Poe key: {out.stderr[:200]}")
    return out.stdout.strip()


def poe_image(prompt: str, key: str, timeout: int = 240) -> bytes:
    payload = {
        "model": "gpt-image-2",
        "messages": [{"role": "user", "content": prompt}],
        "parameters": {"size": "1024x1024", "quality": "high"},
    }
    req = urllib.request.Request(
        POE_URL,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "X-Title": "Balancing Bears coloring sheet",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = json.loads(resp.read().decode())
    text = body["choices"][0]["message"]["content"]
    urls = re.findall(r"https?://[^\s)\]\"'<>]+", text)
    for u in urls:
        if "poecdn.net" in u or re.search(r"\.(png|jpe?g|webp)(\?|$)", u):
            img_url = u.rstrip(".,;")
            break
    else:
        raise RuntimeError(f"no image URL in reply: {text[:200]}")
    with urllib.request.urlopen(
        urllib.request.Request(img_url, headers={"User-Agent": "coloring/1.0"}),
        timeout=120,
    ) as resp:
        return resp.read()


def main() -> None:
    args = [a for a in sys.argv[1:] if a != "--force"]
    force = "--force" in sys.argv
    only = args or list(ANIMALS)
    key = load_key()
    os.makedirs(OUT_DIR, exist_ok=True)
    for name in only:
        out = os.path.join(OUT_DIR, f"{name}.png")
        if os.path.exists(out) and not force:
            print(f"{name}: exists, skip")
            continue
        prompt = STYLE.format(animal=ANIMALS[name])
        print(f"{name}: generating...", flush=True)
        data = poe_image(prompt, key)
        with open(out, "wb") as fh:
            fh.write(data)
        print(f"{name}: saved {len(data)} bytes -> {out}", flush=True)


if __name__ == "__main__":
    main()
