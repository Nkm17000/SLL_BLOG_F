# Multi-account publishing setup

1. Keep `data/blog_history.json` from your existing repository so topic and theme history is retained.
2. Configure `GROQ_API_KEY` and the Page/account secrets in GitHub Actions Secrets.
3. Edit `config/social_accounts.json`. Set `enabled` to `true` for every destination you want to publish to. Add further entries using the prewired numbered secrets (Facebook 1–10; Instagram 1–10).
4. Facebook secret pairs: `FACEBOOK_PAGE_ID`, `FACEBOOK_PAGE_TOKEN`, then `_2` through `_10` on each name.
5. Instagram secret pairs: `INSTAGRAM_USER_ID`, `INSTAGRAM_ACCESS_TOKEN`, then `_2` through `_10` on each name. Each Instagram account must be a professional account eligible for Graph API publishing and the token must have publishing permissions.
6. Instagram image publishing obtains a CDN image URL by uploading the generated image unpublished to the first configured Facebook Page. Therefore at least one working Facebook Page is required when Instagram destinations are enabled.
7. One run generates the image and caption once, then attempts publishing to every enabled destination. Per-destination status and IDs are saved in history/output summary. One successful daily run is enforced across the whole configuration.
8. Workflow runs on every push to `main`, plus once daily at 09:00 IST. The daily guard prevents multiple live publishing runs on the same India-local day.
9. Test with `workflow_dispatch` and `dry_run=true` before enabling live publication.
