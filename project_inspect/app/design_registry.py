from __future__ import annotations

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ROOT / "data" / "designs.json"


def load_designs() -> list[dict]:
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    designs = data.get("designs", [])
    if not designs:
        raise ValueError("data/designs.json contains no designs")
    ids = [d.get("id") for d in designs]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate design IDs in data/designs.json")
    for d in designs:
        if not d.get("id") or not d.get("type") or not d.get("name"):
            raise ValueError(f"Invalid design entry: {d}")
    return designs


DESIGNS = load_designs()


def get_design(index: int) -> dict:
    return DESIGNS[index % len(DESIGNS)]
