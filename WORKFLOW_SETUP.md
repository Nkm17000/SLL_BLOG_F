# GitHub Actions setup

## 1. Put the files at repository root

The repository must contain:

```text
.github/workflows/blog-post.yml
app/
assets/
data/blogs.json
templates/
requirements.txt
```

Do not place the project inside another folder such as `newproj/`.

## 2. Required repository secrets

Create these under **Settings → Secrets and variables → Actions → Repository secrets**:

- `FACEBOOK_PAGE_ID`
- `FACEBOOK_PAGE_TOKEN`

## 3. Enable Actions

Open **Actions** in the repository and make sure workflows are allowed. If GitHub shows a disabled-workflows banner, enable the workflow.

## 4. First test

Open **Actions → Smart Learning Lab - Dynamic Technical Blog → Run workflow**.

For the first test, select `dry_run = true`. This validates JSON, renders one image and does not publish to Facebook.

Then run it again with `dry_run = false` after confirming the image is correct and the Facebook secrets are present.

## 5. Automatic schedule

The workflow is scheduled six times daily at:

- 00:00 UTC
- 04:00 UTC
- 08:00 UTC
- 12:00 UTC
- 16:00 UTC
- 20:00 UTC

GitHub scheduled workflows run from the repository's default branch. The workflow file therefore must be present on the default branch for the schedule to fire.

The workflow also runs on pushes to any branch, which makes it easy to verify that GitHub Actions can start the workflow immediately.

## 6. Manual and scheduled runs use the same selection logic

Each successful run creates exactly one image:

```text
unused topic
   +
unused template/theme combination
   -> one rendered image
   -> one Facebook Page post
```

Template/theme combinations are not repeated until all 50 combinations have been used. Topics are not repeated until all topics have been used.
