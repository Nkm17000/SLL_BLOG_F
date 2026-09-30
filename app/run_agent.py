from __future__ import annotations
import argparse
import json
import random
import sys
import time
from pathlib import Path

from app.blog_generator import load_blogs
from app.config import Config
from app.facebook_service import FacebookService
from app.html_renderer import render
from app.logger import logger
from app.state import load_history, save_history, record
from app.theme_engine import choose_theme

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"
TEMPLATE_NAMES = [
    "asymmetric_magazine", "zigzag_story", "vertical_timeline", "bento_grid", "pill_cards",
    "newspaper_columns", "color_band", "circle_focus", "diagonal_blocks", "premium_minimal"
]

def choose_topic(blogs, state):
    ids = {b["id"] for b in blogs}
    used = set(state.get("topic_used", [])) & ids
    if used >= ids:
        state["topic_cycle"] = int(state.get("topic_cycle", 0)) + 1
        state["topic_used"] = []
        used = set()
    candidates = [b for b in blogs if b["id"] not in used]
    return random.choice(candidates)

def choose_template(state):
    used = set(state.get("template_used", []))
    valid = set(range(1, 11))
    if used >= valid:
        state["template_cycle"] = int(state.get("template_cycle", 0)) + 1
        state["template_used"] = []
        used = set()
    template_id = random.choice([i for i in range(1, 11) if i not in used])
    return template_id

def main():
    ap = argparse.ArgumentParser(description="Smart Learning Lab dynamic technical blog publisher")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    started = time.time()
    OUT.mkdir(exist_ok=True)

    blogs = load_blogs()
    state = load_history()
    logger.info("Loaded %d topics; topic cycle=%s; template cycle=%s", len(blogs), state["topic_cycle"], state["template_cycle"])

    if not args.dry_run:
        Config.validate()
        FacebookService.validate_page_access()

    blog = choose_topic(blogs, state)
    template_id = choose_template(state)
    template_name = TEMPLATE_NAMES[template_id - 1]
    theme = choose_theme(state, template_id)
    logger.info("Selected topic=%s | template=%s | theme=%s", blog["id"], template_name, theme.id)

    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    image = OUT / f"{stamp}_{blog['id']}_t{template_id:02d}.png"

    try:
        render(blog, template_id, image, theme_id=theme.id, orientation=Config.ORIENTATION)

        # Rotation is committed only after rendering succeeds.
        state.setdefault("topic_used", []).append(blog["id"])
        state.setdefault("template_used", []).append(template_id)
        state.setdefault("theme_used", []).append(theme.id)
        record(
            state, blog, "generated",
            topic_cycle=state["topic_cycle"],
            template_id=template_id,
            template_name=template_name,
            theme_id=theme.id,
            image=str(image.relative_to(ROOT)),
        )

        result = {
            "topic": blog["title"],
            "template": template_name,
            "template_id": template_id,
            "theme": theme.id,
            "image": str(image.relative_to(ROOT)),
            "status": "generated",
        }

        if not args.dry_run:
            caption = f"{blog['title']}\n\n{blog['description']}\n\n#SmartLearningLab #AI #Technology #TechBlog"
            fb = FacebookService.post_image(str(image), caption)
            post_id = fb.get("post_id") or fb.get("id")
            record(
                state, blog, "published",
                template_id=template_id,
                template_name=template_name,
                theme_id=theme.id,
                image=str(image.relative_to(ROOT)),
                facebook_post_id=post_id,
            )
            result.update(status="published", facebook_post_id=post_id)

        save_history(state)
        summary = {
            "status": result["status"],
            "result": result,
            "topic_cycle": state["topic_cycle"],
            "template_cycle": state["template_cycle"],
            "theme_cycle": state.get("theme_cycle",0),
            "themes_used_in_cycle": len(state.get("theme_used",[])),
            "topics_used_in_cycle": len(state["topic_used"]),
            "templates_used_in_cycle": len(state["template_used"]),
            "history_records": len(state["history"]),
            "runtime_seconds": round(time.time() - started, 2),
        }
        (OUT / "latest_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    except Exception as exc:
        record(
            state, blog, "failed",
            template_id=template_id,
            template_name=template_name,
            error=str(exc),
        )
        save_history(state)
        raise

if __name__ == "__main__":
    main()
