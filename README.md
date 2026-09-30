# Smart Learning Lab — 5 UX Technical Blog Batch Publisher

This version generates **5 complete technical-blog images in one workflow run**.

Each item uses a different static topic and a different full-page UX:

1. Clean Modern Green — topic 1
2. Dark AI Futuristic — topic 2
3. Warm Friendly Orange — topic 3
4. Nature Fresh Green — topic 4
5. Purple Creative AI — topic 5

The next run continues with the next five topics while the UX cycle repeats 1 → 2 → 3 → 4 → 5.

## Output

Every generated image is **1080 × 1350 JPEG**, suitable for Facebook/Instagram-style posts.

The project uses the supplied section illustrations rather than placing a screenshot of a UX design inside the final image. Each UX has its own header treatment, colors, card styling, spacing, CTA, footer and decorative treatment.

## Local test

Generate five images without Facebook:

```bash
python -m app.run_agent --count 5 --dry-run
```

Generate five preview designs:

```bash
python scripts/generate_five_previews.py
```

Run tests:

```bash
python -m unittest discover -s tests -v
```

## Facebook

Set:

```text
FACEBOOK_PAGE_ID
FACEBOOK_PAGE_TOKEN
FACEBOOK_GRAPH_API_VERSION
```

The publisher performs a Page-access preflight once and then publishes each of the five images separately. If one item fails, the remaining items continue, and the workflow ultimately fails so the run is visible as failed.

## GitHub Actions logging

The workflow prints the Python/Facebook logs live and also saves them under `output/logs/`.

Even when publishing fails, the workflow uploads a debug artifact containing:

- generated images
- metadata JSON
- batch summary
- Python logs
- diagnostics
- `blog_history.json`

## Scheduling

The included workflow currently retains the previous **10 scheduled runs/day**. Because each run now creates five posts, that means up to **50 posts/day** if Facebook publishing succeeds.

If the goal is 10 posts/day, use only two scheduled runs/day instead.
