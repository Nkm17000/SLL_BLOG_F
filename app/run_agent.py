from __future__ import annotations

import argparse
import json
import os
import sys
import time
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
    parser.add_argument("--topic-index", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    started = time.time()
    logger.info("=" * 72)
    logger.info("SMART LEARNING LAB BLOG RUN STARTED")
    logger.info("Python: %s", sys.version.split()[0])
    logger.info("Working directory: %s", ROOT)
    logger.info("Dry run: %s", args.dry_run)
    logger.info("GitHub run number: %s", os.getenv("GITHUB_RUN_NUMBER", "local"))
    logger.info("GitHub event: %s", os.getenv("GITHUB_EVENT_NAME", "local"))
    logger.info("=" * 72)

    if not args.dry_run:
        logger.info("Validating Facebook configuration...")
        Config.validate()
        logger.info("Facebook configuration validated.")
    else:
        logger.info("Dry-run mode: Facebook credentials are not required.")

    OUT.mkdir(exist_ok=True)

    logger.info("Loading static blog JSON...")
    blogs = load_static_blogs()
    logger.info("Loaded %s static blogs.", len(blogs))

    history = load_history()
    logger.info("Current next_generation: %s", history.get("next_generation"))

    generation, ux_index = reserve_generation(history)
    blog_index = args.topic_index if args.topic_index is not None else generation
    blog = get_blog(blog_index)

    logger.info("Generation: #%s", generation + 1)
    logger.info("Selected UX: %s/5", ux_index + 1)
    logger.info("Selected blog index: %s", blog_index % len(blogs))
    logger.info("Topic ID: %s", blog["id"])
    logger.info("Topic title: %s", blog["title"])

    image_path = OUT / f"{generation + 1:05d}_{blog['id']}_ux{ux_index + 1}.jpg"
    blog_path = OUT / f"{generation + 1:05d}_{blog['id']}_ux{ux_index + 1}.json"

    final_blog = dict(blog)
    final_blog["ux_index"] = ux_index
    final_blog["generation"] = generation

    logger.info("Rendering 1080x1350 blog image...")
    try:
        BlogImage.render(final_blog, image_path, ux_index=ux_index)
    except Exception as exc:
        logger.exception("IMAGE GENERATION FAILED: %s", exc)
        record(history, blog, "failed_image", generation=generation, ux_index=ux_index, error=str(exc))
        raise

    logger.info("Image generated successfully: %s", image_path)
    logger.info("Image bytes: %s", image_path.stat().st_size)

    blog_path.write_text(
        json.dumps({"generation": generation, "ux_index": ux_index, "blog": final_blog}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    logger.info("Metadata written: %s", blog_path)

    record(history, blog, "generated", generation=generation, ux_index=ux_index,
           image=str(image_path.relative_to(ROOT)), title=blog["title"])
    logger.info("Generation state saved.")

    if args.dry_run:
        logger.info("DRY RUN COMPLETE - Facebook upload skipped.")
        logger.info("Total runtime: %.2fs", time.time() - started)
        print(json.dumps({
            "status": "dry_run",
            "generation": generation,
            "ux": ux_index + 1,
            "topic": blog["title"],
            "image": str(image_path),
        }, ensure_ascii=False, indent=2))
        return

    logger.info("Starting Facebook preflight...")
    try:
        FacebookService.validate_page_access()
        logger.info("Facebook preflight passed. Starting image upload...")
        result = FacebookService.post_image(str(image_path), blog.get("caption", ""))
    except Exception as exc:
        logger.exception("FACEBOOK PUBLISH FAILED: %s", exc)
        record(history, blog, "failed_facebook", generation=generation, ux_index=ux_index,
               image=str(image_path.relative_to(ROOT)), error=str(exc), title=blog["title"])
        raise

    post_id = result.get("post_id") or result.get("id")
    record(history, blog, "completed", generation=generation, ux_index=ux_index,
           post_id=post_id, image=str(image_path.relative_to(ROOT)), title=blog["title"])

    logger.info("FACEBOOK PUBLISH COMPLETE. Post ID: %s", post_id)
    logger.info("TOTAL RUN TIME: %.2fs", time.time() - started)
    logger.info("SMART LEARNING LAB BLOG RUN FINISHED SUCCESSFULLY")

    print(json.dumps({
        "status": "completed",
        "generation": generation,
        "ux": ux_index + 1,
        "topic": blog["title"],
        "facebook": result,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.exception("BLOG RUN INTERRUPTED")
        raise
    except Exception as exc:
        logger.exception("BLOG RUN FAILED - UNHANDLED EXCEPTION: %s", exc)
        logger.error("See output/logs for the complete run log.")
        raise
