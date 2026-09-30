from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
UX_ROOT = ROOT / "assets" / "ux_designs"

# Five fixed UX systems. The generator cycles strictly 1 -> 2 -> 3 -> 4 -> 5 -> 1...
UX_DESIGNS = [
    {
        "id": "clean_modern_green",
        "page": "#F7FBF9", "hero": "#075B4E", "hero2": "#0D806C",
        "text": "#123B35", "muted": "#61756F", "accent": "#16A579",
        "cards": ["#DDF7EA", "#E8E5FF", "#DDF7EA", "#E7F5EF"],
        "try": "#FFF1B8", "try_text": "#624C00", "dark": False,
    },
    {
        "id": "dark_ai_futuristic",
        "page": "#07111F", "hero": "#0B1630", "hero2": "#152E67",
        "text": "#EAF2FF", "muted": "#A8B7D5", "accent": "#5B8CFF",
        "cards": ["#101F3D", "#151A3B", "#102B38", "#1B2148"],
        "try": "#273C70", "try_text": "#F7FAFF", "dark": True,
    },
    {
        "id": "warm_friendly_orange",
        "page": "#FFF9F3", "hero": "#F26A21", "hero2": "#FF9D3F",
        "text": "#4A2A1B", "muted": "#81685A", "accent": "#EF5B2A",
        "cards": ["#FFE7D3", "#FFE8F0", "#FFF0C9", "#EAF7F0"],
        "try": "#FFE7A1", "try_text": "#694600", "dark": False,
    },
    {
        "id": "nature_fresh_green",
        "page": "#F4FAF3", "hero": "#1C6B3C", "hero2": "#3A9A5A",
        "text": "#183B28", "muted": "#607663", "accent": "#21A45A",
        "cards": ["#DFF3DD", "#EAF6D4", "#DDF4EA", "#E8F0DC"],
        "try": "#FFF0A8", "try_text": "#5C4B00", "dark": False,
    },
    {
        "id": "purple_creative_ai",
        "page": "#FAF7FF", "hero": "#41217E", "hero2": "#7C3AED",
        "text": "#281A4D", "muted": "#70648A", "accent": "#6D35E8",
        "cards": ["#EEE7FF", "#F6E5FF", "#E7E7FF", "#F0E8FF"],
        "try": "#FFE9A6", "try_text": "#604700", "dark": False,
    },
]


def rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))


