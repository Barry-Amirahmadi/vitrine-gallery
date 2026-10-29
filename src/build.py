# Builds index.html from src/site.json. Run: python -I src/build.py
# Reuse for another gallery: edit site.json (page copy, categories, items) and drop thumbnails in media/<key>.webp.
# No external requests: self-hosted font, local WebP posters, one local script.
import base64, html, io, json, pathlib
from collections import Counter
from fractions import Fraction

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "src" / "site.json").read_text(encoding="utf-8"))
P, OFFER, KINDS, ITEMS = DATA["page"], DATA["offer"], DATA["kinds"], DATA["items"]
CATS = dict(DATA["categories"])
FA = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
e = html.escape

# Lucide icons, mirrored where direction matters (arrow-right -> arrow-left, arrow-up-right -> arrow-up-left).
SVG = 'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"'
ICON_SLIDERS = f'<svg class="ico-brand" {SVG}><path d="M10 5H3"/><path d="M12 19H3"/><path d="M14 3v4"/><path d="M16 17v4"/><path d="M21 12h-9"/><path d="M21 19h-5"/><path d="M21 5h-7"/><path d="M8 10v4"/><path d="M8 12H3"/></svg>'
ICON_ARROW = f'<svg class="ico-go" {SVG}><path d="m12 19-7-7 7-7"/><path d="M19 12H5"/></svg>'
ICON_UP = f'<svg {SVG}><path d="M7 17V7h10"/><path d="M17 17 7 7"/></svg>'


