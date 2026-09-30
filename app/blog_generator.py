from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC_BLOGS = ROOT / "data" / "static_blogs.json"


def load_static_blogs() -> list[dict]:
    data = json.loads(STATIC_BLOGS.read_text(encoding="utf-8"))
    blogs = data.get("blogs", [])
    if not blogs:
        raise ValueError("data/static_blogs.json contains no blogs")
    return blogs


def get_blog(index: int) -> dict:
    blogs = load_static_blogs()
    return blogs[index % len(blogs)]
