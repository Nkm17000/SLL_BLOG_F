from __future__ import annotations
import json, tempfile, unittest
from pathlib import Path
from app.blog_generator import load_blogs
from app.state import load_history
from app.run_agent import COMBOS, choose_combo, choose_topic
from app.theme_engine import THEMES

ROOT=Path(__file__).resolve().parents[1]

class ProjectSmokeTests(unittest.TestCase):
    def test_json_has_ten_blogs_and_five_points_each(self):
        blogs=load_blogs()
        self.assertEqual(len(blogs),10)
        for blog in blogs:
            self.assertEqual(len(blog["points"]),5)

    def test_there_are_50_unique_combinations(self):
        self.assertEqual(len(COMBOS),50)
        self.assertEqual(len(set(COMBOS)),50)
        self.assertEqual(len(THEMES),5)

    def test_topic_rotation_avoids_used_topics_until_cycle_end(self):
        blogs=load_blogs(); state={"topic_cycle":0,"topic_used":[]}
        picked=[]
        for _ in range(len(blogs)):
            b=choose_topic(blogs,state); picked.append(b["id"]); state["topic_used"].append(b["id"])
        self.assertEqual(len(set(picked)),10)
        self.assertEqual(state["topic_cycle"],0)
        b=choose_topic(blogs,state)
        self.assertEqual(state["topic_cycle"],1)
        self.assertIn(b["id"],{x["id"] for x in blogs})

    def test_combination_rotation_avoids_repeats_until_all_50(self):
        state={"combo_cycle":0,"combo_used":[]}
        picked=[]
        for _ in range(50):
            _,_,combo=choose_combo(state); picked.append(combo); state["combo_used"].append(combo)
        self.assertEqual(len(set(picked)),50)
        self.assertEqual(state["combo_cycle"],0)
        choose_combo(state)
        self.assertEqual(state["combo_cycle"],1)

    def test_history_file_is_valid(self):
        data=load_history()
        self.assertEqual(data["version"],5)
        self.assertIsInstance(data["history"],list)

if __name__=="__main__": unittest.main()
