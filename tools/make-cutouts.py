#!/usr/bin/env python3
"""Regenerate assets/products/cr-NN.webp — transparent cut-outs of every product.

The Shopify product shots sit on a pure white studio background, which reads as
white slabs on this site's black. This keys the background out.

    python tools/make-cutouts.py            # all products
    python tools/make-cutouts.py --sheet    # also write a review contact sheet

WHY THE THRESHOLD IS STRICT (250, not "near white"):
CR-011 is a WHITE t-shirt on white and CR-009 is close to it. At a loose cut
(236) the fill walks straight through the garment body and deletes the shirt —
both came out ~14% opaque before this was fixed. Measured sweep:

    cut>=236  white tee subject 13.9%   <- shirt destroyed
    cut>=244  white tee subject 44.1%   <- leak closed
    cut>=250  white tee subject 44.3%   <- plateau  (black hoodie only 18.1->18.5)

So: flood-fill at 250 to get the topology right, THEN grow the background a
bounded 3px into merely-near-white (236) to clean the soft edge. The growth is
bounded precisely so it can never travel far enough to eat a garment again.

Re-run this whenever a product photo changes on the store — the site serves these
local copies, so it will NOT pick up new Shopify imagery on its own.

Requires: pillow, numpy.
"""
import base64
import io
import os
import re
import sys
import urllib.request

import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, "index.html")
OUT = os.path.join(ROOT, "assets", "products")

MAXDIM = 1000      # longest edge of the emitted webp
WHITE_CUT = 250    # strict: decides what the flood fill may travel through
HALO_CUT = 236     # looser: soft-edge pixels the background may grow into
HALO_STEPS = 3     # bounded growth, in pixels
QUALITY = 88

# a subject this small/large almost certainly means the key went wrong
MIN_SUBJECT, MAX_SUBJECT = 0.08, 0.95


def fetch(url):
    """Return a PIL image. Some products are SVGs wrapping embedded rasters.

    CR-014 (Party Hoodie — Yellow) is an Affinity export (xmlns:serif) holding
    TWO images: a leftover 3068x2855 white-tee JPEG underneath, and the actual
    1264x1220 yellow hoodie PNG on top. Take the LAST one — SVG paint order puts
    the topmost layer last. Picking the first (or the largest) yields the wrong
    garment, which is exactly what happened before this was fixed.
    """
    raw = urllib.request.urlopen(url, timeout=90).read()
    if raw[:5] in (b"<?xml", b"<svg ") or b"<svg" in raw[:512]:
        text = raw.decode("utf-8", "replace")
        hits = re.findall(
            r'(?:xlink:)?href="data:image/\w+;base64,([A-Za-z0-9+/=\s]+)"', text)
        if not hits:
            raise ValueError("SVG with no embedded raster")
        data = base64.b64decode(re.sub(r"\s+", "", hits[-1]))
        return Image.open(io.BytesIO(data)), f"svg[{len(hits)}]"
    return Image.open(io.BytesIO(raw)), "raster"


def flood_bg(passable):
    """True where `passable` connects to the image border. Span fill, 4-connected."""
    h, w = passable.shape
    seen = np.zeros_like(passable)
    stack = []
    for x in range(w):
        if passable[0, x]:
            stack.append((0, x))
        if passable[h - 1, x]:
            stack.append((h - 1, x))
    for y in range(h):
        if passable[y, 0]:
            stack.append((y, 0))
        if passable[y, w - 1]:
            stack.append((y, w - 1))
    while stack:
        y, x = stack.pop()
        if seen[y, x] or not passable[y, x]:
            continue
        xl = x
        while xl - 1 >= 0 and passable[y, xl - 1] and not seen[y, xl - 1]:
            xl -= 1
        xr = x
        while xr + 1 < w and passable[y, xr + 1] and not seen[y, xr + 1]:
            xr += 1
        seen[y, xl:xr + 1] = True
        for ny in (y - 1, y + 1):
            if 0 <= ny < h:
                row = passable[ny, xl:xr + 1] & ~seen[ny, xl:xr + 1]
                prev = -2
                for i in np.nonzero(row)[0]:
                    if i != prev + 1:
                        stack.append((ny, xl + int(i)))
                    prev = i
    return seen


