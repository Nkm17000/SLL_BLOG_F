from __future__ import annotations
import base64
import html
import mimetypes
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

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
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")

def _hero_path(template_id: int) -> Path:
    path = IMAGE_DIR / f"template-{template_id:02d}-hero.png"
    if not path.exists():
        raise FileNotFoundError(f"Missing hero image for template {template_id}: {path}")
    return path

def build_html(blog, template_id):
    template_file = TEMPLATE_DIR / f"{template_id:02d}_{TEMPLATE_NAMES[template_id - 1]}.html"
    if not template_file.exists():
        raise FileNotFoundError(f"Missing template: {template_file}")
    template = template_file.read_text(encoding="utf-8")
    img = _data_uri(_hero_path(template_id))

    replacements = {
        "{{category}}": _esc(blog["category"]),
        "{{title}}": _esc(blog["title"]),
        "{{description}}": _esc(blog["description"]),
        "{{hero_image_url}}": img,
        "{{hero_image_alt}}": _esc(blog["title"]),
        "{{footer_text}}": "Smart Learning Lab • Learn • Practice • Grow",
        "{{website}}": "Technical AI Blog",
    }
    for key, value in replacements.items():
        template = template.replace(key, value)

    for i, point in enumerate(blog["points"]):
        template = template.replace(f"{{{{points[{i}].title}}}}", _esc(point["title"]))
        template = template.replace(f"{{{{points[{i}].description}}}}", _esc(point["description"]))
        template = template.replace(f"{{{{points[{i}].items[0]}}}}", _esc(point["items"][0]))
        template = template.replace(f"{{{{points[{i}].items[1]}}}}", _esc(point["items"][1]))
    return template

def render(blog, template_id, output_path):
    html_text = build_html(blog, template_id)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        chrome = shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")
        kwargs = {"args": ["--no-sandbox", "--disable-dev-shm-usage"]}
        if chrome:
            kwargs["executable_path"] = chrome
        browser = p.chromium.launch(**kwargs)
        page = browser.new_page(viewport={"width": 800, "height": 1000}, device_scale_factor=2)
        page.set_content(html_text, wait_until="load")
        page.screenshot(path=str(output_path), full_page=False)
        browser.close()
