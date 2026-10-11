from __future__ import annotations
import json, random, time
from pathlib import Path
import requests
from app.config import Config
from app.logger import logger

class FacebookService:
    @staticmethod
    def _payload(response):
        try: return response.json()
        except ValueError: return {"raw": response.text[:1000]}

    @classmethod
    def _request(cls, method, url, **kwargs):
        for attempt in range(1, 5):
            try: response=requests.request(method,url,timeout=90,**kwargs)
            except requests.RequestException:
                if attempt==4: raise
                time.sleep(min(2**attempt,12)); continue
            data=cls._payload(response)
            if response.ok: return data
            error=data.get("error",{}) if isinstance(data,dict) else {}
            code=error.get("code")
            transient=response.status_code in (429,500,502,503,504) or code in (1,2,4,17,32,613)
            if not transient or attempt==4:
                raise RuntimeError(f"Facebook API failed HTTP {response.status_code}, code={code}: {data}")
            time.sleep(min(2**attempt,12)+random.random())
        raise RuntimeError("Facebook request exhausted retries")

    @classmethod
    def validate_page_access(cls):
        url=f"https://graph.facebook.com/{Config.FACEBOOK_GRAPH_API_VERSION}/{Config.FACEBOOK_PAGE_ID}"
        data=cls._request("GET",url,params={"fields":"id,name","access_token":Config.FACEBOOK_PAGE_TOKEN})
        logger.info("Facebook Page access OK: %s (%s)",data.get("name"),data.get("id"))
        return data

    @classmethod
    def post_carousel(cls, image_paths, caption):
        paths=[Path(p) for p in image_paths]
        if not 2 <= len(paths) <= 10: raise ValueError("Facebook multi-photo posts require 2–10 images")
        media=[]
        photos_url=f"https://graph.facebook.com/{Config.FACEBOOK_GRAPH_API_VERSION}/{Config.FACEBOOK_PAGE_ID}/photos"
        for path in paths:
            if not path.is_file(): raise FileNotFoundError(path)
            with path.open("rb") as f:
                data=cls._request("POST",photos_url,files={"source":(path.name,f,"image/jpeg")},data={"published":"false","access_token":Config.FACEBOOK_PAGE_TOKEN})
            photo_id=data.get("id")
            if not photo_id: raise RuntimeError(f"Facebook did not return a photo ID for {path.name}: {data}")
            media.append({"media_fbid":photo_id})
            logger.info("Uploaded carousel image %s/%s",len(media),len(paths))
        feed_url=f"https://graph.facebook.com/{Config.FACEBOOK_GRAPH_API_VERSION}/{Config.FACEBOOK_PAGE_ID}/feed"
        params={"message":caption,"access_token":Config.FACEBOOK_PAGE_TOKEN}
        params.update({f"attached_media[{i}]":json.dumps(item,separators=(",",":")) for i,item in enumerate(media)})
        result=cls._request("POST",feed_url,data=params)
        logger.info("Facebook multi-photo post published: %s",result.get("id"))
        return {"post_id":result.get("id"),"photo_ids":[x["media_fbid"] for x in media],"slide_count":len(media)}