def grow(bg, allow, steps):
    """Dilate bg by `steps` px, only into `allow`. Bounded so it cannot run away."""
    for _ in range(steps):
        nb = bg.copy()
        nb[1:, :] |= bg[:-1, :]
        nb[:-1, :] |= bg[1:, :]
        nb[:, 1:] |= bg[:, :-1]
        nb[:, :-1] |= bg[:, 1:]
        bg = bg | (nb & allow)
    return bg


def cutout(im):
    im = im.convert("RGB")
    if max(im.size) > MAXDIM:
        s = MAXDIM / max(im.size)
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    a = np.array(im)

    bg = flood_bg(np.all(a >= WHITE_CUT, axis=2))
    bg = grow(bg, np.all(a >= HALO_CUT, axis=2), HALO_STEPS)
    # anything unreachable from the border is subject, even if it is white
    bg = flood_bg(bg)

    af = Image.fromarray(((~bg).astype(np.float32) * 255).astype(np.uint8))
    af = np.array(af.filter(ImageFilter.GaussianBlur(1.0))).astype(np.float32) / 255.0
    af = np.clip((af - 0.5) / 0.4, 0, 1)

    # de-spill: partially transparent edge pixels are mixed with white, unmix them
    rgb = a.astype(np.float32)
    edge = (af > 0.02) & (af < 0.98)
    k = af[..., None]
    rgb[edge] = np.clip(
        (rgb[edge] - 255.0 * (1 - k[edge])) / np.maximum(k[edge], 0.25), 0, 255)

    out = Image.fromarray(
        np.dstack([rgb.astype(np.uint8), (af * 255).astype(np.uint8)]), "RGBA")
    return out, float((af > 0.6).mean())


def main():
    html = open(HTML, encoding="utf-8").read()
    cdn = re.search(r'const CDN\s*=\s*"([^"]+)"', html).group(1)
    names = re.findall(r'\{n:"([^"]+)"', html)
    imgs = re.findall(r'i:"([^"]+)"', html)
    if len(names) != len(imgs):
        sys.exit(f"parse mismatch: {len(names)} names vs {len(imgs)} images")

    os.makedirs(OUT, exist_ok=True)
    print(f"{len(imgs)} products -> {OUT}\n")
    total, bad, tiles = 0.0, [], []
    for i, (nm, rel) in enumerate(zip(names, imgs), start=1):
        src, kind = fetch(cdn + rel)
        cut, cov = cutout(src)
        name = f"cr-{i:02d}.webp"
        path = os.path.join(OUT, name)
        cut.save(path, "WEBP", quality=QUALITY, method=6)
        kb = os.path.getsize(path) / 1024
        total += kb
        ok = MIN_SUBJECT <= cov <= MAX_SUBJECT
        if not ok:
            bad.append((name, nm, cov))
        print(f"  {name}  {nm[:32]:34} {cut.width}x{cut.height} "
              f"{kind:6} subject={cov*100:5.1f}%  {kb:6.1f} KB"
              f"{'' if ok else '   <-- SUSPECT'}")
        if "--sheet" in sys.argv:
            t = Image.new("RGB", cut.size, (0, 0, 0))
            t.paste(cut, (0, 0), cut)
            tiles.append(t)

    print(f"\ntotal {total:.0f} KB across {len(imgs)} files")
    if bad:
        print(f"\n{len(bad)} SUSPECT cut-out(s) — inspect before shipping:")
        for n, nm, c in bad:
            print(f"  {n}  {nm}  subject={c*100:.1f}%")

    if tiles:
        tw, cols = 260, 6
        rows = (len(tiles) + cols - 1) // cols
        sheet = Image.new("RGB", (tw * cols, tw * rows), (0, 0, 0))
        for i, t in enumerate(tiles):
            sheet.paste(t.resize((tw, tw), Image.LANCZOS),
                        ((i % cols) * tw, (i // cols) * tw))
        p = os.path.join(OUT, "_contact.png")
        sheet.save(p)
        print(f"\ncontact sheet: {p}")

    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
