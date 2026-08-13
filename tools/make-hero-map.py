#!/usr/bin/env python3
"""Generate assets/hero-map.svg — the faded nautical chart behind the hero.

    python tools/make-hero-map.py [--seed N] [--preview]

Builds a fractal heightfield, then pulls real iso-contours out of it with
marching squares. That is what makes it read as a *map* rather than a texture:
the coastline is a genuine sea-level contour, mountain ranges emerge where
contours bunch together on steep ground, and the bathymetric rings nest inside
each other the way depth soundings actually do.

Deterministic for a given --seed, so the committed SVG is reproducible.
Requires: pillow, numpy.
"""
import argparse
import math
import os

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "hero-map.svg")

W, H = 2400, 1050          # svg viewBox
GW, GH = 300, 132          # heightfield resolution
SEA = 0.50
LAND_STEP, LAND_LEVELS = 0.042, 6
DEEP_STEP, DEEP_LEVELS = 0.048, 3
RDP_EPS = 0.9              # in viewBox units
MIN_PTS = 5                # drop contour scraps shorter than this


def fbm(gh, gw, octaves, rng, ridged=False):
    total = np.zeros((gh, gw), dtype=np.float64)
    amp, norm = 1.0, 0.0
    for o in range(octaves):
        ch, cw = max(2, 3 * 2 ** o), max(2, 6 * 2 ** o)
        g = rng.random((ch, cw))
        up = np.asarray(Image.fromarray((g * 255).astype(np.uint8))
                        .resize((gw, gh), Image.BICUBIC), dtype=np.float64) / 255.0
        if ridged:
            up = 1.0 - np.abs(2.0 * up - 1.0)
        total += up * amp
        norm += amp
        amp *= 0.52
    return total / norm


def heightfield(seed):
    rng = np.random.default_rng(seed)
    base = fbm(GH, GW, 6, rng)
    ridge = fbm(GH, GW, 5, rng, ridged=True)
    # continents from the smooth field, mountain ranges from the ridged one
    h = base * 0.72 + ridge * 0.28
    # push the frame edges under water so landmasses do not run off the canvas
    yy, xx = np.mgrid[0:GH, 0:GW]
    fx = np.minimum(xx, GW - 1 - xx) / (GW * 0.16)
    fy = np.minimum(yy, GH - 1 - yy) / (GH * 0.16)
    edge = np.clip(np.minimum(fx, fy), 0, 1)
    h = h * (0.35 + 0.65 * edge) + (edge - 1) * 0.10
    h -= h.min()
    h /= h.max()
    return h


def contours(field, level):
    """Marching squares with linear interpolation -> list of polylines."""
    gh, gw = field.shape
    segs = []
    f = field
    for y in range(gh - 1):
        for x in range(gw - 1):
            a, b = f[y, x], f[y, x + 1]
            c, d = f[y + 1, x + 1], f[y + 1, x]
            idx = (a >= level) << 3 | (b >= level) << 2 | (c >= level) << 1 | (d >= level)
            if idx in (0, 15):
                continue
            def ip(p, q, vp, vq):
                t = 0.5 if vq == vp else (level - vp) / (vq - vp)
                return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
            T = ip((x, y), (x + 1, y), a, b)
            R = ip((x + 1, y), (x + 1, y + 1), b, c)
            B = ip((x, y + 1), (x + 1, y + 1), d, c)
            L = ip((x, y), (x, y + 1), a, d)
            tbl = {1: [(L, B)], 2: [(B, R)], 3: [(L, R)], 4: [(T, R)], 6: [(T, B)],
                   7: [(L, T)], 8: [(T, L)], 9: [(T, B)], 11: [(T, R)], 12: [(R, L)],
                   13: [(B, R)], 14: [(L, B)], 5: [(L, T), (B, R)], 10: [(T, R), (L, B)]}
            segs.extend(tbl[idx])

    key = lambda p: (round(p[0], 4), round(p[1], 4))
    adj = {}
    for s in segs:
        adj.setdefault(key(s[0]), []).append(s)
        adj.setdefault(key(s[1]), []).append(s)
    used, lines = set(), []
    for s in segs:
        if id(s) in used:
            continue
        used.add(id(s))
        line = [s[0], s[1]]
        for end in (1, 0):                       # walk forward, then backward
            while True:
                cur = line[-1] if end else line[0]
                nxt = None
                for cand in adj.get(key(cur), []):
                    if id(cand) in used:
                        continue
                    nxt = cand
                    break
                if nxt is None:
                    break
                used.add(id(nxt))
                other = nxt[1] if key(nxt[0]) == key(cur) else nxt[0]
                if end:
                    line.append(other)
                else:
                    line.insert(0, other)
            if end:
                line.reverse()
        line.reverse()
        if len(line) >= MIN_PTS:
            lines.append(line)
    return lines


