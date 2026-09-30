from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from app.blog_generator import load_static_blogs
from app.facebook_service import FacebookService
from app.image_generator import BlogImage

ROOT = Path(__file__).resolve().parents[1]


class ProjectSmokeTests(unittest.TestCase):
    def test_static_blogs_have_required_content(self):
        blogs = load_static_blogs()
        self.assertGreaterEqual(len(blogs), 1)
        for blog in blogs:
            self.assertTrue(blog["title"])
            self.assertGreaterEqual(len(blog.get("sections", [])), 8)

    def test_all_five_ux_render_1080x1350(self):
        blogs = load_static_blogs()
        with tempfile.TemporaryDirectory() as tmp:
            for ux in range(5):
                out = Path(tmp) / f"ux{ux + 1}.jpg"
                BlogImage.render(blogs[ux % len(blogs)], out, ux_index=ux)
                self.assertTrue(out.exists())
                from PIL import Image
                with Image.open(out) as image:
                    self.assertEqual(image.size, (1080, 1350))
                    self.assertEqual(image.mode, "RGB")

    def test_hindi_mixed_text_does_not_crash(self):
        blogs = load_static_blogs()
        blog = dict(blogs[0])
        blog["title"] = "AI से पढ़ाई आसान कैसे बनाएं"
        blog["subtitle"] = "Learn AI in a simple Hindi + English format."
        blog["intro"] = "यह एक छोटा technical guide है. Start small and improve."
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "hindi.jpg"
            BlogImage.render(blog, out, ux_index=0)
            self.assertTrue(out.exists())

    @patch("app.facebook_service.requests.request")
    def test_facebook_success_response_is_parsed(self, request):
        response = Mock()
        response.ok = True
        response.status_code = 200
        response.json.return_value = {"id": "123_456"}
        request.return_value = response

        # Only validate response handling here; credentials are never hard-coded.
        FacebookService._request("GET", "https://example.invalid/test")
        request.assert_called_once()


if __name__ == "__main__":
    unittest.main()
