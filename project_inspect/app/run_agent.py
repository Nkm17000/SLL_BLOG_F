from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from app.blog_generator import load_static_blogs
from app.config import Config
from app.design_registry import DESIGNS
from app.facebook_service import FacebookService
from app.image_generator import BlogImage
from app.logger import logger
from app.state import load_history, reserve_generation, record

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"


def main():
    parser = argparse.ArgumentParser(description="Smart Learning Lab - generate 20 technical blog images across 15 UX designs")
    parser.add_argument("--topic-index", type=int, default=None, help="Optional starting topic index.")
    parser.add_argument("--count", type=int, default=20, help="Number of images to generate. Default: 20.")
    parser.add_argument("--dry-run", action="store_true", help="Generate images but skip Facebook publishing.")
    args = parser.parse_args()

    if args.count < 1 or args.count > 20:
        raise SystemExit("--count must be between 1 and 20")

    started = time.time()
    logger.info("=" * 80)
    logger.info("SMART LEARNING LAB - 20 IMAGE / 15 DESIGN BATCH RUN STARTED")
    logger.info("Python: %s", sys.version.split()[0])
    logger.info("Working directory: %s", ROOT)
    logger.info("Dry run: %s", args.dry_run)
    logger.info("Requested image count: %s", args.count)
    logger.info("Design count: %s", len(DESIGNS))
    logger.info("GitHub run number: %s", os.getenv("GITHUB_RUN_NUMBER", "local"))
    logger.info("GitHub event: %s", os.getenv("GITHUB_EVENT_NAME", "local"))
    logger.info("=" * 80)

    if not args.dry_run:
        Config.validate()
        logger.info("Facebook configuration validated.")
    else:
        logger.info("Dry-run mode: Facebook credentials are not required.")

    OUT.mkdir(exist_ok=True)
    blogs = load_static_blogs()
    history = load_history()
    logger.info("Loaded %s topics.", len(blogs))
    logger.info("Current next_generation: %s", history.get("next_generation"))
    logger.info("Design sequence: %s", " -> ".join(str(i + 1) for i in range(len(DESIGNS))))

    if not args.dry_run:
        logger.info("Running Facebook preflight once before the batch...")
        FacebookService.validate_page_access()
        logger.info("Facebook preflight passed.")

    results = []
    failures = []

    for batch_position in range(args.count):
        generation, design_index = reserve_generation(history)
        design = DESIGNS[design_index]
        topic_index = ((args.topic_index + batch_position) if args.topic_index is not None else generation) % len(blogs)
        blog = blogs[topic_index]

        logger.info("=" * 80)
        logger.info("BATCH ITEM %s/%s", batch_position + 1, args.count)
        logger.info("Generation: #%s", generation + 1)
        logger.info("Design: %s/%s - %s", design_index + 1, len(DESIGNS), design["name"])
        logger.info("Topic: %s/%s - %s", topic_index + 1, len(blogs), blog["title"])

        image_path = OUT / f"{generation + 1:05d}_{blog['id']}_design{design_index + 1:02d}.jpg"
        blog_path = OUT / f"{generation + 1:05d}_{blog['id']}_design{design_index + 1:02d}.json"
        final_blog = dict(blog)
        final_blog.update({
            "design_index": design_index,
            "design_id": design["id"],
            "design_name": design["name"],
            "generation": generation,
            "batch_position": batch_position + 1,
            "batch_size": args.count,
        })

        try:
            BlogImage.render(final_blog, image_path, ux_index=design_index)
            logger.info("IMAGE GENERATED: %s", image_path)
            logger.info("Image bytes: %s", image_path.stat().st_size)

            blog_path.write_text(json.dumps({
                "generation": generation,
                "design_index": design_index,
                "design_id": design["id"],
                "design_name": design["name"],
                "topic_index": topic_index,
                "blog": final_blog,
            }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            record(history, blog, "generated", generation=generation, design_index=design_index,
                   design_id=design["id"], image=str(image_path.relative_to(ROOT)),
                   title=blog["title"], design_name=design["name"])

            result_item = {
                "generation": generation,
                "design": design_index + 1,
                "design_id": design["id"],
                "design_name": design["name"],
                "topic_index": topic_index,
                "topic": blog["title"],
                "image": str(image_path.relative_to(ROOT)),
                "status": "generated",
            }

            if args.dry_run:
                logger.info("DRY RUN: Facebook upload skipped for this item.")
            else:
                fb_result = FacebookService.post_image(str(image_path), blog.get("caption", ""))
                post_id = fb_result.get("post_id") or fb_result.get("id")
                record(history, blog, "completed", generation=generation, design_index=design_index,
                       design_id=design["id"], post_id=post_id,
                       image=str(image_path.relative_to(ROOT)), title=blog["title"],
                       design_name=design["name"])
                result_item["status"] = "completed"
                result_item["facebook_post_id"] = post_id
                logger.info("FACEBOOK PUBLISHED: %s", post_id)

            results.append(result_item)

        except Exception as exc:
            logger.exception("ITEM %s/%s FAILED: %s", batch_position + 1, args.count, exc)
            record(history, blog, "failed", generation=generation, design_index=design_index,
                   design_id=design["id"], image=str(image_path.relative_to(ROOT)),
                   title=blog["title"], design_name=design["name"], error=str(exc))
            failures.append({
                "generation": generation,
                "design": design_index + 1,
                "design_id": design["id"],
                "topic": blog["title"],
                "error": str(exc),
            })
            continue

    summary = {
        "status": "failed" if failures else "completed",
        "requested": args.count,
        "successful": len(results),
        "failed": len(failures),
        "design_count": len(DESIGNS),
        "topic_count": len(blogs),
        "results": results,
        "failures": failures,
        "runtime_seconds": round(time.time() - started, 2),
    }

    summary_path = OUT / f"batch_summary_{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    logger.info("=" * 80)
    logger.info("BATCH FINISHED - Requested: %s | Successful: %s | Failed: %s", args.count, len(results), len(failures))
    logger.info("Summary: %s", summary_path)
    logger.info("Total runtime: %.2fs", time.time() - started)
    logger.info("=" * 80)
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if failures:
        raise RuntimeError(f"Batch completed with {len(failures)} failure(s). See logs and batch summary.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.exception("BLOG BATCH INTERRUPTED")
        raise
    except Exception as exc:
        logger.exception("BLOG BATCH FAILED - UNHANDLED EXCEPTION: %s", exc)
        raise