def rdp(pts, eps):
    """Iterative Ramer-Douglas-Peucker.

    Two things matter here and both bit once:
    - Contours are CLOSED rings, so pts[0] == pts[-1] and the baseline has zero
      length. With the usual point-to-line formula every point then measures a
      distance of 0 and the whole ring collapses to two identical points. When
      the baseline is degenerate, measure point-to-point instead.
    - Coastlines run to ~1100 points, deep enough to blow the recursion limit,
      hence the explicit stack.
    """
    n = len(pts)
    if n < 3:
        return list(pts)
    keep = [False] * n
    keep[0] = keep[n - 1] = True
    stack = [(0, n - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1:
            continue
        x1, y1 = pts[i]
        x2, y2 = pts[j]
        dx, dy = x2 - x1, y2 - y1
        den = math.hypot(dx, dy)
        degenerate = den < 1e-12
        dmax, idx = -1.0, -1
        for k in range(i + 1, j):
            px, py = pts[k]
            dist = (math.hypot(px - x1, py - y1) if degenerate
                    else abs(dy * px - dx * py + x2 * y1 - y2 * x1) / den)
            if dist > dmax:
                dmax, idx = dist, k
        if dmax > eps and idx > i:
            keep[idx] = True
            stack.append((i, idx))
            stack.append((idx, j))
    return [p for p, k in zip(pts, keep) if k]


def to_d(line, sx, sy):
    pts = [(p[0] * sx, p[1] * sy) for p in line]
    pts = rdp(pts, RDP_EPS)
    if len(pts) < 2:
        return None
    closed = math.dist(pts[0], pts[-1]) < 1.2
    if closed:
        pts = pts[:-1]
        if len(pts) < 3:
            return None
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}" + "".join(
        f"L{x:.1f} {y:.1f}" for x, y in pts[1:])
    return d + ("Z" if closed else "")


def build(seed):
    f = heightfield(seed)
    sx, sy = W / (GW - 1), H / (GH - 1)
    groups = []

    deep = []
    for k in range(1, DEEP_LEVELS + 1):
        for ln in contours(f, SEA - k * DEEP_STEP):
            d = to_d(ln, sx, sy)
            if d:
                deep.append(d)
    groups.append(("deep", deep, "#8fa0b8", 0.16, 1.0, "6 9"))

    coast = [d for ln in contours(f, SEA) if (d := to_d(ln, sx, sy))]
    groups.append(("coast", coast, "#dfe6f2", 0.42, 1.6, None))

    land = []
    for k in range(1, LAND_LEVELS + 1):
        for ln in contours(f, SEA + k * LAND_STEP):
            d = to_d(ln, sx, sy)
            if d:
                land.append(d)
    groups.append(("relief", land, "#c8cedb", 0.22, 1.0, None))

    return groups


def svg(groups):
    grat = []
    for i in range(1, 16):
        x = W * i / 16
        grat.append(f'<path d="M{x:.0f} 0L{x:.0f} {H}"/>')
    for i in range(1, 8):
        y = H * i / 8
        grat.append(f'<path d="M0 {y:.0f}L{W} {y:.0f}"/>')

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'preserveAspectRatio="xMidYMid slice" role="img" '
        f'aria-label="Faded nautical chart">',
        '<g fill="none" stroke-linejoin="round" stroke-linecap="round">',
        # graticule first, so contours sit on top of it
        f'<g stroke="#f4f5f8" stroke-width="1" opacity=".07">{"".join(grat)}</g>',
    ]
    for name, paths, color, op, sw, dash in groups:
        if not paths:
            continue
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<g id="{name}" stroke="{color}" stroke-width="{sw}" '
                   f'opacity="{op}"{dash_attr}>')
        out.extend(f'<path d="{d}"/>' for d in paths)
        out.append("</g>")
    out.append("</g></svg>")
    return "".join(out)


def preview(groups, path):
    from PIL import ImageDraw
    im = Image.new("RGB", (W // 2, H // 2), (8, 8, 10))
    dr = ImageDraw.Draw(im)
    style = {"deep": (44, 54, 68), "coast": (150, 162, 180), "relief": (86, 94, 108)}
    for name, paths, *_ in groups:
        col = style[name]
        for d in paths:
            nums = [float(v) for v in d.replace("M", " ").replace("L", " ")
                    .replace("Z", " ").split()]
            pts = [(nums[i] / 2, nums[i + 1] / 2) for i in range(0, len(nums) - 1, 2)]
            if len(pts) > 1:
                dr.line(pts, fill=col, width=1)
    im.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--preview", action="store_true")
    a = ap.parse_args()

    groups = build(a.seed)
    for name, paths, *_ in groups:
        print(f"  {name:7} {len(paths):5} paths")
    s = svg(groups)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(s)
    print(f"\nseed={a.seed}  ->  {OUT}  ({len(s)/1024:.0f} KB)")
    if a.preview:
        p = os.path.join(os.path.dirname(OUT), "_hero-map-preview.png")
        preview(groups, p)
        print(f"preview: {p}")


if __name__ == "__main__":
    main()
