from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
HISTORY=ROOT/"data/blog_history.json"
def _default(): return {"version":1,"history":[]}
def load_history():
    if not HISTORY.exists(): return _default()
    try:
        data=json.loads(HISTORY.read_text(encoding="utf-8"))
        return data if isinstance(data,dict) and isinstance(data.get("history",[]),list) else _default()
    except Exception: return _default()
def save_history(data):
    HISTORY.parent.mkdir(parents=True,exist_ok=True); tmp=HISTORY.with_suffix(".tmp")
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); tmp.replace(HISTORY)
def record(data,blog,status,**extra):
    item={"topic_id":blog.get("id"),"topic":blog.get("title"),"category":blog.get("category"),"status":status,"timestamp_utc":datetime.now(timezone.utc).isoformat(),**extra}
    data.setdefault("history",[]).append(item); data["history"]=data["history"][-500:]; return item
