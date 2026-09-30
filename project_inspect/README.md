# Smart Learning Lab — 20 Technical Blog Images / 15 UX Designs

This project keeps the existing 5 programmatic UX designs and adds the 10 supplied full-page UX images as static templates.

## What happens on every push

A push to `main` runs the GitHub Actions workflow once. There is **no cron schedule** and no manual dispatch requirement.

The workflow generates **20 images in one run**:

- Topics: 20
- Designs: 15
- Images per run: 20
- Facebook publishing: preserved from the existing project

### Design rotation

The design registry is in `data/designs.json` and is the single source of truth.

For 20 generated images the exact sequence is:

`1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13 → 14 → 15 → 1 → 2 → 3 → 4 → 5`

So all 15 designs are used before any design repeats.

The next push continues from the saved position in `data/blog_history.json`.

## The 15 designs

### Existing designs — unchanged renderer

1. Clean Modern Green — 1080 × 1350
2. Dark AI Futuristic — 1080 × 1350
3. Warm Friendly Orange — 1080 × 1350
4. Nature Fresh Green — 1080 × 1350
5. Purple Creative AI — 1080 × 1350

### New static UX designs

6. AI Everyday Tasks
7. AI Language Learning
8. AI Study Skills
9. AI Content Creation
10. AI Creative Art
11. AI Life Organization
12. AI Career
13. AI Science Learning
14. AI Math Problem Solving
15. AI Healthy Living

The 10 supplied UX images are stored under `assets/static_templates/`. Their original artwork, branding, illustrations, numbered cards and footer are used as the static visual base. The renderer overlays only the dynamic topic copy from JSON.

The static templates preserve their full 3:5 artwork and are rendered at 1080 × 1800 so the supplied design is not cropped.

## Topic source

`data/topics.json` contains exactly 20 technical topics. Every topic contains:

- title
- category
- description/subtitle
- intro
- 8 sections
- section title, explanation and bullet points
- Try This Today text
- Facebook caption

`data/static_blogs.json` is kept as a compatibility copy for the existing project structure.

## Local generation

Generate all 20 images without Facebook:

```bash
python -m app.run_agent --count 20 --dry-run
```

Run tests:

```bash
python -m unittest discover -s tests -v
```

## GitHub secrets

Keep the existing repository secrets:

```text
FACEBOOK_PAGE_ID
FACEBOOK_PAGE_TOKEN
```

The workflow validates Facebook access once, then processes all 20 items independently. If one item fails, the remaining items continue and the workflow reports the batch failure at the end.

## Important rotation behavior

The generation number is persisted in `data/blog_history.json`. The design index is calculated from:

```text
generation % 15
```

Therefore the first 20 items in a fresh repository use designs 1–15 and then 1–5. Future pushes continue from the saved generation rather than starting over.
