from __future__ import annotations
import json
import re
from groq import Groq
from app.config import Config

SCHEMA = {
    "type":"object",
    "properties":{
        "title":{"type":"string"},
        "subtitle":{"type":"string"},
        "hook":{"type":"string"},
        "sections":{"type":"array","items":{
            "type":"object",
            "properties":{
                "heading":{"type":"string"},
                "body":{"type":"string"},
                "bullets":{"type":"array","items":{"type":"string"}}
            },
            "required":["heading","body","bullets"],
            "additionalProperties":False
        }},
        "try_today":{"type":"string"},
        "caption":{"type":"string"}
    },
    "required":["title","subtitle","hook","sections","try_today","caption"],
    "additionalProperties":False
}

def _clean_json(text: str) -> dict:
    text=text.strip()
    text=re.sub(r"^```(?:json)?\s*","",text,flags=re.I)
    text=re.sub(r"\s*```$","",text)
    return json.loads(text)

def generate_blog(topic: dict) -> dict:
    client=Groq(api_key=Config.GROQ_API_KEY)
    prompt=f"""
Create a highly readable technical/social-media blog for Smart Learning Lab.

TOPIC:
{topic["title"]}

CATEGORY:
{topic["category"]}

GOAL:
{topic["description"]}

AUDIENCE:
Beginners, students and working professionals. A 10th-class student should be able to understand the main idea.

BRAND:
Smart Learning Lab
LEARN • PRACTICE • GROW
By Nitin Mittal Innovation

CONTENT RULES:
- Write original content.
- Use simple English.
- Make it practical and useful in everyday life.
- Avoid hype and unsupported claims.
- Explain technical words in plain language.
- Use short paragraphs.
- Include 4 to 6 sections.
- Include useful bullet points or steps.
- Do not tell readers to blindly trust AI; encourage checking important information.
- Do not include political persuasion, medical diagnosis, financial advice, or unsafe instructions.
- The final image must be readable, so keep each section concise.
- Caption should be suitable for Facebook and invite useful discussion without clickbait.
- Return valid JSON only.

Return exactly the requested schema.
"""
    response=client.chat.completions.create(
        model=Config.GROQ_MODEL,
        messages=[
            {"role":"system","content":"You are a beginner-friendly technical educator and social-media content writer."},
            {"role":"user","content":prompt}
        ],
        response_format={"type":"json_schema","json_schema":{"name":"technical_blog","strict":True,"schema":SCHEMA}},
        temperature=0.7,
        max_completion_tokens=5000,
    )
    return _clean_json(response.choices[0].message.content)
