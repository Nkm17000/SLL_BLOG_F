# Smart Learning Lab 247 — Technical Blog Publisher

Generates a source-grounded technical explainer with Groq, renders a 1080×1350 infographic, and publishes one Facebook Page photo post with the full caption and source URL.

## Behavior
- Every push to `main` triggers the GitHub Actions workflow.
- A scheduled run occurs once daily at 09:00 Asia/Kolkata (03:30 UTC).
- A live-publication guard checks `data/blog_history.json` and skips if a post was already published on the current India-local calendar day. Thus pushes and the scheduler cannot create more than one successful post per day.
- Topic history prevents repeat topics.
- The image palette is stored in history and the last five palettes are excluded from the next selection.
- Caption section headings are bold Unicode text and include the source plus Smart Learning Lab 247 website, Instagram, YouTube, and Facebook URLs.
- Manual workflow runs default to dry-run; inspect `output/latest_post.txt` and `output/images/latest_blog.jpg` before enabling a live run.

## GitHub repository secrets
- `GROQ_API_KEY`
- `FACEBOOK_PAGE_ID`
- `FACEBOOK_PAGE_TOKEN`

Keep `data/blog_history.json` when updating the code. It stores previously used topics, publishing status, and recent image palette history.
