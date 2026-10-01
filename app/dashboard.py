from __future__ import annotations
import html, json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent

def build_dashboard(history: dict, output: Path) -> Path:
    records = history.get("history", [])
    published = [r for r in records if r.get("status") == "published"]
    failed = [r for r in records if r.get("status") == "failed"]
    agents = Counter(r.get("agent_id", "unknown") for r in published)
    themes = Counter(r.get("theme_id", "unknown") for r in published)
    templates = Counter(r.get("template_id", "unknown") for r in published)
    rows = "".join(
        f"<tr><td>{html.escape(str(r.get('timestamp_utc','')))}</td><td>{html.escape(str(r.get('agent_name',r.get('agent_id',''))))}</td><td>{html.escape(str(r.get('topic','')))}</td><td>{html.escape(str(r.get('theme_id','')))}</td><td>{html.escape(str(r.get('template_id','')))}</td><td>{html.escape(str(r.get('status','')))}</td></tr>"
        for r in records[-40:][::-1]
    )
    def lis(counter):
        return "".join(f"<li><b>{html.escape(str(k))}</b>: {v}</li>" for k,v in counter.most_common())
    doc=f'''<!doctype html><html><head><meta charset="utf-8"><title>Smart Learning Lab Dashboard</title><style>body{{font-family:Arial,sans-serif;background:#f5f8fc;color:#172b52;margin:0;padding:32px}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}}.card{{background:#fff;border:1px solid #dce4ee;border-radius:18px;padding:20px;box-shadow:0 8px 24px rgba(30,60,90,.07)}}.num{{font-size:32px;font-weight:900}}table{{width:100%;border-collapse:collapse;background:#fff;border-radius:18px;overflow:hidden}}th,td{{padding:10px;border-bottom:1px solid #edf1f5;text-align:left;font-size:13px}}th{{background:#eef5ff}}ul{{line-height:1.8}}</style></head><body><h1>Smart Learning Lab</h1><p>Publishing and content-quality dashboard</p><div class="grid"><div class="card"><div class="num">{len(published)}</div>Published</div><div class="card"><div class="num">{len(failed)}</div>Failed</div><div class="card"><div class="num">{len(history.get('agent_topic_used',{}))}</div>Active Agents</div><div class="card"><div class="num">30</div>Light Themes</div></div><div class="grid" style="margin-top:16px"><div class="card"><h3>Posts by agent</h3><ul>{lis(agents)}</ul></div><div class="card"><h3>Template usage</h3><ul>{lis(templates)}</ul></div><div class="card"><h3>Theme usage</h3><ul>{lis(themes)}</ul></div><div class="card"><h3>Rotation</h3><p>Topic cycles: {history.get('topic_cycle',0)}</p><p>Template cycles: {history.get('template_cycle',0)}</p><p>Theme cycles: {history.get('theme_cycle',0)}</p></div></div><h2>Recent activity</h2><table><thead><tr><th>UTC</th><th>Agent</th><th>Topic</th><th>Theme</th><th>Template</th><th>Status</th></tr></thead><tbody>{rows}</tbody></table></body></html>'''
    output.parent.mkdir(parents=True,exist_ok=True); output.write_text(doc,encoding='utf-8'); return output
