# Smart Learning Lab 247 — daily fresh technical blog

The job discovers recent technology news (last 14 days), checks `data/blog_history.json` to avoid already-covered technical topics, fetches publisher article text, and uses Groq to write a substantive, accessible five-section Facebook post. The original source URL is included. No images are generated.

## GitHub secrets

`GROQ_API_KEY`, `FACEBOOK_PAGE_ID`, `FACEBOOK_PAGE_TOKEN`. Optional `GROQ_MODEL` locally; the workflow defaults to `openai/gpt-oss-120b`. Do not commit keys or passwords.

## Run locally

```bash
pip install -r requirements.txt
python -m app.run_agent --dry-run
pytest -q
```

Push to `main` or run daily at 09:00 IST to publish; workflow_dispatch dry_run=true previews without publishing. A successful post is saved with technical topic, source, model, timestamp and Facebook post ID. Failed publishing is also recorded to avoid accidental repeats. GitHub Actions commits history back to the repository even when the publish step fails.

**Note:** If no accessible, fresh and unused source is available, the job fails safely instead of publishing a duplicate or headline-only post. Groq generation requires a real API key; unit tests mock external services.

## History and duplicate protection
`data/blog_history.json` stores technical_topic, original article title, source URL, status and Facebook post ID. Previously published and attempted topics are excluded. Keep this file in the repository and commit it after each run. If a Facebook request times out, check the Page before manually retrying. Dry-run does not consume a topic.

The agent uses only a full extracted article and a direct publisher URL. When extraction fails, it skips the candidate rather than writing from a headline. Groq must be configured with `GROQ_API_KEY`.


## Troubleshooting: no fresh article found
The discovery step checks more recent RSS candidates across several technology queries, skips history duplicates, resolves publisher canonical URLs where exposed, and accepts article text from 800 characters upward before Groq quality checks. If it still cannot find a suitable article, the error reports counts for RSS items, old/malformed dates, history duplicates, short articles, unresolved Google URLs, and Groq validation rejections. It does not publish generic filler when no reliable article is available. If the message says `Groq summarization failed`, check the `GROQ_API_KEY`, model name, and Groq rate limits; the job stops immediately rather than retrying the same API failure for every candidate.
