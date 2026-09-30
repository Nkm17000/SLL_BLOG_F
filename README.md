# Smart Learning Lab — Dynamic Technical Blog Publisher

This project accepts **only one input content file**: `data/blogs.json`.
The supplied 10-topic JSON is included as the test dataset.

## Generation rules

### 1. Random template + random theme
There are:
- 10 templates
- 5 themes per template
- **50 unique template/theme combinations**

Every run selects a random unused combination. A combination is not selected again until all 50 combinations have been used.

After all 50 are used, the combination cycle resets and random selection starts again from all 50 combinations.

### 2. Topic history
Each run generates exactly **one blog topic**.
The topic is selected randomly from topics not yet generated in the current topic cycle.

After every topic has been generated once, the topic cycle resets and the next cycle starts from all topics again.

The complete historical record is retained in `data/blog_history.json`.

### 3. One image per topic per workflow run
A workflow run generates exactly one HTML-based image and publishes that one image to Facebook.
There is no 5-image batch anymore.

### 4. Scheduled runs
GitHub Actions runs six times per day:

```text
00:00 UTC
04:00 UTC
08:00 UTC
12:00 UTC
16:00 UTC
20:00 UTC
```

These correspond to 05:30, 09:30, 13:30, 17:30, 21:30 and 01:30 IST.

### 5. Manual push
`workflow_dispatch` uses exactly the same code path as the scheduled workflow.
There is no separate manual selection algorithm.

## Input JSON

Put your blog data in:

```text
data/blogs.json
```

Each blog must contain:
- `id`
- `category`
- `title`
- `description`
- exactly 5 `points`
- each point has `title`, `description` and at least 2 `items`

No template, theme, HTML, CSS or image fields are required in the JSON.

## Rendering

The selected HTML template is filled with the JSON content and rendered with Playwright/Chromium at 800x1000 CSS pixels with a 2x device scale factor, producing a 1600x2000 PNG.

The matching template hero SVG is embedded directly into the HTML, so no external image URL is needed.

## Facebook secrets

Configure these GitHub repository secrets:

```text
FACEBOOK_PAGE_ID
FACEBOOK_PAGE_TOKEN
```

The Graph API version defaults to `v23.0`.

## Local testing

Install dependencies:

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

Run tests:

```bash
python -m unittest discover -s tests -v
```

Generate one local image without Facebook:

```bash
python -m app.run_agent --dry-run
```

The dry run still advances the local rotation/history because it represents a real generation test. Reset `data/blog_history.json` if you want to start the test cycle from zero.

## GitHub Actions troubleshooting

The workflow file MUST exist at the repository root:

```text
.github/workflows/blog-post.yml
```

Do not keep it under an extra `newproj/` folder. This ZIP is packaged with `.github/` at the root.

The workflow supports:
- Manual run from **Actions → Smart Learning Lab - Dynamic Technical Blog → Run workflow**
- Git push to `main` or `master`
- Six scheduled runs per day

GitHub scheduled workflows run only from the repository's default branch and may be delayed during high GitHub load. Make sure Actions are enabled for the repository.

Required repository secrets:
- `FACEBOOK_PAGE_ID`
- `FACEBOOK_PAGE_TOKEN`

For a first test, use **Run workflow** manually. The run should appear immediately under the Actions tab and should execute the same code path as the scheduler.
