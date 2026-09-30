import json
import unittest
from pathlib import Path

from app.run_agent import choose_combo, choose_topic
from app.theme_engine import THEMES

ROOT = Path(__file__).resolve().parents[1]

class ProjectSmokeTests(unittest.TestCase):
    def test_json_has_ten_blogs_and_five_points_each(self):
        data = json.loads((ROOT / "data/blogs.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["blogs"]), 10)
        for blog in data["blogs"]:
            self.assertEqual(len(blog["points"]), 5)
            for point in blog["points"]:
                self.assertEqual(len(point["items"]), 2)

    def test_history_file_is_valid(self):
        data = json.loads((ROOT / "data/blog_history.json").read_text(encoding="utf-8"))
        self.assertIn("topic_cycle", data)
        self.assertIn("combo_cycle", data)
        self.assertIn("history", data)

    def test_there_are_50_unique_combinations(self):
        combos = {(t, th) for t in range(1, 11) for th in range(1, 6)}
        self.assertEqual(len(combos), 50)

    def test_combination_rotation_avoids_repeats_until_all_50(self):
        used = set()
        for _ in range(50):
            t, th, combo = choose_combo({"combo_used": list(used)})
            self.assertNotIn(combo, used)
            used.add(combo)
        self.assertEqual(len(used), 50)
        t, th, combo = choose_combo({"combo_used": list(used)})
        self.assertIn((t, th), {(a, b) for a in range(1, 11) for b in range(1, 6)})

    def test_topic_rotation_avoids_used_topics_until_cycle_end(self):
        data = json.loads((ROOT / "data/blogs.json").read_text(encoding="utf-8"))
        ids = [b["id"] for b in data["blogs"]]
        used = set()
        for _ in range(len(ids)):
            topic = choose_topic([{"id": x} for x in ids], {"topic_used": list(used)})["id"]
            self.assertNotIn(topic, used)
            used.add(topic)
        self.assertEqual(used, set(ids))

    def test_all_themes_are_light(self):
        for theme in THEMES:
            self.assertFalse(theme["bg"].lower() in {"#111827", "#000000", "#0b1220", "#0f172a"})
            self.assertEqual(theme["card"].lower(), "#ffffff")
            self.assertNotEqual(theme["ink"].lower(), "#ffffff")

    def test_all_templates_have_real_hero_pngs(self):
        for i in range(1, 11):
            p = ROOT / f"assets/images/template-{i:02d}-hero.png"
            self.assertTrue(p.exists(), p)
            self.assertGreater(p.stat().st_size, 100_000)

if __name__ == "__main__":
    unittest.main()
