import json
import unittest
from pathlib import Path
from app.run_agent import choose_template, choose_topic
from app.html_renderer import build_html
from app.theme_engine import THEMES, choose_theme

ROOT = Path(__file__).resolve().parents[1]

class ProjectSmokeTests(unittest.TestCase):
    def test_json_has_2000_blogs_and_five_points_each(self):
        data=json.loads((ROOT/"data/blogs.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["blogs"]),2000)
        for blog in data["blogs"]:
            self.assertEqual(len(blog["points"]),5)
            for point in blog["points"]:
                self.assertEqual(len(point["items"]),2)

    def test_history_schema_has_no_theme_state(self):
        data=json.loads((ROOT/"data/blog_history.json").read_text(encoding="utf-8"))
        self.assertIn("topic_cycle",data)
        self.assertIn("template_cycle",data)
        self.assertIn("template_used",data)
        self.assertIn("theme_cycle",data)
        self.assertIn("theme_used",data)
        self.assertNotIn("combo_used",data)

    def test_template_rotation_avoids_repeats_until_all_ten(self):
        used=set()
        for _ in range(10):
            template=choose_template({"template_used":list(used)})
            self.assertNotIn(template,used)
            used.add(template)
        self.assertEqual(used,set(range(1,11)))
        template=choose_template({"template_used":list(used)})
        self.assertIn(template,range(1,11))

    def test_topic_rotation_avoids_used_topics_until_cycle_end(self):
        data=json.loads((ROOT/"data/blogs.json").read_text(encoding="utf-8"))
        ids=[b["id"] for b in data["blogs"]]
        used=set()
        for _ in ids:
            topic=choose_topic([{"id":x} for x in ids],{"topic_used":list(used)})["id"]
            self.assertNotIn(topic,used)
            used.add(topic)
        self.assertEqual(used,set(ids))

    def test_all_templates_have_real_hero_pngs(self):
        for i in range(1,11):
            p=ROOT/f"assets/images/template-{i:02d}-hero.png"
            self.assertTrue(p.exists(),p)
            self.assertGreater(p.stat().st_size,100_000)

    def test_template_has_dynamic_placeholders(self):
        data=json.loads((ROOT/"data/blogs.json").read_text(encoding="utf-8"))
        blog=data["blogs"][0]
        html=build_html(blog,1)
        self.assertNotIn("{{title}}",html)
        self.assertNotIn("{{points[0].title}}",html)
        self.assertIn(blog["title"],html)

    def test_theme_rotation_has_no_repeat_before_cycle_end(self):
        state={"theme_used":[]}
        used=set()
        for _ in range(len(THEMES)):
            t=choose_theme(state,1)
            self.assertNotIn(t.id,used)
            used.add(t.id); state["theme_used"].append(t.id)
        self.assertEqual(len(used),len(THEMES))

if __name__=="__main__":
    unittest.main()
