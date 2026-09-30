from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
HISTORY = ROOT / "data/blog_history.json"

def _default():
    return {"version": 5, "topic_cycle": 0, "topic_used": [], "combo_cycle": 0, "combo_used": [], "history": []}

def load_history():
    if not HISTORY.exists(): return _default()
    try:
        data=json.loads(HISTORY.read_text(encoding="utf-8"))
        if not isinstance(data,dict): raise ValueError("history is not an object")
        base=_default(); base.update(data); base["version"]=5
        for k in ("topic_used","combo_used","history"):
            if not isinstance(base.get(k),list): base[k]=[]
        return base
    except Exception as exc:
        print(f"WARNING: invalid history file: {exc}; starting fresh")
        return _default()

def save_history(data):
    HISTORY.parent.mkdir(parents=True,exist_ok=True)
    payload={k:data.get(k) for k in ("version","topic_cycle","topic_used","combo_cycle","combo_used","history")}
    tmp=HISTORY.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    tmp.replace(HISTORY)

def record(data, blog, status, **extra):
    item={"topic_id":blog["id"],"topic":blog["title"],"category":blog["category"],"status":status,"timestamp_utc":datetime.now(timezone.utc).isoformat(),**extra}
    data.setdefault("history",[]).append(item); save_history(data); return item
