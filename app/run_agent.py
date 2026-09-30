from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.blog_generator import get_blog, load_static_blogs
from app.config import Config
from app.facebook_service import FacebookService
from app.image_generator import BlogImage
from app.logger import logger
from app.state import load_history, reserve_generation, record

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"


def main():
    parser = argparse.ArgumentParser(description="Smart Learning Lab static UX blog publisher")
    parser.add_argument("--topic-index", type=int, default=None,
                        help="Static blog index from data/static_blogs.json")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.dry_run:
        Config.validate()
    OUT.mkdir(exist_ok=True)

    load_static_blogs()
    history = load_history()

    generation, ux_index = reserve_generation(history)
    blog_index = args.topic_index if args.topic_index is not None else generation
    blog = get_blog(blog_index)

    logger.info("Generation #%s | UX %s | Topic: %s", generation + 1, ux_index + 1, blog["title"])

    image_path = OUT / f"{generation + 1:05d}_{blog['id']}_ux{ux_index + 1}.jpg"
    blog_path = OUT / f"{generation + 1:05d}_{blog['id']}_ux{ux_index + 1}.json"

    final_blog = dict(blog)
    final_blog["ux_index"] = ux_index
    final_blog["generation"] = generation

    BlogImage.render(final_blog, image_path, ux_index=ux_index)

    blog_path.write_text(
        json.dumps({"generation": generation, "ux_index": ux_index, "blog": final_blog},
                   ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    record(history, blog, "generated", generation=generation, ux_index=ux_index,
           image=str(image_path.relative_to(ROOT)), title=blog["title"])

    if args.dry_run:
        print(json.dumps({
            "status": "dry_run",
            "generation": generation,
            "ux": ux_index + 1,
            "topic": blog["title"],
            "image": str(image_path),
        }, ensure_ascii=False, indent=2))
        return

    try:
        result = FacebookService.post_image(str(image_path), blog["caption"])
    except Exception as exc:
        record(history, blog, "failed", generation=generation, ux_index=ux_index,
               image=str(image_path.relative_to(ROOT)), error=str(exc))
        raise

    record(history, blog, "completed", generation=generation, ux_index=ux_index,
           post_id=result.get("post_id") or result.get("id"),
           image=str(image_path.relative_to(ROOT)), title=blog["title"])

    print(json.dumps({
        "status": "completed",
        "generation": generation,
        "ux": ux_index + 1,
        "topic": blog["title"],
        "facebook": result,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
