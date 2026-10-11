import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from app.facebook_service import FacebookService

class FacebookMultiPhotoPostTests(unittest.TestCase):
    def test_seven_slides_are_attached_to_one_feed_post(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths=[]
            for i in range(7):
                p=Path(tmp)/f"slide_{i+1}.jpg"
                p.write_bytes(b"fake-image")
                paths.append(p)

            calls=[]
            def fake_request(method, url, **kwargs):
                calls.append((method, url, kwargs))
                if url.endswith('/photos'):
                    return {"id": f"photo_{len([c for c in calls if c[1].endswith('/photos')])}"}
                return {"id":"page_post_123"}

            with patch.object(FacebookService, "_request", side_effect=fake_request):
                with patch("app.facebook_service.Config.FACEBOOK_GRAPH_API_VERSION", "v23.0"):
                    with patch("app.facebook_service.Config.FACEBOOK_PAGE_ID", "page_1"):
                        with patch("app.facebook_service.Config.FACEBOOK_PAGE_TOKEN", "token"):
                            result=FacebookService.post_carousel(paths, "Sample caption")

            photo_calls=[c for c in calls if c[1].endswith('/photos')]
            feed_calls=[c for c in calls if c[1].endswith('/feed')]
            self.assertEqual(len(photo_calls), 7)
            self.assertEqual(len(feed_calls), 1)
            self.assertEqual(result["slide_count"], 7)
            self.assertEqual(result["post_id"], "page_post_123")
            params=feed_calls[0][2]["data"]
            self.assertEqual(params["message"], "Sample caption")
            self.assertEqual(len([k for k in params if k.startswith("attached_media[")]), 7)
            self.assertTrue(all(c[2]["data"]["published"] == "false" for c in photo_calls))

if __name__ == '__main__':
    unittest.main()
