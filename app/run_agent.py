from __future__ import annotations
import argparse, json, time, re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from app.config import Config
from app.content_agents import fetch_news_topic, get_agent
from app.facebook_service import FacebookService
from app.carousel_builder import build_carousel
from app.logger import logger
from app.quality_engine import prepare_blog, validate_blog, make_caption
from app.state import load_history, save_history, record

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/"output"

def main():
    parser=argparse.ArgumentParser(description="Daily sourced technical blog carousel publisher")
    parser.add_argument("--dry-run",action="store_true",help="Create slides without publishing")
    args=parser.parse_args(); started=time.time(); OUT.mkdir(exist_ok=True)
    state=load_history(); agent=get_agent("technical_blog")
    blog,source_url=fetch_news_topic()
    blog=prepare_blog(blog,agent.id,state.get("history",[]))
    # A current headline can recur in news feeds; retain source and allow repeat only if content differs.
    valid,errors=validate_blog(blog)
    if not valid: raise ValueError(f"Content quality validation failed: {errors}")
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    carousel_dir=OUT/"carousels"/stamp
    slides=build_carousel(blog,carousel_dir)
    caption=(f"{blog['hook']}\n\n{blog['original_title']}\n\n{blog['description']}\n\n"
             f"Source: {source_url}\n\nTechnical takeaways and practical context in the slides. Verify critical details with the original source and official documentation.\n\n"
             f"Follow {Config.APP_NAME} for daily technical explainers.\n{Config.FACEBOOK_PAGE_URL}\n{Config.INSTAGRAM_URL}\n{Config.YOUTUBE_URL}\n{Config.WEBSITE_URL}\n\n#Technology #SoftwareEngineering #AI #CloudComputing #CyberSecurity #Developers")
    result={"status":"generated","topic":blog["original_title"],"source_url":source_url,"slides":[str(p.relative_to(ROOT)) for p in slides],"slide_count":len(slides)}
    if not args.dry_run:
        Config.validate_facebook(); FacebookService.validate_page_access()
        fb=FacebookService.post_carousel(slides,caption)
        result.update({"status":"published","facebook_post_id":fb.get("post_id"),"slide_count":fb.get("slide_count")})
    record(state,blog,result["status"],agent_id=agent.id,agent_name=agent.name,source_url=source_url,slides=result["slides"],slide_count=len(slides),facebook_post_id=result.get("facebook_post_id"),content_fingerprint=blog["content_fingerprint"],error=None)
    save_history(state)
    summary={**result,"app_name":Config.APP_NAME,"scheduled_at_utc":datetime.now(timezone.utc).isoformat(),"runtime_seconds":round(time.time()-started,2)}
    (OUT/"latest_summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    logger.info("Run finished: %s",json.dumps(summary,ensure_ascii=False))
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
