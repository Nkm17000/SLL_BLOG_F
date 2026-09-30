from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOPICS = ROOT / "data/topics.json"
HISTORY = ROOT / "data/blog_history.json"

DEFAULT_HISTORY = {"version": 3, "history": []}


def load_topics():
    return json.loads(TOPICS.read_text(encoding="utf-8"))["topics"]


def _default_history():
    return {"version": DEFAULT_HISTORY["version"], "history": []}


def load_history():
    """Load history safely. A damaged/empty history file must not crash a run."""
    if not HISTORY.exists():
        return _default_history()

    try:
        raw = HISTORY.read_text(encoding="utf-8").strip()
        if not raw:
            print("WARNING: data/blog_history.json is empty. Starting with empty history.")
            return _default_history()

        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("history root must be a JSON object")
        if not isinstance(data.get("history"), list):
            raise ValueError("history must be a JSON array")

        data["version"] = 3
        return data

    except (json.JSONDecodeError, UnicodeDecodeError, OSError, ValueError) as exc:
        # Never stop the publisher just because state is damaged.
        # The next successful save will replace the invalid file atomically.
        print(f"WARNING: invalid data/blog_history.json: {exc}")
        print("WARNING: continuing with empty history.")
        return _default_history()


def save_history(data):
    """Write history atomically so GitHub Actions never sees a half-written JSON file."""
    HISTORY.parent.mkdir(parents=True, exist_ok=True)

    normalized = {
        "version": 3,
        "history": data.get("history", []),
    }

    temp = HISTORY.with_suffix(".tmp")
    payload = json.dumps(normalized, ensure_ascii=False, indent=2) + "\n"
    temp.write_text(payload, encoding="utf-8")
    temp.replace(HISTORY)


def next_pending(topics, history):
    completed = {
        x["topic_id"]
        for x in history.get("history", [])
        if x.get("status") == "completed" and x.get("topic_id")
    }
    for topic in topics:
        if topic["id"] not in completed:
            return topic
    return None


def previous_theme_id(history):
    for item in reversed(history.get("history", [])):
        if item.get("status") == "completed" and item.get("theme_id"):
            return item["theme_id"]
    return None


def record(topic, status, **extra):
    data = load_history()
    data.setdefault("history", [])

    item = {
        "topic_id": topic["id"],
        "topic": topic["title"],
        "category": topic["category"],
        "status": status,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        **extra,
    }

    data["history"].append(item)
    save_history(data)
    return item
