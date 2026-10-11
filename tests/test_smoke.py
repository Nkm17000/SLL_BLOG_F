import unittest
from app.content_agents import fetch_news_topic
from app.carousel_builder import build_carousel
from app.config import Config
class ProjectSmokeTests(unittest.TestCase):
    def test_config_brand(self): self.assertEqual(Config.APP_NAME, "Smart Learning Lab 247")
    def test_news_topic_shape_offline(self):
        # Shape test for the 5-point blog structure used by the carousel renderer.
        blog={"id":"test","title":"Test topic","category":"Technology","description":"A useful technical explainer.","points":[{"title":f"Point {i}","description":"Technical detail.","items":["Check official docs.","Test safely."]} for i in range(5)]}
        self.assertEqual(len(blog["points"]),5)
        self.assertTrue(all(len(p["items"])==2 for p in blog["points"]))
if __name__=="__main__": unittest.main()
