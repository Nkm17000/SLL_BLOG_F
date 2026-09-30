from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
BLOGS = ROOT / "data" / "blogs.json"

def load_blogs() -> list[dict]:
    data = json.loads(BLOGS.read_text(encoding="utf-8"))
    if data.get("version") != 1 or not isinstance(data.get("blogs"), list) or not data["blogs"]:
        raise ValueError("data/blogs.json must contain version=1 and a non-empty blogs array")
    blogs = data["blogs"]
    for i, blog in enumerate(blogs):
        for key in ("id", "category", "title", "description", "points"):
            if not blog.get(key): raise ValueError(f"Blog {i} missing {key}")
        if len(blog["points"]) != 5: raise ValueError(f"Blog {blog['id']} must contain exactly 5 points")
        for j, point in enumerate(blog["points"]):
            if not point.get("title") or not point.get("description") or len(point.get("items", [])) < 2:
                raise ValueError(f"Blog {blog['id']} point {j+1} is invalid")
    return blogs
