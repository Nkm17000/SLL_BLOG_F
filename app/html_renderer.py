from __future__ import annotations
import base64, html, mimetypes, shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
from app.theme_engine import BY_ID
from app.quality_engine import prepare_blog

ROOT=Path(__file__).resolve().parent.parent
TEMPLATE_DIR=ROOT/'templates'; IMAGE_DIR=ROOT/'assets/images'
TEMPLATE_NAMES=["asymmetric_magazine","zigzag_story","vertical_timeline","bento_grid","pill_cards","newspaper_columns","color_band","circle_focus","diagonal_blocks","premium_minimal"]

def _esc(v): return html.escape(str(v or ''),quote=True)
def _data_uri(path):
    mime=mimetypes.guess_type(path.name)[0] or 'image/png'
    return f'data:{mime};base64,'+base64.b64encode(path.read_bytes()).decode('ascii')

def _hero_path(tid):
    p=IMAGE_DIR/f'template-{tid:02d}-hero.png'
    if not p.exists(): raise FileNotFoundError(p)
    return p

def build_html(blog,template_id,theme_id=None,orientation='square'):
    f=TEMPLATE_DIR/f'{template_id:02d}_{TEMPLATE_NAMES[template_id-1]}.html'
    s=f.read_text(encoding='utf-8'); theme=BY_ID.get(theme_id) if theme_id else None
    if theme is None: theme=next(iter(BY_ID.values()))
    # The renderer accepts both raw JSON records and enriched runtime records.
    display_title=blog.get('hook') or blog.get('title','')
    original_title=blog.get('original_title') or blog.get('title','')
    level=str(blog.get('difficulty','intermediate')).title()
    series=blog.get('series','Smart Learning Lab')
    short_desc=f"{original_title}. {blog.get('description','')}"
    short_desc=' '.join(short_desc.split())
    if len(short_desc)>310: short_desc=short_desc[:307].rsplit(' ',1)[0]+'…'
    category=f"{series} • {level}"
    vals={
      '{{category}}':_esc(category),'{{title}}':_esc(display_title),'{{description}}':_esc(short_desc),
      '{{hero_image_url}}':_data_uri(_hero_path(template_id)),'{{hero_image_alt}}':_esc(original_title),
      '{{theme.background}}':theme.background,'{{theme.surface}}':theme.surface,'{{theme.text}}':theme.text,'{{theme.muted}}':theme.muted,
      '{{theme.accent}}':theme.accent,'{{theme.accent2}}':theme.accent2,'{{theme.border}}':theme.border,'{{theme.hero_overlay}}':theme.hero_overlay}
    for k,v in vals.items(): s=s.replace(k,v)
    for i,p in enumerate(blog['points']):
      s=s.replace(f'{{{{points[{i}].title}}}}',_esc(p['title'])).replace(f'{{{{points[{i}].description}}}}',_esc(p['description']))
      s=s.replace(f'{{{{points[{i}].items[0]}}}}',_esc(p['items'][0])).replace(f'{{{{points[{i}].items[1]}}}}',_esc(p['items'][1]))
    cta=_esc(blog.get('cta','Save this for later 📌'))
    series_esc=_esc(series)
    s=s.replace('Smart Learning Lab • Learn • Practice • Grow', f'Smart Learning Lab • {_esc(blog.get("cta","Save this for later 📌"))}')
    s=s.replace('Technical AI Blog', series_esc)
    # Square 10:10, high-readability layout. The export is 4000x4000 at 2x DPR.
    extra=f'''<style>
.canvas{{width:2000px!important;height:2000px!important}}
.hero{{height:520px!important}}
.hero-content{{width:56%!important;padding:54px 48px!important}}
.title{{font-size:64px!important;line-height:1.05!important;max-width:1050px!important;letter-spacing:-.8px!important}}
.description{{font-size:24px!important;line-height:1.45!important;max-width:980px!important}}
.points{{height:1320px!important;padding:38px 54px 80px!important;gap:20px!important;grid-template-rows:repeat(3,1fr)!important;align-items:stretch!important}}
.point{{min-height:0!important;height:100%!important;padding:24px!important}}
.point h2{{font-size:28px!important;line-height:1.18!important}}
.point p{{font-size:20px!important;line-height:1.4!important}}
.point ul{{font-size:18px!important;line-height:1.4!important}}
.footer{{height:82px!important;padding:20px 54px!important;font-size:17px!important}}
</style>'''
    return s.replace('</body>',extra+'</body>')

def render(blog,template_id,output_path,theme_id=None,orientation='square'):
    text=build_html(blog,template_id,theme_id,orientation)
    out=Path(output_path); out.parent.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as p:
      chrome=shutil.which('chromium') or shutil.which('chromium-browser') or shutil.which('google-chrome')
      kwargs={'args':['--no-sandbox','--disable-dev-shm-usage']}
      if chrome: kwargs['executable_path']=chrome
      browser=p.chromium.launch(**kwargs)
      page=browser.new_page(viewport={'width':2000,'height':2000},device_scale_factor=2)
      page.set_content(text,wait_until='networkidle')
      page.add_style_tag(content='''html,body{-webkit-font-smoothing:antialiased!important;text-rendering:geometricPrecision!important;}img{image-rendering:auto!important;}''')
      page.screenshot(path=str(out),full_page=False)
      browser.close()
