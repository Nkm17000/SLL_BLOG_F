from dataclasses import dataclass
from typing import Dict, List
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

# Light themes only. Palettes are deliberately compatible with bright hero artwork.
THEMES: List[Theme] = [
    Theme("sky-breeze","Sky Breeze","#F2FAFF","#FFFFFF","#17384D","#466274","#0EA5E9","#14B8A6","#D7ECF5","rgba(242,250,255,.94)"),
    Theme("mint-fresh","Mint Fresh","#EFFBF6","#FFFFFF","#17473B","#486A61","#10B981","#06B6D4","#D7F0E5","rgba(239,251,246,.95)"),
    Theme("peach-glow","Peach Glow","#FFF7F0","#FFFFFF","#4A2D20","#6F5749","#F97316","#F59E0B","#F3E0D1","rgba(255,247,240,.95)"),
    Theme("lavender-pop","Lavender Pop","#F7F5FF","#FFFFFF","#30265A","#625A7D","#8B5CF6","#6366F1","#E7E1FF","rgba(247,245,255,.95)"),
    Theme("rose-petal","Rose Petal","#FFF6FA","#FFFFFF","#4B2341","#705566","#EC4899","#F43F5E","#F5DDE8","rgba(255,246,250,.95)"),
    Theme("lemon-sun","Lemon Sun","#FFFBEA","#FFFFFF","#463A12","#6B5D2D","#EAB308","#F59E0B","#F0E5AE","rgba(255,251,234,.95)"),
    Theme("aqua-glass","Aqua Glass","#EFFCFF","#FFFFFF","#123F49","#456872","#06B6D4","#22C55E","#D4F1F5","rgba(239,252,255,.95)"),
    Theme("coral-wave","Coral Wave","#FFF6F2","#FFFFFF","#4B2923","#6D514A","#F43F5E","#FB7185","#F3DCD5","rgba(255,246,242,.95)"),
    Theme("indigo-sky","Indigo Sky","#F3F7FF","#FFFFFF","#202D52","#52627D","#4F46E5","#3B82F6","#DCE4FA","rgba(243,247,255,.95)"),
    Theme("teal-garden","Teal Garden","#F1FCF9","#FFFFFF","#173F3B","#4C6964","#0F766E","#14B8A6","#D7EEE9","rgba(241,252,249,.95)"),
    Theme("blueberry","Blueberry","#F5F8FF","#FFFFFF","#24365C","#52637F","#2563EB","#7C3AED","#DDE6FA","rgba(245,248,255,.95)"),
    Theme("apricot","Apricot","#FFF8EF","#FFFFFF","#49301D","#6D5843","#EA580C","#F59E0B","#F3E3CE","rgba(255,248,239,.95)"),
]

def choose_unused_theme(used_ids, rng=None):
    rng = rng or random.SystemRandom()
    available = [t for t in THEMES if t.id not in set(used_ids)]
    if not available:
        available = THEMES[:]
    return rng.choice(available)

def theme_dict(theme: Theme) -> Dict[str,str]:
    return theme.__dict__.copy()
