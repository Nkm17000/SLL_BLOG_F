from __future__ import annotations

import random
import time
from pathlib import Path

import requests
from app.config import Config
from app.logger import logger


class FacebookService:
    @staticmethod
    def _safe_json(response):
        try:
            return response.json()
        except ValueError:
            return {"raw": response.text[:2000]}

    @staticmethod
    def _request(method, url, **kwargs):
        last = None
        for attempt in range(1, 6):
            logger.info("Facebook API attempt %s/5: %s %s", attempt, method, url)
            try:
                response = requests.request(method, url, timeout=60, **kwargs)
            except requests.RequestException as exc:
                logger.error("Facebook HTTP request exception: %s", exc)
                if attempt == 5:
                    raise
                delay = min(20, 2 ** (attempt - 1)) + random.uniform(0, 0.5)
                logger.warning("Retrying in %.1fs", delay)
                time.sleep(delay)
                continue

            last = response
            payload = FacebookService._safe_json(response)
            logger.info("Facebook response: HTTP %s", response.status_code)

            if response.ok:
                logger.info("Facebook API success: %s", str(payload)[:1500])
                return response

            error = payload.get("error", {}) if isinstance(payload, dict) else {}
            logger.error(
                "Facebook API error: HTTP=%s code=%s type=%s message=%s",
                response.status_code,
                error.get("code"),
                error.get("type"),
                error.get("message") or payload,
            )

            code = error.get("code")
            transient = response.status_code in {429, 500, 502, 503, 504} or code in {1, 2, 4, 17, 32, 613}
            if not transient or attempt == 5:
                return response

            delay = min(20, 2 ** (attempt - 1)) + random.uniform(0, 0.5)
            logger.warning("Transient Facebook error. Retrying in %.1fs", delay)
            time.sleep(delay)

        return last


    @classmethod
    def validate_page_access(cls):
        """Verify the configured Page ID/token before uploading the image."""
        url = f"https://graph.facebook.com/{Config.FACEBOOK_GRAPH_API_VERSION}/{Config.FACEBOOK_PAGE_ID}"
        logger.info("Facebook preflight: validating Page access...")
        response = cls._request(
            "GET",
            url,
            params={"fields": "id,name", "access_token": Config.FACEBOOK_PAGE_TOKEN},
        )
        payload = cls._safe_json(response)
        if not response.ok:
            raise RuntimeError(f"Facebook Page access check failed: HTTP {response.status_code}: {payload}")
        logger.info("Facebook Page access OK. Page ID=%s Name=%s", payload.get("id"), payload.get("name"))
        return payload

    @classmethod
    def post_image(cls, image_path, caption):
        image = Path(image_path)
        if not image.exists():
            raise FileNotFoundError(f"Image does not exist: {image}")

        logger.info("Preparing Facebook image upload")
        logger.info("Image path: %s", image)
        logger.info("Image size: %s bytes", image.stat().st_size)
        logger.info("Caption length: %s characters", len(caption or ""))
        logger.info("Page ID configured: %s", bool(Config.FACEBOOK_PAGE_ID))
        logger.info("Page token configured: %s", bool(Config.FACEBOOK_PAGE_TOKEN))
        logger.info("Graph API version: %s", Config.FACEBOOK_GRAPH_API_VERSION)

        url = f"https://graph.facebook.com/{Config.FACEBOOK_GRAPH_API_VERSION}/{Config.FACEBOOK_PAGE_ID}/photos"
        with image.open("rb") as handle:
            files = {"source": (image.name, handle, "image/jpeg")}
            data = {
                "published": "true",
                "caption": caption or "",
                "access_token": Config.FACEBOOK_PAGE_TOKEN,
            }
            response = cls._request("POST", url, files=files, data=data)

        payload = cls._safe_json(response)
        if not response.ok:
            raise RuntimeError(f"Facebook upload failed: HTTP {response.status_code}: {payload}")

        post_id = payload.get("post_id") or payload.get("id")
        logger.info("Facebook image published successfully. Post ID: %s", post_id)
        return payload
