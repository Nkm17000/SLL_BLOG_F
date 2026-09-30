from __future__ import annotations

import asyncio
from pathlib import Path
import shutil

from app.config import Config
from app.template_engine import render_html

ROOT = Path(__file__).resolve().parent.parent
TMP = ROOT / "output" / "rendered_html"


def render(blog: dict, output_path: Path, template_index: int, theme_index: int):
    html_text, metadata = render_html(blog, template_index, theme_index)
    TMP.mkdir(parents=True, exist_ok=True)
    html_path = TMP / f"{output_path.stem}.html"
    html_path.write_text(html_text, encoding="utf-8")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    asyncio.run(_screenshot(html_path, output_path))
    return metadata


async def _screenshot(html_path: Path, output_path: Path):
    try:
        from playwright.async_api import async_playwright
    except ImportError as exc:
        raise RuntimeError("Playwright is required. Install dependencies from requirements.txt and run 'python -m playwright install chromium'.") from exc

    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
    import threading

    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    try:
        async with async_playwright() as p:
            executable = shutil.which("chromium") or shutil.which("google-chrome") or None
            browser = await p.chromium.launch(headless=True, executable_path=executable)
            page = await browser.new_page(viewport={"width": 800, "height": 1000}, device_scale_factor=2)
            # Serve from the HTML file's directory so local SVG hero assets are available.
            import os
            os.chdir(str(html_path.parent))
            await page.goto(f"http://127.0.0.1:{server.server_port}/{html_path.name}", wait_until="networkidle")
            await page.screenshot(path=str(output_path), full_page=False, type="png")
            await browser.close()
    finally:
        server.shutdown()
        server.server_close()

    # The template is intentionally 800x1000 CSS px and device scale 2 => 1600x2000 output.
    if not output_path.exists():
        raise RuntimeError(f"Screenshot was not created: {output_path}")
