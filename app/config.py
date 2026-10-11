from __future__ import annotations
import os, json
from dotenv import load_dotenv
load_dotenv(override=True)

class Config:
    APP_NAME = os.getenv("APP_NAME", "Smart Learning Lab 247")
    FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "").strip()
    FACEBOOK_PAGE_TOKEN = os.getenv("FACEBOOK_PAGE_TOKEN", "").strip()
    FACEBOOK_GRAPH_API_VERSION = os.getenv("FACEBOOK_GRAPH_API_VERSION", "v23.0")
    FACEBOOK_PAGE_URL = os.getenv("FACEBOOK_PAGE_URL", "https://www.facebook.com/smartlearninglab247")
    INSTAGRAM_URL = os.getenv("INSTAGRAM_URL", "https://www.instagram.com/smartlearninglab247")
    YOUTUBE_URL = os.getenv("YOUTUBE_URL", "https://www.youtube.com/@smartlearninglab247")
    WEBSITE_URL = os.getenv("WEBSITE_URL", "https://smartlearninglab-react.pages.dev/")
    RSS_QUERY = os.getenv("RSS_QUERY", "latest technology software engineering AI cybersecurity cloud developer tools")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    # Config supports multiple destinations through config/social_accounts.json.
    SOCIAL_ACCOUNTS_PATH = os.getenv("SOCIAL_ACCOUNTS_PATH", "config/social_accounts.json")
    TEXT_ONLY_POST = False

    @classmethod
    def social_accounts(cls):
        path = __import__("pathlib").Path(cls.SOCIAL_ACCOUNTS_PATH)
        accounts = {"facebook": [], "instagram": []}
        if path.exists():
            raw = json.loads(path.read_text(encoding="utf-8"))
            for platform in accounts:
                values = raw.get(platform, [])
                if isinstance(values, dict):
                    values = [dict(v, key=k) if isinstance(v, dict) else {"key": k} for k, v in values.items()]
                for i, item in enumerate(values, 1):
                    if not isinstance(item, dict) or item.get("enabled", True) is False:
                        continue
                    id_env = item.get("id_env", "")
                    token_env = item.get("token_env", "")
                    page_id = os.getenv(id_env, "").strip() if id_env else ""
                    token = os.getenv(token_env, "").strip() if token_env else ""
                    # Backwards compatibility for the original single Facebook Page secrets.
                    if platform == "facebook" and not id_env and i == 1:
                        page_id = page_id or cls.FACEBOOK_PAGE_ID
                        token = token or cls.FACEBOOK_PAGE_TOKEN
                    if page_id and token:
                        accounts[platform].append({"name": item.get("name", f"{platform.title()} {i}"), "id": page_id, "token": token})
                    else:
                        logger_msg = f"Skipping {platform} account {item.get('name', i)}: missing configured ID/token secret."
                        print(logger_msg)
        # Legacy mode if no JSON exists or has no Facebook entries.
        if not accounts["facebook"] and cls.FACEBOOK_PAGE_ID and cls.FACEBOOK_PAGE_TOKEN:
            accounts["facebook"].append({"name": "Facebook Page (legacy)", "id": cls.FACEBOOK_PAGE_ID, "token": cls.FACEBOOK_PAGE_TOKEN})
        return accounts

    @classmethod
    def validate_facebook(cls):
        missing = [k for k, v in (("FACEBOOK_PAGE_ID", cls.FACEBOOK_PAGE_ID), ("FACEBOOK_PAGE_TOKEN", cls.FACEBOOK_PAGE_TOKEN)) if not v]
        if missing:
            raise ValueError("Missing GitHub repository secrets: " + ", ".join(missing))
