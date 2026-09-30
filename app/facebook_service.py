from __future__ import annotations
import random, time, requests
from requests.exceptions import RequestException
from app.config import Config
from app.logger import logger

class FacebookService:
    @staticmethod
    def _request(method,url,**kwargs):
        last=None
        for attempt in range(1,6):
            r=requests.request(method,url,timeout=45,**kwargs)
            last=r
            if r.ok: return r
            try: p=r.json()
            except ValueError: p={}
            e=p.get("error",{}) if isinstance(p,dict) else {}
            code=e.get("code")
            transient=r.status_code in {429,500,502,503,504} or code in {1,2,4,17,32,613}
            if not transient or attempt==5:
                logger.error("Facebook API failed: HTTP=%s body=%s",r.status_code,str(p)[:1000])
                return r
            delay=min(20,1.5*(2**(attempt-1)))+random.uniform(0,.5)
            logger.warning("Retrying Facebook API in %.1fs",delay)
            time.sleep(delay)
        return last

    @classmethod
    def post_image(cls,image_path,caption):
        url=f"https://graph.facebook.com/{Config.FACEBOOK_GRAPH_API_VERSION}/{Config.FACEBOOK_PAGE_ID}/photos"
        with open(image_path,"rb") as f:
            files={"source":(image_path.split("/")[-1],f,"image/jpeg")}
            data={"published":"true","caption":caption,"access_token":Config.FACEBOOK_PAGE_TOKEN}
            r=cls._request("POST",url,files=files,data=data)
        r.raise_for_status()
        return r.json()

    @classmethod
    def post_text(cls,message):
        url=f"https://graph.facebook.com/{Config.FACEBOOK_GRAPH_API_VERSION}/{Config.FACEBOOK_PAGE_ID}/feed"
        r=cls._request("POST",url,data={"message":message,"access_token":Config.FACEBOOK_PAGE_TOKEN})
        r.raise_for_status()
        return r.json()
