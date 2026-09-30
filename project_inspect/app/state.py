from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from app.design_registry import DESIGNS

ROOT = Path(__file__).resolve().parent.parent
HISTORY = ROOT / "data/blog_history.json"
DEFAULT_HISTORY = {"version": 5, "next_generation": 0, "history": []}


def load_history():
    if not HISTORY.exists():
        return DEFAULT_HISTORY.copy()
    try:
        data = json.loads(HISTORY.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("history", []), list):
            raise ValueError("invalid history format")
        data.setdefault("next_generation", len(data.get("history", [])))
        data["version"] = 5
        return data
    except Exception as exc:
        print(f"WARNING: invalid history file: {exc}")
        return DEFAULT_HISTORY.copy()


def save_history(data):
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 5,
        "next_generation": int(data.get("next_generation", 0)),
        "history": data.get("history", []),
    }
    tmp = HISTORY.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(HISTORY)


def reserve_generation(data):
    # Design order is the single source of truth in data/designs.json.
    # For 15 designs: generations 0..14 use designs 1..15,
    # generation 15 starts again at design 1.
    generation = int(data.get("next_generation", 0))
    design_index = generation % len(DESIGNS)
    data["next_generation"] = generation + 1
    save_history(data)
    return generation, design_index


def record(data, topic, status, **extra):
    item = {
        "generation": extra.pop("generation", None),
        "design_index": extra.pop("design_index", None),
        "design_id": extra.pop("design_id", None),
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
