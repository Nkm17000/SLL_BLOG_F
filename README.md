# Smart Learning Lab — Multi-Agent Technical Content Publisher

A single GitHub Actions project that runs multiple specialized content agents and publishes one image post per scheduled slot to a Facebook Page.

## Agents

1. **Student Learning Agent** — beginner-friendly explanations
2. **AI Agent** — AI and AI engineering
3. **Coding Agent** — programming and developer topics
4. **How-To Agent** — implementation-oriented tutorials
5. **Tech News Agent** — current technology items from RSS feeds
6. **Cybersecurity Agent** — defensive security awareness and engineering
7. **Project Ideas Agent** — project concepts and architecture
8. **Tech Career Agent** — technical skills and career learning
9. **Technical Blog Agent** — full 2,000-topic technical library

## Daily IST schedule

| IST | Agent |
|---|---|
| 06:00 | Student Learning |
| 08:00 | AI |
| 10:00 | Coding |
| 12:00 | How-To |
| 14:00 | Tech News |
| 16:00 | Cybersecurity |
| 18:00 | Project Ideas |
| 20:00 | Tech Career |
| 22:00 | Technical Blog |

GitHub Actions uses UTC cron values equivalent to these India times.

## Design

- 10 visual templates
- 30 light themes
- Theme rotation avoids repeats until the complete theme cycle is used
- Template rotation avoids repeats until all 10 templates are used
- Hero images are integrated into the design
- No WordArt
- No music/audio
- No video generation
- Image-only Facebook publishing
- Horizontal 12:10 output: **1200×1000**
- Vertical 10:12 output: **1000×1200**
- Exactly 5 content points per topic
- 2,000 source topics

## News behavior

The Tech News Agent reads a technology RSS feed at runtime. The generated news post includes source context. If the RSS service is temporarily unavailable, the workflow falls back to a technical topic instead of publishing fabricated news.

## Manual runs

GitHub Actions → workflow → Run workflow → choose an agent or `auto`.

`auto` uses the current India time to select the scheduled agent. Manual agent selection is useful for testing.

## Secrets

Add these repository secrets:

- `FACEBOOK_PAGE_ID`
- `FACEBOOK_PAGE_TOKEN`

## Local test

```bash
pip install -r requirements.txt
python -m playwright install chromium
python -m unittest discover -s tests -v
python -m app.run_agent --agent ai --dry-run
```

## Important

The project publishes images only. It does not use audio, MP4 generation, WordArt, or copyrighted music.

### Image clarity update

Rendered images keep the same 12:10 / 10:12 layout ratios but are now exported at 2x device pixel density for sharper Facebook/social-media rendering:
- Horizontal: 2400 x 2000
- Vertical: 2000 x 2400

Typography was also increased for the title, description and five content cards so text remains readable after platform resizing/compression.
