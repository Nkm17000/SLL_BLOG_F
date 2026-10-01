import json
import unittest
from pathlib import Path
from app.run_agent import choose_template, choose_topic
from app.html_renderer import build_html
from app.theme_engine import THEMES, choose_theme
from app.content_agents import AGENTS, SCHEDULE, agent_for_hour
from app.quality_engine import prepare_blog, validate_blog

ROOT = Path(__file__).resolve().parents[1]

class ProjectSmokeTests(unittest.TestCase):
    def test_existing_blog_library_has_2000_blogs_and_five_points(self):
        data=json.loads((ROOT/"data/blogs.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["blogs"]),2000)
        for blog in data["blogs"]:
            self.assertEqual(len(blog["points"]),5)
            for point in blog["points"]: self.assertEqual(len(point["items"]),2)

    def test_history_schema(self):
        data=json.loads((ROOT/"data/blog_history.json").read_text(encoding="utf-8"))
        self.assertIn("topic_cycle",data); self.assertIn("template_cycle",data); self.assertIn("theme_cycle",data)
        self.assertIn("agent_topic_used",data); self.assertIn("history",data)
        self.assertNotIn("combo_used",data)

    def test_template_rotation_avoids_repeats_until_all_ten(self):
        used=set()
        for _ in range(10):
            template=choose_template({"template_used":list(used)})
            self.assertNotIn(template,used); used.add(template)
        self.assertEqual(used,set(range(1,11)))

    def test_topic_rotation_avoids_used_topics_until_cycle_end(self):
        data=json.loads((ROOT/"data/blogs.json").read_text(encoding="utf-8")); ids=[b["id"] for b in data["blogs"]]
        used=set()
        for _ in ids:
            topic=choose_topic([{"id":x} for x in ids],{"topic_used":list(used)})["id"]
            self.assertNotIn(topic,used); used.add(topic)
        self.assertEqual(used,set(ids))

    def test_all_templates_have_real_hero_pngs(self):
        for i in range(1,11):
            p=ROOT/f"assets/images/template-{i:02d}-hero.png"
            self.assertTrue(p.exists(),p); self.assertGreater(p.stat().st_size,100_000)

    def test_template_has_dynamic_placeholders(self):
        data=json.loads((ROOT/"data/blogs.json").read_text(encoding="utf-8")); blog=data["blogs"][0]
        html=build_html(blog,1); self.assertNotIn("{{title}}",html); self.assertNotIn("{{points[0].title}}",html)
        self.assertIn(blog.get("hook",blog["title"]),html)

    def test_multi_agent_schedule_has_twenty_slots(self):
        self.assertEqual(len(AGENTS),20); self.assertEqual(len(SCHEDULE),20)
        self.assertEqual([h for h,_ in SCHEDULE],list(range(4,24)))
        for hour,agent_id in SCHEDULE: self.assertEqual(agent_for_hour(hour).id,agent_id)

    def test_square_render_config_is_high_resolution(self):
        data=json.loads((ROOT/"data/render_config.json").read_text(encoding="utf-8"))
        self.assertEqual(data["output_ratio"],"10:10"); self.assertEqual(data["width"],2000); self.assertEqual(data["height"],2000)
        self.assertEqual(data["export_width"],4000); self.assertEqual(data["export_height"],4000)

    def test_every_agent_has_2000_topics_and_engagement_fields(self):
        banks=sorted((ROOT/"data/agents").glob("*_topics.json")); self.assertEqual(len(banks),20)
        required={'hook','original_title','difficulty','series','language','format','content_type','real_world_example','cta','content_fingerprint','quality_schema'}
        for path in banks:
            data=json.loads(path.read_text(encoding="utf-8")); self.assertEqual(data["count"],2000,path); self.assertEqual(len(data["blogs"]),2000,path)
            for blog in data["blogs"][:10]: self.assertTrue(required.issubset(blog),blog["id"]); self.assertEqual(len(blog["points"]),5)

    def test_theme_rotation_has_no_repeat_before_cycle_end_and_has_30_themes(self):
        self.assertGreaterEqual(len(THEMES),30); state={"theme_used":[]}; used=set()
        for _ in range(len(THEMES)):
            t=choose_theme(state,1); self.assertNotIn(t.id,used); used.add(t.id); state["theme_used"].append(t.id)
        self.assertEqual(len(used),len(THEMES))

    def test_quality_gate_and_hook(self):
        data=json.loads((ROOT/"data/blogs.json").read_text(encoding="utf-8")); blog=prepare_blog(data["blogs"][0],"ai",[])
        ok,errors=validate_blog(blog); self.assertTrue(ok,errors); self.assertTrue(18<=len(blog["hook"])<=72); self.assertTrue(blog["cta"]); self.assertTrue(blog["real_world_example"])

    def test_workflow_has_push_and_schedule(self):
        text=(ROOT/".github/workflows/blog-post.yml").read_text(encoding="utf-8")
        self.assertIn("push:",text); self.assertIn("workflow_dispatch:",text); self.assertIn("schedule:",text); self.assertIn("paths-ignore:",text)

if __name__=="__main__": unittest.main()
