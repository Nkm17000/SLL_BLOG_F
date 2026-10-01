from __future__ import annotations
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright


def build_carousel(blog: dict, output_dir: Path) -> list[Path]:
    """Create six square companion slides as local assets; publishing remains one image post by default."""
    output_dir.mkdir(parents=True, exist_ok=True)
    slides=[]
    accent="#2563EB"
    items=[
        ("HOOK", blog.get("hook", blog.get("title","")), blog.get("description","")),
        *[(f"{i:02d}", p.get("title",""), p.get("description","")) for i,p in enumerate(blog.get("points",[]),1)],
    ]
    items.append(("TAKEAWAY", "What to remember", blog.get("cta","Save this for later 📌")))
    with sync_playwright() as p:
        chrome=shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")
        kwargs={"args":["--no-sandbox","--disable-dev-shm-usage"]}
        if chrome: kwargs["executable_path"]=chrome
        browser=p.chromium.launch(**kwargs)
        page=browser.new_page(viewport={"width":1000,"height":1000},device_scale_factor=2)
        for idx,(label,title,body) in enumerate(items,1):
            html=f'''<html><body style="margin:0;background:#f7fbff;font-family:Arial,sans-serif"><main style="width:1000px;height:1000px;box-sizing:border-box;padding:85px;display:flex;flex-direction:column;justify-content:space-between;background:linear-gradient(135deg,#ffffff,#eef7ff)"><div><div style="font-size:28px;font-weight:900;letter-spacing:2px;color:{accent}">SMART LEARNING LAB</div><div style="margin-top:100px;font-size:28px;font-weight:900;color:#64748b">{label}</div><h1 style="font-size:62px;line-height:1.05;color:#172b52;margin:22px 0">{title}</h1><p style="font-size:30px;line-height:1.45;color:#475569">{body}</p></div><div style="font-size:24px;color:#64748b">LEARN • PRACTICE • GROW</div></main></body></html>'''
            page.set_content(html,wait_until="load")
            path=output_dir/f"slide-{idx:02d}.png"; page.screenshot(path=str(path),full_page=False); slides.append(path)
        browser.close()
    return slides
