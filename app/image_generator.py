from __future__ import annotations
import io, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent.parent
FONT_DIR=ROOT/"assets"/"fonts"

class BlogImage:
    WIDTH=1080
    HEIGHT=1350
    MARGIN=64

    COLORS=[
        (232,244,255),(255,244,218),(235,249,240),
        (244,237,255),(255,232,238),(231,247,248)
    ]

    @classmethod
    def font(cls,size,bold=False,hindi=False):
        if hindi:
            p=FONT_DIR/("NotoSansDevanagari-CondensedBold.ttf" if bold else "NotoSansDevanagari-Regular.ttf")
        else:
            p=Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
        return ImageFont.truetype(str(p),size)

    @staticmethod
    def clean(s):
        return re.sub(r"[\U00010000-\U0010ffff]","",str(s or "")).strip()

    @classmethod
    def wrap(cls,draw,text,font,max_width):
        text=cls.clean(text)
        words=text.split()
        lines=[]; cur=""
        for word in words:
            test=word if not cur else cur+" "+word
            if draw.textbbox((0,0),test,font=font)[2] <= max_width:
                cur=test
            else:
                if cur: lines.append(cur)
                cur=word
        if cur: lines.append(cur)
        return lines or [""]

    @classmethod
    def render(cls,blog,path):
        img=Image.new("RGB",(cls.WIDTH,cls.HEIGHT),(247,249,252))
        d=ImageDraw.Draw(img)

        # Header
        d.rounded_rectangle((0,0,cls.WIDTH,205),radius=0,fill=(22,64,140))
        brand=cls.font(27,True)
        d.text((cls.MARGIN,28),"SMART LEARNING LAB",font=brand,fill="white")
        d.text((cls.MARGIN,72),"LEARN • PRACTICE • GROW",font=cls.font(21),fill=(220,235,255))

        title_font=cls.font(48,True)
        y=112
        for line in cls.wrap(d,blog["title"],title_font,cls.WIDTH-2*cls.MARGIN):
            d.text((cls.MARGIN,y),line,font=title_font,fill="white"); y+=56

        # Hook
        y=230
        hook_font=cls.font(27)
        for line in cls.wrap(d,blog["hook"],hook_font,cls.WIDTH-2*cls.MARGIN):
            d.text((cls.MARGIN,y),line,font=hook_font,fill=(30,45,65)); y+=38
        y+=18

        section_font=cls.font(28,True)
        body_font=cls.font(21)
        bullet_font=cls.font(20)
        card_gap=16

        for i,sec in enumerate(blog["sections"]):
            bullets=sec.get("bullets",[])
            body_lines=cls.wrap(d,sec["body"],body_font,cls.WIDTH-2*cls.MARGIN-44)
            bullet_lines=[]
            for b in bullets:
                bullet_lines.extend(["• "+line for line in cls.wrap(d,b,bullet_font,cls.WIDTH-2*cls.MARGIN-70)])
            h=28+len(cls.wrap(d,sec["heading"],section_font,cls.WIDTH-2*cls.MARGIN-44))*34
            h+=len(body_lines)*29+len(bullet_lines)*27+25
            h=max(h,125)
            if y+h>cls.HEIGHT-190:
                break
            color=cls.COLORS[i%len(cls.COLORS)]
            d.rounded_rectangle((cls.MARGIN,y,cls.WIDTH-cls.MARGIN,y+h),radius=20,fill=color)
            d.ellipse((cls.MARGIN+18,y+18,cls.MARGIN+58,y+58),fill=(35,105,210))
            d.text((cls.MARGIN+29,y+22),str(i+1),font=cls.font(20,True),fill="white")
            ty=y+15
            for line in cls.wrap(d,sec["heading"],section_font,cls.WIDTH-2*cls.MARGIN-80):
                d.text((cls.MARGIN+72,ty),line,font=section_font,fill=(20,45,85)); ty+=34
            ty+=5
            for line in body_lines:
                d.text((cls.MARGIN+22,ty),line,font=body_font,fill=(35,45,55)); ty+=29
            for line in bullet_lines:
                d.text((cls.MARGIN+26,ty),line,font=bullet_font,fill=(35,45,55)); ty+=27
            y+=h+card_gap

        # Try today box
        box_top=min(y+8,cls.HEIGHT-175)
        d.rounded_rectangle((cls.MARGIN,box_top,cls.WIDTH-cls.MARGIN,cls.HEIGHT-72),radius=20,fill=(255,237,165))
        d.text((cls.MARGIN+22,box_top+16),"TRY THIS TODAY",font=cls.font(27,True),fill=(110,70,0))
        lines=cls.wrap(d,blog["try_today"],body_font,cls.WIDTH-2*cls.MARGIN-44)
        ty=box_top+55
        for line in lines[:3]:
            d.text((cls.MARGIN+22,ty),line,font=body_font,fill=(70,55,20)); ty+=29

        footer="By Nitin Mittal Innovation"
        fb=cls.font(19,True)
        tw=d.textbbox((0,0),footer,font=fb)[2]
        d.text(((cls.WIDTH-tw)/2,cls.HEIGHT-48),footer,font=fb,fill=(90,100,110))

        img.save(path,format="JPEG",quality=92,optimize=True)
        return path
