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
- [x] New logo asset: chrome `CR` badge, hand-drawn SVG (`assets/cr-mark.svg`) — replaces the
      old low-res GIF. Reused in header (top-middle), loader, footer, favicon, and 3D coin.
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
- [x] Git initialized, one commit on `main`

**Repo HEAD:** `7853704` — "Captain Rebel chrome redesign: 3D spinning chrome logo, custom loader, web3 UI"

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
- **3D coin engraving** → `makeBadgeCanvas()` function (draws CR monogram, star, ring text, reeded edge).
- **Coin material / spin / lights** → the `/* 3D CHROME COIN */` block (search `chrome =`, `spin`, rim lights `redL`/`yelL`).
- **Loader timing/behavior** → the `/* loader */` block (`PRELOAD`, `tickLoader()`).
- **Colors** → CSS `:root` variables at the very top of `<style>`.
- **Fonts** → Unbounded (display), Space Grotesk (body), Space Mono (utility), via Google Fonts `<link>`.

---

## 4. NEXT STEPS — what to do in the new session

### A. Get it on GitHub (this becomes the durable handoff)
```bash
# from the unzipped project folder
git remote add origin https://github.com/<YOUR-USERNAME>/captain-rebel-website.git
git branch -M main
git push -u origin main
```
Then enable **Settings → Pages → Deploy from branch → main / root**.
Live URL: `https://<YOUR-USERNAME>.github.io/captain-rebel-website/` (opens on any phone/desktop).

> Note: this file already lists `HANDOFF.md` in the repo, so once pushed, ANY future session
> just clones the repo and reads this to get full context. The repo IS the handoff.

### B. Preview locally + reach it from your phone (same Wi-Fi)
```bash
npx serve .
# open the printed http://192.168.x.x:PORT address on your phone
```

### C. Open ideas / possible follow-ups (not yet done)
- [ ] Add a real "Mint / Add to cart" button that deep-links into Shopify checkout
- [ ] Wire the cart count to the live Shopify cart (currently static `(0)`)
- [ ] Second page: full lookbook gallery matching the chrome theme
- [ ] Product hover: quick-view modal instead of link-out
- [ ] Swap Three.js CDN for a pinned local copy so the coin works fully offline
- [ ] Optional: tune coin spin speed / chrome tint per brand feedback

---

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
>  Repo is committed at HEAD 7853704. Next: push to GitHub + enable Pages, then optionally wire
>  the live Shopify cart and add a lookbook page. Read section 3 for where to edit what."
