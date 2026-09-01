# Social sharing card generator

Generates `images/og-image.jpg` — the image people see when a link to the site
is shared on LinkedIn, X/Twitter, Facebook, Slack, iMessage or WhatsApp.

The card is authored as HTML and rendered by headless Chromium, so the text is
real type rather than pixels: edit `og-card.html`, re-render, done.

## Regenerating

```sh
pip install playwright pillow
playwright install chromium      # skip if a browser is already installed
python3 tools/og/render.py
```

Rendering needs network access the first time, because `og-card.html` pulls
Inter and Playfair Display from Google Fonts. The script fails loudly rather
than silently falling back to a system font.

## Files

| File | Purpose |
| --- | --- |
| `og-card.html` | The card layout. 1200×630, brand tokens copied from `styles.css`. |
| `portrait.png` | Circular headshot, 720×720 grayscale + alpha. |
| `render.py` | Renders at 2× and downsamples to 1200×630. |

## Editing the card

The proof row near the bottom is the part that goes stale — it currently reads
Founder / FinMango, Building / Fresho, Speaker / 2× TEDx. Update those in
`og-card.html` and re-render whenever the ventures change.

`render.py` refuses to write the image if the name, tagline or proof row
overflows the text column, so a longer venture name fails the render instead of
shipping a clipped card. If that happens, shorten the text or drop `.name`'s
`font-size` a few px.

## Why these dimensions and this format

- **1200×630** is the 1.91:1 ratio LinkedIn, Facebook and X all expect. The
  previous card was 1024×1024 while its meta tags claimed 1200×630, so
  platforms laid out a wide card and got a square image.
- **JPEG at quality 92, 4:4:4 chroma** is ~95KB. The identical PNG is 450KB and
  the peak per-pixel difference is 4/255 — invisible, so the smaller file wins.
  4:4:4 (`subsampling=0`) matters: the default 4:2:0 smears colour at the edges
  of white-on-dark text.
- **Rendered at 2× then downsampled** with Lanczos plus a light unsharp mask.
  Rasterising straight at 1200×630 gives noticeably softer type.

## Replacing the headshot

`portrait.png` was recovered from the previous sharing image, which was itself a
composite — so it is not a pristine original. To swap in a real headshot:

```python
from PIL import Image, ImageDraw, ImageFilter
im = Image.open('headshot.jpg').convert('RGB')   # square, tightly cropped
im = im.convert('L').resize((720, 720), Image.LANCZOS)   # drop .convert('L') to keep colour
im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=55, threshold=3))
mask = Image.new('L', (2880, 2880), 0)
ImageDraw.Draw(mask).ellipse((0, 0, 2879, 2879), fill=255)
Image.merge('LA', (im, mask.resize((720, 720), Image.LANCZOS))).save(
    'tools/og/portrait.png', optimize=True)
```

720×720 is deliberate: the card shows the portrait at 398 CSS px, which is 796
device px at 2× — so 720 needs no meaningful upscaling.

## Per-page cards

`travel.html` and `projects.html` use their own cards, built from the same
script with `--card` and `--out`. Every other page shares `og-image.jpg`.
