# Workflow setup — text-only technical articles

1. Put this project at the root of the GitHub repository so `.github/workflows/blog-post.yml` is detected.
2. Add repository secrets `FACEBOOK_PAGE_ID`, `FACEBOOK_PAGE_TOKEN`, and `GROQ_API_KEY`. Groq is required; the default model is `openai/gpt-oss-120b`. Never commit the key into code.
3. Push to `main` to run; the daily schedule is 09:00 IST. The workflow generates a single text-only Facebook Page post, not image slides.
4. Inspect `output/latest_post.txt` in the workflow artifact. If the publisher article cannot be extracted or Groq fails validation, the run fails safely and does not publish an RSS-only summary.
5. Use manual workflow dispatch with dry-run enabled to generate text without publishing.

6. Run local checks with `python -m unittest discover -s tests -v` (8 tests).
