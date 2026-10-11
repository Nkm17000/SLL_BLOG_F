from __future__ import annotations

import copy
import html
import random
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

import requests

ROOT = Path(__file__).resolve().parent.parent

@dataclass(frozen=True)
class AgentProfile:
    id: str
    name: str
    description: str
    categories: tuple[str, ...] = ()
    hashtags: tuple[str, ...] = ()

AGENTS: dict[str, AgentProfile] = {
    'student': AgentProfile('student','Student Learning Agent','Beginner-friendly technical learning.',hashtags=('#SmartLearningLab','#LearnTechnology','#Students')),
    'tech_facts': AgentProfile('tech_facts','Tech Facts Agent','Interesting technical facts and mechanisms.',hashtags=('#SmartLearningLab','#TechFacts','#Technology')),
    'ai': AgentProfile('ai','AI Agent','AI and AI-engineering explainers.',hashtags=('#SmartLearningLab','#AI','#ArtificialIntelligence')),
    'ai_tools': AgentProfile('ai_tools','AI Tools Agent','Practical AI tool guides and evaluations.',hashtags=('#SmartLearningLab','#AITools','#AI')),
    'coding': AgentProfile('coding','Coding Agent','Programming and software development explainers.',hashtags=('#SmartLearningLab','#Coding','#Programming')),
    'debugging': AgentProfile('debugging','Debugging Agent','Errors, diagnostics, root causes and fixes.',hashtags=('#SmartLearningLab','#Debugging','#Developers')),
    'howto': AgentProfile('howto','How-To Agent','Step-by-step technical implementation guides.',hashtags=('#SmartLearningLab','#HowTo','#TechTutorial')),
    'concepts': AgentProfile('concepts','Concept Explainer Agent','One technical concept explained clearly.',hashtags=('#SmartLearningLab','#TechExplained','#Learning')),
    'cloud': AgentProfile('cloud','Cloud Agent','Cloud architecture, deployment and operations.',hashtags=('#SmartLearningLab','#Cloud','#DevOps')),
    'database': AgentProfile('database','Database Agent','Database design, queries and reliability.',hashtags=('#SmartLearningLab','#Database','#SQL')),
    'app_development': AgentProfile('app_development','App Development Agent','Web, mobile, frontend, backend and APIs.',hashtags=('#SmartLearningLab','#AppDevelopment','#SoftwareEngineering')),
    'cybersecurity': AgentProfile('cybersecurity','Cybersecurity Agent','Defensive security and privacy education.',hashtags=('#SmartLearningLab','#CyberSecurity','#Security')),
    'experiments': AgentProfile('experiments','Tech Experiment Agent','Small reproducible technical experiments.',hashtags=('#SmartLearningLab','#TechExperiment','#LearnByDoing')),
    'projects': AgentProfile('projects','Project Ideas Agent','Practical project architecture ideas.',hashtags=('#SmartLearningLab','#ProjectIdeas','#SoftwareEngineering')),
    'productivity': AgentProfile('productivity','Developer Productivity Agent','Developer tools, workflows and automation.',hashtags=('#SmartLearningLab','#DeveloperProductivity','#GitHub')),
    'career': AgentProfile('career','Tech Career Agent','Technical skills and career learning paths.',hashtags=('#SmartLearningLab','#TechCareer','#Developer')),
    'news': AgentProfile('news','Tech News Agent','Current technology updates from RSS sources.',hashtags=('#SmartLearningLab','#TechNews','#Technology')),
    'infographic': AgentProfile('infographic','Tech Infographic Agent','Visual-first technical explainers.',hashtags=('#SmartLearningLab','#Infographic','#Technology')),
    'repurposing': AgentProfile('repurposing','Content Repurposing Agent','Turns one topic into multiple useful formats.',hashtags=('#SmartLearningLab','#ContentRepurposing','#Technology')),
    'technical_blog': AgentProfile('technical_blog','Technical Blog Agent','Full technical topic library.',hashtags=('#SmartLearningLab','#Technology','#TechBlog')),
}

