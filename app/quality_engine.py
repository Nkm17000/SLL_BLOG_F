from __future__ import annotations

import hashlib
import re
from difflib import SequenceMatcher

AGENT_SERIES = {
    "student": "Tech Made Simple",
    "tech_facts": "Tech Fact of the Day",
    "ai": "AI Explained",
    "ai_tools": "AI Tools in Practice",
    "coding": "Code Better",
    "debugging": "Debug This",
    "howto": "Build It Step by Step",
    "concepts": "One Concept, Clearly",
    "cloud": "Cloud Architecture",
    "database": "Database Fundamentals",
    "app_development": "Build Better Apps",
    "cybersecurity": "Secure by Design",
    "experiments": "Tech Lab",
    "projects": "Build This Project",
    "productivity": "Developer Productivity",
    "career": "Tech Career Skills",
    "news": "Tech News Explained",
    "infographic": "Visual Tech",
    "repurposing": "Tech in Multiple Angles",
    "technical_blog": "Technical Deep Dive",
}

CTAS = (
    "Save this for later 📌",
    "Follow Smart Learning Lab for the next concept.",
    "Share this with someone learning tech.",
    "Which part should we explain next?",
    "Keep this as your quick technical reference.",
)

DIFFICULTY_BY_AGENT = {
    "student": "beginner", "tech_facts": "beginner", "ai": "intermediate", "ai_tools": "beginner",
    "coding": "intermediate", "debugging": "intermediate", "howto": "intermediate", "concepts": "beginner",
    "cloud": "intermediate", "database": "intermediate", "app_development": "intermediate",
    "cybersecurity": "intermediate", "experiments": "intermediate", "projects": "intermediate",
    "productivity": "beginner", "career": "beginner", "news": "intermediate", "infographic": "beginner",
    "repurposing": "beginner", "technical_blog": "intermediate",
}

PREFIXES = re.compile(r"^(?:Learn Simply|How-To|Project Idea|Career Skills|Security Guide|Developer Guide|AI Explained|AI Tool Guide|Cloud Guide|Database Guide|App Development|Debugging Guide|Tech Fact|Tech Experiment|Productivity Tip|Visual Explainer|Content Repurpose|Concept Explained|Build It|Technical Deep Dive|Tech News Explained)\s*:\s*", re.I)

def clean_topic_title(title: str) -> str:
    title = PREFIXES.sub("", title or "").strip()
    title = re.sub(r"\s+", " ", title)
    return title[:110].rstrip(" .")

def make_hook(title: str, agent_id: str) -> str:
    topic = clean_topic_title(title)
    templates = {
        "student": f"{topic} — explained simply",
        "tech_facts": f"One tech idea you should know: {topic}",
        "ai": f"How does {topic} actually work?",
        "ai_tools": f"How to use {topic} in practice",
        "coding": f"Build better with {topic}",
        "debugging": f"Debug this: {topic}",
        "howto": (topic if topic.lower().startswith("how to ") else f"How to build {topic}"),
        "concepts": f"{topic} — the simple explanation",
        "cloud": f"{topic}: architecture made clear",
        "database": f"{topic}: what developers need to know",
        "app_development": f"Build smarter apps with {topic}",
        "cybersecurity": f"{topic}: secure it the right way",
        "experiments": f"Try this tech experiment: {topic}",
        "projects": f"Build this: {topic}",
        "productivity": f"Work smarter with {topic}",
        "career": f"A practical skill: {topic}",
        "news": f"What this tech update means: {topic}",
        "infographic": f"{topic} — visualized",
        "repurposing": f"{topic}: 5 useful angles",
        "technical_blog": f"{topic} — technical deep dive",
    }
    hook = templates.get(agent_id, f"{topic} — explained clearly")
    # Keep the visual headline compact.
    if len(hook) > 72:
        hook = hook[:69].rsplit(" ", 1)[0] + "…"
    return hook

def real_world_example(blog: dict) -> str:
    p = blog.get("points", [])
    if len(p) >= 3:
        return f"Real-world lens: {p[2].get('description','See how the idea appears in a practical system.')}"
    return "Real-world lens: connect the concept to a practical system or workflow."

