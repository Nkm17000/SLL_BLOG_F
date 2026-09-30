from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parent.parent
TOPICS=ROOT/"data/topics.json"
HISTORY=ROOT/"data/blog_history.json"

def load_topics():
    return json.loads(TOPICS.read_text(encoding="utf-8"))["topics"]

def load_history():
    if not HISTORY.exists(): return {"version":1,"history":[]}
    return json.loads(HISTORY.read_text(encoding="utf-8"))

def save_history(data):
    HISTORY.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")

def next_pending(topics,history):
    completed={x["topic_id"] for x in history.get("history",[]) if x.get("status")=="completed"}
    for t in topics:
        if t["id"] not in completed: return t
    return None

def record(topic,status,**extra):
    data=load_history()
    item={
        "topic_id":topic["id"],
        "topic":topic["title"],
        "category":topic["category"],
        "status":status,
        "timestamp_utc":datetime.now(timezone.utc).isoformat(),
        **extra
    }
    data["history"].append(item)
    save_history(data)
    return item
