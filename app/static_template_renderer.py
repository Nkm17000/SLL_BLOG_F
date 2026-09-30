from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_ROOT = ROOT / "assets" / "static_templates"

THEMES = {
    "blue":       {"panel":"#F4FAFF", "card":"#FCFEFF", "text":"#123B93", "muted":"#405B75", "accent":"#1677F2", "cta":"#BDE7FF", "button":"#1677F2"},
    "pink":       {"panel":"#FFF2FB", "card":"#FFFDFE", "text":"#54208F", "muted":"#6B5578", "accent":"#E83E8C", "cta":"#F8C4E2", "button":"#E83E8C"},
    "green":      {"panel":"#F0F9EA", "card":"#FCFFFB", "text":"#0C6B45", "muted":"#4F6657", "accent":"#159A62", "cta":"#D6F3BD", "button":"#159A62"},
    "coral":      {"panel":"#FFF2F4", "card":"#FFFDFD", "text":"#8D174E", "muted":"#6D5260", "accent":"#F23D68", "cta":"#FFD1D8", "button":"#F23D68"},
    "purple_dark": {"panel":"#181A4A", "card":"#FCF9FF", "text":"#1B1D68", "muted":"#665B7A", "accent":"#7C3AED", "cta":"#D8C6F1", "button":"#6D28D9"},
    "gold":       {"panel":"#FFF6DE", "card":"#FFFDF8", "text":"#5A4300", "muted":"#6E6244", "accent":"#E99A00", "cta":"#FBE29A", "button":"#E99A00"},
    "sky":        {"panel":"#F0F8FF", "card":"#FFFFFF", "text":"#14518F", "muted":"#526A83", "accent":"#2377D9", "cta":"#C9EAFF", "button":"#2377D9"},
    "violet":     {"panel":"#F5F0FF", "card":"#FFFFFF", "text":"#472083", "muted":"#685B7B", "accent":"#6D35E8", "cta":"#E7D2FA", "button":"#6D35E8"},
    "cyan":       {"panel":"#F0FAFF", "card":"#FFFFFF", "text":"#174C76", "muted":"#536B7B", "accent":"#1687D9", "cta":"#C9EEFF", "button":"#1687D9"},
    "leaf":       {"panel":"#F1FAEC", "card":"#FFFFFF", "text":"#12624C", "muted":"#526B5E", "accent":"#159A63", "cta":"#D8F3B8", "button":"#159A63"}
}


class StaticTemplateRenderer:
    WIDTH = 1080
    HEIGHT = 1800

    @classmethod
    def font(cls, size: int, bold: bool = False):
        candidates = [
            Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf') if bold else Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
            Path('/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf') if bold else Path('/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf'),
        ]
        for p in candidates:
            if p.exists():
                return ImageFont.truetype(str(p), size)
        return ImageFont.load_default()

    @classmethod
    def text_width(cls, draw, text, size, bold=False):
        f = cls.font(size, bold)
        b = draw.textbbox((0, 0), str(text), font=f)
        return b[2] - b[0]

    @classmethod
    def wrap(cls, draw, text, size, width, bold=False):
        words = str(text or '').replace('\n', ' ').split()
        if not words:
            return ['']
        lines, current = [], words[0]
        for word in words[1:]:
            candidate = current + ' ' + word
            if cls.text_width(draw, candidate, size, bold) <= width:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
        return lines

    @classmethod
    def fit(cls, draw, text, size, width, max_lines, bold=False):
        lines = cls.wrap(draw, text, size, width, bold)
        if len(lines) <= max_lines:
            return lines
        lines = lines[:max_lines]
        last = lines[-1]
        while last and cls.text_width(draw, last + '…', size, bold) > width:
            last = last.rsplit(' ', 1)[0] if ' ' in last else last[:-1]
        lines[-1] = (last or '…') + '…'
        return lines

    @staticmethod
    def hexrgb(value):
        value = value.lstrip('#')
        return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))

    @classmethod
    def rounded_panel(cls, draw, box, fill, radius=24, outline=None, width=1):
        draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

    @classmethod
    def render(cls, blog: dict, path: str | Path, design: dict):
        template = TEMPLATE_ROOT / design["template"]
        if not template.exists():
            raise FileNotFoundError(f"Static UX template missing: {template}")

        img = Image.open(template).convert('RGB').resize((cls.WIDTH, cls.HEIGHT), Image.Resampling.LANCZOS)
        d = ImageDraw.Draw(img)
        theme = THEMES.get(design.get("theme", "blue"), THEMES["blue"])
        panel = cls.hexrgb(theme["panel"])
        card = cls.hexrgb(theme["card"])
        text = cls.hexrgb(theme["text"])
        muted = cls.hexrgb(theme["muted"])
        accent = cls.hexrgb(theme["accent"])
        cta = cls.hexrgb(theme["cta"])
        button = cls.hexrgb(theme["button"])

        # The supplied UX image remains the visual base. These opaque content zones
        # cover only the old copy; all artwork, icons, branding and footer remain static.
        cls.rounded_panel(d, (52, 185, 900, 500), panel, 30)
        title_lines = cls.fit(d, blog.get('title', ''), 43, 680, 3, True)
        y = 220
        for line in title_lines:
            d.text((78, y), line, font=cls.font(43, True), fill=text)
            y += 52
        subtitle = blog.get('subtitle') or blog.get('description') or ''
        for line in cls.fit(d, subtitle, 17, 680, 3, False):
            d.text((80, y + 8), line, font=cls.font(17), fill=muted)
            y += 23

        sections = (blog.get('sections') or [])[:8]
        row_y = [625, 825, 1025, 1225]
        for i in range(8):
            sec = sections[i] if i < len(sections) else {"title": "", "text": "", "points": []}
            row = i // 2
            col = i % 2
            x0 = 145 if col == 0 else 650
            x1 = 500 if col == 0 else 1000
            y0 = row_y[row]
            y1 = y0 + 170

            # Leave the original numbered circle untouched and cover only copy.
            cls.rounded_panel(d, (x0 - 8, y0 - 6, x1 + 35, y1), card, 18)
            title_lines = cls.fit(d, sec.get('title', ''), 19, x1 - x0 - 8, 2, True)
            ty = y0 + 10
            for line in title_lines:
                d.text((x0, ty), line, font=cls.font(19, True), fill=text)
                ty += 23

            body = sec.get('text', '')
            body_lines = cls.fit(d, body, 12, x1 - x0 - 8, 2, False)
            by = ty + 4
            for line in body_lines:
                d.text((x0, by), line, font=cls.font(12), fill=muted)
                by += 16

            for point in (sec.get('points') or [])[:2]:
                if by > y1 - 17:
                    break
                line = cls.fit(d, '• ' + point, 10, x1 - x0 - 8, 1, False)[0]
                d.text((x0, by), line, font=cls.font(10), fill=text)
                by += 14

        # Dynamic CTA copy. Original icon and Start Now button remain visible.
        cls.rounded_panel(d, (140, 1480, 790, 1648), cta, 22)
        d.text((170, 1498), 'TRY THIS TODAY!', font=cls.font(22, True), fill=text)
        cta_text = blog.get('try_today') or 'Pick one small task this week, try it, then review the result.'
        yy = 1535
        for line in cls.fit(d, cta_text, 13, 580, 3, False):
            d.text((170, yy), line, font=cls.font(13), fill=muted)
            yy += 18

        # Keep the original footer and all original illustrations unchanged.
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        img.save(path, format='JPEG', quality=95, optimize=True, progressive=True)
        return path
