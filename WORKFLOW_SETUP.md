# Workflow setup — text-only technical articles

1. Put this project at the root of the GitHub repository so `.github/workflows/blog-post.yml` is detected.
2. Add repository secrets `FACEBOOK_PAGE_ID` and `FACEBOOK_PAGE_TOKEN`. Add `GROQ_API_KEY` for higher-quality article-grounded summaries (recommended).
3. Push to `main` to run; the daily schedule is 09:00 IST. The workflow generates a single text-only Facebook Page post, not image slides.
4. Inspect `output/latest_post.txt` in the workflow artifact. If article access is blocked, `content_mode` is `rss_fallback`; do not rely on that fallback as a full-article summary.
5. Use manual workflow dispatch with dry-run enabled to generate text without publishing.
