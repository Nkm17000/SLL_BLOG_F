from __future__ import annotations

import random
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "assets" / "fonts"


# 20 complete visual themes. Each topic gets one randomly selected theme.
THEMES = [
    {"id": "ocean", "page": (246, 250, 255), "header": (18, 62, 125), "header2": (35, 116, 210), "text": (28, 42, 61), "muted": (92, 108, 130), "accent": (38, 111, 214), "cards": [(226, 240, 255), (235, 248, 255), (228, 246, 239)], "try": (255, 239, 169), "try_text": (104, 70, 0)},
    {"id": "sunrise", "page": (255, 250, 245), "header": (150, 64, 35), "header2": (232, 118, 55), "text": (61, 40, 34), "muted": (126, 101, 89), "accent": (224, 101, 42), "cards": [(255, 235, 216), (255, 243, 224), (248, 231, 239)], "try": (255, 225, 157), "try_text": (111, 69, 0)},
    {"id": "mint", "page": (246, 252, 249), "header": (20, 94, 79), "header2": (39, 151, 124), "text": (29, 55, 49), "muted": (86, 112, 105), "accent": (25, 139, 111), "cards": [(224, 247, 239), (232, 250, 244), (239, 245, 220)], "try": (250, 235, 168), "try_text": (79, 70, 0)},
    {"id": "lavender", "page": (250, 248, 255), "header": (73, 54, 126), "header2": (122, 91, 194), "text": (47, 39, 67), "muted": (105, 96, 124), "accent": (113, 83, 189), "cards": [(239, 232, 255), (245, 238, 255), (230, 242, 255)], "try": (255, 232, 173), "try_text": (94, 67, 0)},
    {"id": "coral", "page": (255, 248, 248), "header": (135, 48, 67), "header2": (219, 83, 99), "text": (62, 39, 45), "muted": (125, 91, 99), "accent": (210, 75, 93), "cards": [(255, 226, 231), (255, 239, 224), (237, 235, 255)], "try": (255, 232, 164), "try_text": (96, 63, 0)},
    {"id": "sky", "page": (244, 251, 255), "header": (23, 88, 142), "header2": (45, 162, 211), "text": (28, 50, 65), "muted": (87, 113, 130), "accent": (35, 145, 205), "cards": [(221, 242, 255), (230, 249, 250), (239, 238, 255)], "try": (255, 235, 168), "try_text": (91, 68, 0)},
    {"id": "forest", "page": (247, 251, 247), "header": (34, 91, 58), "header2": (77, 151, 86), "text": (34, 54, 40), "muted": (90, 112, 94), "accent": (58, 137, 72), "cards": [(224, 243, 226), (235, 248, 229), (244, 239, 211)], "try": (255, 235, 166), "try_text": (82, 65, 0)},
    {"id": "indigo", "page": (247, 248, 255), "header": (44, 48, 111), "header2": (83, 91, 190), "text": (36, 39, 69), "muted": (93, 98, 130), "accent": (75, 83, 181), "cards": [(229, 232, 255), (236, 244, 255), (237, 251, 245)], "try": (255, 236, 168), "try_text": (89, 67, 0)},
    {"id": "teal", "page": (245, 252, 252), "header": (17, 92, 95), "header2": (27, 156, 155), "text": (29, 57, 58), "muted": (86, 113, 113), "accent": (24, 145, 145), "cards": [(222, 246, 245), (232, 250, 242), (239, 240, 255)], "try": (255, 236, 167), "try_text": (82, 67, 0)},
    {"id": "royal", "page": (249, 249, 255), "header": (43, 36, 106), "header2": (89, 72, 190), "text": (42, 38, 67), "muted": (100, 95, 126), "accent": (85, 69, 184), "cards": [(235, 230, 255), (228, 243, 255), (240, 247, 229)], "try": (255, 235, 166), "try_text": (88, 67, 0)},
    {"id": "peach", "page": (255, 250, 247), "header": (125, 65, 45), "header2": (220, 126, 84), "text": (62, 45, 39), "muted": (126, 101, 91), "accent": (209, 112, 73), "cards": [(255, 232, 218), (255, 241, 227), (239, 235, 255)], "try": (255, 230, 163), "try_text": (99, 64, 0)},
    {"id": "aqua", "page": (244, 252, 255), "header": (17, 83, 113), "header2": (20, 166, 184), "text": (27, 52, 64), "muted": (83, 111, 125), "accent": (21, 151, 172), "cards": [(220, 245, 253), (228, 249, 244), (237, 236, 255)], "try": (255, 236, 165), "try_text": (82, 65, 0)},
    {"id": "plum", "page": (253, 248, 253), "header": (103, 44, 101), "header2": (177, 77, 157), "text": (59, 38, 58), "muted": (119, 90, 117), "accent": (169, 69, 150), "cards": [(249, 226, 245), (235, 232, 255), (229, 247, 242)], "try": (255, 235, 167), "try_text": (91, 64, 0)},
    {"id": "lime", "page": (250, 253, 244), "header": (71, 105, 25), "header2": (137, 173, 45), "text": (50, 61, 31), "muted": (101, 113, 80), "accent": (119, 157, 34), "cards": [(236, 248, 211), (228, 244, 235), (239, 235, 255)], "try": (255, 233, 163), "try_text": (87, 67, 0)},
    {"id": "midnight", "page": (245, 247, 252), "header": (27, 38, 69), "header2": (61, 89, 159), "text": (30, 39, 57), "muted": (91, 101, 121), "accent": (59, 88, 165), "cards": [(225, 234, 255), (232, 246, 241), (245, 234, 251)], "try": (255, 235, 165), "try_text": (84, 65, 0)},
    {"id": "rose", "page": (255, 249, 252), "header": (133, 46, 81), "header2": (210, 86, 126), "text": (63, 39, 49), "muted": (126, 91, 104), "accent": (201, 75, 117), "cards": [(255, 225, 237), (255, 240, 225), (232, 239, 255)], "try": (255, 231, 164), "try_text": (93, 63, 0)},
    {"id": "cobalt", "page": (246, 249, 255), "header": (20, 67, 139), "header2": (43, 119, 221), "text": (27, 44, 65), "muted": (88, 107, 131), "accent": (37, 105, 208), "cards": [(224, 237, 255), (234, 247, 255), (236, 247, 231)], "try": (255, 237, 167), "try_text": (87, 67, 0)},
    {"id": "emerald", "page": (246, 253, 250), "header": (13, 91, 66), "header2": (34, 158, 112), "text": (27, 56, 47), "muted": (83, 112, 100), "accent": (27, 144, 100), "cards": [(220, 247, 236), (231, 248, 255), (244, 238, 214)], "try": (255, 235, 166), "try_text": (78, 66, 0)},
    {"id": "berry", "page": (251, 248, 255), "header": (91, 41, 119), "header2": (154, 78, 194), "text": (50, 38, 61), "muted": (104, 91, 116), "accent": (146, 70, 187), "cards": [(242, 226, 255), (228, 240, 255), (232, 248, 239)], "try": (255, 234, 166), "try_text": (87, 64, 0)},
]


