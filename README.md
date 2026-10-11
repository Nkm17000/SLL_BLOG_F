# Smart Learning Lab 247 — Source-Based Technical Article Publisher

This workflow finds a current technology story, follows the Google News RSS link to the publisher, extracts the available full article text, and creates **one descriptive text-only Facebook Page post**. It does not convert text into images and does not upload carousel images.

## What changed
- Retrieves the publisher article instead of relying only on the RSS headline/snippet.
- Extracts article text from JSON-LD, article/main containers, and paragraph fallbacks.
- With `GROQ_API_KEY`, generates five distinct, descriptive sections grounded in the fetched article and preserves technical details, named products, numbers, context and limitations.
- Without the optional key, uses source sentences as an extractive fallback and explicitly warns when the full article was not accessible; it does not invent missing details.
- Publishes one text-only Facebook post with context, five sections, source link, and Smart Learning Lab 247 branding.
- Refuses to publish if the resulting post is too short or lacks five descriptive sections.
- Saves the generated text at `output/latest_post.txt` and run details in `output/latest_summary.json`.

## GitHub secrets
Required: `FACEBOOK_PAGE_ID`, `FACEBOOK_PAGE_TOKEN`.
Recommended for better summaries: `GROQ_API_KEY` (Groq API key). `GROQ_MODEL` defaults to `llama-3.3-70b-versatile`. If the publisher blocks automated access, the system falls back to the RSS text and records `content_mode: rss_fallback`; review the output before enabling live publishing.

## Run locally
```bash
python -m pip install -r requirements.txt
cp .env.example .env  # set Facebook credentials and optional GROQ_API_KEY
python -m app.run_agent --dry-run  # fetch article and generate text, no publishing
python -m app.run_agent           # publishes one text post
```

The workflow runs at 09:00 India time daily, on push to `main`, or manually. The manual workflow input supports dry-run. Verify `output/latest_post.txt` before the first live publish.
