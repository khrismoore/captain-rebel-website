# CAPTAIN REBEL — Chrome Redesign

A Web3-styled redesign concept for [captainrebelclothing.com](https://captainrebelclothing.com), built as a single self-contained page. Dark asphalt, liquid chrome, rebel red and caution yellow — matched to the FW-25 apparel colorways.

## What's inside

| Feature | Detail |
|---|---|
| 3D chrome spinning logo | Three.js coin with a PMREM studio environment map, engraved CR badge (canvas roughness + bump maps), red/yellow rim lights, mouse parallax |
| New logo asset | Hand-drawn `CR` monogram badge SVG (`assets/cr-mark.svg`) replacing the low-res GIF — used in the header, loader, footer, favicon, and as the 3D coin engraving |
| Loading screen | Real image-preload progress with animated chrome sweep, percent counter, and clip-path wipe reveal |
| Web3 techniques | Glassmorphic sticky header, film grain overlay, animated chrome gradient type, holographic cursor-tracked card shine, magnetic buttons, custom cursor, ticker marquee, scroll-reveal, serial-numbered "minted" product cards |
| Live commerce | All 17 products pull real imagery from the Shopify CDN and link to live product pages + cart |
| Responsive | Mobile-first grid, touch-safe interactions, `prefers-reduced-motion` respected, WebGL fallback to 2D spinning badge |

## Run it

No build step. Open `index.html` in a browser, or serve it:

```bash
npx serve .
```

## Deploy to GitHub Pages

```bash
git remote add origin https://github.com/<your-username>/captain-rebel-website.git
git branch -M main
git push -u origin main
```

Then in the repo: **Settings → Pages → Source: Deploy from branch → main / root**. The site will be live at `https://<your-username>.github.io/captain-rebel-website/`.

## Structure

```
index.html          # full site (styles + JS inline, zero dependencies except Three.js CDN)
assets/cr-mark.svg  # standalone chrome CR badge logo
favicon.svg         # favicon version of the mark
```

## Notes

- Product data lives in the `PRODUCTS` array at the top of the script in `index.html` — edit names/prices/links there.
- The 3D coin engraving is drawn programmatically; tweak `makeBadgeCanvas()` to restyle it.
- Fonts: Unbounded (display), Space Grotesk (body), Space Mono (utility) via Google Fonts.
