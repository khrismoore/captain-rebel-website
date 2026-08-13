# HANDOFF — Captain Rebel Website

> Drop this file (or the whole repo) into a new Claude / Claude Code / Cowork / Dispatch
> session and it can pick up exactly where the last session left off. No prior context needed.

---

## 1. What this project is

A Web3-styled redesign of **captainrebelclothing.com** (currently a Shopify store).
It's a single self-contained landing/shop page — no build step, no framework, no server
required to view. Aesthetic is matched to the FW-25 apparel: dark asphalt, liquid chrome,
rebel red (`#ff2e2e`) and caution yellow (`#ffd400`).

**Live reference site:** https://captainrebelclothing.com/collections/all

---

## 2. Current state — DONE

- [x] Full page built in `index.html` (~697 lines, styles + JS inline)
- [x] ~~New logo asset: chrome `CR` badge~~ **SUPERSEDED 2026-08-12 — see "The mark" below.**
      The CR monogram was wrong; the real Captain Rebel mark is the **chain**.
- [x] Loading screen: real image-preload progress + chrome sweep + percent counter + clip-path wipe
- [x] 3D spinning chrome coin (Three.js r128) in the hero — PMREM studio env map for real
      metallic reflections, badge engraved via canvas roughness/bump maps, red+yellow rim lights,
      mouse parallax, 2D fallback if WebGL is unavailable
- [x] Web3 UI: glassmorphic sticky header, film grain, animated chrome gradient type, ticker
      marquee, serial-numbered "minted" product cards (CR-001/017) with holographic cursor shine +
      tilt, magnetic buttons, custom cursor, scroll reveals
- [x] All 17 real products wired: live Shopify CDN imagery + links to product pages and cart,
      filterable by hoodie / tee / bottoms
- [x] Mobile + desktop responsive; `prefers-reduced-motion` respected
- [x] Git history: `7853704` (build) + `e757d2c` (handoff), merged into `main`
- [x] **Pushed to GitHub and deployed to Pages** — 2026-08-12

**Repo:** https://github.com/khrismoore/captain-rebel-website (public)
**Live:** https://khrismoore.github.io/captain-rebel-website/
**Repo HEAD:** `8b97f99` — merge of the chrome redesign into the repo scaffold

### Verified on 2026-08-12
Confirmed by direct check, not assumption:
- Pages build `built` from commit `8b97f99` in 42.8s, no error
- Live URL returns HTTP 200; `assets/cr-mark.svg` and `favicon.svg` both 200
- All 17 `PRODUCTS` entries present in the served HTML
- Three.js r128 loads (CDN 200) and a WebGL context is available
- Shopify CDN product images return 200

**NOT yet verified by anyone:** the loader completing, the 3D coin actually
rendering, and the animations. These were checked in a headless pane where
`requestAnimationFrame` never fired (0 frames, viewport width 0), so the result
proves nothing either way. **Open the live URL in a real browser to confirm.**

---

## 3. File map

```
captain-rebel/
├── index.html          # THE site — all HTML/CSS/JS inline. Only external dep: Three.js via CDN.
├── assets/
│   └── cr-mark.svg     # standalone chrome CR badge logo
├── favicon.svg         # favicon copy of the mark
├── README.md           # run + deploy instructions
├── HANDOFF.md          # this file
└── .gitignore
```

### Where to edit things (all inside `index.html`)
- **Products** → `const PRODUCTS = [...]` near the top of the `<script>`. Each entry:
  `{n:name, p:price, c:category('hoodie'|'tee'|'bottoms'), u:shopify-handle, i:cdn-image-path}`.
- **The 3D chain** → `const CHAIN` (contour data) then `shapes` → `ExtrudeGeometry`.
  `makeBadgeCanvas()` and the coin's `CylinderGeometry`/`CircleGeometry` are **gone**.
- **Chain material / spin / lights** → same block (search `chainMesh`, `spin`, rim lights `redL`/`yelL`).
- **Loader timing/behavior** → the `/* loader */` block (`PRELOAD`, `tickLoader()`).
- **Colors** → CSS `:root` variables at the very top of `<style>`.
- **Fonts** → Unbounded (display), Space Grotesk (body), Space Mono (utility), via Google Fonts `<link>`.

