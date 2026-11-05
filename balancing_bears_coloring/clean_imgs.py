#!/usr/bin/env python3
"""Whiten near-white PNG backgrounds to pure white and trim excess margins.

The Poe PNGs have slightly off-white backgrounds which show as visible
rectangle edges on the printed PDF. This maps near-white pixels to pure
white and crops the empty margin so animals fill their cells.
"""
import os
from PIL import Image, ImageChops

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
DST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img_clean")
os.makedirs(DST, exist_ok=True)

THRESHOLD = 238  # anything this light becomes pure white

for name in sorted(os.listdir(SRC)):
    if not name.endswith(".png"):
        continue
    im = Image.open(os.path.join(SRC, name)).convert("L")
    # push near-white to pure white
    im = im.point(lambda p: 255 if p >= THRESHOLD else p)
    # trim remaining white margins
    bg = Image.new("L", im.size, 255)
    bbox = ImageChops.difference(im, bg).getbbox()
    if bbox:
        pad = 12
        l, t, r, b = bbox
        im = im.crop((max(0, l - pad), max(0, t - pad),
                      min(im.width, r + pad), min(im.height, b + pad)))
    im.convert("RGB").save(os.path.join(DST, name))
    print(f"{name}: {im.size} -> {DST}/{name}")
