from __future__ import annotations
import base64, html, mimetypes, shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
from app.theme_engine import THEMES

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = ROOT / "templates"
IMAGE_DIR = ROOT / "assets/images"

TEMPLATE_NAMES = [
    "asymmetric_magazine", "zigzag_story", "vertical_timeline", "bento_grid", "pill_cards",
    "newspaper_columns", "color_band", "circle_focus", "diagonal_blocks", "premium_minimal"
]

def _esc(v):
    return html.escape(str(v or ""), quote=True)

def _data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    raw = path.read_bytes()
    return f"data:{mime};base64," + base64.b64encode(raw).decode("ascii")

def _hero_path(template_id: int) -> Path:
    png = IMAGE_DIR / f"template-{template_id:02d}-hero.png"
    if png.exists():
        return png
    # Backward-compatible fallback for old checkouts.
    svg = IMAGE_DIR / f"template-{template_id:02d}-hero.svg"
    if svg.exists():
        return svg
    raise FileNotFoundError(f"Missing hero image for template {template_id}: {png}")

def build_html(blog, template_id, theme_id):
    template_file = TEMPLATE_DIR / f"{template_id:02d}_{TEMPLATE_NAMES[template_id-1]}.html"
    template = template_file.read_text(encoding="utf-8")
    img = _data_uri(_hero_path(template_id))

    template = (template
        .replace("{{category}}", _esc(blog["category"]))
        .replace("{{title}}", _esc(blog["title"]))
        .replace("{{description}}", _esc(blog["description"]))
        .replace("{{hero_image_url}}", img)
        .replace("{{hero_image_alt}}", _esc(blog["title"])))
    template = template.replace("{{footer_text}}", "Smart Learning Lab • Learn • Practice • Grow")
    template = template.replace("{{website}}", "Technical AI Blog")

    for i, point in enumerate(blog["points"]):
        template = template.replace(f"{{{{points[{i}].title}}}}", _esc(point["title"]))
        template = template.replace(f"{{{{points[{i}].description}}}}", _esc(point["description"]))
        template = template.replace(f"{{{{points[{i}].items[0]}}}}", _esc(point["items"][0]))
        template = template.replace(f"{{{{points[{i}].items[1]}}}}", _esc(point["items"][1]))

    t = THEMES[theme_id - 1]
    # Global accessibility/readability layer. It intentionally neutralizes any legacy dark
    # template styling and makes every theme light, airy, and content-filling.
    override = f'''<style id="dynamic-theme">
html,body{{margin:0!important;padding:0!important;background:#ffffff!important;color:{t["ink"]}!important;font-family:Inter,Arial,sans-serif!important}}
.canvas{{background:{t["bg"]}!important;color:{t["ink"]}!important;height:1000px!important;overflow:hidden!important}}
.header{{height:74px!important;background:#ffffff!important;color:{t["ink"]}!important;border-bottom:2px solid {t["soft"]}!important}}
.brand{{color:{t["ink"]}!important}} .brand small{{color:{t["ink"]}!important;opacity:.65!important}}
.header>div:last-child{{color:{t["accent"]}!important;font-weight:800!important}}
.hero{{min-height:244px!important;padding:22px 30px 18px!important;background:linear-gradient(135deg,#ffffff 0%,{t["soft"]} 100%)!important;color:{t["ink"]}!important;border-radius:0 0 28px 28px!important}}
.category{{color:{t["accent"]}!important}}
.hero h1,.hero p{{color:{t["ink"]}!important}}
.hero h1{{font-size:34px!important;line-height:1.04!important}}
.hero p{{font-size:13px!important}}
.hero img{{height:205px!important;width:100%!important;object-fit:cover!important;object-position:center!important;border-radius:22px!important;box-shadow:0 10px 30px rgba(24,45,75,.12)!important;background:#fff!important}}
.points{{height:620px!important;padding:16px 30px 10px!important;gap:13px!important;align-content:stretch!important;grid-auto-rows:1fr!important}}
.point{{background:{t["card"]}!important;color:{t["ink"]}!important;border:1px solid {t["soft"]}!important;box-shadow:0 7px 20px rgba(32,55,80,.08)!important;border-radius:20px!important;min-height:130px!important}}
.point h2,.point p,.point li{{color:{t["ink"]}!important}}
.point h2{{font-size:16px!important;line-height:1.15!important}}
.point p{{font-size:10.5px!important;line-height:1.35!important}}
.point ul{{font-size:10px!important;line-height:1.35!important}}
.num{{background:{t["accent"]}!important;color:#ffffff!important}}
.footer{{background:#ffffff!important;color:{t["ink"]}!important;border-top:2px solid {t["soft"]}!important;height:48px!important}}
/* Neutralize legacy dark/strong-color template accents while preserving each layout's geometry. */
.hero[style],.point[style]{{color:{t["ink"]}!important}}
</style>'''
    return template.replace("</head>", override + "</head>")

def render(blog, template_id, theme_id, output_path):
    html_text = build_html(blog, template_id, theme_id)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        chrome = shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")
        kwargs = {"args": ["--no-sandbox", "--disable-dev-shm-usage"]}
        if chrome:
            kwargs["executable_path"] = chrome
        browser = p.chromium.launch(**kwargs)
        page = browser.new_page(viewport={"width":800,"height":1000}, device_scale_factor=2)
        page.set_content(html_text, wait_until="load")
        page.screenshot(path=str(output_path), full_page=False)
        browser.close()
