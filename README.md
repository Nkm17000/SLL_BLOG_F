# Smart Learning Lab — Static UX Technical Blog Publisher

This version removes Groq completely.

## What it does

- Uses `data/static_blogs.json` as the content source.
- No AI text-generation API is required.
- Uses 5 supplied Smart Learning Lab UX systems.
- UX selection is deterministic:

`UX 1 → UX 2 → UX 3 → UX 4 → UX 5 → UX 1 → ...`

- Every generated image gets a unique generation number.
- If you run it 10 times in one day, the UX sequence is:

`1, 2, 3, 4, 5, 1, 2, 3, 4, 5`

- The next run continues from the saved state, even after GitHub Actions restarts.
- Static blog content is selected cyclically from `data/static_blogs.json`.
- The supplied UX sub-images are stored under `assets/ux_designs/` and used as artwork references/decorations.
- Output is a 1080×1350 JPEG suitable for Facebook/Instagram-style blog graphics.

## Project structure

```text
app/
  blog_generator.py
  config.py
  facebook_service.py
  image_generator.py
  run_agent.py
  state.py

data/
  static_blogs.json
  topics.json
  blog_history.json

assets/
  fonts/
  ux_designs/
    clean_modern_green/
    dark_ai_futuristic/
    warm_friendly_orange/
    nature_fresh_green/
    purple_creative_ai/

output/
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.run_agent --dry-run
```

The first run uses UX 1, the second UX 2, and so on.

To test a particular static content item:

```bash
python -m app.run_agent --topic-index 3 --dry-run
```

The UX sequence is still controlled by `data/blog_history.json`.

## Facebook publishing

Set:

```text
FACEBOOK_PAGE_ID=
FACEBOOK_PAGE_TOKEN=
FACEBOOK_GRAPH_API_VERSION=v23.0
```

Then remove `--dry-run`.

## GitHub Actions

The workflow supports:

- `push` to `main` for an immediate test run
- Manual `workflow_dispatch`
- 10 scheduled executions per day
- Schedule timezone: `Asia/Kolkata`
- Scheduled times: 06:30, 08:30, 10:30, 12:30, 14:30, 16:30, 18:30, 20:30, 22:30 and 00:30 IST
- Persistent UX rotation through `data/blog_history.json`
- GitHub Actions artifact containing the generated output

Required GitHub repository secrets:

```text
FACEBOOK_PAGE_ID
FACEBOOK_PAGE_TOKEN
```

Do not add a Groq secret. This project does not use Groq.

## Important rotation behavior

The UX index is reserved before image generation and stored immediately. Therefore a generated image always consumes the next UX slot.

Example:

```text
Generation 1  -> UX 1
Generation 2  -> UX 2
Generation 3  -> UX 3
Generation 4  -> UX 4
Generation 5  -> UX 5
Generation 6  -> UX 1
...
```

If a Facebook upload fails after image generation, the next run still moves forward. This prevents the same UX from being repeatedly selected after a failed publication.
