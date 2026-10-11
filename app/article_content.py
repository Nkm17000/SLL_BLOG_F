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

def _publisher_url(page_html: str, current_url: str) -> str:
    """Resolve publisher canonical URL from a news redirect page when exposed."""
    soup=BeautifulSoup(page_html,"html.parser")
    for selector, attr in (("link[rel='canonical']","href"),("meta[property='og:url']","content")):
        node=soup.select_one(selector)
        candidate=(node.get(attr,"").strip() if node else "")
        if candidate and urlparse(candidate).scheme in ("http","https"):
            return candidate
    for node in soup.find_all("script",attrs={"type":"application/ld+json"}):
        try: data=json.loads(node.string or node.get_text())
        except Exception: continue
        queue=data if isinstance(data,list) else [data]
        while queue:
            obj=queue.pop(0)
            if not isinstance(obj,dict): continue
            graph=obj.get("@graph")
            if isinstance(graph,list): queue.extend(graph)
            candidate=obj.get("url") or obj.get("mainEntityOfPage")
            if isinstance(candidate,dict): candidate=candidate.get("@id") or candidate.get("url")
            if isinstance(candidate,str) and urlparse(candidate).scheme in ("http","https"):
                host=(urlparse(candidate).hostname or "").lower()
                if host and not (host == "news.google.com" or host.endswith(".google.com")):
                    return candidate
    return current_url

def fetch_article(url: str) -> tuple[str,str]:
    try:
        r=requests.get(url,headers=HEADERS,timeout=12,allow_redirects=True); r.raise_for_status()
        text=extract_article(r.text)
        resolved=_publisher_url(r.text,r.url)
        # If Google News served only a redirect/landing page, try the canonical publisher URL.
        if resolved != r.url and (len(text) < 800 or (urlparse(r.url).hostname or "").endswith("google.com")):
            try:
                publisher=requests.get(resolved,headers=HEADERS,timeout=12,allow_redirects=True)
                publisher.raise_for_status()
                publisher_text=extract_article(publisher.text)
                if len(publisher_text)>len(text):
                    return publisher_text[:30000],publisher.url
            except Exception:
                pass
        return text[:30000],resolved or r.url
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
    """Create a source-grounded, detailed explainer with Groq; never silently mask model errors."""
    key = os.getenv("GROQ_API_KEY", "").strip()
    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b").strip()
    if not key:
        raise RuntimeError("GROQ_API_KEY is required for the full-article technical explainer")
    article = clean(article)
    if len(article) < 800:
        raise RuntimeError(f"Publisher article text is too short ({len(article)} characters); refusing to summarize an RSS headline/snippet as a full article.")

    prompt = f"""You are writing a substantive technical explainer for Smart Learning Lab 247. Read the complete article text below before writing.

GOAL: Write for a curious beginner on a Facebook Page. Clearly define the underlying technology, how it works step by step, a concrete example/use case, tradeoffs, and what is actually new. Create a clear, descriptive, technically useful explanation. Do not merely restate the headline, list topic names, or use generic filler. Explain what the source actually reports and why details matter.

CONTENT RULES:
- Use only facts supported by the supplied article. Never invent specifications, benchmarks, release dates, capabilities, compatibility, quotes, or vendor claims.
- Preserve product/model names, companies, versions, numbers, dates, standards, protocols, architecture, and qualifications accurately.
- Explain cause and effect: what changed, how the technology works (only as described or safely inferable), where it fits, and practical implications.
- Separate reported facts from analysis. Mark implications as implications, not publisher claims.
- Mention limitations and unknowns. If the source omits a detail, say it is not specified rather than guessing.
- Avoid repetition; every section must include concrete details from the article. Explain specialized terms briefly.

RETURN JSON ONLY, no markdown fences, with this schema:
{{"technical_topic":"specific underlying technology in 3-10 words (not the headline)","description":"2-4 sentence overview grounded in the article","points":[{{"title":"specific section title","description":"substantive paragraph of about 65-95 words","items":["optional concrete fact"]}}]}}
Return exactly 5 distinct points in this order:
1. What was announced/reported (who, what, when, if provided)
2. Technical details/components (specific names, specifications, roles)
3. How the solution fits into the wider architecture (source-supported only)
4. Practical impact, use cases, trade-offs and limitations (separate facts from implications)
5. What developers/operators should verify next (specific checks; do not invent features)
Each paragraph must be descriptive, not a list of topic labels. Include 0-2 useful short items per section.

HEADLINE: {title}
RSS CONTEXT (secondary; prefer full article): {rss}
SOURCE URL: {source_url}
FULL ARTICLE TEXT ({len(article)} characters):
{article[:26000]}"""
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "temperature": 0.15,
                "max_tokens": 4200,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": "You are a meticulous technical journalist. Never fabricate facts. Follow the JSON schema exactly."},
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=90,
        )
        response.raise_for_status()
        data = json.loads(response.json()["choices"][0]["message"]["content"])
    except Exception as exc:
        raise RuntimeError(f"Groq summarization failed; refusing to publish generic or unverified content: {exc}") from exc

    if not isinstance(data, dict) or not isinstance(data.get("technical_topic"), str) or len(data["technical_topic"].strip()) < 8 or not isinstance(data.get("description"), str) or len(data["description"].strip()) < 100:
        raise RuntimeError("Groq returned an overview that is too short; refusing to publish")
    points = data.get("points")
    if not isinstance(points, list) or len(points) != 5:
        raise RuntimeError("Groq response must contain exactly five substantive sections")
    seen = set()
    for index, point in enumerate(points, 1):
        if not isinstance(point, dict) or not isinstance(point.get("title"), str) or not isinstance(point.get("description"), str):
            raise RuntimeError(f"Groq section {index} is missing a title or paragraph")
        point["title"] = clean(point["title"])
        point["description"] = clean(point["description"])
        if len(point["description"]) < 280:
            raise RuntimeError(f"Groq section {index} is too brief ({len(point['description'])} characters); refusing headline-only content")
        if not point["title"] or point["title"].lower() in seen:
            raise RuntimeError("Groq returned an empty or duplicate section title")
        seen.add(point["title"].lower())
        items = point.get("items", [])
        point["items"] = [clean(str(item)) for item in items[:2] if clean(str(item))] if isinstance(items, list) else []
    data["technical_topic"] = clean(data["technical_topic"])
    data["technical_topic"] = clean(data["technical_topic"])
    data["description"] = clean(data["description"])
    data["model"] = model
    data["summary_mode"] = "groq_full_article"
    return data

