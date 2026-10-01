from dataclasses import dataclass
from typing import List
import random

@dataclass(frozen=True)
class Theme:
    id: str
    name: str
    background: str
    surface: str
    text: str
    muted: str
    accent: str
    accent2: str
    border: str
    hero_overlay: str

# All themes are intentionally light. The accent palette changes substantially
# between themes so successive posts can have clearly different visual identities.
THEMES = [
    Theme("sky-breeze", "Sky Breeze", "#F2FAFF", "#FFFFFF", "#17384D", "#466274", "#0EA5E9", "#14B8A6", "#D7ECF5", "rgba(242,250,255,.94)"),
    Theme("mint-fresh", "Mint Fresh", "#EFFBF6", "#FFFFFF", "#17473B", "#486A61", "#10B981", "#06B6D4", "#D7F0E5", "rgba(239,251,246,.95)"),
    Theme("peach-glow", "Peach Glow", "#FFF7F0", "#FFFFFF", "#4A2D20", "#6F5749", "#F97316", "#F59E0B", "#F3E0D1", "rgba(255,247,240,.95)"),
    Theme("lavender-pop", "Lavender Pop", "#F7F5FF", "#FFFFFF", "#30265A", "#625A7D", "#8B5CF6", "#6366F1", "#E7E1FF", "rgba(247,245,255,.95)"),
    Theme("rose-petal", "Rose Petal", "#FFF6FA", "#FFFFFF", "#4B2341", "#705566", "#EC4899", "#F43F5E", "#F5DDE8", "rgba(255,246,250,.95)"),
    Theme("lemon-sun", "Lemon Sun", "#FFFBEA", "#FFFFFF", "#463A12", "#6B5D2D", "#EAB308", "#F59E0B", "#F0E5AE", "rgba(255,251,234,.95)"),
    Theme("aqua-glass", "Aqua Glass", "#EFFCFF", "#FFFFFF", "#123F49", "#456872", "#06B6D4", "#22C55E", "#D4F1F5", "rgba(239,252,255,.95)"),
    Theme("coral-wave", "Coral Wave", "#FFF6F2", "#FFFFFF", "#4B2923", "#6D514A", "#F43F5E", "#FB7185", "#F3DCD5", "rgba(255,246,242,.95)"),
    Theme("indigo-sky", "Indigo Sky", "#F3F7FF", "#FFFFFF", "#202D52", "#52627D", "#4F46E5", "#3B82F6", "#DCE4FA", "rgba(243,247,255,.95)"),
    Theme("teal-garden", "Teal Garden", "#F1FCF9", "#FFFFFF", "#173F3B", "#4C6964", "#0F766E", "#14B8A6", "#D7EEE9", "rgba(241,252,249,.95)"),
    Theme("blueberry", "Blueberry", "#F5F8FF", "#FFFFFF", "#24365C", "#52637F", "#2563EB", "#7C3AED", "#DDE6FA", "rgba(245,248,255,.95)"),
    Theme("apricot", "Apricot", "#FFF8EF", "#FFFFFF", "#49301D", "#6D5843", "#EA580C", "#F59E0B", "#F3E3CE", "rgba(255,248,239,.95)"),
    # Additional requested color families
    Theme("ruby-red", "Ruby Red", "#FFF5F5", "#FFFFFF", "#4A1717", "#714242", "#DC2626", "#F43F5E", "#F5D5D5", "rgba(255,245,245,.95)"),
    Theme("forest-green", "Forest Green", "#F3FBF4", "#FFFFFF", "#173B20", "#4D6752", "#16A34A", "#15803D", "#D6EED9", "rgba(243,251,244,.95)"),
    Theme("royal-blue", "Royal Blue", "#F3F7FF", "#FFFFFF", "#172B52", "#52627A", "#1D4ED8", "#2563EB", "#D9E4FA", "rgba(243,247,255,.95)"),
    Theme("sunny-yellow", "Sunny Yellow", "#FFFDEB", "#FFFFFF", "#4A3A08", "#6C5D25", "#CA8A04", "#EAB308", "#F0E4A8", "rgba(255,253,235,.95)"),
    Theme("hot-pink", "Hot Pink", "#FFF4FB", "#FFFFFF", "#4A173B", "#70465F", "#DB2777", "#EC4899", "#F3D3E5", "rgba(255,244,251,.95)"),
    Theme("soft-gray", "Soft Gray", "#F7F8FA", "#FFFFFF", "#252A31", "#59616B", "#4B5563", "#64748B", "#E1E5EA", "rgba(247,248,250,.96)"),
    Theme("orange-flame", "Orange Flame", "#FFF7ED", "#FFFFFF", "#4A2410", "#6C4A35", "#EA580C", "#F97316", "#F3DDC7", "rgba(255,247,237,.95)"),
    Theme("purple-bloom", "Purple Bloom", "#FAF7FF", "#FFFFFF", "#32184D", "#685577", "#9333EA", "#A855F7", "#E8DDF5", "rgba(250,247,255,.95)"),
    Theme("cyan-wave", "Cyan Wave", "#F0FCFF", "#FFFFFF", "#123A45", "#4B6870", "#0891B2", "#06B6D4", "#D3EEF3", "rgba(240,252,255,.95)"),
    Theme("emerald-leaf", "Emerald Leaf", "#F1FCF7", "#FFFFFF", "#143C2B", "#4C675A", "#059669", "#10B981", "#D4EDE1", "rgba(241,252,247,.95)"),
    Theme("lime-light", "Lime Light", "#F8FDEB", "#FFFFFF", "#34420F", "#5E6A3C", "#65A30D", "#84CC16", "#E2ECC2", "rgba(248,253,235,.95)"),
    Theme("magenta-pop", "Magenta Pop", "#FFF4FC", "#FFFFFF", "#48133D", "#704D68", "#C026D3", "#DB2777", "#F0D6EA", "rgba(255,244,252,.95)"),
    Theme("turquoise-mint", "Turquoise Mint", "#EFFDFA", "#FFFFFF", "#123E3B", "#4A6864", "#0D9488", "#14B8A6", "#D2EEEA", "rgba(239,253,250,.95)"),
    Theme("violet-night", "Violet Light", "#F7F4FF", "#FFFFFF", "#302052", "#62577A", "#7C3AED", "#8B5CF6", "#E3DDF5", "rgba(247,244,255,.95)"),
    Theme("amber-glow", "Amber Glow", "#FFFAEF", "#FFFFFF", "#49330F", "#6C5B36", "#D97706", "#F59E0B", "#F1E2BE", "rgba(255,250,239,.95)"),
    Theme("slate-blue", "Slate Blue", "#F5F8FC", "#FFFFFF", "#26364A", "#59697B", "#475569", "#3B82F6", "#DDE4EC", "rgba(245,248,252,.96)"),
    Theme("coral-red", "Coral Red", "#FFF5F3", "#FFFFFF", "#4A1F1B", "#714F4A", "#E11D48", "#F97316", "#F2D8D3", "rgba(255,245,243,.95)"),
    Theme("seafoam", "Seafoam", "#F0FCF8", "#FFFFFF", "#173D36", "#4E6962", "#0F9F83", "#22C55E", "#D5EEE6", "rgba(240,252,248,.95)"),
]

