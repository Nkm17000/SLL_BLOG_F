# Smart Learning Lab — Technical Blog Publisher (Final)

This version is designed for automated technical-blog image creation and Facebook Page publishing.

## What was fixed

### 1. Detailed live GitHub Actions logs
Every workflow step now prints clear progress messages:

```text
WORKFLOW STARTED
Checkout
Python setup
Dependency installation
Facebook secret validation
Project validation
Static JSON validation
Rotation state
Image generation
Facebook preflight
Facebook image upload
Generated files
Artifact upload
State commit
WORKFLOW FINISHED
```

The Python application also writes a timestamped log file to:

```text
output/logs/run_YYYYMMDDTHHMMSSZ.log
```

The workflow uploads these logs as a GitHub Actions artifact even when a later step fails.

Artifact name:

```text
smart-learning-lab-debug-<run-number>
```

### 2. Blog image redesigned around the supplied Smart Learning Lab UX

The renderer no longer produces a page made only from empty text boxes.

It now uses the supplied artwork for:

- Hero student + laptop image
- AI robot
- Target / productivity illustration
- AI chip
- AI devices
- Beginner project checklist
- Implementation checklist
- Real-world student illustration
- Calendar / notification illustration
- Try Today rocket
- Footer benefit icons

The layout follows the supplied UX direction:

- Branded hero
- Large title
- Highlighted title line
- Hero illustration
- Intro callout
- 8 numbered content cards
- One illustration per card
- Try This Today section
- CTA button
- Footer benefit row

Output:

```text
1080 × 1350 JPEG
```

### 3. Font problem fixed

The old version used a Devanagari-only font for English text. That caused the square-box characters visible in the generated image.

The new renderer uses:

- DejaVu Sans for Latin/English text
- Noto Sans Devanagari for Devanagari text
- Automatic mixed-text handling

So English text renders normally and Hindi/Devanagari can also be rendered.

### 4. Facebook preflight

Before uploading the image, the application verifies the configured Page ID and token against the Graph API.

The log reports:

```text
Facebook preflight: validating Page access...
Facebook Page access OK. Page ID=... Name=...
Facebook preflight passed. Starting image upload...
```

If Facebook rejects the request, the HTTP status, error code, error type and error message are logged without printing the access token.

### 5. Automatic UX rotation

The sequence remains:

```text
Run 1  → UX 1
Run 2  → UX 2
Run 3  → UX 3
Run 4  → UX 4
Run 5  → UX 5
Run 6  → UX 1
...
```

The state is stored in:

```text
data/blog_history.json
```

### 6. 10 scheduled runs per day

The workflow uses Asia/Kolkata timezone and runs at:

```text
06:30 IST
08:30 IST
10:30 IST
12:30 IST
14:30 IST
16:30 IST
18:30 IST
20:30 IST
22:30 IST
00:30 IST
```

### 7. Push trigger for immediate testing

The workflow also runs when code is pushed to `main`.

This means after uploading the project you do not have to wait for the next scheduled execution to test it.

## Required GitHub Secrets

Repository → Settings → Secrets and variables → Actions:

```text
FACEBOOK_PAGE_ID
FACEBOOK_PAGE_TOKEN
```

The workflow never prints the actual token.

## Manual test

Go to:

```text
GitHub → Actions → Smart Learning Lab - Technical Blog Publisher → Run workflow
```

Leave the topic index blank for normal rotation.

## Where to diagnose a failure

Open:

```text
GitHub → Actions → workflow run → Generate + Publish Technical Blog
```

The failed step will show its detailed log.

Also download:

```text
smart-learning-lab-debug-<run-number>
```

This contains generated images, JSON metadata and the application log.

## Local dry run

No Facebook credentials are required for a dry run:

```bash
python -m app.run_agent --dry-run
```

## Local production run

Set:

```text
FACEBOOK_PAGE_ID=...
FACEBOOK_PAGE_TOKEN=...
FACEBOOK_GRAPH_API_VERSION=v23.0
```

Then:

```bash
python -m app.run_agent
```

## Testing

The project includes a smoke test for:

- Static blog JSON
- All 5 UX renderers
- 1080×1350 output dimensions
- JPEG/RGB output
- Facebook response handling

Run:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

## No Groq

This project does not use Groq or any AI text-generation API. Blog content comes from:

```text
data/static_blogs.json
```
