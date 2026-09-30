# Smart Learning Lab — Technical Blog Facebook Publisher

A blog-only Facebook Page publisher. It uses Groq to create a compact beginner-friendly technical blog, selects one of 20 visual themes, renders a 1080×1350 social-media image, and publishes it to a Facebook Page.

## Automatic GitHub workflow

A push to `main` starts `.github/workflows/blog-post.yml` and publishes the next unfinished topic.

The workflow also supports **Run workflow** from GitHub Actions with an optional topic ID.

The bot commits only `data/blog_history.json` and generated `output/*.json`. Those paths are ignored by the push trigger so the history commit cannot start another publication.

## Required GitHub Secrets

Add these under **Settings → Secrets and variables → Actions**:

- `GROQ_API_KEY`
- `FACEBOOK_PAGE_ID`
- `FACEBOOK_PAGE_TOKEN`

Never commit a real API key or token.

## Topics and history

`data/topics.json` contains 10 starter topics covering:

- AI for Everyone
- AI for Students
- AI for Professionals
- Technology
- AI prompts
- Python
- AI and resumes
- AI research
- Cybersecurity
- Learning with AI

`data/blog_history.json` records the topic, status, timestamp, selected theme, generated title, image path, and Facebook post ID after a successful post.

## Visual design

The renderer is intentionally fixed to **1080×1350** and uses the requested reference style:

- Smart Learning Lab header
- Strong colored hero section
- Short introduction
- Exactly 8 numbered cards in a 2-column grid
- Four rows of pastel cards
- `TRY THIS TODAY` box
- Footer branding
- 20 complete visual themes

A new theme is selected randomly for every topic and the immediately previous completed theme is avoided when possible.

The renderer uses Pillow rather than Playwright, so GitHub Actions does not need Chrome or Linux browser libraries.

## Local dry run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.run_agent --dry-run
```

## Manual topic

```bash
python -m app.run_agent --topic ai-study-assistant --dry-run
```

Remove `--dry-run` to publish.

## Important

This project intentionally contains no quiz generation, quiz banks, or Instagram publishing logic.
