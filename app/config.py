from __future__ import annotations
import os
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
    # Text-only publishing: no slide or image conversion.
    TEXT_ONLY_POST = True

    @classmethod
    def validate_facebook(cls):
        missing = [k for k, v in (("FACEBOOK_PAGE_ID", cls.FACEBOOK_PAGE_ID), ("FACEBOOK_PAGE_TOKEN", cls.FACEBOOK_PAGE_TOKEN)) if not v]
        if missing:
            raise ValueError("Missing GitHub repository secrets: " + ", ".join(missing))