def lqip(path):
    """A 16px-wide blurred stand-in, inlined so each card has colour before its poster loads."""
    with Image.open(path) as im:
        im = im.convert("RGB")
        im.thumbnail((16, 16 * im.height // im.width))
        buf = io.BytesIO()
        im.save(buf, "WEBP", quality=40)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()


def card(i, s):
    w, h = (int(v) for v in s["ratio"].split("/"))
    search = " ".join([s["name"], s["trade"], s["style"], s["tags"]])
    return f"""      <li class="item" data-key="{e(s['key'])}" data-kind="{e(s['kind'])}" data-cat="{e(s['cat'])}" data-ratio="{float(Fraction(h, w)):.5f}" data-search="{e(search)}">
        <a class="card" href="{e(P['base_url'] + s['path'])}/" target="_blank" rel="noopener" aria-label="{e(s['name'])}، {e(s['trade'])}، سبک {e(s['style'])}">
          <div class="media" style="aspect-ratio:{w} / {h}">
            <div class="media-in">
              <img class="lqip" src="{lqip(ROOT / 'media' / (s['key'] + '.webp'))}" alt="" aria-hidden="true">
              <img class="full" src="media/{e(s['key'])}.webp" width="{w}" height="{h}" alt="" loading="{'eager' if i < 5 else 'lazy'}" decoding="async">
            </div>
            <span class="tag">{e(s['style'])}</span>
          </div>
          <div class="meta">
            <span class="avatar" aria-hidden="true">{e(s['name'][0])}</span>
            <span class="who"><b>{e(s['name'])}</b> · {e(s['trade'])}</span>
          </div>
        </a>
      </li>"""


def chips(group, options, counts):
    out = []
    for value, label in options:
        out.append(f'<button type="button" class="chip" data-value="{e(value)}" aria-pressed="false">{e(label)}'
                   f'<span class="count num">{str(counts[value]).translate(FA)}</span></button>')
    return "\n          ".join(out)


def contact():
    c, out = DATA["contact"], []
    if c.get("telegram"):
        out.append(f'<a class="btn-solid" style="display:inline-flex;align-items:center" href="https://t.me/{e(c["telegram"])}">پیام در تلگرام</a>')
    if c.get("whatsapp"):
        out.append(f'<a class="btn-solid" style="display:inline-flex;align-items:center" href="https://wa.me/{e(c["whatsapp"])}">پیام در واتساپ</a>')
    return "\n        ".join(out) if out else '<span class="soon">راه ارتباطی به‌زودی اضافه می‌شود.</span>'


n = len(ITEMS)
styles = len({s["style"] for s in ITEMS})
kind_counts = Counter(s["kind"] for s in ITEMS)
cat_counts = Counter(s["cat"] for s in ITEMS)
missing = [s["key"] for s in ITEMS if not (ROOT / "media" / (s["key"] + ".webp")).exists()]
assert not missing, f"missing posters: {missing}"
assert all(s["cat"] in CATS and s["kind"] in KINDS for s in ITEMS), "unknown cat or kind"
h1 = f"{str(n).translate(FA)} سایت فارسی، در {str(styles).translate(FA)} سبک طراحی"

page = f"""<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(P['title'])}</title>
<meta name="description" content="{e(P['description'])}">
<meta name="theme-color" content="#ffffff">
<link rel="preload" href="fonts/Vazirmatn.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/site.css">
</head>
<body>
<header class="top">
  <a class="wordmark" href="./">{e(P['brand'])}</a>
  <nav class="nav" aria-label="اصلی">
    <a class="ghost" href="#work">نمونه‌ها</a>
    <a class="ghost" href="#work" data-show-kind="template">قالب‌ها</a>
    <a class="ghost" href="#contact">سفارش</a>
  </nav>
</header>
<main>
  <section class="hero">
    <div>
      <h1>{e(h1)}</h1>
      <p class="lead">{e(P['lead'])}</p>
      <form class="ask" role="search" novalidate>
        <label class="sr-only" for="q">{e(P['search_label'])}</label>
        <div class="ask-row">
          <input id="q" name="q" type="search" autocomplete="off" placeholder="{e(P['search_placeholder'])}" aria-describedby="ask-note">
          <button class="btn-solid" type="submit">{e(P['search_button'])}</button>
        </div>
        <p id="ask-note" class="ask-note" aria-live="polite">{e(P['search_note'])}</p>
      </form>
      <a class="news" href="#contact">{ICON_SLIDERS}{e(P['news'])}{ICON_ARROW}</a>
    </div>
    <aside class="offer" aria-label="{e(OFFER['title'])}">
      <a href="#contact">
        <div class="offer-media">
          <strong>{e(OFFER['headline'])}</strong>
          <span>{e(OFFER['body'])}</span>
          <span class="chip-float">{e(OFFER['chip'])}</span>
        </div>
        <div class="offer-foot">
          <span class="slot" aria-hidden="true"></span>
          <span class="offer-text"><b>{e(OFFER['title'])}</b><small>{e(OFFER['subtitle'])}</small></span>
          <span class="pill">{e(OFFER['button'])}{ICON_UP}</span>
        </div>
      </a>
    </aside>
  </section>

  <section id="work" aria-label="نمونه‌کارها">
    <div class="filters">
      <div class="filter-row">
        <span class="filter-label" id="filter-label">فیلتر:</span>
        <div class="filter-row" data-filter="kind" role="group" aria-labelledby="filter-label">
          {chips('kind', KINDS.items(), kind_counts)}
        </div>
        <button type="button" class="ghost reset" hidden>پاک کردن فیلترها</button>
      </div>
      <div class="filter-row cats" data-filter="cat" role="group" aria-label="دسته‌ها">
          {chips('cat', CATS.items(), cat_counts)}
      </div>
    </div>
    <ul class="grid">
{chr(10).join(card(i, s) for i, s in enumerate(ITEMS))}
    </ul>
    <div class="empty" hidden>
      <p>نمونه‌ای با این فیلتر نیست.</p>
      <button type="button" class="chip">نمایش همه</button>
    </div>
  </section>

  <footer class="foot" id="contact">
    <h2>{e(OFFER['title'])}</h2>
    <p>{e(OFFER['subtitle'])} {e(OFFER['body'])}</p>
    <div class="row">
        {contact()}
    </div>
    <p>{e(P['disclaimer'])}</p>
  </footer>
</main>
<script src="assets/site.js" defer></script>
</body>
</html>
"""
(ROOT / "index.html").write_text(page, encoding="utf-8")
(ROOT / ".nojekyll").write_text("", encoding="utf-8")
print("wrote index.html", len(page.encode()), "bytes,", n, "items,", styles, "styles,", dict(cat_counts))
