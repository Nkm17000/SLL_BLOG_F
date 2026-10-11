from __future__ import annotations
import json, os, re
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

HEADERS={"User-Agent":"Mozilla/5.0 (compatible; SmartLearningLab247/1.0)"}

def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()

def extract_article(html: str) -> str:
    soup=BeautifulSoup(html,"html.parser")
    found=[]
    for node in soup.find_all("script",attrs={"type":"application/ld+json"}):
        try: data=json.loads(node.string or node.get_text())
        except Exception: continue
        queue=data if isinstance(data,list) else [data]
        while queue:
            obj=queue.pop(0)
            if isinstance(obj,dict):
                queue.extend(obj.get("@graph",[]) if isinstance(obj.get("@graph"),list) else [])
                body=obj.get("articleBody")
                if isinstance(body,str) and len(body)>400: found.append(clean(body))
    if found: return max(found,key=len)
    for x in soup(["script","style","nav","header","footer","aside","form","noscript"]): x.decompose()
    candidates=[]
    for selector in ("article","main","[itemprop='articleBody']",".article-body",".article-content",".story-body",".entry-content"):
        for node in soup.select(selector):
            text=clean(" ".join(p.get_text(" ",strip=True) for p in node.find_all(["p","h2","h3","li"])))
            if len(text)>400: candidates.append(text)
    if candidates: return max(candidates,key=len)
    return clean(" ".join(p.get_text(" ",strip=True) for p in soup.find_all(["p","h2","h3"]) if len(p.get_text(" ",strip=True))>40))

def fetch_article(url: str) -> tuple[str,str]:
    try:
        r=requests.get(url,headers=HEADERS,timeout=25,allow_redirects=True); r.raise_for_status()
        return extract_article(r.text)[:30000],r.url
    except Exception:
        return "",url

def _fallback(title: str, article: str, rss: str) -> dict:
    source=article or rss
    sentences=[clean(s) for s in re.split(r"(?<=[.!?])\s+|\n+",source)]
    sentences=[s for s in sentences if len(s)>45 and not re.match(r"(?i)^(subscribe|sign in|advertisement|cookie policy)",s)]
    # Use source sentences, never fabricate technical claims or generic placeholder bullets.
    groups=[[] for _ in range(5)]
    for i,s in enumerate(sentences): groups[min(4,i*5//max(1,len(sentences)))].append(s)
    labels=["What the report says","Technical details reported","How the technology fits","Practical implications","What to verify"]
    points=[]
    for label,group in zip(labels,groups):
        text=" ".join(group)[:1050]
        if not text: text="The accessible source did not provide enough detail for this section. Open the original article to confirm the technical specifics before drawing conclusions."
        points.append({"title":label,"description":text,"items":[]})
    return {"description":("This summary uses extracted publisher article text where available. Details that the source does not specify are not inferred; check the original article for exact claims, specifications and limitations."),"points":points}

def summarize_article(title: str, article: str, rss: str, source_url: str) -> dict:
    key=os.getenv("GROQ_API_KEY","").strip()
    if key and article:
        prompt=("Read the entire source text and write a descriptive technical explainer for a general developer audience. Use only source-supported facts; preserve named products, companies, architecture, versions, numbers, dates, what changed, how it works, impact, limitations and caveats. Never invent missing details. Avoid repeating the headline as body text. Return JSON only: {\"description\": string, \"points\": [{\"title\": string, \"description\": string, \"items\": [string]}]} with exactly 5 points. Each point's description should explain context and meaning, not just name a topic. Sections: what happened; specific technical details; how it works; practical impact and limitations; what developers should verify next. Each section should be informative and distinct; items may contain at most 2 facts.\n"+f"HEADLINE: {title}\nRSS SUMMARY: {rss}\nSOURCE URL: {source_url}\nFULL ARTICLE:\n{article[:24000]}")
        try:
            r=requests.post("https://api.groq.com/openai/v1/chat/completions",headers={"Authorization":f"Bearer {key}"},json={"model":os.getenv("GROQ_MODEL","llama-3.3-70b-versatile"),"temperature":0.2,"response_format":{"type":"json_object"},"messages":[{"role":"system","content":"You are a meticulous technical journalist. Cite no unsupported facts."},{"role":"user","content":prompt}]},timeout=60)
            r.raise_for_status(); data=json.loads(r.json()["choices"][0]["message"]["content"])
            if isinstance(data.get("description"),str) and len(data.get("points",[]))==5 and all(p.get("title") and p.get("description") for p in data["points"]):
                for p in data["points"]: p["items"]=[str(x) for x in p.get("items",[])[:2]]
                return data
        except Exception: pass
    return _fallback(title,article,rss)

def build_text_post(title: str, content: dict, source_url: str, published: str="", app_name: str="Smart Learning Lab 247") -> str:
    lines=[f"{title}","",content.get("description","").strip(),""]
    for i,p in enumerate(content.get("points",[]),1):
        lines.extend([f"{i}. {p.get('title','Technical insight')}",p.get("description","").strip()])
        for item in p.get("items",[])[:2]: lines.append(f"• {item}")
        lines.append("")
    if published: lines.extend([f"Source publication date: {published}"])
    lines.extend([f"Read the original report: {source_url}","",f"Follow {app_name} for practical, source-based technical explainers.","#Technology #SoftwareEngineering #AI #CloudComputing #CyberSecurity #Developers"])
    return "\n".join(x for x in lines if x is not None).strip()