def _bold_unicode(text: str) -> str:
    """Convert ASCII letters/digits to Unicode bold for Facebook heading emphasis."""
    out=[]
    for ch in str(text):
        code=ord(ch)
        if 65 <= code <= 90: out.append(chr(0x1D400 + code-65))
        elif 97 <= code <= 122: out.append(chr(0x1D41A + code-97))
        elif 48 <= code <= 57: out.append(chr(0x1D7CE + code-48))
        else: out.append(ch)
    return ''.join(out)

def build_text_post(title: str, content: dict, source_url: str, published: str="", app_name: str="Smart Learning Lab 247") -> str:
    topic = content.get('technical_topic', title)
    lines=[f"🔎 {_bold_unicode(topic)}", "", _bold_unicode("What this means"), content.get("description", "").strip(), ""]
    for i,p in enumerate(content.get("points",[]),1):
        lines.extend([f"{i}. {_bold_unicode(p.get('title','Technical insight'))}",p.get('description', '').strip()])
        for item in p.get('items',[])[:2]: lines.append(f"• {item}")
        lines.append("")
    if published: lines.extend([f"🗓️ Source publication date: {published}", ""])
    lines.extend([
        f"🔗 {_bold_unicode('Original source')}: {source_url}", "",
        "📚 𝗦𝗺𝗮𝗿𝘁 𝗟𝗲𝗮𝗿𝗻𝗶𝗻𝗴 𝗟𝗮𝗯 𝟮𝟰𝟳 | Daily practice for serious aspirants",
        "🎯 SSC | UPSC | Banking | Railway | RAS | IAS",
        "🌐 Learn more: https://smartlearninglab-react.pages.dev/",
        "📸 Instagram: https://www.instagram.com/smartlearninglab247",
        "▶️ YouTube: https://www.youtube.com/@smartlearninglab247",
        "📘 Facebook: https://www.facebook.com/smartlearninglab247", "",
        "Follow Smart Learning Lab 247 for practical, source-based technical explainers.",
        "#Technology #SoftwareEngineering #AI #CloudComputing #CyberSecurity #Developers"
    ])
    return "\n".join(x for x in lines if x is not None).strip()
