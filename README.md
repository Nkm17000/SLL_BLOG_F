# Smart Learning Lab — Technical Blog Facebook Publisher

This project automatically creates a beginner-friendly technical blog image with Groq and publishes it to a Facebook Page.

## Automatic behavior

A push to `main` starts the GitHub Actions workflow. The workflow:

1. Finds the first topic in `data/topics.json` that is not marked `completed`.
2. Uses Groq `openai/gpt-oss-120b` to generate the blog in structured JSON.
3. Randomly selects one of 20 visual themes. The selected theme is different from the previous completed theme when possible.
4. Creates one 1080x1350 JPEG.
5. Publishes the image and caption to the Facebook Page.
6. Only after Facebook succeeds, records the topic as `completed` and saves the selected `theme_id`.
7. Commits the history and generated blog JSON back to `main`.

The bot's own commit changes only `data/blog_history.json` and `output/**`, which are excluded from the `push` trigger. This prevents an infinite workflow/posting loop.

Groq documents `openai/gpt-oss-120b` as supporting JSON Schema / Structured Outputs. urlGroq GPT-OSS 120B documentationhttps://console.groq.com/docs/model/openai/gpt-oss-120b

## Required GitHub Secrets

Repository → Settings → Secrets and variables → Actions → New repository secret:

- `GROQ_API_KEY`
- `FACEBOOK_PAGE_ID`
- `FACEBOOK_PAGE_TOKEN`

Never put real tokens into the repository.

## Topics

Edit `data/topics.json` to add or change topics. The project includes 10 starter topics across:

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

## History

`data/blog_history.json` records every attempt, including:

- topic ID
- topic title
- category
- status
- timestamp
- theme ID
- Facebook post ID after success
- generated image path
- generated title

A topic is considered completed only after the Facebook API request succeeds.

## 20 visual themes

`app/image_generator.py` contains 20 complete palettes. Each generated topic receives a random theme, while avoiding the immediately previous completed theme when possible.

## Manual run

GitHub Actions → Smart Learning Lab - Technical Blog Publisher → Run workflow.

Leave `topic_id` blank to publish the next pending topic, or enter a specific ID such as:

`ai-study-assistant`

## Local test

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.run_agent --dry-run
```

## Important

The project intentionally contains no quiz/question-bank or Instagram publishing logic.
