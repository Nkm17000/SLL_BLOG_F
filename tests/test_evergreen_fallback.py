from unittest.mock import patch
import requests
from app.content_agents import fetch_news_topic


def fake_summary(title, article, rss, source_url):
    return {
        "technical_topic": "HTTP caching explained for developers",
        "description": "HTTP caching lets clients reuse valid responses instead of downloading the same resources repeatedly. Correct cache rules can improve speed and reduce server load.",
        "points": [
            {"title": f"Section {i}: practical details", "description": (f"This detailed explanation covers the technical behavior of the official documentation and how developers can apply it safely in real applications. " * 5).strip(), "items": []}
            for i in range(1, 6)
        ],
        "model": "test-model",
    }


def test_evergreen_fallback_when_all_news_feeds_fail():
    article = "Official documentation content about HTTP caching and response directives. " * 30
    with patch("app.content_agents.requests.get", side_effect=requests.RequestException("offline")), \
         patch("app.article_content.fetch_article", return_value=(article, "https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching")), \
         patch("app.article_content.summarize_article", side_effect=fake_summary):
        blog, source = fetch_news_topic({"history": []})
    assert blog["content_mode"] == "evergreen_official_docs_groq"
    assert blog["technical_topic"] == "HTTP caching explained for developers"
    assert source.startswith("https://developer.mozilla.org/")
    assert len(blog["points"]) == 5
