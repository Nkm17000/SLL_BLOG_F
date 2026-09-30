from __future__ import annotations

import json
import re
from groq import Groq
from app.config import Config

SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "subtitle": {"type": "string"},
        "intro": {"type": "string"},
        "sections": {
            "type": "array",
            "minItems": 8,
            "maxItems": 8,
            "items": {
                "type": "object",
                "properties": {
                    "number": {"type": "integer"},
                    "title": {"type": "string"},
                    "text": {"type": "string"},
                    "points": {
                        "type": "array",
                        "minItems": 3,
                        "maxItems": 3,
                        "items": {"type": "string"},
                    },
                },
                "required": ["number", "title", "text", "points"],
                "additionalProperties": False,
            },
        },
        "try_today": {"type": "string"},
        "caption": {"type": "string"},
    },
    "required": ["title", "subtitle", "intro", "sections", "try_today", "caption"],
    "additionalProperties": False,
}


def _clean_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def generate_blog(topic: dict) -> dict:
    client = Groq(api_key=Config.GROQ_API_KEY)

    prompt = f"""
Create a beginner-friendly technical/social-media blog for Smart Learning Lab.

TOPIC:
{topic['title']}

CATEGORY:
{topic['category']}

GOAL:
{topic['description']}

AUDIENCE:
10th-class students, beginners, students, and working professionals.

BRAND:
Smart Learning Lab
LEARN • PRACTICE • GROW
By Nitin Mittal Innovation

The final content will be rendered into ONE 1080x1350 social-media image.
Use the clean two-column pastel-card design style: a strong hero, short intro,
eight compact numbered cards arranged as four rows of two cards, a Try This Today
box, and a footer.

CONTENT LIMITS — STRICT:
- Exactly 8 sections.
- Title: maximum 55 characters.
- Subtitle: maximum 80 characters.
- Intro: maximum 250 characters.
- Section title: maximum 34 characters.
- Section text: maximum 220 characters.
- Exactly 3 bullet points per section.
- Each bullet: maximum 85 characters.
- Try This Today: maximum 200 characters.
- Caption: maximum 500 characters.
- Keep every sentence short.
- Use simple English.
- Avoid Markdown.
- Explain technical terms in plain language.
- Give practical, safe examples.
- Do not make unsupported claims.
- Encourage checking important information when relevant.
- Do not include political persuasion, medical diagnosis, financial advice, or unsafe instructions.
- Return ONLY valid JSON matching the schema.

Section progression:
1. What is it?
2. Why is it useful?
3. How does it work?
4. Simple technology stack
5. Beginner project idea
6. Step-by-step implementation
7. Real-world example
8. Next-level features

The caption should briefly summarize the blog and invite readers to learn or discuss,
without clickbait.
"""

    response = client.chat.completions.create(
        model=Config.GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are an expert technical educator who explains technology simply and concisely.",
            },
            {"role": "user", "content": prompt},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "smart_learning_lab_blog",
                "strict": True,
                "schema": SCHEMA,
            },
        },
        temperature=0.7,
        max_completion_tokens=5000,
    )

    blog = _clean_json(response.choices[0].message.content)

    # Defensive normalization for the renderer.
    blog["sections"] = blog["sections"][:8]
    for index, section in enumerate(blog["sections"], start=1):
        section["number"] = index
        section["points"] = section.get("points", [])[:3]

    return blog
