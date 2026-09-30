# Workflow setup

The workflow is at `.github/workflows/blog-post.yml`.

It supports:
- manual `workflow_dispatch`
- push triggers
- six scheduled runs per day

Each run performs exactly one topic + one template + one image.

No theme selection exists in this version.

Required GitHub repository secrets:
- `FACEBOOK_PAGE_ID`
- `FACEBOOK_PAGE_TOKEN`

For a first test, run the workflow manually with `dry_run=true`. This renders the image and updates history without publishing to Facebook.
