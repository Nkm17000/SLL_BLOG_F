from __future__ import annotations
import random, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
PALETTES = [
    ((12, 22, 54), (21, 107, 156), (70, 221, 190), (255, 255, 255)),
    ((42, 16, 63), (144, 43, 121), (255, 174, 95), (255, 250, 242)),
    ((11, 45, 44), (26, 128, 108), (196, 239, 125), (250, 255, 239)),
    ((50, 26, 14), (166, 78, 40), (255, 202, 89), (255, 248, 229)),
    ((17, 28, 76), (69, 68, 174), (109, 216, 255), (248, 250, 255)),
    ((45, 18, 32), (172, 43, 81), (255, 137, 168), (255, 246, 249)),
]

def _font(size: int, bold: bool=False):
    candidates = (["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"] if bold else ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"])
    for path in candidates:
        if Path(path).exists(): return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def _wrap_pixels(draw, text, font, max_width):
    words = str(text or "").split()
    lines, line = [], ""
    for word in words:
        candidate = word if not line else f"{line} {word}"
        if draw.textlength(candidate, font=font) <= max_width:
            line = candidate
        else:
            if line: lines.append(line)
            line = word
    if line: lines.append(line)
    return lines

def _draw_paragraph(draw, text, x, y, font, fill, max_width, max_lines=None, spacing=7):
    lines = _wrap_pixels(draw, text, font, max_width)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines[-1] and draw.textlength(lines[-1] + "…", font=font) > max_width:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1].rstrip(" .") + "…"
    line_h = int(font.size * 1.35)
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_h
        if y > H - 90: break
    return y + spacing

def create_blog_image(blog: dict, source_url: str, app_name: str, output_path: str | Path, previous_palette: int | None = None) -> tuple[Path, int]:
    """Render the actual generated explainer into a readable 4:5 Facebook image.
    Palette is selected randomly each run; caption retains the full detailed text."""
    choices = [i for i in range(len(PALETTES)) if i != previous_palette]
    palette_index = random.choice(choices or list(range(len(PALETTES))))
    bg, accent, highlight, fg = PALETTES[palette_index]
    image = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(image)
    # Decorative color field/header
    draw.rounded_rectangle((-80, -160, W+100, 310), radius=130, fill=accent)
    draw.ellipse((W-270, -100, W+90, 260), fill=highlight)
    draw.rounded_rectangle((42, 38, W-42, H-42), radius=34, outline=highlight, width=3)
    small = _font(27, True); title_font = _font(49, True); body = _font(25); section_font = _font(28, True); footer = _font(19, False)
    draw.text((70, 68), app_name.upper(), font=small, fill=fg)
    draw.text((70, 122), "TECH EXPLAINER", font=_font(21, True), fill=highlight)
    topic = blog.get("technical_topic") or blog.get("original_title") or "Technology explained"
    y = _draw_paragraph(draw, topic, 70, 166, title_font, fg, W-140, max_lines=2, spacing=8)
    summary = blog.get("description", "")
    y = _draw_paragraph(draw, summary, 70, y, body, fg, W-140, max_lines=3, spacing=17)
    # content cards; fit all five sections as concise, source-grounded excerpts
    points = blog.get("points", [])[:5]
    remaining = H - 125 - y - 120
    card_h = max(112, min(154, int(remaining / max(1, len(points)))))
    for i, point in enumerate(points, 1):
        if y + card_h > H-130: break
        draw.rounded_rectangle((62, y, W-62, y+card_h-10), radius=22, fill=(255,255,255), outline=highlight, width=2)
        draw.ellipse((82, y+18, 126, y+62), fill=highlight)
        draw.text((96, y+23), str(i), font=_font(22, True), fill=bg)
        tx = _draw_paragraph(draw, point.get("title", f"Key insight {i}"), 145, y+17, section_font, bg, W-230, max_lines=1, spacing=3)
        # Prioritize the section's own descriptive context, not just its heading.
        available_lines = 3 if card_h >= 140 else 2
        _draw_paragraph(draw, point.get("description", ""), 145, tx, _font(20), bg, W-230, max_lines=available_lines, spacing=0)
        y += card_h
    # Footer source is displayed shortened to fit, while full URL is in the Facebook caption.
    source_host = source_url.replace("https://", "").replace("http://", "").split("/")[0]
    footer_y = H - 111
    draw.line((70, footer_y-14, W-70, footer_y-14), fill=highlight, width=2)
    draw.text((70, footer_y), f"SOURCE: {source_host[:60]}", font=footer, fill=fg)
    draw.text((70, footer_y+31), "Read the full source in the post caption", font=footer, fill=fg)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="JPEG", quality=92, optimize=True)
    return path, palette_index
