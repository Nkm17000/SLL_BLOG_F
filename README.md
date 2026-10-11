# Smart Learning Lab 247 — Daily Technical Blog Carousel

A deliberately simplified GitHub Actions project that finds one recent technology topic from a Google News RSS search each day, creates a concise seven-slide educational carousel, and publishes it as one multi-photo Facebook post. It no longer runs the 20-agent schedule, large topic libraries, dashboards, template rotations, or hourly posts.

## Daily behavior
- Runs daily at 09:00 India time (03:30 UTC), or manually via Actions.
- Fetches a current topic from a technology-focused RSS search and preserves the source link.
- Produces 7 square JPG slides: headline/context, five technical insight slides, and a takeaway.
- Uploads each slide as an unpublished Facebook photo, then publishes all photos together in one feed post.
- Saves a compact topic/post history and workflow artifacts.
- Manual workflow runs default to dry-run; turn it off to publish.

## Required GitHub repository secrets
- `FACEBOOK_PAGE_ID` — Facebook Page ID, not a personal profile ID.
- `FACEBOOK_PAGE_TOKEN` — access token with the permissions needed to publish Page content.

## Run locally
```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
cp .env.example .env  # then fill in credentials
python -m app.run_agent --dry-run
python -m app.run_agent  # publishes if valid Facebook credentials are configured
```

## Files
- `app/run_agent.py`: one daily workflow from topic fetch to post
- `app/content_agents.py`: current technical topic RSS fetcher
- `app/carousel_builder.py`: slide rendering
- `app/facebook_service.py`: multi-photo Facebook publishing
- `app/config.py`: central app name, URLs, and publishing settings
- `data/blog_history.json`: compact publication history

The RSS headline and summary are used as source context; the carousel gives practical framing and recommends checking the original source and official documentation. Review the generated carousel artifact before turning off dry-run for the first time.
