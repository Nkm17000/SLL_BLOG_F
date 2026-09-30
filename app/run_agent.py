from __future__ import annotations
import argparse, json
from pathlib import Path
from app.config import Config
from app.logger import logger
from app.blog_generator import generate_blog
from app.image_generator import BlogImage
from app.facebook_service import FacebookService
from app.state import load_topics, load_history, next_pending, record

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/"output"

def main():
    parser=argparse.ArgumentParser(description="Smart Learning Lab Technical Blog Facebook Publisher")
    parser.add_argument("--topic",default=None,help="Topic ID from data/topics.json")
    parser.add_argument("--dry-run",action="store_true",help="Generate content/image but do not publish")
    args=parser.parse_args()

    Config.validate()
    OUT.mkdir(exist_ok=True)

    topics=load_topics()
    if args.topic:
        topic=next((t for t in topics if t["id"]==args.topic),None)
        if not topic: raise ValueError(f"Unknown topic: {args.topic}")
    else:
        topic=next_pending(topics,load_history())
        if not topic:
            print("All configured topics are completed. Add new topics to data/topics.json or use --topic after resetting history.")
            return

    logger.info("Generating blog: %s",topic["title"])
    blog=generate_blog(topic)

    safe=topic["id"].replace("/","-")
    image_path=OUT/f"{safe}.jpg"
    BlogImage.render(blog,image_path)

    blog_path=OUT/f"{safe}.json"
    blog_path.write_text(json.dumps(blog,ensure_ascii=False,indent=2),encoding="utf-8")

    if args.dry_run:
        record(topic,"generated",image=str(image_path.relative_to(ROOT)),title=blog["title"])
        print(json.dumps({"status":"dry_run","topic":topic,"image":str(image_path)},ensure_ascii=False,indent=2))
        return

    caption=blog["caption"]
    logger.info("Publishing to Facebook Page")
    try:
        result=FacebookService.post_image(str(image_path),caption)
    except Exception as exc:
        record(topic,"failed",error=str(exc),image=str(image_path.relative_to(ROOT)),title=blog["title"])
        raise

    record(topic,"completed",post_id=result.get("post_id") or result.get("id"),image=str(image_path.relative_to(ROOT)),title=blog["title"])
    print(json.dumps({"status":"completed","topic":topic["title"],"facebook":result,"image":str(image_path)},ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