---

## 4. NEXT STEPS — what to do in the new session

### A. ~~Get it on GitHub~~ — DONE 2026-08-12
Repo is public at https://github.com/khrismoore/captain-rebel-website and Pages
is serving `main` / root at https://khrismoore.github.io/captain-rebel-website/.
Pushing to `main` redeploys automatically — no further setup.

To pick this up on another machine:
```bash
git clone https://github.com/khrismoore/captain-rebel-website.git
```
The repo IS the handoff — clone it, read this file, you have full context.

### B. Preview locally
```bash
python -m http.server 8137
# then http://localhost:8137/index.html
```
For phone-on-same-Wi-Fi, use the machine's LAN IP instead of localhost. On Khris's
PC a VPN (NordVPN) is often active and will block LAN access — turn it off first.
Simplest option now that Pages is live: just open the live URL on the phone.

### C. FIRST THING NEXT SESSION — confirm the visuals
Nobody has yet watched the loader finish or seen the 3D coin spin. Load the live
URL in a real browser and check:
- [ ] Loader counts past `000%` and wipes away (it stalls at 000% in headless)
- [ ] Chrome coin renders and spins in the hero
- [ ] Product images load from the Shopify CDN
- [ ] Mobile layout holds up

### D. Open ideas / possible follow-ups (not yet done)
- [ ] Add a real "Mint / Add to cart" button that deep-links into Shopify checkout
- [ ] Wire the cart count to the live Shopify cart (currently static `(0)`)
- [ ] Second page: full lookbook gallery matching the chrome theme
- [ ] Product hover: quick-view modal instead of link-out
- [ ] Swap Three.js CDN for a pinned local copy so the coin works fully offline
- [ ] Optional: tune coin spin speed / chrome tint per brand feedback

---

## 4b. THE MARK — read this before touching the logo

**The Captain Rebel mark is a CHAIN — two interlocking open C-links on a ~35° diagonal.**
It is NOT a "CR" monogram. An earlier session invented a CR badge and shipped it in every
logo slot; Khris caught it and it has been reverted.

- **Source of truth:** the store's own animated logo,
  `https://captainrebelclothing.com/cdn/shop/files/3dgifmaker78319.gif` — 391×391, 150 frames.
  Frame 0 is face-on. Frame 38 is a thin vertical line, which proves the mark is a **flat
  plane spinning on its vertical axis** — that is the brand's canonical motion.
- **How the vector was made:** auto-traced from that GIF (marching squares → RDP →
  Catmull-Rom → cubic bezier), **not redrawn by eye**. Measured **95.4% IoU** against the
  source bitmap, 1.5% missed / 3.3% added, all of it sub-pixel edge halo.
- **Two closed contours, no holes** — the links are open "C" shapes, so each is
  simply-connected. Do not add `fill-rule="evenodd"`; it is not needed and will break them.

Where it lives now:
- `#cr-badge` in the inline `<defs>` — **one definition, five `<use>` sites** (loader,
  header logo, WebGL fallback, manifesto stamp, footer). Edit the def, not the five uses.
- `#markClip` — the same two paths as a clipPath. The loader's shine sweep is clipped to
  the mark itself. It used to be clipped to a circle, which only worked because the old
  badge was a filled disc; on the chain a circular clip leaks the sweep into empty space.
- `assets/cr-mark.svg` and `favicon.svg` — standalone copies (favicon has the dark bg).
- `const CHAIN` in the script — the same contours as flat `[x,y,...]` arrays in world
  units, fed to `THREE.Shape` → `ExtrudeGeometry`. **Regenerate all four together** if the
  mark ever changes, or they will drift apart.

**Verified 2026-08-12** by building the geometry headlessly against the real three r128:
24,232 triangles, 0 NaN positions/normals, 4 degenerate tris (0.02%), surface area 24.0,
bbox 4.010 × 3.162 × 0.410. Still **not** visually confirmed spinning in a real browser.

## 4c. IMAGERY — all 17 products are local cut-outs on black

