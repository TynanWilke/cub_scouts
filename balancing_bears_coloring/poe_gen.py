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
    "Black and white coloring page line art for young children (ages 6-8). "
    "Full body of a {animal}, facing the viewer, centered, plain solid white background. "
    "Thick clean uniform black outlines only, closed shapes, bold cartoon style, "
    "friendly round eyes and a gentle smile. "
    "NO shading, NO gray fills, NO hatching, NO texture, NO color anywhere. "
    "The body must be mostly large EMPTY blank areas so kids can draw their own "
    "patterns on it - do not draw stripes, spots, scales or any pattern on the body. "
    "Very simple shapes, not realistic, not detailed. "
    "No text, no words, no border, no frame, no background scenery, no ground."
)

ANIMALS = {
    "frog": "cute happy frog sitting with legs tucked",
    "zebra": "cute zebra standing in side view with its head turned toward the viewer",
    "butterfly": "cute butterfly with wings spread wide open, seen from above",
    "snake": "cute friendly snake curled in a loose S shape with its head raised",
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
    only = sys.argv[1:] or list(ANIMALS)
    key = load_key()
    os.makedirs(OUT_DIR, exist_ok=True)
    for name in only:
        out = os.path.join(OUT_DIR, f"{name}.png")
        if os.path.exists(out) and "--force" not in sys.argv:
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