class BlogImage:
    WIDTH = 1080
    HEIGHT = 1350
    MARGIN = 42

    @classmethod
    def font(cls, size, bold=False):
        candidates = [
            ROOT / "assets/fonts/NotoSansDevanagari-CondensedBold.ttf" if bold else ROOT / "assets/fonts/NotoSansDevanagari-Regular.ttf",
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf") if bold else Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ]
        for p in candidates:
            if p.exists():
                return ImageFont.truetype(str(p), size)
        return ImageFont.load_default()

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
    def fit(cls, draw, text, font, width, max_lines):
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
    def illustration(cls, ux_index, section_name):
        """Use the supplied UX artwork as a visual reference/illustration.
        We crop the right side so embedded copy is mostly avoided."""
        ux = UX_DESIGNS[ux_index]
        folder = UX_ROOT / ux["id"]
        path = folder / f"{section_name}.png"
        if not path.exists():
            return None
        try:
            im = Image.open(path).convert("RGBA")
            # Most supplied section designs put the visual on the right.
            crop = im.crop((int(im.width * 0.48), 0, im.width, im.height))
            return crop
        except Exception:
            return None

    @classmethod
    def paste_art(cls, base, art, box, dark=False):
        if art is None:
            return
        x0, y0, x1, y1 = box
        target_w, target_h = x1-x0, y1-y0
        art = ImageOps.contain(art, (target_w, target_h))
        # Soft rounded mask.
        mask = Image.new("L", (art.width, art.height), 0)
        md = ImageDraw.Draw(mask)
        md.rounded_rectangle((0, 0, art.width-1, art.height-1), radius=min(24, art.width//8), fill=255)
        px = x0 + (target_w-art.width)//2
        py = y0 + (target_h-art.height)//2
        base.paste(art, (px, py), mask)

    @classmethod
    def render(cls, blog, path, ux_index=0):
        ux = UX_DESIGNS[ux_index % len(UX_DESIGNS)]
        bg = rgb(ux["page"])
        img = Image.new("RGB", (cls.WIDTH, cls.HEIGHT), bg)
        d = ImageDraw.Draw(img)

        white = "#FFFFFF"
        text = rgb(ux["text"])
        muted = rgb(ux["muted"])
        hero_text = rgb("#FFFFFF")

        # Hero differs strongly by UX.
        if ux["dark"]:
            d.rounded_rectangle((0, 0, cls.WIDTH, 300), radius=0, fill=rgb(ux["hero"]))
            # Futuristic bubbles.
            for cx, cy, r in [(900, 55, 48), (970, 145, 70), (800, 85, 30), (1000, 235, 32)]:
                d.ellipse((cx-r, cy-r, cx+r, cy+r), fill=rgb(ux["hero2"]))
        else:
            d.rounded_rectangle((0, 0, cls.WIDTH, 270), radius=0, fill=rgb(ux["hero"]))
            d.rounded_rectangle((0, 0, cls.WIDTH, 300), radius=0, fill=rgb(ux["hero2"]))

        # Brand
        d.text((cls.MARGIN, 20), "SMART LEARNING LAB", font=cls.font(24, True), fill=hero_text)
        d.text((cls.MARGIN, 52), "LEARN • PRACTICE • GROW", font=cls.font(15), fill=(225, 238, 255))

        # Hero title
        title_font = cls.font(42, True)
        title_lines = cls.fit(d, blog["title"], title_font, 660, 2)
        ty = 94
        for line in title_lines:
            # Highlight title line in a capsule for UX 1/3/4/5.
            if not ux["dark"] and len(title_lines) > 1 and line == title_lines[-1]:
                bbox = d.textbbox((0, 0), line, font=title_font)
                d.rounded_rectangle((cls.MARGIN-8, ty-3, cls.MARGIN+bbox[2]+12, ty+47), radius=16, fill=rgb(ux["accent"]))
                d.text((cls.MARGIN, ty), line, font=title_font, fill=hero_text)
            else:
                d.text((cls.MARGIN, ty), line, font=title_font, fill=hero_text)
            ty += 47

        subtitle = blog.get("subtitle", "")
        sub_lines = cls.fit(d, subtitle, cls.font(17), 640, 2)
        sy = 190
        for line in sub_lines:
            d.text((cls.MARGIN, sy), line, font=cls.font(17), fill=(235, 245, 255))
            sy += 22

        # Hero artwork from supplied UX design.
        hero_art = cls.illustration(ux_index, "01_header_hero")
        cls.paste_art(img, hero_art, (690, 20, 1040, 275), dark=ux["dark"])

        # Intro callout.
        intro_top = 290
        intro_h = 108
        intro_fill = rgb("#112B4A") if ux["dark"] else rgb("#E8F3F8")
        intro_text = white if ux["dark"] else text
        d.rounded_rectangle((cls.MARGIN, intro_top, cls.WIDTH-cls.MARGIN, intro_top+intro_h),
                             radius=24, fill=intro_fill)
        d.ellipse((cls.MARGIN+18, intro_top+25, cls.MARGIN+70, intro_top+77), fill=rgb("#FFC928"))
        d.text((cls.MARGIN+31, intro_top+31), "!", font=cls.font(26, True), fill="#FFFFFF")
        intro_lines = cls.fit(d, blog.get("intro",""), cls.font(17), cls.WIDTH-2*cls.MARGIN-105, 3)
        iy = intro_top+18
        for line in intro_lines:
            d.text((cls.MARGIN+88, iy), line, font=cls.font(17), fill=intro_text)
            iy += 22

        # Cards: two-column, four rows, compact and readable.
        grid_top = 415
        card_w = (cls.WIDTH - 2*cls.MARGIN - 18)//2
        card_h = 184
        gap = 16
        body = cls.font(13)
        bullet = cls.font(12)
        head = cls.font(19, True)

        for i, sec in enumerate(blog["sections"][:8]):
            row, col = divmod(i, 2)
            x = cls.MARGIN + col*(card_w+18)
            y = grid_top + row*(card_h+gap)
            fill = rgb(ux["cards"][i % len(ux["cards"])])
            if ux["dark"]:
                # Add a subtle outline for dark UX.
                d.rounded_rectangle((x, y, x+card_w, y+card_h), radius=20, fill=fill, outline=rgb("#304A79"), width=2)
            else:
                d.rounded_rectangle((x, y, x+card_w, y+card_h), radius=20, fill=fill)

            d.ellipse((x+14,y+14,x+52,y+52), fill=rgb(ux["accent"]))
            nfont=cls.font(15,True)
            nb=d.textbbox((0,0),str(i+1),font=nfont)
            d.text((x+33-(nb[2]-nb[0])/2,y+20),str(i+1),font=nfont,fill="#FFFFFF")

            hlines=cls.fit(d,sec["title"],head,card_w-70,2)
            hy=y+13
            for line in hlines:
                d.text((x+62,hy),line,font=head,fill=rgb(ux["text"]) if not ux["dark"] else (240,246,255))
                hy+=22

            # Small supplied illustration on the right.
            art_name = f"{i+3:02d}_{['what_is_ai','why_use_ai','how_ai_works','simple_tech_stack','beginner_project','implementation','real_world_example','next_level_features'][i]}.png"
            art = cls.illustration(ux_index, art_name)
            if art:
                cls.paste_art(img, art, (x+card_w-125, y+62, x+card_w-12, y+155), dark=ux["dark"])

            max_text_w = card_w-145 if art else card_w-30
            body_lines=cls.fit(d,sec["text"],body,max_text_w,2)
            by=y+62 if len(hlines)==1 else y+82
            for line in body_lines:
                d.text((x+15,by),line,font=body,fill=rgb(ux["text"]) if not ux["dark"] else (220,230,248))
                by+=17
            for point in sec["points"][:3]:
                line=cls.fit(d,"✓ "+point,bullet,max_text_w,1)[0]
                if by<y+card_h-12:
                    d.text((x+15,by),line,font=bullet,fill=rgb(ux["text"]) if not ux["dark"] else (205,220,245))
                    by+=16

        # Try today
        try_y=1165
        d.rounded_rectangle((cls.MARGIN,try_y,cls.WIDTH-cls.MARGIN,1270),radius=22,fill=rgb(ux["try"]))
        d.text((cls.MARGIN+20,try_y+12),"TRY THIS TODAY!",font=cls.font(22,True),fill=rgb(ux["try_text"]))
        lines=cls.fit(d,blog["try_today"],cls.font(14),740,3)
        yy=try_y+45
        for line in lines:
            d.text((cls.MARGIN+20,yy),line,font=cls.font(14),fill=rgb(ux["try_text"]))
            yy+=18
        # CTA
        cta_x=840
        d.rounded_rectangle((cta_x,try_y+28,1035,try_y+77),radius=25,fill=rgb(ux["accent"]))
        d.text((cta_x+24,try_y+40),"Start Now →",font=cls.font(16,True),fill="#FFFFFF")

        # Footer
        if ux["dark"]:
            footer_fill=rgb("#050B18")
        else:
            footer_fill=rgb(ux["hero"])
        d.rectangle((0,1288,cls.WIDTH,1350),fill=footer_fill)
        benefits=["Plan Smarter","Work Faster","Learn Better","Live Happier"]
        bx=48
        for b in benefits:
            d.text((bx,1305),"●",font=cls.font(12,True),fill=rgb("#FFFFFF"))
            d.text((bx+18,1303),b,font=cls.font(13,True),fill="#FFFFFF")
            bx+=225
        d.text((865,1303),"By Nitin Mittal Innovation",font=cls.font(11,True),fill="#FFFFFF")

        path=Path(path)
        path.parent.mkdir(parents=True,exist_ok=True)
        img.save(path,format="JPEG",quality=94,optimize=True)
        return ux
