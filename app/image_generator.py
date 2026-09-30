from __future__ import annotations

import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SOURCE_ROOT = ROOT / "assets" / "source" / "smart_learning_lab_section_assets"

UX_DESIGNS = [
    {"id":"clean_modern_green","name":"Clean Modern Green"},
    {"id":"dark_ai_futuristic","name":"Dark AI Futuristic"},
    {"id":"warm_friendly_orange","name":"Warm Friendly Orange"},
    {"id":"nature_fresh_green","name":"Nature Fresh Green"},
    {"id":"purple_creative_ai","name":"Purple Creative AI"},
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
FOOTER_ASSETS = [
    ("Plan Smarter", "13_footer_benefits/17_plan_smarter.png"),
    ("Work Faster", "13_footer_benefits/18_work_faster.png"),
    ("Learn Better", "13_footer_benefits/19_learn_better.png"),
    ("Live Happier", "13_footer_benefits/20_live_happier.png"),
]


def rgb(v):
    v=v.lstrip('#'); return tuple(int(v[i:i+2],16) for i in (0,2,4))

class BlogImage:
    WIDTH, HEIGHT, MARGIN = 1080, 1350, 48

    @classmethod
    def font(cls,size,bold=False,devanagari=False):
        if devanagari:
            p=ROOT/"assets/fonts/NotoSansDevanagari-CondensedBold.ttf" if bold else ROOT/"assets/fonts/NotoSansDevanagari-Regular.ttf"
            if p.exists(): return ImageFont.truetype(str(p),size)
        candidates=[
            Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf') if bold else Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
            Path('/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf') if bold else Path('/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf')]
        for p in candidates:
            if p.exists(): return ImageFont.truetype(str(p),size)
        return ImageFont.load_default()

    @staticmethod
    def has_devanagari(text): return bool(re.search(r'[\u0900-\u097F]',str(text or '')))

    @classmethod
    def text_width(cls,d,text,size,bold=False):
        total=0
        for part in re.findall(r'[\u0900-\u097F]+|[^\u0900-\u097F]+',str(text or '')):
            f=cls.font(size,bold,cls.has_devanagari(part)); b=d.textbbox((0,0),part,font=f); total+=b[2]-b[0]
        return total

    @classmethod
    def draw_mixed(cls,d,xy,text,size,fill,bold=False):
        x,y=xy
        for part in re.findall(r'[\u0900-\u097F]+|[^\u0900-\u097F]+',str(text or '')):
            f=cls.font(size,bold,cls.has_devanagari(part)); d.text((x,y),part,font=f,fill=fill)
            x+=d.textbbox((0,0),part,font=f)[2]
        return x

    @classmethod
    def wrap(cls,d,text,size,width,bold=False):
        words=str(text or '').replace('\n',' ').split()
        if not words:return ['']
        lines=[]; cur=words[0]
        for w in words[1:]:
            c=cur+' '+w
            if cls.text_width(d,c,size,bold)<=width: cur=c
            else: lines.append(cur); cur=w
        lines.append(cur); return lines

    @classmethod
    def fit(cls,d,text,size,width,max_lines,bold=False):
        lines=cls.wrap(d,text,size,width,bold)
        if len(lines)<=max_lines:return lines
        lines=lines[:max_lines]; last=lines[-1]
        while last and cls.text_width(d,last+'…',size,bold)>width:
            last=last.rsplit(' ',1)[0] if ' ' in last else last[:-1]
        lines[-1]=(last or '…')+'…'; return lines

    @classmethod
    def load_asset(cls,relative):
        p=SOURCE_ROOT/relative
        if not p.exists(): return None
        try:return Image.open(p).convert('RGBA')
        except Exception:return None

    @classmethod
    def paste_cover(cls,base,asset,box,radius=20):
        if asset is None:return
        x0,y0,x1,y1=box; w,h=x1-x0,y1-y0
        asset=ImageOps.fit(asset,(w,h),method=Image.Resampling.LANCZOS)
        mask=Image.new('L',(w,h),0); ImageDraw.Draw(mask).rounded_rectangle((0,0,w-1,h-1),radius=radius,fill=255)
        base.paste(asset,(x0,y0),mask)

    @classmethod
    def shadow_card(cls,img,box,fill,radius=24,shadow=8,outline=None):
        x0,y0,x1,y1=box
        layer=Image.new('RGBA',img.size,(0,0,0,0)); ld=ImageDraw.Draw(layer)
        ld.rounded_rectangle((x0+shadow,y0+shadow,x1+shadow,y1+shadow),radius=radius,fill=(0,0,0,32))
        img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(max(2,shadow//2))))
        d=ImageDraw.Draw(img); d.rounded_rectangle(box,radius=radius,fill=fill,outline=outline,width=2 if outline else 1)

    @classmethod
    def brand(cls,img,d,x,y,fg,sub):
        logo=cls.load_asset('01_branding/01_logo.png')
        if logo: cls.paste_cover(img,logo.crop((100,20,310,210)),(x,y,x+62,y+62),radius=18)
        cls.draw_mixed(d,(x+78,y-1),'SMART LEARNING LAB',24,fg,True)
        cls.draw_mixed(d,(x+78,y+28),'LEARN • PRACTICE • GROW',13,sub,False)
        cls.draw_mixed(d,(x+78,y+48),'by Nitin Mittal Innovation',11,sub,False)

    @classmethod
    def title(cls,d,blog,x,y,width,size,fg,accent=None):
        lines=cls.fit(d,blog['title'],size,width,3,True); yy=y
        for i,line in enumerate(lines):
            if accent and i==len(lines)-1:
                w=cls.text_width(d,line,size,True)
                d.rounded_rectangle((x-8,yy-4,min(x+w+14,x+width+10),yy+size+10),radius=16,fill=rgb(accent))
            cls.draw_mixed(d,(x,yy),line,size,fg,True); yy+=size+5
        return yy

    @classmethod
    def card_text(cls,img,sec,i,box,theme,style='normal'):
        d=ImageDraw.Draw(img); x,y,x1,y1=box; w=x1-x; h=y1-y
        fill,fg,muted,accent=map(rgb,theme)
        cls.shadow_card(img,box,fill,radius=22,shadow=6)
        d=ImageDraw.Draw(img)
        if style=='dark':
            d.rounded_rectangle((x+14,y+14,x+58,y+58),radius=14,fill=accent)
            cls.draw_mixed(d,(x+27,y+22),f'{i+1:02d}',14,(255,255,255),True)
            tx=x+72; iw=108
        elif style=='nature':
            d.ellipse((x+15,y+15,x+59,y+59),fill=accent)
            cls.draw_mixed(d,(x+28,y+23),f'{i+1}',14,(255,255,255),True)
            tx=x+72; iw=112
        elif style=='purple':
            d.rounded_rectangle((x+15,y+14,x+65,y+64),radius=16,fill=accent)
            cls.draw_mixed(d,(x+31,y+23),f'{i+1:02d}',13,(255,255,255),True)
            tx=x+80; iw=112
        else:
            d.ellipse((x+16,y+15,x+58,y+57),fill=accent)
            cls.draw_mixed(d,(x+29,y+23),f'{i+1:02d}',13,(255,255,255),True)
            tx=x+72; iw=112
        title_w=w-iw-90
        tl=cls.fit(d,sec.get('title',''),18,title_w,2,True); yy=y+14
        for line in tl: cls.draw_mixed(d,(tx,yy),line,18,fg,True); yy+=20
        asset=cls.load_asset(SECTION_ASSETS[i])
        if asset: cls.paste_cover(img,asset,(x1-iw-10,y+18,x1-10,y+18+iw),radius=16)
        body_w=w-iw-35
        by=y+66 if len(tl)==1 else y+86
        for line in cls.fit(d,sec.get('text',''),11,body_w,2,False):
            if by>y+h-38:break
            cls.draw_mixed(d,(x+18,by),line,11,muted,False); by+=15
        for p in (sec.get('points') or [])[:2]:
            if by>y+h-22:break
            line=cls.fit(d,'• '+p,10,body_w,1,False)[0]
            cls.draw_mixed(d,(x+18,by),line,10,fg,False); by+=14

    @classmethod
    def intro(cls,img,blog,y,theme,icon='!'):
        d=ImageDraw.Draw(img); fill,fg,muted,accent=map(rgb,theme)
        box=(48,y,1032,y+88); cls.shadow_card(img,box,fill,radius=24,shadow=7); d=ImageDraw.Draw(img)
        d.ellipse((70,y+18,122,y+70),fill=accent); cls.draw_mixed(d,(88,y+23),icon,24,(255,255,255),True)
        lines=cls.fit(d,blog.get('intro',''),15,820,3,False); yy=y+16
        for line in lines: cls.draw_mixed(d,(145,yy),line,15,fg,False); yy+=20

    @classmethod
    def try_today(cls,img,blog,y,theme,style=0):
        d=ImageDraw.Draw(img); fill,fg,muted,accent=map(rgb,theme)
        if style==1:
            d.rounded_rectangle((38,y,1042,y+102),radius=34,fill=fill,outline=accent,width=2)
            cls.draw_mixed(d,(70,y+14),'BUILD IT TODAY',21,fg,True)
            for j,line in enumerate(cls.fit(d,blog.get('try_today','Start with one small task.'),12,650,2,False)): cls.draw_mixed(d,(70,y+48+j*17),line,12,muted,False)
            d.rounded_rectangle((810,y+26,1015,y+75),radius=25,fill=accent); cls.draw_mixed(d,(850,y+39),'TRY IT →',15,(255,255,255),True)
        elif style==2:
            d.rectangle((0,y,1080,y+96),fill=accent); cls.draw_mixed(d,(55,y+12),'YOUR NEXT SMALL STEP',20,(255,255,255),True)
            cls.draw_mixed(d,(55,y+45),cls.fit(d,blog.get('try_today','Start with one small task.'),12,740,2,False)[0],12,(255,255,255),False)
            d.rounded_rectangle((835,y+25,1025,y+70),radius=22,fill=(255,255,255)); cls.draw_mixed(d,(874,y+38),'START →',14,fg,True)
        else:
            cls.shadow_card(img,(48,y,1032,y+94),fill,radius=24,shadow=5)
            d=ImageDraw.Draw(img); cls.draw_mixed(d,(75,y+12),'TRY THIS TODAY!',20,fg,True)
            lines=cls.fit(d,blog.get('try_today','Start with one small task.'),12,640,2,False)
            for j,line in enumerate(lines): cls.draw_mixed(d,(75,y+43+j*17),line,12,muted,False)
            d.rounded_rectangle((825,y+24,1025,y+72),radius=24,fill=accent); cls.draw_mixed(d,(864,y+37),'Start Now →',15,(255,255,255),True)

    @classmethod
    def footer(cls,img,y,theme,style=0):
        fill=rgb(theme[0])
        fg=theme[1] if isinstance(theme[1], tuple) else rgb(theme[1])
        muted=theme[2] if isinstance(theme[2], tuple) else rgb(theme[2])
        accent=rgb(theme[3])
        d=ImageDraw.Draw(img)
        d.rectangle((0,y,1080,1350),fill=fill)
        if style==1:
            cls.draw_mixed(d,(48,y+10),'SMART LEARNING LAB',18,fg,True)
            for i,(label,p) in enumerate(FOOTER_ASSETS):
                x=60+i*255; a=cls.load_asset(p)
                if a: cls.paste_cover(img,a,(x,y+42,x+48,y+90),radius=24)
                cls.draw_mixed(d,(x+58,y+56),label,11,fg,True)
        else:
            for i,(label,p) in enumerate(FOOTER_ASSETS):
                cx=145+i*265; a=cls.load_asset(p)
                if a: cls.paste_cover(img,a,(cx-24,y+3,cx+24,y+51),radius=24)
                cls.draw_mixed(d,(cx-52,y+54),label,10,fg,True)

    @classmethod
    def render_ux1(cls,blog,path):
        # Clean modern green: matches the supplied working reference.
        img=Image.new('RGBA',(cls.WIDTH,cls.HEIGHT),rgb('#F5FBF8')+(255,)); d=ImageDraw.Draw(img)
        d.rectangle((0,0,1080,335),fill=rgb('#0B7D6C')); d.rectangle((0,255,1080,335),fill=rgb('#19A47F'))
        d.ellipse((875,-20,1060,165),fill=rgb('#19A47F')); cls.brand(img,d,42,25,(255,255,255),(220,245,238))
        cls.title(d,blog,48,112,610,43,(255,255,255),'#19A47F')
        sub=blog.get('subtitle') or blog.get('description',''); sy=255
        for line in cls.fit(d,sub,17,560,2,False): cls.draw_mixed(d,(48,sy),line,17,(236,250,246),False); sy+=22
        hero=cls.load_asset('03_hero/07_student_ai_laptop.png')
        if hero:
            d.rounded_rectangle((690,75,1040,320),radius=28,fill=(255,255,255)); cls.paste_cover(img,hero,(703,88,1027,307),radius=22)
        cls.intro(img,blog,350,('#E6F2F7','#123B35','#60746F','#FFC928'))
        theme=('#DDF6E9','#123B35','#60746F','#0FA879')
        for i,s in enumerate(blog.get('sections',[])[:8]):
            r,c=divmod(i,2); cls.card_text(img,s,i,(48+c*504,455+r*150,528+c*504,595+r*150),theme if i%2==0 else ('#E8E4FF','#123B35','#60746F','#0FA879'))
        cls.try_today(img,blog,1078,('#FFF0A8','#5C4B00','#7A6B31','#0FA879'))
        cls.footer(img,1260,('#0B7D6C',(255,255,255),(220,245,238),'#19A47F'))
        return cls.save(img,path)

    @classmethod
    def render_ux2(cls,blog,path):
        # Dark futuristic: neon grid, glass panels, asymmetric hero.
        img=Image.new('RGBA',(1080,1350),rgb('#060B18')+(255,)); d=ImageDraw.Draw(img)
        for x in range(0,1081,54): d.line((x,0,x,1350),fill=(50,80,130,45),width=1)
        for y in range(0,1351,54): d.line((0,y,1080,y),fill=(50,80,130,45),width=1)
        d.rounded_rectangle((28,22,1052,310),radius=32,fill=rgb('#0B1730'),outline=rgb('#3559A8'),width=2)
        cls.brand(img,d,48,40,(235,244,255),(156,181,225)); cls.title(d,blog,48,118,600,42,(245,248,255),'#5B8CFF')
        hero=cls.load_asset('03_hero/07_student_ai_laptop.png')
        if hero:
            d.ellipse((735,78,1018,361),fill=rgb('#12244A'),outline=rgb('#5B8CFF'),width=3); cls.paste_cover(img,hero,(760,103,993,280),radius=30)
        cls.intro(img,blog,330,('#0D1B34','#EAF2FF','#AAB9D6','#5B8CFF'),'>')
        theme=('#0E1A31','#EAF2FF','#AAB9D6','#5B8CFF')
        for i,s in enumerate(blog.get('sections',[])[:8]):
            r,c=divmod(i,2); cls.card_text(img,s,i,(42+c*498,435+r*152,540+c*498,579+r*152),theme,'dark')
        cls.try_today(img,blog,1085,('#14284A','#EAF2FF','#AAB9D6','#5B8CFF'),1)
        cls.footer(img,1210,('#07111F',(234,242,255),(170,185,214),'#5B8CFF'),1)
        return cls.save(img,path)

    @classmethod
    def render_ux3(cls,blog,path):
        # Warm friendly orange: paper-like background, oversized orange hero and playful cards.
        img=Image.new('RGBA',(1080,1350),rgb('#FFF8EF')+(255,)); d=ImageDraw.Draw(img)
        d.rounded_rectangle((20,20,1060,340),radius=42,fill=rgb('#F16A24'))
        d.ellipse((805,-45,1110,260),fill=rgb('#FF9D40')); d.ellipse((-80,245,170,470),fill=rgb('#FFD7AE'))
        cls.brand(img,d,52,45,(255,255,255),(255,235,215)); cls.title(d,blog,52,120,620,41,(255,255,255),'#E95016')
        hero=cls.load_asset('03_hero/07_student_ai_laptop.png')
        if hero:
            d.rounded_rectangle((700,112,1018,318),radius=34,fill=(255,246,236)); cls.paste_cover(img,hero,(714,126,1004,302),radius=28)
        cls.intro(img,blog,365,('#FFF0E3','#4A2A1B','#81685A','#F06B22'),'✓')
        fills=['#FFE7D3','#FFE8F0','#FFF0C9','#EAF7F0']; theme_base=['#4A2A1B','#81685A','#EF5B2A']
        for i,s in enumerate(blog.get('sections',[])[:8]):
            r,c=divmod(i,2); cls.card_text(img,s,i,(38+c*502,472+r*145,540+c*502,610+r*145),(fills[i%4],*theme_base),'normal')
        cls.try_today(img,blog,1095,('#FFE6A0','#694600','#80613A','#EF5B2A'),2)
        cls.footer(img,1210,('#F06B22',(255,255,255),(255,235,215),'#FF9D40'),1)
        return cls.save(img,path)

    @classmethod
    def render_ux4(cls,blog,path):
        # Nature fresh green: leafy corners, organic cards, timeline-like numbering.
        img=Image.new('RGBA',(1080,1350),rgb('#F4FAF3')+(255,)); d=ImageDraw.Draw(img)
        d.rectangle((0,0,1080,330),fill=rgb('#1C6B3C')); d.rectangle((0,285,1080,330),fill=rgb('#3D9C5B'))
        for cx,cy,r in [(100,40,90),(1010,90,120),(920,260,70)]: d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(61,156,91,80))
        cls.brand(img,d,44,35,(255,255,255),(215,244,220)); cls.title(d,blog,48,110,610,41,(255,255,255),'#3D9C5B')
        hero=cls.load_asset('03_hero/07_student_ai_laptop.png')
        if hero:
            d.rounded_rectangle((710,92,1025,300),radius=70,fill=(235,250,235)); cls.paste_cover(img,hero,(724,106,1011,286),radius=58)
        cls.intro(img,blog,350,('#E7F4E5','#183B28','#607663','#20A35A'),'•')
        theme=('#DFF3DD','#183B28','#607663','#20A35A'); theme2=('#EAF6D4','#183B28','#607663','#20A35A')
        d=ImageDraw.Draw(img); d.line((540,455,540,1060),fill=rgb('#B8DDBB'),width=5)
        for i,s in enumerate(blog.get('sections',[])[:8]):
            r,c=divmod(i,2); box=(45+c*500,465+r*145,535+c*500,603+r*145)
            cls.card_text(img,s,i,box,theme if i%2==0 else theme2,'nature')
        cls.try_today(img,blog,1090,('#FFF0A8','#5C4B00','#7A6B31','#20A35A'),0)
        cls.footer(img,1210,('#1C6B3C',(255,255,255),(215,244,220),'#3D9C5B'))
        return cls.save(img,path)

    @classmethod
    def render_ux5(cls,blog,path):
        # Purple creative AI: diagonal header, floating panels, lavender palette.
        img=Image.new('RGBA',(1080,1350),rgb('#FAF7FF')+(255,)); d=ImageDraw.Draw(img)
        d.polygon([(0,0),(1080,0),(1080,300),(0,370)],fill=rgb('#41217E'))
        d.polygon([(0,260),(1080,200),(1080,330),(0,420)],fill=rgb('#7C3AED'))
        cls.brand(img,d,44,34,(255,255,255),(235,225,255)); cls.title(d,blog,48,112,610,40,(255,255,255),'#7C3AED')
        hero=cls.load_asset('03_hero/07_student_ai_laptop.png')
        if hero:
            d.rounded_rectangle((718,72,1028,295),radius=38,fill=(255,255,255,235)); cls.paste_cover(img,hero,(733,87,1013,278),radius=30)
        cls.intro(img,blog,350,('#F0E8FF','#281A4D','#70648A','#6D35E8'),'✦')
        fills=['#EEE7FF','#F6E5FF','#E7E7FF','#F0E8FF'];
        for i,s in enumerate(blog.get('sections',[])[:8]):
            r,c=divmod(i,2); cls.card_text(img,s,i,(36+c*504,465+r*145,540+c*504,603+r*145),(fills[i%4],'#281A4D','#70648A','#6D35E8'),'purple')
        cls.try_today(img,blog,1090,('#FFE9A6','#604700','#7B6840','#6D35E8'),1)
        cls.footer(img,1210,('#41217E',(255,255,255),(235,225,255),'#7C3AED'),1)
        return cls.save(img,path)

    @classmethod
    def save(cls,img,path):
        Path(path).parent.mkdir(parents=True,exist_ok=True); img.convert('RGB').save(path,format='JPEG',quality=95,optimize=True,progressive=True); return path

    @classmethod
    def render(cls,blog,path,ux_index=0):
        return [cls.render_ux1,cls.render_ux2,cls.render_ux3,cls.render_ux4,cls.render_ux5][ux_index%5](blog,path)
