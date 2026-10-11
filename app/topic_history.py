"""Topic-level deduplication across previous generated and published articles."""
import re
from difflib import SequenceMatcher
from urllib.parse import urlsplit, urlunsplit

STOP = set("the a an and or of for in on to by with via from at new latest announces announced unveils unveiled launches launched introduces introduced expands update updates release released now how what why technical technology news report reports".split())

def normalize_topic(value: str) -> str:
    value = re.sub(r"[^a-z0-9 ]", " ", (value or "").casefold())
    words = [w for w in value.split() if w not in STOP]
    return " ".join(words)

def canonical_url(value: str) -> str:
    p = urlsplit(value or "")
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip("/"), "", ""))

def is_repeated_topic(topic: str, state: dict, title: str = "", source_url: str = "") -> bool:
    current = [normalize_topic(x) for x in (topic, title) if x]
    if source_url and any(canonical_url(x.get("source_url", "")) == canonical_url(source_url) for x in state.get("history", []) if x.get("source_url")):
        return True
    for row in state.get("history", []):
        # Include previous generated attempts, to avoid repeating a topic after a failed post.
        previous = [normalize_topic(str(row.get(k, ""))) for k in ("technical_topic", "topic", "article_title", "original_title")]
        for a in current:
            for b in previous:
                if not a or not b: continue
                if a == b or (len(a) > 12 and len(b) > 12 and (a in b or b in a)): return True
                wa, wb = set(a.split()), set(b.split())
                if len(wa) >= 3 and len(wb) >= 3 and len(wa & wb) / min(len(wa), len(wb)) >= .78: return True
                if len(a) >= 25 and len(b) >= 25 and SequenceMatcher(None, a, b).ratio() >= .88: return True
    return False