class BlogImage:
    WIDTH = 1080
    HEIGHT = 1350
    MARGIN = 64

    @classmethod
    def font(cls, size, bold=False, hindi=False):
        if hindi:
            p = FONT_DIR / ("NotoSansDevanagari-CondensedBold.ttf" if bold else "NotoSansDevanagari-Regular.ttf")
        else:
            p = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
        return ImageFont.truetype(str(p), size)

    @staticmethod
    def clean(s):
        return re.sub(r"[\U00010000-\U0010ffff]", "", str(s or "")).strip()

    @classmethod
    def wrap(cls, draw, text, font, max_width):
        text = cls.clean(text)
        words = text.split()
        lines, cur = [], ""
        for word in words:
            test = word if not cur else cur + " " + word
            if draw.textbbox((0, 0), test, font=font)[2] <= max_width:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines or [""]

    @classmethod
    def choose_theme(cls, previous_theme_id=None):
        choices = [t for t in THEMES if t["id"] != previous_theme_id] or THEMES
        return random.SystemRandom().choice(choices)

    @classmethod
    def render(cls, blog, path, theme=None, previous_theme_id=None):
        theme = theme or cls.choose_theme(previous_theme_id)
        img = Image.new("RGB", (cls.WIDTH, cls.HEIGHT), theme["page"])
        d = ImageDraw.Draw(img)

        d.rectangle((0, 0, cls.WIDTH, 205), fill=theme["header"])
        brand = cls.font(27, True)
        d.text((cls.MARGIN, 28), "SMART LEARNING LAB", font=brand, fill="white")
        d.text((cls.MARGIN, 72), "LEARN • PRACTICE • GROW", font=cls.font(21), fill=(225, 238, 255))

        title_font = cls.font(48, True)
        y = 112
        for line in cls.wrap(d, blog["title"], title_font, cls.WIDTH - 2 * cls.MARGIN):
            d.text((cls.MARGIN, y), line, font=title_font, fill="white")
            y += 56

        y = 230
        hook_font = cls.font(27)
        for line in cls.wrap(d, blog["hook"], hook_font, cls.WIDTH - 2 * cls.MARGIN):
            d.text((cls.MARGIN, y), line, font=hook_font, fill=theme["text"])
            y += 38
        y += 18

        section_font = cls.font(28, True)
        body_font = cls.font(21)
        bullet_font = cls.font(20)
        card_gap = 16

        for i, sec in enumerate(blog["sections"]):
            bullets = sec.get("bullets", [])
            body_lines = cls.wrap(d, sec["body"], body_font, cls.WIDTH - 2 * cls.MARGIN - 44)
            bullet_lines = []
            for b in bullets:
                bullet_lines.extend(["• " + line for line in cls.wrap(d, b, bullet_font, cls.WIDTH - 2 * cls.MARGIN - 70)])
            h = 28 + len(cls.wrap(d, sec["heading"], section_font, cls.WIDTH - 2 * cls.MARGIN - 44)) * 34
            h += len(body_lines) * 29 + len(bullet_lines) * 27 + 25
            h = max(h, 125)
            if y + h > cls.HEIGHT - 190:
                break
            color = theme["cards"][i % len(theme["cards"])]
            d.rounded_rectangle((cls.MARGIN, y, cls.WIDTH - cls.MARGIN, y + h), radius=20, fill=color)
            d.ellipse((cls.MARGIN + 18, y + 18, cls.MARGIN + 58, y + 58), fill=theme["accent"])
            d.text((cls.MARGIN + 29, y + 22), str(i + 1), font=cls.font(20, True), fill="white")
            ty = y + 15
            for line in cls.wrap(d, sec["heading"], section_font, cls.WIDTH - 2 * cls.MARGIN - 80):
                d.text((cls.MARGIN + 72, ty), line, font=section_font, fill=theme["header"])
                ty += 34
            ty += 5
            for line in body_lines:
                d.text((cls.MARGIN + 22, ty), line, font=body_font, fill=theme["text"])
                ty += 29
            for line in bullet_lines:
                d.text((cls.MARGIN + 26, ty), line, font=bullet_font, fill=theme["text"])
                ty += 27
            y += h + card_gap

        box_top = min(y + 8, cls.HEIGHT - 175)
        d.rounded_rectangle((cls.MARGIN, box_top, cls.WIDTH - cls.MARGIN, cls.HEIGHT - 72), radius=20, fill=theme["try"])
        d.text((cls.MARGIN + 22, box_top + 16), "TRY THIS TODAY", font=cls.font(27, True), fill=theme["try_text"])
        lines = cls.wrap(d, blog["try_today"], body_font, cls.WIDTH - 2 * cls.MARGIN - 44)
        ty = box_top + 55
        for line in lines[:3]:
            d.text((cls.MARGIN + 22, ty), line, font=body_font, fill=theme["try_text"])
            ty += 29

        footer = "By Nitin Mittal Innovation"
        fb = cls.font(19, True)
        tw = d.textbbox((0, 0), footer, font=fb)[2]
        d.text(((cls.WIDTH - tw) / 2, cls.HEIGHT - 48), footer, font=fb, fill=theme["muted"])

        img.save(path, format="JPEG", quality=92, optimize=True)
        return theme
