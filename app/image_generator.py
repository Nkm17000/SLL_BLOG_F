from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SOURCE_ROOT = ROOT / "assets" / "source" / "smart_learning_lab_section_assets"

UX_DESIGNS = [
    {
        "id": "clean_modern_green", "page": "#F5FBF8", "hero": "#0B7D6C", "hero2": "#19A47F",
        "text": "#123B35", "muted": "#60746F", "accent": "#0FA879",
        "cards": ["#DDF6E9", "#E8E4FF", "#DFF5EE", "#EAF4EF"], "try": "#FFF0A8", "try_text": "#5C4B00", "dark": False,
    },
    {
        "id": "dark_ai_futuristic", "page": "#07111F", "hero": "#0A1731", "hero2": "#183A78",
        "text": "#EAF2FF", "muted": "#AAB9D6", "accent": "#5B8CFF",
        "cards": ["#102044", "#171A40", "#102D3C", "#1A244B"], "try": "#263B70", "try_text": "#F7FAFF", "dark": True,
    },
    {
        "id": "warm_friendly_orange", "page": "#FFF9F3", "hero": "#F06B22", "hero2": "#FF9D40",
        "text": "#4A2A1B", "muted": "#81685A", "accent": "#EF5B2A",
        "cards": ["#FFE7D3", "#FFE8F0", "#FFF0C9", "#EAF7F0"], "try": "#FFE6A0", "try_text": "#694600", "dark": False,
    },
    {
        "id": "nature_fresh_green", "page": "#F4FAF3", "hero": "#1C6B3C", "hero2": "#3D9C5B",
        "text": "#183B28", "muted": "#607663", "accent": "#20A35A",
        "cards": ["#DFF3DD", "#EAF6D4", "#DDF4EA", "#E8F0DC"], "try": "#FFF0A8", "try_text": "#5C4B00", "dark": False,
    },
    {
        "id": "purple_creative_ai", "page": "#FAF7FF", "hero": "#41217E", "hero2": "#7C3AED",
        "text": "#281A4D", "muted": "#70648A", "accent": "#6D35E8",
        "cards": ["#EEE7FF", "#F6E5FF", "#E7E7FF", "#F0E8FF"], "try": "#FFE9A6", "try_text": "#604700", "dark": False,
    },
]

SECTION_ASSETS = [
    "04_section_01_what_is_ai/08_ai_robot.png",
    "05_section_02_why_use_ai/09_target.png",
    "06_section_03_how_ai_works/10_ai_chip.png",
    "07_section_04_simple_tech_stack/11_ai_devices.png",
    "08_section_05_beginner_project/12_checklist_target.png",
    "09_section_06_implementation/13_checklist_pencil.png",
    "10_section_07_real_world_example/14_student_studying.png",
    "11_section_08_next_level_features/15_calendar_bell.png",
]


def rgb(value: str):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


