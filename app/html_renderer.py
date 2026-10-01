from __future__ import annotations
import base64, html, mimetypes, shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
from app.theme_engine import BY_ID

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

def build_html(blog,template_id,theme_id=None,orientation='horizontal'):
    f=TEMPLATE_DIR/f'{template_id:02d}_{TEMPLATE_NAMES[template_id-1]}.html'
    s=f.read_text(encoding='utf-8'); theme=BY_ID.get(theme_id) if theme_id else None
    if theme is None:
        theme=next(iter(BY_ID.values()))
    vals={
      '{{category}}':_esc(blog['category']),'{{title}}':_esc(blog['title']),'{{description}}':_esc(blog['description']),
      '{{hero_image_url}}':_data_uri(_hero_path(template_id)),'{{hero_image_alt}}':_esc(blog['title']),
      '{{theme.background}}':theme.background,'{{theme.surface}}':theme.surface,'{{theme.text}}':theme.text,'{{theme.muted}}':theme.muted,
      '{{theme.accent}}':theme.accent,'{{theme.accent2}}':theme.accent2,'{{theme.border}}':theme.border,'{{theme.hero_overlay}}':theme.hero_overlay}
    for k,v in vals.items(): s=s.replace(k,v)
    for i,p in enumerate(blog['points']):
      s=s.replace(f'{{{{points[{i}].title}}}}',_esc(p['title'])).replace(f'{{{{points[{i}].description}}}}',_esc(p['description']))
      s=s.replace(f'{{{{points[{i}].items[0]}}}}',_esc(p['items'][0])).replace(f'{{{{points[{i}].items[1]}}}}',_esc(p['items'][1]))
    if orientation=='vertical':
      extra='''<style>
.canvas{width:1000px!important;height:1200px!important}
.hero{height:350px!important}
.hero-content{width:60%!important;padding:42px 34px!important}
.title{font-size:48px!important;line-height:1.04!important;max-width:570px!important}
.description{font-size:17px!important;line-height:1.45!important;max-width:540px!important}
.points{padding:22px 34px 86px!important}
.point{min-height:128px!important}
.point h2{font-size:19px!important;line-height:1.18!important}
.point p{font-size:13px!important;line-height:1.4!important}
.point ul{font-size:12px!important;line-height:1.35!important}
.footer{height:48px!important}
</style>'''
    else:
      extra='''<style>
.canvas{width:1200px!important;height:1000px!important}
.hero{height:300px!important}
.hero-content{width:56%!important;padding:34px 28px!important}
.title{font-size:48px!important;line-height:1.04!important;max-width:620px!important;letter-spacing:-.8px!important}
.description{font-size:16px!important;line-height:1.45!important;max-width:590px!important}
.points{padding-left:36px!important;padding-right:36px!important;gap:14px!important}
.point{min-height:120px!important;padding:16px!important}
.point h2{font-size:19px!important;line-height:1.18!important}
.point p{font-size:13px!important;line-height:1.4!important}
.point ul{font-size:12px!important;line-height:1.35!important}
</style>'''
    return s.replace('</body>',extra+'</body>')

def render(blog,template_id,output_path,theme_id=None,orientation='horizontal'):
    text=build_html(blog,template_id,theme_id,orientation)
    out=Path(output_path); out.parent.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as p:
      chrome=shutil.which('chromium') or shutil.which('chromium-browser') or shutil.which('google-chrome')
      kwargs={'args':['--no-sandbox','--disable-dev-shm-usage']}
      if chrome: kwargs['executable_path']=chrome
      browser=p.chromium.launch(**kwargs)
      size={'horizontal':(1200,1000),'vertical':(1000,1200)}[orientation]
      page=browser.new_page(viewport={'width':size[0],'height':size[1]},device_scale_factor=2)
      page.set_content(text,wait_until='networkidle')
      page.add_style_tag(content='''html,body{
  -webkit-font-smoothing:antialiased!important;
  text-rendering:geometricPrecision!important;
} img{image-rendering:auto!important;}''')
      page.screenshot(path=str(out),full_page=False)
      browser.close()
