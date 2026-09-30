from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.blog_generator import generate_blog
from app.config import Config
from app.facebook_service import FacebookService
from app.image_generator import BlogImage
from app.logger import logger
from app.state import load_history, load_topics, next_pending, previous_theme_id, record

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"


def main():
    parser = argparse.ArgumentParser(description="Smart Learning Lab Technical Blog Facebook Publisher")
    parser.add_argument("--topic", default=None, help="Topic ID from data/topics.json")
    parser.add_argument("--dry-run", action="store_true", help="Generate content/image but do not publish")
    args = parser.parse_args()

    Config.validate()
    OUT.mkdir(exist_ok=True)

    topics = load_topics()
    history = load_history()

    if args.topic:
        topic = next((t for t in topics if t["id"] == args.topic), None)
        if not topic:
            raise ValueError(f"Unknown topic: {args.topic}")
    else:
        topic = next_pending(topics, history)
        if not topic:
            print("All configured topics are completed. Add new topics to data/topics.json.")
            return

    logger.info("Generating blog: %s", topic["title"])
    blog = generate_blog(topic)

    safe = topic["id"].replace("/", "-")
    image_path = OUT / f"{safe}.jpg"
    theme = BlogImage.render(blog, image_path, previous_theme_id=previous_theme_id(history))

    blog_path = OUT / f"{safe}.json"
    payload = {
        "topic": topic,
        "theme_id": theme["id"],
        "blog": blog,
    }
    blog_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.dry_run:
        record(topic, "generated", theme_id=theme["id"], image=str(image_path.relative_to(ROOT)), title=blog["title"])
        print(json.dumps({"status": "dry_run", "topic": topic, "theme": theme["id"], "image": str(image_path)}, ensure_ascii=False, indent=2))
        return

    logger.info("Selected theme: %s", theme["id"])
    logger.info("Publishing to Facebook Page")
    try:
        result = FacebookService.post_image(str(image_path), blog["caption"])
    except Exception as exc:
        record(topic, "failed", theme_id=theme["id"], error=str(exc), image=str(image_path.relative_to(ROOT)), title=blog["title"])
        raise

    record(
        topic,
        "completed",
        theme_id=theme["id"],
        post_id=result.get("post_id") or result.get("id"),
        image=str(image_path.relative_to(ROOT)),
        title=blog["title"],
    )
    print(json.dumps({"status": "completed", "topic": topic["title"], "theme": theme["id"], "facebook": result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
