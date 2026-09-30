from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from app.blog_generator import load_static_blogs
from app.design_registry import DESIGNS
from app.facebook_service import FacebookService
from app.image_generator import BlogImage

ROOT = Path(__file__).resolve().parents[1]


class ProjectSmokeTests(unittest.TestCase):
    def test_exactly_20_topics_have_required_content(self):
        blogs = load_static_blogs()
        self.assertEqual(len(blogs), 20)
        for blog in blogs:
            self.assertTrue(blog["id"])
            self.assertTrue(blog["title"])
            self.assertGreaterEqual(len(blog.get("sections", [])), 8)
            self.assertTrue(blog.get("try_today"))

    def test_exactly_15_designs_are_registered(self):
        self.assertEqual(len(DESIGNS), 15)
        self.assertEqual(len({d["id"] for d in DESIGNS}), 15)
        self.assertEqual(sum(d["type"] == "legacy" for d in DESIGNS), 5)
        self.assertEqual(sum(d["type"] == "static" for d in DESIGNS), 10)

    def test_all_15_designs_render(self):
        blogs = load_static_blogs()
        with tempfile.TemporaryDirectory() as tmp:
            for design_index in range(15):
                out = Path(tmp) / f"design{design_index + 1}.jpg"
                BlogImage.render(blogs[design_index % len(blogs)], out, ux_index=design_index)
                self.assertTrue(out.exists())
                from PIL import Image
                with Image.open(out) as image:
                    self.assertEqual(image.mode, "RGB")
                    if design_index < 5:
                        self.assertEqual(image.size, (1080, 1350))
                    else:
                        self.assertEqual(image.size, (1080, 1800))

    def test_twenty_generation_sequence_uses_designs_1_to_15_then_1_to_5(self):
        expected = list(range(15)) + list(range(5))
        actual = [i % len(DESIGNS) for i in range(20)]
        self.assertEqual(actual, expected)

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
        FacebookService._request("GET", "https://example.invalid/test")
        request.assert_called_once()


if __name__ == "__main__":
    unittest.main()
