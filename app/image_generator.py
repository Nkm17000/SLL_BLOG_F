from __future__ import annotations

import random
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "assets" / "fonts"

THEMES = [
    {"id":"ocean","page":"#F4F8FC","hero1":"#123A8F","hero2":"#1976D2","primary":"#173B8F","accent":"#1769E0","cards":["#FFE8EF","#E5F3FF","#FFF3D6","#E8E5FF"],"try":"#FFF1A8","try_text":"#7A4B00"},
    {"id":"mint","page":"#F3FAF7","hero1":"#087F5B","hero2":"#20A77A","primary":"#086B50","accent":"#099268","cards":["#E2F7EE","#E0F7FA","#F0F9E8","#E8F5E9"],"try":"#FFF4B8","try_text":"#5C4700"},
    {"id":"lavender","page":"#F8F6FC","hero1":"#4C1D95","hero2":"#7C3AED","primary":"#4C1D95","accent":"#7C3AED","cards":["#F3E8FF","#EDE9FE","#E0E7FF","#FAE8FF"],"try":"#FEF3C7","try_text":"#6B4B00"},
    {"id":"sunrise","page":"#FFF9F2","hero1":"#C2410C","hero2":"#F97316","primary":"#9A3412","accent":"#EA580C","cards":["#FFEDD5","#FEF3C7","#FCE7F3","#FFEDD5"],"try":"#FEF08A","try_text":"#704600"},
    {"id":"sky","page":"#F2F9FF","hero1":"#075985","hero2":"#0284C7","primary":"#075985","accent":"#0284C7","cards":["#E0F2FE","#DBEAFE","#E0F7FA","#ECFEFF"],"try":"#FEF3C7","try_text":"#6B4B00"},
    {"id":"coral","page":"#FFF7F5","hero1":"#9F1239","hero2":"#E11D48","primary":"#9F1239","accent":"#E11D48","cards":["#FFE4E6","#FCE7F3","#FFE4E6","#FFF1F2"],"try":"#FEF3C7","try_text":"#6B4B00"},
    {"id":"forest","page":"#F4F9F4","hero1":"#14532D","hero2":"#16A34A","primary":"#166534","accent":"#16A34A","cards":["#DCFCE7","#ECFCCB","#D1FAE5","#E0F2F1"],"try":"#FEF3C7","try_text":"#5C4700"},
    {"id":"indigo","page":"#F5F6FC","hero1":"#1E1B4B","hero2":"#4338CA","primary":"#312E81","accent":"#4F46E5","cards":["#E0E7FF","#EEF2FF","#EDE9FE","#DBEAFE"],"try":"#FEF08A","try_text":"#5C4700"},
    {"id":"teal","page":"#F2FAFA","hero1":"#134E4A","hero2":"#0D9488","primary":"#115E59","accent":"#0F766E","cards":["#CCFBF1","#CFFAFE","#E0F2FE","#D1FAE5"],"try":"#FEF3C7","try_text":"#5C4700"},
    {"id":"berry","page":"#FCF6FA","hero1":"#701A75","hero2":"#C026D3","primary":"#86198F","accent":"#A21CAF","cards":["#FAE8FF","#FCE7F3","#F5D0FE","#FDF2F8"],"try":"#FEF3C7","try_text":"#6B4B00"},
    {"id":"emerald","page":"#F3FAF7","hero1":"#064E3B","hero2":"#059669","primary":"#065F46","accent":"#059669","cards":["#D1FAE5","#DCFCE7","#CCFBF1","#ECFDF5"],"try":"#FEF3C7","try_text":"#5C4700"},
    {"id":"aqua","page":"#F2FAFC","hero1":"#155E75","hero2":"#06B6D4","primary":"#155E75","accent":"#0891B2","cards":["#CFFAFE","#E0F2FE","#CCFBF1","#ECFEFF"],"try":"#FEF3C7","try_text":"#5C4700"},
    {"id":"rose","page":"#FFF7F9","hero1":"#881337","hero2":"#E11D48","primary":"#9F1239","accent":"#E11D48","cards":["#FFE4E6","#FCE7F3","#FFF1F2","#FDF2F8"],"try":"#FEF3C7","try_text":"#6B4B00"},
    {"id":"cobalt","page":"#F4F7FC","hero1":"#172554","hero2":"#2563EB","primary":"#1E3A8A","accent":"#2563EB","cards":["#DBEAFE","#E0F2FE","#E0E7FF","#EFF6FF"],"try":"#FEF08A","try_text":"#5C4700"},
    {"id":"lime","page":"#F7FAF2","hero1":"#365314","hero2":"#65A30D","primary":"#3F6212","accent":"#65A30D","cards":["#ECFCCB","#DCFCE7","#F0FDF4","#FEF9C3"],"try":"#FEF08A","try_text":"#5C4700"},
    {"id":"plum","page":"#FAF7FC","hero1":"#581C87","hero2":"#9333EA","primary":"#6B21A8","accent":"#9333EA","cards":["#F3E8FF","#FAE8FF","#EDE9FE","#F5F3FF"],"try":"#FEF3C7","try_text":"#5C4700"},
    {"id":"midnight","page":"#F4F7FB","hero1":"#0F172A","hero2":"#334155","primary":"#0F172A","accent":"#2563EB","cards":["#E2E8F0","#DBEAFE","#E0F2FE","#EDE9FE"],"try":"#FEF08A","try_text":"#5C4700"},
    {"id":"tropical","page":"#F4FBFA","hero1":"#115E59","hero2":"#0EA5A4","primary":"#115E59","accent":"#0D9488","cards":["#CCFBF1","#DCFCE7","#CFFAFE","#ECFCCB"],"try":"#FEF3C7","try_text":"#5C4700"},
    {"id":"peach","page":"#FFF8F4","hero1":"#9A3412","hero2":"#FB923C","primary":"#9A3412","accent":"#EA580C","cards":["#FFEDD5","#FFE4E6","#FEF3C7","#FFEDD5"],"try":"#FEF08A","try_text":"#704600"},
    {"id":"royal","page":"#F7F5FC","hero1":"#312E81","hero2":"#6366F1","primary":"#3730A3","accent":"#4F46E5","cards":["#EDE9FE","#E0E7FF","#F3E8FF","#EEF2FF"],"try":"#FEF08A","try_text":"#5C4700"},
]


