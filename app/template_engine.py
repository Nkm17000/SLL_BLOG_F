from __future__ import annotations

import html
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = ROOT / "templates"
IMAGE_DIR = ROOT / "assets" / "templates" / "images"

TEMPLATES = [
    {"id": "01_asymmetric_magazine", "name": "Asymmetric Magazine", "file": "01_asymmetric_magazine.html", "hero": "template-01-hero.svg"},
    {"id": "02_zigzag_story", "name": "Zigzag Story", "file": "02_zigzag_story.html", "hero": "template-02-hero.svg"},
    {"id": "03_vertical_timeline", "name": "Vertical Timeline", "file": "03_vertical_timeline.html", "hero": "template-03-hero.svg"},
    {"id": "04_bento_grid", "name": "Bento Grid", "file": "04_bento_grid.html", "hero": "template-04-hero.svg"},
    {"id": "05_pill_cards", "name": "Pill Cards", "file": "05_pill_cards.html", "hero": "template-05-hero.svg"},
    {"id": "06_newspaper_columns", "name": "Newspaper Columns", "file": "06_newspaper_columns.html", "hero": "template-06-hero.svg"},
    {"id": "07_color_band", "name": "Color Band", "file": "07_color_band.html", "hero": "template-07-hero.svg"},
    {"id": "08_circle_focus", "name": "Circle Focus", "file": "08_circle_focus.html", "hero": "template-08-hero.svg"},
    {"id": "09_diagonal_blocks", "name": "Diagonal Blocks", "file": "09_diagonal_blocks.html", "hero": "template-09-hero.svg"},
    {"id": "10_premium_minimal", "name": "Premium Minimal", "file": "10_premium_minimal.html", "hero": "template-10-hero.svg"},
]

THEMES = [
    {"id":"ocean_blue", "name":"Ocean Blue", "bg":"#0B1220", "accent":"#2563EB", "soft":"#E0F2FE", "text":"#111827"},
    {"id":"purple_ai", "name":"Purple AI", "bg":"#21133B", "accent":"#8B5CF6", "soft":"#F3E8FF", "text":"#17111F"},
    {"id":"emerald_tech", "name":"Emerald Tech", "bg":"#062E26", "accent":"#10B981", "soft":"#D1FAE5", "text":"#10231F"},
    {"id":"sunset_orange", "name":"Sunset Orange", "bg":"#431407", "accent":"#F97316", "soft":"#FFEDD5", "text":"#26150F"},
    {"id":"premium_gold", "name":"Premium Gold", "bg":"#18181B", "accent":"#CA8A04", "soft":"#FEF3C7", "text":"#171717"},
]


def template_for(index):
    return TEMPLATES[index % len(TEMPLATES)]


def theme_for(index):
    return THEMES[index % len(THEMES)]


def _file_url(path: Path) -> str:
    return path.resolve().as_uri()


def _safe(value):
    return html.escape(str(value or ""), quote=True)


def _theme_css(theme):
    # Override the base template palette while retaining each template's unique geometry.
    return f"""
<style id=\"runtime-theme\">
.canvas{{background:{theme['soft']} !important;color:{theme['text']} !important}}
.header,.footer{{background:{theme['bg']} !important;color:#fff !important}}
.category{{color:{theme['accent']} !important}}
.num{{background:{theme['accent']} !important}}
.point{{color:{theme['text']} !important}}
.hero{{color:{theme['text']} !important}}
.hero h1,.point h2{{color:{theme['text']} !important}}
</style>
"""


def render_html(blog: dict, template_index: int, theme_index: int) -> tuple[str, dict]:
    template = template_for(template_index)
    theme = theme_for(theme_index)
    template_path = TEMPLATE_DIR / template["file"]
    source = template_path.read_text(encoding="utf-8")
    hero_path = IMAGE_DIR / template["hero"]
    if not hero_path.exists():
        raise FileNotFoundError(f"Missing hero asset: {hero_path}")

    values = {
        "category": _safe(blog["category"]),
        "title": _safe(blog["title"]),
        "description": _safe(blog["description"]),
        "hero_image_url": f"../../assets/templates/images/{hero_path.name}",
        "hero_image_alt": _safe(blog["hero_image_alt"]),
        "footer_text": _safe(blog["footer_text"]),
        "website": _safe(blog["website"]),
    }
    for key, value in values.items():
        source = source.replace("{{" + key + "}}", value)
    for i, point in enumerate(blog["points"]):
        source = source.replace(f"{{{{points[{i}].title}}}}", _safe(point["title"]))
        source = source.replace(f"{{{{points[{i}].description}}}}", _safe(point["description"]))
        source = source.replace(f"{{{{points[{i}].items[0]}}}}", _safe(point["items"][0]))
        source = source.replace(f"{{{{points[{i}].items[1]}}}}", _safe(point["items"][1]))

    source = source.replace("</style>", _theme_css(theme) + "</style>", 1)
    metadata = {
        "template_id": template["id"], "template_name": template["name"],
        "theme_id": theme["id"], "theme_name": theme["name"],
        "hero_asset": str(hero_path.relative_to(ROOT)),
    }
    return source, metadata
