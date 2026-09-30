from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOPICS = ROOT / "data" / "topics.json"
STATIC_BLOGS = ROOT / "data" / "static_blogs.json"


def load_static_blogs() -> list[dict]:
    path = TOPICS if TOPICS.exists() else STATIC_BLOGS
    data = json.loads(path.read_text(encoding="utf-8"))
    blogs = data.get("topics") or data.get("blogs") or []
    if not blogs:
        raise ValueError(f"{path} contains no topics")
    return blogs


def get_blog(index: int) -> dict:
    blogs = load_static_blogs()
    return blogs[index % len(blogs)]