def rgb(hex_color: str):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


class BlogImage:
    WIDTH = 1080
    HEIGHT = 1350
    MARGIN = 42

    @classmethod
    def font(cls, size, bold=False):
        path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        return ImageFont.truetype(path, size)

    @staticmethod
    def clean(value):
        return re.sub(r"[\U00010000-\U0010ffff]", "", str(value or "")).strip()

    @classmethod
    def wrap(cls, draw, text, font, width):
        words = cls.clean(text).split()
        if not words:
            return [""]
        lines, current = [], words[0]
        for word in words[1:]:
            candidate = current + " " + word
            if draw.textbbox((0, 0), candidate, font=font)[2] <= width:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
        return lines

    @classmethod
    def fit_lines(cls, draw, text, font, width, max_lines):
        lines = cls.wrap(draw, text, font, width)
        if len(lines) <= max_lines:
            return lines
        lines = lines[:max_lines]
        last = lines[-1]
        while last and draw.textbbox((0, 0), last + "…", font=font)[2] > width:
            last = last.rsplit(" ", 1)[0] if " " in last else last[:-1]
        lines[-1] = (last or "…") + "…"
        return lines

    @classmethod
    def choose_theme(cls, previous_theme_id=None):
        choices = [t for t in THEMES if t["id"] != previous_theme_id] or THEMES
        return random.SystemRandom().choice(choices)

    @classmethod
    def render(cls, blog, path, theme=None, previous_theme_id=None):
        theme = theme or cls.choose_theme(previous_theme_id)
        theme = {**theme, "text": theme.get("text", "#172554"), "muted": theme.get("muted", "#64748B")}
        img = Image.new("RGB", (cls.WIDTH, cls.HEIGHT), rgb(theme["page"]))
        d = ImageDraw.Draw(img)

        # Header / brand
        d.rounded_rectangle((0, 0, cls.WIDTH, 196), radius=0, fill=rgb(theme["hero1"]))
        brand = cls.font(25, True)
        d.text((cls.MARGIN, 22), "SMART LEARNING LAB", font=brand, fill="white")
        d.text((cls.MARGIN, 58), "LEARN • PRACTICE • GROW", font=cls.font(17), fill=(225, 238, 255))

        # Hero title. Reserve enough room and clip to 2 lines.
        title_font = cls.font(43, True)
        title_lines = cls.fit_lines(d, blog["title"], title_font, cls.WIDTH - 2 * cls.MARGIN, 2)
        y = 94
        for line in title_lines:
            d.text((cls.MARGIN, y), line, font=title_font, fill="white")
            y += 48

        subtitle_font = cls.font(18)
        subtitle_lines = cls.fit_lines(d, blog["subtitle"], subtitle_font, cls.WIDTH - 2 * cls.MARGIN, 1)
        d.text((cls.MARGIN, 166), subtitle_lines[0], font=subtitle_font, fill="white")

        # Intro
        intro_font = cls.font(18)
        intro_lines = cls.fit_lines(d, blog.get("intro", ""), intro_font, cls.WIDTH - 2 * cls.MARGIN - 20, 3)
        y = 218
        for line in intro_lines:
            d.text((cls.MARGIN + 8, y), line, font=intro_font, fill=rgb(theme["text"]))
            y += 25

        # Fixed two-column card grid matching the reference design.
        grid_top = 300
        card_w = (cls.WIDTH - 2 * cls.MARGIN - 20) // 2
        card_h = 195
        col_gap = 20
        row_gap = 16
        body_font = cls.font(14)
        bullet_font = cls.font(13)
        heading_font = cls.font(20, True)

        for i, section in enumerate(blog.get("sections", [])[:8]):
            row = i // 2
            col = i % 2
            x = cls.MARGIN + col * (card_w + col_gap)
            top = grid_top + row * (card_h + row_gap)
            bottom = top + card_h
            fill = rgb(theme["cards"][i % len(theme["cards"])])
            d.rounded_rectangle((x, top, x + card_w, bottom), radius=20, fill=fill)

            # Number circle
            d.ellipse((x + 16, top + 17, x + 52, top + 53), fill=rgb(theme["accent"]))
            num_font = cls.font(16, True)
            num = str(section.get("number", i + 1))
            bbox = d.textbbox((0, 0), num, font=num_font)
            d.text((x + 34 - (bbox[2]-bbox[0])/2, top + 22), num, font=num_font, fill="white")

            # Heading
            heading_x = x + 62
            heading_lines = cls.fit_lines(d, section.get("title", ""), heading_font, card_w - 78, 2)
            hy = top + 14
            for line in heading_lines:
                d.text((heading_x, hy), line, font=heading_font, fill=rgb(theme["primary"]))
                hy += 24

            # Body
            body_lines = cls.fit_lines(d, section.get("text", ""), body_font, card_w - 32, 3)
            ty = top + 63 if len(heading_lines) == 1 else top + 84
            for line in body_lines:
                d.text((x + 16, ty), line, font=body_font, fill=rgb(theme["text"]))
                ty += 20

            # Three bullets, compact.
            for point in section.get("points", [])[:3]:
                lines = cls.fit_lines(d, "• " + point, bullet_font, card_w - 34, 2)
                for line in lines[:2]:
                    if ty > bottom - 18:
                        break
                    d.text((x + 17, ty), line, font=bullet_font, fill=rgb(theme["text"]))
                    ty += 17

        # Try-this box
        try_top = 1142
        try_bottom = 1272
        d.rounded_rectangle((cls.MARGIN, try_top, cls.WIDTH - cls.MARGIN, try_bottom), radius=20, fill=rgb(theme["try"]))
        try_heading = cls.font(22, True)
        d.text((cls.MARGIN + 20, try_top + 15), "TRY THIS TODAY", font=try_heading, fill=rgb(theme["try_text"]))
        try_font = cls.font(15)
        try_lines = cls.fit_lines(d, blog.get("try_today", ""), try_font, cls.WIDTH - 2 * cls.MARGIN - 40, 3)
        ty = try_top + 50
        for line in try_lines:
            d.text((cls.MARGIN + 20, ty), line, font=try_font, fill=rgb(theme["try_text"]))
            ty += 21

        # Footer
        footer = "By Nitin Mittal Innovation"
        footer_font = cls.font(16, True)
        bbox = d.textbbox((0, 0), footer, font=footer_font)
        tw = bbox[2] - bbox[0]
        d.text(((cls.WIDTH - tw) / 2, 1298), footer, font=footer_font, fill=rgb(theme["muted"]))

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        img.save(path, format="JPEG", quality=94, optimize=True)
        return theme
