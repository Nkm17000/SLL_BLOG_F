from __future__ import annotations
import argparse, json, time
from datetime import datetime, timezone
from pathlib import Path
from app.config import Config
from app.content_agents import fetch_news_topic, get_agent
from app.facebook_service import FacebookService
from app.logger import logger
from app.article_content import build_text_post
from app.image_generator import create_blog_image
from app.state import load_history, save_history, record

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/"output"

def main():
    parser = argparse.ArgumentParser(description="Publish a new source-grounded technical topic")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    started = time.time()
    OUT.mkdir(exist_ok=True)
    state = load_history()
    agent = get_agent("technical_blog")
    blog, source_url = fetch_news_topic(state)
    if len(blog.get("points", [])) != 5 or any(not p.get("description", "").strip() for p in blog["points"]):
        raise ValueError("Article content quality check failed")
    caption = build_text_post(blog["original_title"], {**blog, "technical_topic": blog["technical_topic"]}, source_url, blog.get("published", ""), Config.APP_NAME)
    if not 1200 <= len(caption) <= 9000:
        raise ValueError("Generated explanation is too short; nothing published")
    (OUT / "latest_post.txt").write_text(caption + "\n", encoding="utf-8")
    previous_palette = state.get("last_image_palette")
    image_path, palette_index = create_blog_image(blog, source_url, Config.APP_NAME, OUT / "images" / "latest_blog.jpg", previous_palette=previous_palette)
    state["last_image_palette"] = palette_index
    # Reserve the topic before making the external publish call. If publishing fails,
    # record the failure, and avoid accidentally reposting it on the next run.
    entry = record(state, blog, "generated" if args.dry_run else "pending_publish",
                   agent_id=agent.id, agent_name=agent.name,
                   technical_topic=blog["technical_topic"], article_title=blog["original_title"],
                   source_url=source_url, source_published=blog.get("published", ""),
                   content_mode=blog["content_mode"], summary_model=blog.get("summary_model"),
                   article_text_length=blog["article_text_length"], image_palette=palette_index)
    if not args.dry_run:
        save_history(state)
    result = {"status": entry["status"], "technical_topic": blog["technical_topic"],
              "article_title": blog["original_title"], "source_url": source_url,
              "post_character_count": len(caption), "image_path": str(image_path.relative_to(ROOT)), "image_palette": palette_index, "post_type": "image_with_caption"}
    try:
        if not args.dry_run:
            Config.validate_facebook()
            FacebookService.validate_page_access()
            fb = FacebookService.post_photo(image_path, caption)
            entry.update(status="published", facebook_post_id=fb["post_id"])
            result.update(status="published", facebook_post_id=fb["post_id"])
    except Exception as exc:
        entry.update(status="failed", error=str(exc)[:500])
        result.update(status="failed", error=str(exc)[:500])
        raise
    finally:
        if not args.dry_run:
            save_history(state)
        summary = {**result, "app_name": Config.APP_NAME,
                   "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                   "runtime_seconds": round(time.time() - started, 2)}
        (OUT / "latest_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        logger.info("Run finished: %s", json.dumps(summary, ensure_ascii=False))
        print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
