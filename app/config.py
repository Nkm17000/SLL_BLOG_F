import os
from dotenv import load_dotenv

load_dotenv(override=True)


class Config:
    FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
    FACEBOOK_PAGE_TOKEN = os.getenv("FACEBOOK_PAGE_TOKEN")
    FACEBOOK_GRAPH_API_VERSION = os.getenv("FACEBOOK_GRAPH_API_VERSION", "v23.0")
    POST_MODE = os.getenv("POST_MODE", "video")
    ORIENTATION = os.getenv("ORIENTATION", "horizontal")
    IMAGE_WIDTH = int(os.getenv("IMAGE_WIDTH", "1080"))
    IMAGE_HEIGHT = int(os.getenv("IMAGE_HEIGHT", "1350"))

    @classmethod
    def validate(cls):
        missing = []
        for key in ("FACEBOOK_PAGE_ID", "FACEBOOK_PAGE_TOKEN"):
            if not getattr(cls, key):
                missing.append(key)
        if missing:
            raise ValueError("Missing required environment variables: " + ", ".join(missing))
