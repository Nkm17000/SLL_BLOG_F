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
NEWS_QUERIES=['artificial intelligence technology','software technology cloud cybersecurity','developer technology open source']

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
    return random.choice(candidates)

def mark_agent_topic_used(state:dict,profile:AgentProfile,topic_id:str)->None:
    state.setdefault('agent_topic_used',{}).setdefault(profile.id,[]).append(topic_id)

def _clean_text(value:str)->str:
    value=re.sub(r'<[^>]+>',' ',value or '')
    value=html.unescape(value)
    return re.sub(r'\s+',' ',value).strip()

def fetch_news_topic()->tuple[dict,str]:
    query=random.choice(NEWS_QUERIES); url=NEWS_FEEDS[0].format(query=quote(query))
    response=requests.get(url,timeout=20,headers={'User-Agent':'SmartLearningLab/1.0'}); response.raise_for_status()
    root=ET.fromstring(response.content); items=root.findall('.//item')
    if not items: raise RuntimeError('News RSS returned no items')
    item=random.choice(items[:10]); title=_clean_text(item.findtext('title','Technology update'))
    summary=_clean_text(item.findtext('description','')); link=_clean_text(item.findtext('link','')); published=_clean_text(item.findtext('pubDate',''))
    if not title: raise RuntimeError('News item has no title')
    if len(summary)>450: summary=summary[:447].rstrip()+'...'
    blog={'id':'news-'+re.sub(r'[^a-z0-9]+','-',title.lower()).strip('-')[:80],'category':'Technology News','title':title,
          'description':'A current technology update explained with practical context.',
          'points':[
            {'title':'What happened','description':summary or 'A new technology development was reported.','items':['Read the source before acting on the information.','Separate confirmed facts from interpretation.']},
            {'title':'Why it matters','description':'The update may affect developers, businesses, users or the wider technology ecosystem.','items':['Identify who is affected.','Look for measurable changes rather than headlines alone.']},
            {'title':'Technology context','description':'Understanding the underlying technology makes the announcement easier to evaluate.','items':['Check the technology or product involved.','Compare it with the existing approach.']},
            {'title':'Practical takeaway','description':'Focus on what changed and whether it has a real-world impact.','items':['Track official documentation or announcements.','Avoid repeating unverified claims.']},
            {'title':'Source and next watch','description':f'Published: {published or "date not supplied"}. Source: {link or "RSS item source not supplied"}.','items':['Watch for follow-up announcements.','Re-check important facts as the story develops.']},
          ]}
    return blog,link

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
