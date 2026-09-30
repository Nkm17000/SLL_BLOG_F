from __future__ import annotations
import base64, html, json, re, shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
from app.theme_engine import THEMES
ROOT=Path(__file__).resolve().parent.parent
TEMPLATE_DIR=ROOT/"templates"
IMAGE_DIR=ROOT/"assets/images"

def _esc(v): return html.escape(str(v or ""), quote=True)
def _data_uri(path):
    raw=path.read_bytes(); return "data:image/svg+xml;base64,"+base64.b64encode(raw).decode()

def build_html(blog, template_id, theme_id):
    template=(TEMPLATE_DIR / (f"{template_id:02d}_" + [
        "asymmetric_magazine","zigzag_story","vertical_timeline","bento_grid","pill_cards","newspaper_columns","color_band","circle_focus","diagonal_blocks","premium_minimal"
    ][template_id-1] + ".html")).read_text(encoding="utf-8")
    img=_data_uri(IMAGE_DIR/f"template-{template_id:02d}-hero.svg")
    template=template.replace("{{category}}",_esc(blog["category"])).replace("{{title}}",_esc(blog["title"])).replace("{{description}}",_esc(blog["description"]))
    template=template.replace("{{hero_image_url}}",img).replace("{{hero_image_alt}}",_esc(blog["title"]))
    template=template.replace("{{footer_text}}","Smart Learning Lab • Learn • Practice • Grow").replace("{{website}}","Technical AI Blog")
    for i,p in enumerate(blog["points"]):
        template=template.replace(f"{{{{points[{i}].title}}}}",_esc(p["title"]))
        template=template.replace(f"{{{{points[{i}].description}}}}",_esc(p["description"]))
        template=template.replace(f"{{{{points[{i}].items[0]}}}}",_esc(p["items"][0]))
        template=template.replace(f"{{{{points[{i}].items[1]}}}}",_esc(p["items"][1]))
    t=THEMES[theme_id-1]
    # Theme override is appended after the template's own CSS so every template keeps its layout.
    override=f'''<style id="dynamic-theme">html,body{{background:{t["bg"]}!important}}.canvas{{background:{t["bg"]}!important;color:{t["ink"]}!important}}.header,.footer{{background:{t["ink"]}!important;color:#fff!important}}.category{{color:{t["accent"]}!important}}.point{{background:{t["card"]}!important;color:{t["ink"]}!important;border-color:{t["accent"]}!important}}.num{{background:{t["accent"]}!important}}.hero h1,.hero p,.point h2,.point p,.point li{{color:{t["ink"]}!important}}.footer{{border-color:{t["accent"]}!important}} </style>'''
    return template.replace("</head>",override+"</head>")

def render(blog, template_id, theme_id, output_path):
    html_text=build_html(blog,template_id,theme_id)
    output_path=Path(output_path); output_path.parent.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as p:
        chrome=shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")
        kwargs={"args":["--no-sandbox","--disable-dev-shm-usage"]}
        if chrome: kwargs["executable_path"]=chrome
        browser=p.chromium.launch(**kwargs)
        page=browser.new_page(viewport={"width":800,"height":1000}, device_scale_factor=2)
        page.set_content(html_text, wait_until="load")
        page.screenshot(path=str(output_path), full_page=False)
        browser.close()
