# Smart Learning Lab — Technical Blog Facebook Publisher

This project is a blog-only replacement for the previous quiz agent.

## What it does

1. Reads the next pending topic from `data/topics.json`.
2. Uses Groq `openai/gpt-oss-120b` to create a beginner-friendly technical blog.
3. Creates one 1080x1350 social-media image using Pillow.
4. Publishes that image + caption to the configured Facebook Page.
5. Only after a successful Facebook response, records the topic as `completed`.
6. GitHub Actions commits `data/blog_history.json` so the next run continues from the next topic.

Groq's current documentation lists `openai/gpt-oss-120b` and supports structured JSON output, which this project uses for predictable blog generation.

## Topics

The initial 10 topics cover:
- AI for everyone
- AI for students
- AI for professionals
- Technology
- AI prompts
- Python
- AI and resumes
- AI research
- Cybersecurity basics
- Learning with AI

Edit `data/topics.json` to add more topics.

## GitHub Secrets

Add these repository secrets:

- `GROQ_API_KEY`
- `FACEBOOK_PAGE_ID`
- `FACEBOOK_PAGE_TOKEN`

Do NOT put the actual Groq or Facebook tokens in the repository.

## Facebook permissions

The Page access token must have the permissions required by your Meta app/Page setup to publish Page content. If Meta rejects the request, the workflow will stop and the topic will remain uncompleted.

## Manual run

GitHub Actions → Smart Learning Lab - Technical Blog Publisher → Run workflow.

Leave `topic_id` blank to publish the next pending topic.

Or choose a specific ID such as:

`ai-study-assistant`

## Local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# fill in GROQ_API_KEY, FACEBOOK_PAGE_ID and FACEBOOK_PAGE_TOKEN

python -m app.run_agent
```

Generate without posting:

```bash
python -m app.run_agent --dry-run
```

Publish a specific topic:

```bash
python -m app.run_agent --topic ai-study-assistant
```

## History

`data/blog_history.json` records:
- topic ID
- topic title
- category
- status
- timestamp
- Facebook post ID when available
- generated image path
- generated title

A topic is marked `completed` only after the Facebook API call succeeds.

## Output

Each run creates:

`output/<topic-id>.jpg`

and:

`output/<topic-id>.json`

The image is 1080x1350, designed for social media.

## Important design choice

The project does NOT include:
- quiz/question-bank logic
- Instagram publishing
- old quiz images
- quiz scheduling
- quiz-specific state

It is intentionally a separate technical-blog publisher.
