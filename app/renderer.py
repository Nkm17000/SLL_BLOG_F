from pathlib import Path
import json, re, html as html_lib
from typing import Dict

ROOT = Path(__file__).resolve().parents[1]

def inject_template(template_path: Path, blog: dict, hero_path: Path, theme: dict) -> str:
    s = template_path.read_text(encoding="utf-8")
    replacements = {
        "{{category}}": str(blog.get("category","")),
        "{{title}}": str(blog.get("title","")),
        "{{description}}": str(blog.get("description","")),
        "{{hero_image_url}}": hero_path.resolve().as_uri(),
        "{{hero_image_alt}}": str(blog.get("title","")),
        "{{theme.background}}": theme["background"],
        "{{theme.surface}}": theme["surface"],
        "{{theme.text}}": theme["text"],
        "{{theme.muted}}": theme["muted"],
        "{{theme.accent}}": theme["accent"],
        "{{theme.accent2}}": theme["accent2"],
        "{{theme.border}}": theme["border"],
        "{{theme.hero_overlay}}": theme["hero_overlay"],
    }
    for k,v in replacements.items():
        s=s.replace(k,html_lib.escape(v, quote=True) if k != "{{hero_image_url}}" else v)
    points=blog.get("points",[])
    for i in range(5):
        pt=points[i] if i<len(points) else {"title":"","description":"","items":["",""]}
        s=s.replace(f"{{{{points[{i}].title}}}}",html_lib.escape(str(pt.get("title",""))))
        s=s.replace(f"{{{{points[{i}].description}}}}",html_lib.escape(str(pt.get("description",""))))
        items=pt.get("items",[])
        for j in range(2):
            val=items[j] if j<len(items) else ""
            s=s.replace(f"{{{{points[{i}].items[{j}]}}}}",html_lib.escape(str(val)))
    return s

def make_responsive_square(html_text: str) -> str:
    extra = """<style>
.canvas{width:2000px!important;height:2000px!important}
.hero{height:520px!important}
.hero-content{width:56%!important;padding:54px 48px!important}
.title{font-size:64px!important;line-height:1.05!important;max-width:1050px!important}
.description{font-size:24px!important;line-height:1.45!important;max-width:980px!important}
.points{padding:38px 54px 110px!important;gap:20px!important}
.point{min-height:220px!important;padding:24px!important}
.point h2{font-size:28px!important;line-height:1.18!important}
.point p{font-size:20px!important;line-height:1.4!important}
.point ul{font-size:18px!important;line-height:1.4!important}
.footer{height:70px!important}
</style>"""
    return html_text.replace("</body>", extra+"</body>")

def render(template_path, blog, hero_path, theme, orientation, out_html):
    html = inject_template(template_path, blog, hero_path, theme)
    html = make_responsive_square(html)
    Path(out_html).write_text(html, encoding="utf-8")