class BlogImage:
    WIDTH = 1080
    HEIGHT = 1350
    MARGIN = 48

    @classmethod
    def font(cls, size: int, bold: bool = False, devanagari: bool = False):
        if devanagari:
            candidates = [
                ROOT / "assets/fonts/NotoSansDevanagari-CondensedBold.ttf" if bold else ROOT / "assets/fonts/NotoSansDevanagari-Regular.ttf",
            ]
        else:
            candidates = [
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf") if bold else Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
                Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf") if bold else Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
            ]
        for path in candidates:
            if path.exists():
                return ImageFont.truetype(str(path), size)
        return ImageFont.load_default()

    @staticmethod
    def has_devanagari(text: str) -> bool:
        return bool(re.search(r"[\u0900-\u097F]", str(text or "")))

    @classmethod
    def text_width(cls, draw, text: str, size: int, bold: bool = False):
        total = 0
        # Render each Unicode run using a font that actually contains its glyphs.
        parts = re.findall(r"[\u0900-\u097F]+|[^\u0900-\u097F]+", str(text or ""))
        for part in parts:
            f = cls.font(size, bold, devanagari=cls.has_devanagari(part))
            box = draw.textbbox((0, 0), part, font=f)
            total += box[2] - box[0]
        return total

    @classmethod
    def draw_mixed(cls, draw, xy, text: str, size: int, fill, bold: bool = False):
        x, y = xy
        parts = re.findall(r"[\u0900-\u097F]+|[^\u0900-\u097F]+", str(text or ""))
        for part in parts:
            f = cls.font(size, bold, devanagari=cls.has_devanagari(part))
            draw.text((x, y), part, font=f, fill=fill)
            x += draw.textbbox((0, 0), part, font=f)[2]
        return x

    @classmethod
    def wrap(cls, draw, text: str, size: int, width: int, bold: bool = False):
        words = str(text or "").replace("\n", " ").split()
        if not words:
            return [""]
        lines = []
        current = words[0]
        for word in words[1:]:
            candidate = current + " " + word
            if cls.text_width(draw, candidate, size, bold) <= width:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
        return lines

    @classmethod
    def fit(cls, draw, text: str, size: int, width: int, max_lines: int, bold: bool = False):
        lines = cls.wrap(draw, text, size, width, bold)
        if len(lines) <= max_lines:
            return lines
        lines = lines[:max_lines]
        last = lines[-1]
        while last and cls.text_width(draw, last + "…", size, bold) > width:
            last = last.rsplit(" ", 1)[0] if " " in last else last[:-1]
        lines[-1] = (last or "…") + "…"
        return lines

    @classmethod
    def load_asset(cls, relative: str):
        path = SOURCE_ROOT / relative
        if not path.exists():
            return None
        try:
            return Image.open(path).convert("RGBA")
        except Exception:
            return None

    @classmethod
    def paste_cover(cls, base, asset, box, radius=24, opacity=255):
        if asset is None:
            return
        x0, y0, x1, y1 = box
        w, h = x1 - x0, y1 - y0
        asset = ImageOps.fit(asset, (w, h), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        if opacity != 255:
            alpha = asset.getchannel("A").point(lambda p: p * opacity // 255)
            asset.putalpha(alpha)
        mask = Image.new("L", (w, h), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=255)
        base.paste(asset, (x0, y0), mask)

    @classmethod
    def add_shadow_card(cls, img, box, fill, radius=24, shadow=12, outline=None):
        x0, y0, x1, y1 = box
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        ld.rounded_rectangle((x0 + shadow, y0 + shadow, x1 + shadow, y1 + shadow), radius=radius, fill=(0, 0, 0, 30))
        layer = layer.filter(ImageFilter.GaussianBlur(shadow // 2))
        img.alpha_composite(layer)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=2 if outline else 1)

    @classmethod
    def render(cls, blog: dict, path, ux_index: int = 0):
        ux = UX_DESIGNS[ux_index % len(UX_DESIGNS)]
        bg = rgb(ux["page"])
        img = Image.new("RGBA", (cls.WIDTH, cls.HEIGHT), bg + (255,))
        d = ImageDraw.Draw(img)
        text = rgb(ux["text"])
        muted = rgb(ux["muted"])
        white = (255, 255, 255)

        # ---------- HERO: intentionally follows the supplied UX ----------
        hero_h = 335
        d.rectangle((0, 0, cls.WIDTH, hero_h), fill=rgb(ux["hero"]))
        d.rectangle((0, 255, cls.WIDTH, hero_h), fill=rgb(ux["hero2"]))

        # Decorative blobs.
        for cx, cy, r, col in [(970, 70, 92, ux["hero2"]), (875, 220, 58, ux["accent"]), (1015, 250, 36, "#FFFFFF")]:
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=rgb(col) + ((65 if ux["dark"] else 38),))

        # Brand block.
        logo_icon = cls.load_asset("01_branding/01_logo.png")
        if logo_icon:
            # Crop the book/cap icon from the supplied logo artwork.
            icon = logo_icon.crop((100, 20, 310, 210))
            cls.paste_cover(img, icon, (42, 25, 105, 88), radius=18)
        cls.draw_mixed(d, (120, 25), "SMART LEARNING LAB", 25, white, True)
        cls.draw_mixed(d, (120, 57), "LEARN • PRACTICE • GROW", 14, (220, 245, 238), False)
        cls.draw_mixed(d, (120, 80), "by Nitin Mittal Innovation", 12, (210, 240, 233), False)

        # Title and subtitle on left.
        title_lines = cls.fit(d, blog["title"], 43, 610, 3, True)
        ty = 112
        for idx, line in enumerate(title_lines):
            if idx == len(title_lines) - 1 and not ux["dark"]:
                width = cls.text_width(d, line, 43, True)
                d.rounded_rectangle((cls.MARGIN - 10, ty - 5, min(650, cls.MARGIN + width + 20), ty + 48), radius=18, fill=rgb(ux["accent"]))
            cls.draw_mixed(d, (cls.MARGIN, ty), line, 43, white, True)
            ty += 48

        sub = blog.get("subtitle") or blog.get("description") or "Practical technical learning made simple."
        sub_lines = cls.fit(d, sub, 17, 560, 3, False)
        sy = ty + 6
        for line in sub_lines:
            cls.draw_mixed(d, (cls.MARGIN, sy), line, 17, (236, 250, 246), False)
            sy += 23

        # Hero image: the actual supplied student image, not an embedded UX screenshot.
        hero_asset = cls.load_asset("03_hero/07_student_ai_laptop.png")
        if hero_asset:
            # Add a soft white frame to mimic the original UX composition.
            d.rounded_rectangle((690, 83, 1040, 320), radius=28, fill=(255, 255, 255, 245))
            cls.paste_cover(img, hero_asset, (703, 96, 1027, 307), radius=22)

        # ---------- INTRO CALLOUT ----------
        intro_y = 350
        intro_h = 100
        intro_fill = rgb("#122E49") if ux["dark"] else rgb("#E6F2F7")
        cls.add_shadow_card(img, (cls.MARGIN, intro_y, cls.WIDTH - cls.MARGIN, intro_y + intro_h), intro_fill, radius=25, shadow=8)
        d = ImageDraw.Draw(img)
        d.ellipse((70, intro_y + 24, 122, intro_y + 76), fill=rgb("#FFC928"))
        cls.draw_mixed(d, (88, intro_y + 29), "!", 26, white, True)
        intro_lines = cls.fit(d, blog.get("intro", ""), 16, 820, 3, False)
        iy = intro_y + 18
        for line in intro_lines:
            cls.draw_mixed(d, (145, iy), line, 16, white if ux["dark"] else text, False)
            iy += 22

        # ---------- 8 CONTENT CARDS ----------
        grid_top = 470
        card_w = 480
        card_h = 170
        gap_x = 24
        gap_y = 16
        body_size = 13
        for i, sec in enumerate(blog.get("sections", [])[:8]):
            row, col = divmod(i, 2)
            x = cls.MARGIN + col * (card_w + gap_x)
            y = grid_top + row * (card_h + gap_y)
            fill = rgb(ux["cards"][i % len(ux["cards"])])
            outline = rgb("#31527A") if ux["dark"] else None
            cls.add_shadow_card(img, (x, y, x + card_w, y + card_h), fill, radius=24, shadow=6, outline=outline)
            d = ImageDraw.Draw(img)

            # Number pill.
            d.ellipse((x + 16, y + 15, x + 58, y + 57), fill=rgb(ux["accent"]))
            num = str(i + 1).zfill(2)
            nw = cls.text_width(d, num, 14, True)
            cls.draw_mixed(d, (x + 37 - nw / 2, y + 23), num, 14, white, True)

            # Section title.
            title_x = x + 72
            title_lines = cls.fit(d, sec.get("title", ""), 19, 255, 2, True)
            hy = y + 16
            for line in title_lines:
                cls.draw_mixed(d, (title_x, hy), line, 19, text, True)
                hy += 21

            # Illustration at the right.
            asset = cls.load_asset(SECTION_ASSETS[i])
            if asset:
                # Keep image small so it reads as a real visual, not a text box.
                cls.paste_cover(img, asset, (x + 342, y + 18, x + 462, y + 130), radius=18)

            content_w = 318
            body_lines = cls.fit(d, sec.get("text", ""), body_size, content_w, 2, False)
            by = y + 66 if len(title_lines) == 1 else y + 82
            for line in body_lines:
                cls.draw_mixed(d, (x + 18, by), line, body_size, muted if not ux["dark"] else (210, 224, 247), False)
                by += 17

            for point in (sec.get("points") or [])[:2]:
                if by > y + card_h - 28:
                    break
                point_lines = cls.fit(d, "• " + point, 11, content_w, 1, False)
                cls.draw_mixed(d, (x + 18, by), point_lines[0], 11, text, False)
                by += 15

        # ---------- TRY TODAY ----------
        try_y = 1180
        try_h = 94
        try_fill = rgb(ux["try"])
        cls.add_shadow_card(img, (cls.MARGIN, try_y, cls.WIDTH - cls.MARGIN, try_y + try_h), try_fill, radius=24, shadow=5)
        d = ImageDraw.Draw(img)
        rocket = cls.load_asset("12_try_this_today/16_rocket.png")
        if rocket:
            cls.paste_cover(img, rocket, (54, try_y + 8, 150, try_y + 86), radius=18)
        cls.draw_mixed(d, (165, try_y + 12), "TRY THIS TODAY!", 21, rgb(ux["try_text"]), True)
        try_lines = cls.fit(d, blog.get("try_today", "Start with one small task."), 13, 600, 3, False)
        yy = try_y + 43
        for line in try_lines:
            cls.draw_mixed(d, (165, yy), line, 13, rgb(ux["try_text"]), False)
            yy += 17
        d.rounded_rectangle((825, try_y + 27, 1028, try_y + 76), radius=25, fill=rgb(ux["accent"]))
        cls.draw_mixed(d, (858, try_y + 41), "Start Now →", 16, white, True)

        # ---------- FOOTER BENEFITS ----------
        footer_y = 1278
        d.rectangle((0, footer_y, cls.WIDTH, cls.HEIGHT), fill=rgb(ux["hero"]))
        footer_items = [
            ("Plan Smarter", "13_footer_benefits/17_plan_smarter.png"),
            ("Work Faster", "13_footer_benefits/18_work_faster.png"),
            ("Learn Better", "13_footer_benefits/19_learn_better.png"),
            ("Live Happier", "13_footer_benefits/20_live_happier.png"),
        ]
        for i, (label, asset_path) in enumerate(footer_items):
            cx = 145 + i * 265
            asset = cls.load_asset(asset_path)
            if asset:
                cls.paste_cover(img, asset, (cx - 24, footer_y + 2, cx + 24, footer_y + 48), radius=28)
            cls.draw_mixed(d, (cx - 52, footer_y + 48), label, 10, white, True)

        # Final sanity: convert to RGB for Facebook-compatible JPEG.
        img = img.convert("RGB")
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        img.save(path, format="JPEG", quality=95, optimize=True, progressive=True)
        return path
