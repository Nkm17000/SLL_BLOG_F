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

def make_responsive_12x10(html_text: str, orientation: str) -> str:
    # Base design is 800x1000. Reflow into 12:10 horizontal or 10:12 vertical while
    # preserving the template's visual hierarchy.
    if orientation == "horizontal":
        extra = """
<style>
.canvas{width:1200px!important;height:1000px!important}
.hero{height:300px!important}
.hero-content{width:53%!important}
.points{padding-left:36px!important;padding-right:36px!important}
.point{min-height:112px!important}
</style>
"""
    else:
        extra = """
<style>
.canvas{width:1000px!important;height:1200px!important}
.header{height:78px!important}
.hero{height:350px!important}
.hero-content{width:55%!important;padding:42px 34px!important}
.title{font-size:45px!important}
.description{font-size:16px!important;max-width:500px!important}
.points{padding:22px 34px 86px!important}
.point{min-height:128px!important}
.footer{height:48px!important}
</style>
"""
    return html_text.replace("</body>", extra+"</body>")

def render(template_path, blog, hero_path, theme, orientation, out_html):
    html = inject_template(template_path, blog, hero_path, theme)
    html = make_responsive_12x10(html, orientation)
    Path(out_html).write_text(html, encoding="utf-8")
