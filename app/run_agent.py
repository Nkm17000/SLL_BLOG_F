from __future__ import annotations
import argparse, json, time
from datetime import datetime, timezone
from pathlib import Path
from app.config import Config
from app.content_agents import fetch_news_topic, get_agent
from app.facebook_service import FacebookService
from app.logger import logger
from app.article_content import build_text_post
from app.state import load_history, save_history, record

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/"output"

def main():
    parser=argparse.ArgumentParser(description="Fetch and publish a source-based technical article as one text-only Facebook post")
    parser.add_argument("--dry-run",action="store_true",help="Generate descriptive post text without publishing")
    args=parser.parse_args(); started=time.time(); OUT.mkdir(exist_ok=True)
    state=load_history(); agent=get_agent("technical_blog")
    blog,source_url=fetch_news_topic()
    if len(blog.get("points",[])) != 5 or any(not p.get("description","").strip() for p in blog["points"]):
        raise ValueError("Article content quality check failed: expected five descriptive sections")
    caption=build_text_post(blog["original_title"],blog,source_url,blog.get("published",""),Config.APP_NAME)
    if len(caption)<500:
        raise ValueError("Generated article summary is too short; refusing to publish headline-only content")
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (OUT/"latest_post.txt").write_text(caption+"\n",encoding="utf-8")
    result={"status":"generated","topic":blog["original_title"],"source_url":source_url,"content_mode":blog.get("content_mode","rss_fallback"),"article_text_length":blog.get("article_text_length",0),"post_character_count":len(caption),"post_type":"text_only"}
    if not args.dry_run:
        Config.validate_facebook(); FacebookService.validate_page_access()
        fb=FacebookService.post_text(caption)
        result.update({"status":"published","facebook_post_id":fb.get("post_id")})
    record(state,blog,result["status"],agent_id=agent.id,agent_name=agent.name,source_url=source_url,content_mode=result["content_mode"],article_text_length=result["article_text_length"],facebook_post_id=result.get("facebook_post_id"),error=None)
    save_history(state)
    summary={**result,"app_name":Config.APP_NAME,"scheduled_at_utc":datetime.now(timezone.utc).isoformat(),"runtime_seconds":round(time.time()-started,2)}
    (OUT/"latest_summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    logger.info("Run finished: %s",json.dumps(summary,ensure_ascii=False))
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