# Hero-aware compatibility is used as a preference only. If a preferred palette
# is already used, choose another unused theme so every theme participates.
HERO_THEME_MAP = {
    1: ["sky-breeze", "aqua-glass", "royal-blue", "cyan-wave", "mint-fresh", "indigo-sky"],
    2: ["peach-glow", "apricot", "orange-flame", "amber-glow", "coral-wave", "sunny-yellow"],
    3: ["mint-fresh", "forest-green", "emerald-leaf", "teal-garden", "turquoise-mint", "lime-light"],
    4: ["lavender-pop", "purple-bloom", "violet-night", "indigo-sky", "blueberry", "royal-blue"],
    5: ["rose-petal", "hot-pink", "magenta-pop", "ruby-red", "coral-wave", "purple-bloom"],
    6: ["lemon-sun", "sunny-yellow", "amber-glow", "apricot", "orange-flame", "lime-light"],
    7: ["aqua-glass", "cyan-wave", "turquoise-mint", "sky-breeze", "teal-garden", "royal-blue"],
    8: ["lavender-pop", "purple-bloom", "violet-night", "blueberry", "rose-petal", "hot-pink"],
    9: ["aqua-glass", "royal-blue", "cyan-wave", "indigo-sky", "peach-glow", "lemon-sun"],
    10: ["sky-breeze", "mint-fresh", "soft-gray", "slate-blue", "lavender-pop", "blueberry"],
}
BY_ID = {t.id: t for t in THEMES}

def choose_theme(state, template_id):
    used = set(state.get("theme_used", []))
    compatible = HERO_THEME_MAP.get(template_id, [t.id for t in THEMES])
    available = [tid for tid in compatible if tid not in used]
    if not available:
        available = [t.id for t in THEMES if t.id not in used]
    if not available:
        state["theme_cycle"] = int(state.get("theme_cycle", 0)) + 1
        state["theme_used"] = []
        used = set()
        available = [t.id for t in THEMES]
    tid = random.choice(available)
    return BY_ID[tid]
