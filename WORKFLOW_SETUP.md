# Workflow setup

Place this project at the **root of the GitHub repository** so `.github/workflows/blog-post.yml` is discovered by GitHub Actions.

The workflow supports:
- automatic push runs
- manual `workflow_dispatch`
- 20 scheduled hourly slots in Asia/Kolkata
- agent selection for manual tests
- dry-run mode

Required GitHub repository secrets:
- `FACEBOOK_PAGE_ID`
- `FACEBOOK_PAGE_TOKEN`

The workflow validates all 20 JSON banks and the existing 2,000-topic blog library before generating content.

After each successful run it commits only `data/blog_history.json` with `[skip ci]`; the push trigger ignores that file so it cannot recursively start another run.
