from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from app.blog_generator import load_static_blogs
from app.config import Config
from app.facebook_service import FacebookService
from app.image_generator import BlogImage, UX_DESIGNS
from app.logger import logger
from app.state import load_history, reserve_generation, record

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"


def main():
    parser = argparse.ArgumentParser(description="Smart Learning Lab - generate 5 technical blog images with 5 UX designs")
    parser.add_argument("--topic-index", type=int, default=None, help="Start topic index. Five consecutive topics are generated.")
    parser.add_argument("--count", type=int, default=5, help="Number of images to generate. Default: 5.")
    parser.add_argument("--dry-run", action="store_true", help="Generate images but skip Facebook publishing.")
    args = parser.parse_args()

    if args.count < 1 or args.count > 5:
        raise SystemExit("--count must be between 1 and 5")

    started = time.time()
    logger.info("=" * 80)
    logger.info("SMART LEARNING LAB - 5 UX BATCH RUN STARTED")
    logger.info("Python: %s", sys.version.split()[0])
    logger.info("Working directory: %s", ROOT)
    logger.info("Dry run: %s", args.dry_run)
    logger.info("Requested image count: %s", args.count)
    logger.info("GitHub run number: %s", os.getenv("GITHUB_RUN_NUMBER", "local"))
    logger.info("GitHub event: %s", os.getenv("GITHUB_EVENT_NAME", "local"))
    logger.info("=" * 80)

    if not args.dry_run:
        logger.info("Validating Facebook configuration...")
        Config.validate()
        logger.info("Facebook configuration validated.")
    else:
        logger.info("Dry-run mode: Facebook credentials are not required.")

    OUT.mkdir(exist_ok=True)
    blogs = load_static_blogs()
    history = load_history()
    logger.info("Loaded %s static blogs.", len(blogs))
    logger.info("Current next_generation: %s", history.get("next_generation"))
    logger.info("UX sequence for this batch: %s", ", ".join(str(i + 1) for i in range(args.count)))

    if not args.dry_run:
        logger.info("Running Facebook preflight once before the batch...")
        FacebookService.validate_page_access()
        logger.info("Facebook preflight passed.")

    results = []
    failures = []

    for batch_position in range(args.count):
        generation, ux_index = reserve_generation(history)
        if args.topic_index is None:
            topic_index = generation % len(blogs)
        else:
            topic_index = (args.topic_index + batch_position) % len(blogs)
        blog = blogs[topic_index]

        logger.info("=" * 80)
        logger.info("BATCH ITEM %s/%s", batch_position + 1, args.count)
        logger.info("Generation: #%s", generation + 1)
        logger.info("UX: %s/5 - %s", ux_index + 1, UX_DESIGNS[ux_index]["name"])
        logger.info("Topic index: %s", topic_index)
        logger.info("Topic ID: %s", blog["id"])
        logger.info("Topic title: %s", blog["title"])

        image_path = OUT / f"{generation + 1:05d}_{blog['id']}_ux{ux_index + 1}.jpg"
        blog_path = OUT / f"{generation + 1:05d}_{blog['id']}_ux{ux_index + 1}.json"
        final_blog = dict(blog)
        final_blog["ux_index"] = ux_index
        final_blog["ux_name"] = UX_DESIGNS[ux_index]["name"]
        final_blog["generation"] = generation
        final_blog["batch_position"] = batch_position + 1
        final_blog["batch_size"] = args.count

        try:
            logger.info("Rendering full UX design at 1080x1350...")
            BlogImage.render(final_blog, image_path, ux_index=ux_index)
            logger.info("IMAGE GENERATED: %s", image_path)
            logger.info("Image bytes: %s", image_path.stat().st_size)

            blog_path.write_text(
                json.dumps({
                    "generation": generation,
                    "ux_index": ux_index,
                    "ux_name": UX_DESIGNS[ux_index]["name"],
                    "blog": final_blog,
                }, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            record(history, blog, "generated", generation=generation, ux_index=ux_index,
                   image=str(image_path.relative_to(ROOT)), title=blog["title"],
                   ux_name=UX_DESIGNS[ux_index]["name"])

            result_item = {
                "generation": generation,
                "ux": ux_index + 1,
                "ux_name": UX_DESIGNS[ux_index]["name"],
                "topic_index": topic_index,
                "topic": blog["title"],
                "image": str(image_path.relative_to(ROOT)),
                "status": "generated",
            }

            if args.dry_run:
                logger.info("DRY RUN: Facebook upload skipped for this item.")
            else:
                logger.info("Publishing item %s/%s to Facebook...", batch_position + 1, args.count)
                fb_result = FacebookService.post_image(str(image_path), blog.get("caption", ""))
                post_id = fb_result.get("post_id") or fb_result.get("id")
                record(history, blog, "completed", generation=generation, ux_index=ux_index,
                       post_id=post_id, image=str(image_path.relative_to(ROOT)), title=blog["title"],
                       ux_name=UX_DESIGNS[ux_index]["name"])
                result_item["status"] = "completed"
                result_item["facebook_post_id"] = post_id
                logger.info("FACEBOOK PUBLISHED: %s", post_id)

            results.append(result_item)

        except Exception as exc:
            logger.exception("ITEM %s/%s FAILED: %s", batch_position + 1, args.count, exc)
            record(history, blog, "failed", generation=generation, ux_index=ux_index,
                   image=str(image_path.relative_to(ROOT)), title=blog["title"],
                   ux_name=UX_DESIGNS[ux_index]["name"], error=str(exc))
            failures.append({
                "generation": generation,
                "ux": ux_index + 1,
                "topic": blog["title"],
                "error": str(exc),
            })
            # Continue to the next topic so one bad post cannot hide the other four.
            continue

    summary = {
        "status": "failed" if failures else "completed",
        "requested": args.count,
        "successful": len(results),
        "failed": len(failures),
        "results": results,
        "failures": failures,
        "runtime_seconds": round(time.time() - started, 2),
    }

    summary_path = OUT / f"batch_summary_{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    logger.info("=" * 80)
    logger.info("BATCH FINISHED")
    logger.info("Requested: %s | Successful: %s | Failed: %s", args.count, len(results), len(failures))
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
