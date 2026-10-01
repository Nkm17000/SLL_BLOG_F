# Smart Learning Lab — Final Multi-Agent Content Engine

A single GitHub Actions project for a versatile technical-learning Facebook Page. It contains 20 specialized content agents, 40,000 agent topic records, the existing 2,000-topic blog library, 10 visual templates, 30 light themes, high-resolution 10:10 images, content-quality checks, duplicate protection, a publishing calendar, retry handling, dashboard output, and carousel companion assets.

## Content system

**20 agents × 2,000 topics = 40,000 agent-topic records**, plus the existing `data/blogs.json` 2,000-topic library. Every topic keeps exactly 5 points and 2 supporting items per point.

Agents: Student Learning, Tech Facts, AI, AI Tools, Coding, Debugging, How-To, Concept Explainer, Cloud, Database, App Development, Cybersecurity, Tech Experiments, Project Ideas, Developer Productivity, Tech Career, Tech News, Tech Infographic, Content Repurposing, Technical Blog.

## Daily India schedule

The workflow posts one image per hour from **04:00 through 23:00 Asia/Kolkata**. The UTC cron in `.github/workflows/blog-post.yml` handles the conversion.

## Engagement and quality improvements

Each topic JSON includes:
- `hook` — concise scroll-stopping headline
- `original_title` — source topic title
- `difficulty` — beginner/intermediate/advanced level
- `series` — recurring content-series identity
- `real_world_example` — practical context for the topic
- `cta` — rotating, useful call to action
- `language` — `en-IN` metadata
- `format` — `square_single_image`
- `content_type` — agent category
- `content_fingerprint` — duplicate detection key
- `quality_schema` — structural validation metadata

At runtime the quality engine also checks hook length, five points, two items per point, real-world context, CTA, and near-duplicate history.

## Visual system

- 10 distinct templates
- 30 light themes: red, green, blue, yellow, pink, gray, purple, orange, cyan, teal and more
- Hero artwork integrated into the composition
- Theme rotation without repeats until the theme cycle is complete
- Template rotation without repeats until all 10 are used
- **10:10 square output**
- **4000×4000 PNG export** using a 2000×2000 CSS canvas at 2× device scale
- Larger typography and high-contrast spacing for social-media readability
- No WordArt
- No music/audio
- No MP4 generation

The renderer uses the generated hook as the visual headline and keeps the original topic title in the supporting description.

## Content variety

The orchestrator keeps the page from feeling repetitive through agent-specific series, difficulty labels, hooks, CTAs, templates, themes and topic history. The design engine can also create **7 square carousel companion slides** as local workflow artifacts: hook, five points, and takeaway. Facebook publishing remains one image post per scheduled run by default, so the page is not flooded with multiple posts.

## News safety

The Tech News Agent fetches current technology items from RSS at runtime. It includes source context and falls back to an evergreen technical topic if the RSS service is unavailable; it does not fabricate a news item.

## Reliability

- Facebook API requests retry transient failures up to five times with backoff.
- A failed publish is recorded in `data/blog_history.json` and does not silently disappear.
- Topic usage is recorded per agent.
- Templates and themes rotate independently and avoid repeats within their cycles.
- Near-duplicate content is filtered against recent history when possible.
- `output/dashboard.html` summarizes publishing, failures, agents, themes and templates.

## GitHub Actions

Triggers:
- `push` to any branch except history-only updates
- `workflow_dispatch` with agent selection and dry-run option
- hourly schedule from 04:00–23:00 IST

Required repository secrets:
- `FACEBOOK_PAGE_ID`
- `FACEBOOK_PAGE_TOKEN`

## Local test

```bash
pip install -r requirements.txt
python -m playwright install chromium
python -m unittest discover -s tests -v
python -u -m app.run_agent --agent ai --dry-run
```

A dry run creates the PNG, carousel companion slides, dashboard and summary without publishing to Facebook.
