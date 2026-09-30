# Smart Learning Lab — Dynamic Technical Blog Publisher

This version uses **10 HTML layouts × 5 light themes = 50 visual combinations**.

## Important design fixes
- All five themes are intentionally light. The old dark/midnight theme has been removed.
- Every template has a real high-resolution PNG hero image stored locally in `assets/images/`.
- No external image download is required during the GitHub Actions run.
- The renderer embeds the local hero image directly into the HTML before Chromium renders it.
- Text uses dark, high-contrast colors on light surfaces.
- The content area is sized to use the full 10:8 poster canvas instead of leaving a large empty bottom area.
- Output is rendered at **1600 × 2000 PNG**.

## Input
Only edit:

`data/blogs.json`

Each blog must contain exactly 5 points, and each point must contain 2 `items`.

## Rotation
- Random unused template + random unused theme.
- 50 combinations total.
- A combination is not reused until all 50 are consumed.
- After all 50 combinations are consumed, the combination cycle resets.
- Topic history is tracked separately and a topic is not reused until every topic has been generated.
- One workflow run creates exactly one blog image.
- Manual `workflow_dispatch` follows exactly the same rules as the scheduled workflow.

## Schedule
Six scheduled workflow runs per day:
`0 0,4,8,12,16,20 * * *` UTC.

## Facebook
Set repository secrets:
- `FACEBOOK_PAGE_ID`
- `FACEBOOK_PAGE_TOKEN`

The workflow renders one PNG and publishes it using the existing Facebook Page publishing service.