def fingerprint(blog: dict) -> str:
    text = " ".join([
        blog.get("title", ""), blog.get("description", ""),
        *[p.get("title", "") + " " + p.get("description", "") for p in blog.get("points", [])]
    ])
    normalized = re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:20]

def similar_to_history(blog: dict, history: list[dict], threshold: float = 0.86) -> bool:
    title = re.sub(r"[^a-z0-9]+", " ", clean_topic_title(blog.get("title", "")).lower()).strip()
    if not title:
        return False
    fp = fingerprint(blog)
    for item in history[-1500:]:
        if item.get("content_fingerprint") == fp:
            return True
        old = re.sub(r"[^a-z0-9]+", " ", clean_topic_title(item.get("topic", "")).lower()).strip()
        if old and SequenceMatcher(None, title, old).ratio() >= threshold:
            return True
    return False

def clean_point_text(blog: dict, agent_id: str) -> dict:
    result=dict(blog)
    result["description"]=re.sub(r"\s*Apply this through the [^.]+ perspective\.?", "", result.get("description", ""), flags=re.I).strip()
    points=[]
    for p in result.get("points", []):
        q=dict(p)
        q["title"]=re.sub(r"^.*?—\s*\d+:\s*", "", q.get("title", "")).strip()
        q["title"]=re.sub(r"^[A-Za-z ]+\s*[-–]\s*\d+:\s*", "", q["title"]).strip()
        q["description"]=re.sub(r"\s*Apply this through the [^.]+ perspective\.?", "", q.get("description", ""), flags=re.I).strip()
        q["items"]=[re.sub(r"\s*;\s*focus on [^;]+", "", str(x), flags=re.I).strip() for x in q.get("items", [])]
        points.append(q)
    result["points"]=points
    return result

def prepare_blog(blog: dict, agent_id: str, history: list[dict]) -> dict:
    result = clean_point_text(blog, agent_id)
    result["original_title"] = clean_topic_title(blog.get("original_title") or blog.get("title", ""))
    result["hook"] = blog.get("hook") or make_hook(result["original_title"], agent_id)
    result["difficulty"] = blog.get("difficulty") or DIFFICULTY_BY_AGENT.get(agent_id, "intermediate")
    result["series"] = blog.get("series") or AGENT_SERIES.get(agent_id, "Smart Learning Lab")
    result["language"] = blog.get("language") or "en-IN"
    result["format"] = "square_single_image"
    result["real_world_example"] = blog.get("real_world_example") or real_world_example(blog)
    result["cta"] = blog.get("cta") or CTAS[(len(history) + len(result.get("title", ""))) % len(CTAS)]
    result["content_fingerprint"] = fingerprint(result)
    result["quality"] = {
        "five_points": len(result.get("points", [])) == 5,
        "two_items_per_point": all(len(p.get("items", [])) == 2 for p in result.get("points", [])),
        "hook_length_ok": 18 <= len(result["hook"]) <= 72,
        "title_length_ok": len(result["original_title"]) <= 120,
        "has_real_world_example": bool(result["real_world_example"]),
        "has_cta": bool(result["cta"]),
        "not_duplicate": not similar_to_history(result, history),
    }
    return result

def validate_blog(blog: dict) -> tuple[bool, list[str]]:
    q = blog.get("quality", {})
    errors = [k for k, ok in q.items() if not ok]
    if len(blog.get("points", [])) != 5:
        errors.append("exactly_5_points")
    if any(len(p.get("items", [])) != 2 for p in blog.get("points", [])):
        errors.append("exactly_2_items_per_point")
    return not errors, errors

def make_caption(blog: dict, agent) -> str:
    hashtags = " ".join(agent.hashtags)
    difficulty = blog.get("difficulty", "intermediate").title()
    series = blog.get("series", "Smart Learning Lab")
    hook = blog.get("hook", blog.get("title", ""))
    return f"{hook}\n\n{blog.get('original_title', blog.get('title',''))}\n{blog.get('description','')}\n\nSeries: {series} • Level: {difficulty}\n\n{blog.get('cta','Save this for later 📌')}\n\n{hashtags}"