# 20 posts/day, one agent each hour from 04:00 through 23:00 IST.
SCHEDULE = [
    (4,'student'),(5,'tech_facts'),(6,'ai'),(7,'ai_tools'),(8,'coding'),(9,'debugging'),
    (10,'howto'),(11,'concepts'),(12,'cloud'),(13,'database'),(14,'app_development'),
    (15,'cybersecurity'),(16,'experiments'),(17,'projects'),(18,'productivity'),(19,'career'),
    (20,'news'),(21,'infographic'),(22,'repurposing'),(23,'technical_blog'),
]

NEWS_FEEDS=['https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en']
NEWS_QUERIES=[
    'technology news AI infrastructure software engineering developer tools',
    'cloud computing cybersecurity open source software release',
    'semiconductor hardware server architecture technology announcement',
    'developer platform database programming language release',
    'robotics networking data center security technology research',
]

_BANK_CACHE: dict[str,list[dict]] = {}

def agent_for_hour(hour_ist:int)->AgentProfile:
    exact={h:AGENTS[a] for h,a in SCHEDULE}
    if hour_ist in exact: return exact[hour_ist]
    return AGENTS[min(SCHEDULE,key=lambda x:abs(x[0]-hour_ist))[1]]

def get_agent(agent_id:str)->AgentProfile:
    if agent_id not in AGENTS:
        raise ValueError(f"Unknown agent '{agent_id}'. Available: {', '.join(AGENTS)}")
    return AGENTS[agent_id]

def load_agent_topics(agent_id:str)->list[dict]:
    if agent_id in _BANK_CACHE: return _BANK_CACHE[agent_id]
    path=ROOT/'data'/'agents'/f'{agent_id}_topics.json'
    if not path.exists(): raise FileNotFoundError(f'Missing topic bank: {path}')
    import json
    data=json.loads(path.read_text(encoding='utf-8'))
    blogs=data.get('blogs',[])
    if len(blogs)!=2000: raise ValueError(f'{path} must contain exactly 2000 topics; found {len(blogs)}')
    _BANK_CACHE[agent_id]=blogs
    return blogs

def choose_topic_for_agent(blogs:list[dict], state:dict, profile:AgentProfile)->dict:
    # The blogs argument is retained for compatibility; each agent now owns its own 2,000-topic bank.
    bank=load_agent_topics(profile.id)
    used=set(state.setdefault('agent_topic_used',{}).get(profile.id,[]))
    ids={b['id'] for b in bank}
    if used >= ids:
        state['agent_topic_used'][profile.id]=[]; used=set()
    candidates=[b for b in bank if b['id'] not in used]
    # Avoid near-duplicate titles/content across agents when history is available.
    try:
        from app.quality_engine import similar_to_history
        history=state.get("history", [])
        fresh=[b for b in candidates if not similar_to_history(b, history)]
        if fresh:
            candidates=fresh
    except Exception:
        pass
    return random.choice(candidates)

def mark_agent_topic_used(state:dict,profile:AgentProfile,topic_id:str)->None:
    state.setdefault('agent_topic_used',{}).setdefault(profile.id,[]).append(topic_id)

def _clean_text(value:str)->str:
    value=re.sub(r'<[^>]+>',' ',value or '')
    value=html.unescape(value)
    return re.sub(r'\s+',' ',value).strip()