Every Shopify product shot sits on a **pure white (255,255,255) studio background**, so
they read as white slabs on this site's black. No CSS blend mode can fix that without
wrecking the garment colours, so the background is keyed out ahead of time.

- **`assets/products/cr-01..17.webp`** — transparent, max 1000px, ~1.1 MB for all 17.
  Numbering matches the serials: `cr-07.webp` is CR-007.
- **Regenerate with `python tools/make-cutouts.py --sheet`.** The script is in the repo
  and reads `CDN` + the `i:` fields out of `index.html` — that is why those stay even
  though the page no longer loads imagery from the CDN.
- Grid and lookbook share ONE set via `IMG(i)`. There is no second copy to drift.
- **The page no longer auto-follows store imagery.** Change a product photo on Shopify
  and you must re-run the tool.

### Two traps that already bit once — do not re-introduce them

**1. The white cut MUST stay strict (250).** CR-011 is a white tee on white and CR-009 is
close. At a loose 236 cut the fill walks through the garment and deletes it — both shipped
at ~14% opaque before this was caught. Measured:

| cut | white tee subject | black hoodie (control) |
|---|---|---|
| 236 | **13.9%** — shirt destroyed | 18.1% |
| 244 | 44.1% — leak closed | 18.2% |
| 250 | 44.3% — plateau | 18.5% |

So: flood-fill at **250** for topology, then grow the background a **bounded 3px** into
near-white (236) to clean the soft edge. The bound is what stops it eating a garment.

**2. CR-014 is an SVG, not a photo.** `yellow_hoodie_*.svg` is a 3.8 MB Affinity export
(`xmlns:serif`) holding **two** embedded rasters: a leftover 3068×2855 white-tee JPEG
underneath, and the real 1264×1220 yellow hoodie PNG on top. Take the **last** one — SVG
paint order puts the topmost layer last. Taking the first (or the largest) silently ships
the wrong garment, which is exactly what happened.

The script prints a `subject=%` per image and flags anything outside 8–95% as SUSPECT,
and `--sheet` writes `assets/products/_contact.png` (gitignored) to eyeball all 17 on
black. **Look at the sheet after regenerating** — a wrong-but-plausible cut-out will not
trip the numeric check.

### Treatment
Both sections put the garment on `#000` with an ambient halo tinted to its own colour
(`PGLOW`, one table indexed by product). Lookbook adds a faded chrome grid floor, a
blurred conic holographic wash on hover, scanlines, cursor-tracked sheen, RGB-split
drop-shadow, staggered float, and token-style metadata (`Look 01 / 07`, garment name, a
stable FNV-1a hash of the handle, `1 / 1`). Motion respects `prefers-reduced-motion`.
The hash is decorative — it is **not** on any chain.

## 5. Gotchas / things that weren't obvious
- The hero `<h1>` is visually hidden (`.sr-only`) with the animated chrome word-art marked
  `aria-hidden` — keeps it accessible without duplicating the display type. Don't "fix" the
  empty-looking h1; it's intentional.
- Three.js is **r128** specifically. `THREE.CapsuleGeometry` and `OrbitControls` are NOT
  available in r128 — the coin uses `CylinderGeometry` + `CircleGeometry` on purpose.
- Product images come straight from `captainrebelclothing.com/cdn/...`. If a product handle or
  image version (`?v=...`) changes on the live store, update the matching `PRODUCTS` entry.
- No localStorage/sessionStorage anywhere (not supported in some sandboxes) — all state is in-memory.
- The whole thing runs from `file://` — you can literally double-click `index.html`.

---

## 6. One-line summary for the next session
> "Continue the Captain Rebel chrome/web3 site. Everything's in `index.html` (self-contained).
>  Repo is public at github.com/khrismoore/captain-rebel-website, HEAD `8b97f99`, live on Pages
>  at khrismoore.github.io/captain-rebel-website. FIRST: eyeball the live site — the loader and
>  3D coin have never been visually confirmed by a human. Then optionally wire the live Shopify
>  cart and add a lookbook page. Read section 3 for where to edit what."
