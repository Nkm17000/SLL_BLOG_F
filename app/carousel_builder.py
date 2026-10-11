from __future__ import annotations
from pathlib import Path
import html
from playwright.sync_api import sync_playwright
from app.config import Config

def _esc(value): return html.escape(str(value or ""), quote=True)

def build_carousel(blog: dict, output_dir: Path) -> list[Path]:
    """Build a seven-slide, Facebook multi-photo carousel from one sourced tech update."""
    output_dir.mkdir(parents=True, exist_ok=True)
    points = list(blog.get("points", []))[:5]
    slides = [("TODAY IN TECH", blog.get("hook") or blog.get("title", "Technology update"), blog.get("description", ""))]
    for idx, point in enumerate(points, 1):
        body = point.get("description", "")
        items = point.get("items", [])
        if items: body += "\n\n" + " • ".join(str(x) for x in items[:2])
        slides.append((f"{idx:02d} / 05  •  {point.get('title', 'Key insight')}", point.get("title", "Key insight"), body))
    slides.append(("KEY TAKEAWAY", "What to do next", "Verify important details in the original source. Test technical changes in a safe environment, and check official documentation before applying them. Save this carousel for reference."))
    slides = slides[:max(3, min(Config.CAROUSEL_SLIDES, 10))]
    out=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
        page=browser.new_page(viewport={"width":1080,"height":1080}, device_scale_factor=1)
        for idx,(label,title,body) in enumerate(slides,1):
            body_html="<br>".join(_esc(line) for line in body.splitlines())
            doc=f'''<!doctype html><html><head><meta charset="utf-8"><style>*{{box-sizing:border-box}}body{{margin:0;font-family:Arial,Helvetica,sans-serif;background:#eff6ff;color:#122343}}main{{width:1080px;height:1080px;padding:76px;display:flex;flex-direction:column;justify-content:space-between;overflow:hidden;background:radial-gradient(circle at 85% 10%,#dbeafe,transparent 35%),linear-gradient(145deg,#fff 0%,#eff6ff 100%);border:18px solid #2563eb}}.brand{{font-size:28px;font-weight:900;letter-spacing:1.8px;color:#1d4ed8}}.pill{{display:inline-block;margin-top:78px;background:#ffedd5;color:#9a3412;padding:14px 22px;border-radius:24px;font-size:23px;font-weight:800;letter-spacing:1px}}h1{{font-size:61px;line-height:1.08;margin:26px 0;color:#0f1f42;overflow-wrap:anywhere}}.body{{font-size:31px;line-height:1.45;color:#334155;white-space:normal;overflow-wrap:anywhere}}.footer{{display:flex;justify-content:space-between;align-items:center;border-top:2px solid #cbd5e1;padding-top:24px;color:#475569;font-size:20px}}.number{{font-size:20px;font-weight:800;color:#f97316}}a{{color:#1d4ed8}}</style></head><body><main><section><div class="brand">{_esc(Config.APP_NAME.upper())}</div><div class="pill">{_esc(label)}</div><h1>{_esc(title)}</h1><div class="body">{body_html}</div></section><footer class="footer"><span>LEARN • PRACTICE • GROW</span><span class="number">{idx:02d} / {len(slides):02d}</span></footer></main></body></html>'''
            page.set_content(doc,wait_until="load")
            path=output_dir/f"slide-{idx:02d}.jpg"
            page.screenshot(path=str(path),type="jpeg",quality=90)
            out.append(path)
        browser.close()
    return out
