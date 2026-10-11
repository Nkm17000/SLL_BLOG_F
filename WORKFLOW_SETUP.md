# GitHub Actions setup

1. Place these files at the repository root so `.github/workflows/blog-post.yml` is at that exact path.
2. Add repository secrets `GROQ_API_KEY`, `FACEBOOK_PAGE_ID`, and `FACEBOOK_PAGE_TOKEN`.
3. Push to `main` to start the workflow. A daily scheduled run is set for 09:00 India Standard Time (03:30 UTC).
4. A successful live post is recorded in `data/blog_history.json`. Any further push or scheduled run on the same IST date exits with `skipped_daily_limit`, preventing more than one successful post that day.
5. Manual `workflow_dispatch` defaults to dry-run. Review `output/latest_post.txt` and `output/images/latest_blog.jpg` before requesting a live run.

The workflow commits updated topic/palette history back to `main`. Its history commit message contains `[skip ci]` to prevent a self-trigger loop.
