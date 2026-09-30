"""Render one sample for each UX using five different static topics."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.blog_generator import load_static_blogs
from app.image_generator import BlogImage, UX_DESIGNS

OUT = ROOT / "preview"
OUT.mkdir(exist_ok=True)
blogs = load_static_blogs()
for i in range(5):
    path = OUT / f"ux{i+1}_{blogs[i]['id']}.jpg"
    BlogImage.render(blogs[i], path, ux_index=i)
    print(f"UX {i+1}: {UX_DESIGNS[i]['name']} -> {path}")
