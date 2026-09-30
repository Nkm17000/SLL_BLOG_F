import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
    FACEBOOK_PAGE_TOKEN = os.getenv("FACEBOOK_PAGE_TOKEN")
    FACEBOOK_GRAPH_API_VERSION = os.getenv("FACEBOOK_GRAPH_API_VERSION", "v23.0")
    POST_MODE = os.getenv("POST_MODE", "image")  # image or text
    IMAGE_WIDTH = int(os.getenv("IMAGE_WIDTH", "1080"))
    IMAGE_HEIGHT = int(os.getenv("IMAGE_HEIGHT", "1350"))

    @classmethod
    def validate(cls):
        missing=[]
        for key in ("GROQ_API_KEY","FACEBOOK_PAGE_ID","FACEBOOK_PAGE_TOKEN"):
            if not getattr(cls,key):
                missing.append(key)
        if missing:
            raise ValueError("Missing required environment variables: " + ", ".join(missing))
