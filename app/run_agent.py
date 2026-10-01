from __future__ import annotations
import argparse
import json
import random
import time
from pathlib import Path

from app.content_agents import load_agent_topics
from app.config import Config
from app.content_agents import get_agent, choose_topic_for_agent, mark_agent_topic_used, fetch_news_topic, transform_for_agent
from app.facebook_service import FacebookService
from app.html_renderer import render
from app.logger import logger
from app.scheduler import scheduled_agent, current_ist, schedule_table
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
    return random.choice([i for i in range(1, 11) if i not in used])


def make_caption(blog, agent):
    hashtags = " ".join(agent.hashtags)
    return f"{blog['title']}\n\n{blog['description']}\n\n{hashtags}"


def main():
    ap = argparse.ArgumentParser(description="Smart Learning Lab multi-agent technical content publisher")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--agent", choices=["auto", "student", "tech_facts", "ai", "ai_tools", "coding", "debugging", "howto", "concepts", "cloud", "database", "app_development", "cybersecurity", "experiments", "projects", "productivity", "career", "news", "infographic", "repurposing", "technical_blog"], default="auto")
    args = ap.parse_args()
    started = time.time()
    OUT.mkdir(exist_ok=True)

    blogs = load_agent_topics("technical_blog")
    state = load_history()
    now_ist = current_ist()
    agent = scheduled_agent(now_ist) if args.agent == "auto" else get_agent(args.agent)
    logger.info("IST=%s | agent=%s | %s", now_ist.isoformat(), agent.id, agent.name)
    logger.info("Schedule=%s", schedule_table())

    if not args.dry_run:
        Config.validate()
        FacebookService.validate_page_access()

    source_url = ""
    if agent.id == "news":
        try:
            raw_blog, source_url = fetch_news_topic()
            blog = raw_blog
        except Exception as exc:
            logger.warning("News fetch failed: %s. Falling back to emerging technology topic.", exc)
            fallback = get_agent("technical_blog")
            blog = choose_topic_for_agent(blogs, state, fallback)
            blog = transform_for_agent(blog, agent)
    else:
        raw = choose_topic_for_agent(blogs, state, agent)
        # Each agent has its own pre-specialized 2,000-topic JSON bank.
        blog = raw

    template_id = choose_template(state)
    template_name = TEMPLATE_NAMES[template_id - 1]
    theme = choose_theme(state, template_id)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    safe_agent = agent.id.replace("_", "-")
    image = OUT / f"{stamp}_{safe_agent}_{blog['id']}_t{template_id:02d}.png"

    logger.info("Selected topic=%s | agent=%s | template=%s | theme=%s", blog["id"], agent.id, template_name, theme.id)
    try:
        render(blog, template_id, image, theme_id=theme.id, orientation=Config.ORIENTATION)

        mark_agent_topic_used(state, agent, blog["id"])
        if agent.id == "technical_blog":
            state.setdefault("topic_used", []).append(blog["id"])
        state.setdefault("template_used", []).append(template_id)
        state.setdefault("theme_used", []).append(theme.id)

        record(state, blog, "generated", agent_id=agent.id, agent_name=agent.name, template_id=template_id,
               template_name=template_name, theme_id=theme.id, image=str(image.relative_to(ROOT)), source_url=source_url)

        result = {"topic": blog["title"], "agent": agent.id, "template": template_name, "template_id": template_id,
                  "theme": theme.id, "orientation": Config.ORIENTATION, "image": str(image.relative_to(ROOT)), "status": "generated"}

        if not args.dry_run:
            fb = FacebookService.post_image(str(image), make_caption(blog, agent))
            post_id = fb.get("post_id") or fb.get("id")
            record(state, blog, "published", agent_id=agent.id, agent_name=agent.name, template_id=template_id,
                   template_name=template_name, theme_id=theme.id, image=str(image.relative_to(ROOT)), facebook_post_id=post_id,
                   source_url=source_url)
            result.update(status="published", facebook_post_id=post_id)

        save_history(state)
        summary = {"status": result["status"], "result": result, "scheduled_time_ist": now_ist.isoformat(),
                   "topic_cycle": state["topic_cycle"], "template_cycle": state["template_cycle"],
                   "theme_cycle": state.get("theme_cycle", 0), "themes_used_in_cycle": len(state.get("theme_used", [])),
                   "templates_used_in_cycle": len(state["template_used"]), "runtime_seconds": round(time.time()-started, 2)}
        (OUT / "latest_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    except Exception as exc:
        record(state, blog, "failed", agent_id=agent.id, agent_name=agent.name, template_id=template_id,
               template_name=template_name, error=str(exc), source_url=source_url)
        save_history(state)
        raise

if __name__ == "__main__":
    main()
