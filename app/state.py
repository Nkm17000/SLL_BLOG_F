from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HISTORY = ROOT / "data/blog_history.json"
DEFAULT_HISTORY = {"version": 4, "next_generation": 0, "history": []}


def load_history():
    if not HISTORY.exists():
        return DEFAULT_HISTORY.copy()
    try:
        data = json.loads(HISTORY.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("history", []), list):
            raise ValueError("invalid history format")
        data.setdefault("next_generation", len(data.get("history", [])))
        data["version"] = 4
        return data
    except Exception as exc:
        print(f"WARNING: invalid history file: {exc}")
        return DEFAULT_HISTORY.copy()


def save_history(data):
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 4,
        "next_generation": int(data.get("next_generation", 0)),
        "history": data.get("history", []),
    }
    tmp = HISTORY.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(HISTORY)


def reserve_generation(data):
    # UX order: 1,2,3,4,5,1,2,3,4,5...
    generation = int(data.get("next_generation", 0))
    ux_index = generation % 5
    data["next_generation"] = generation + 1
    save_history(data)
    return generation, ux_index


def record(data, topic, status, **extra):
    item = {
        "generation": extra.pop("generation", None),
        "ux_index": extra.pop("ux_index", None),
        "topic_id": topic["id"],
        "topic": topic["title"],
        "category": topic["category"],
        "status": status,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        **extra,
    }
    data.setdefault("history", []).append(item)
    save_history(data)
    return item