def fetch_news_topic(history: dict | None = None) -> tuple[dict, str]:
    """Find a recent unused topic, resolve the publisher URL, and summarize real article text."""
    from app.article_content import fetch_article, summarize_article
    from app.topic_history import is_repeated_topic, normalize_topic
    from datetime import datetime, timedelta, timezone
    from email.utils import parsedate_to_datetime
    from urllib.parse import urlparse
    history = history or {"history": []}
    candidates = []
    diagnostics = {"feeds_ok": 0, "items_seen": 0, "stale_or_bad_date": 0,
                  "history_duplicates": 0, "article_too_short": 0,
                  "unresolved_google_url": 0, "groq_rejected": 0}
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)

    for query in NEWS_QUERIES:
        url = NEWS_FEEDS[0].format(query=quote(query))
        try:
            response = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0 SmartLearningLab247/1.0"})
            response.raise_for_status()
            items = ET.fromstring(response.content).findall('.//item')
            diagnostics["feeds_ok"] += 1
        except (requests.RequestException, ET.ParseError):
            continue
        for item in items[:60]:
            diagnostics["items_seen"] += 1
            title = _clean_text(item.findtext('title', ''))
            rss = _clean_text(item.findtext('description', ''))
            link = _clean_text(item.findtext('link', ''))
            published = _clean_text(item.findtext('pubDate', ''))
            if not title or not link:
                continue
            try:
                published_dt = parsedate_to_datetime(published)
                if published_dt.tzinfo is None: published_dt = published_dt.replace(tzinfo=timezone.utc)
                if published_dt < cutoff:
                    diagnostics["stale_or_bad_date"] += 1
                    continue
            except (ValueError, TypeError, OverflowError):
                diagnostics["stale_or_bad_date"] += 1
                continue
            if is_repeated_topic(title, history):
                diagnostics["history_duplicates"] += 1
                continue
            candidates.append((published_dt, title, rss, link, published))

    candidates.sort(key=lambda x: x[0], reverse=True)
    seen = set()
    # Try substantially more distinct results; several publishers block extraction, so one
    # inaccessible site must not prevent the job from finding another recent topic.
    for _, title, rss, link, published in candidates[:60]:
        fingerprint = normalize_topic(title)
        if not fingerprint or fingerprint in seen:
            continue
        seen.add(fingerprint)
        article, final_url = fetch_article(link)
        if len(article.strip()) < 800:
            diagnostics["article_too_short"] += 1
            continue
        source_url = final_url or link
        host = (urlparse(source_url).hostname or '').lower()
        if host == 'news.google.com' or host.endswith('.google.com'):
            diagnostics["unresolved_google_url"] += 1
            continue
        # Run Groq only on article text, never an RSS headline alone. If one article/model
        # response is unsuitable, continue to the next candidate and report diagnostics.
        try:
            generated = summarize_article(title, article, rss, source_url)
        except RuntimeError as exc:
            # API/auth/rate-limit failures will affect every candidate; fail immediately
            # instead of making repeated billable requests for the same underlying error.
            if "Groq summarization failed" in str(exc):
                raise
            diagnostics["groq_rejected"] += 1
            logger = __import__('logging').getLogger(__name__)
            logger.warning("Skipping article '%s': %s", title[:120], str(exc)[:240])
            continue
        technical_topic = generated["technical_topic"]
        if is_repeated_topic(technical_topic, history, title=title, source_url=source_url):
            diagnostics["history_duplicates"] += 1
            continue
        blog = {
            "id": "news-" + normalize_topic(technical_topic).replace(" ", "-")[:80],
            "category": "Technology News", "title": technical_topic,
            "technical_topic": technical_topic, "original_title": title,
            "description": generated["description"], "points": generated["points"],
            "source_url": source_url, "source_link": link,
            "published": published, "article_text_length": len(article),
            "content_mode": "full_article_groq", "summary_model": generated.get("model"),
        }
        return blog, source_url
    raise RuntimeError(
        "No usable fresh technical article was found after checking "
        f"{diagnostics['items_seen']} RSS items. Diagnostics: {diagnostics}. "
        "No post was published and history was not changed. Check RSS access, publisher article access, "
        "GROQ_API_KEY/model availability, and whether the recent candidates are already in blog_history.json."
    )

def transform_for_agent(blog:dict,profile:AgentProfile)->dict:
    result=copy.deepcopy(blog)
    prefix={
      'student':'Learn Simply','howto':'How-To','projects':'Project Idea','career':'Career Skills','cybersecurity':'Security Guide',
      'coding':'Developer Guide','ai':'AI Explained','ai_tools':'AI Tool Guide','cloud':'Cloud Guide','database':'Database Guide',
      'app_development':'App Development','debugging':'Debugging Guide','concepts':'Concept Explained','tech_facts':'Tech Fact',
      'experiments':'Tech Experiment','productivity':'Productivity Tip','infographic':'Visual Explainer','repurposing':'Content Repurpose'
    }.get(profile.id)
    if prefix: result['title']=f'{prefix}: {blog["title"]}'
    result['description']=f'{profile.name} perspective: {profile.description} Topic focus: {blog["title"]}.'
    return result
