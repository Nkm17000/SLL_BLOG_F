# Smart Learning Lab — 10 Integrated Hero Templates

This version removes the theme concept completely.

## Design rules

- Exactly 10 templates.
- Each template has its own matching hero image.
- The hero image is integrated into the hero/background area; it is not rendered as a separate white image card.
- All templates are light, readable and social-media friendly.
- The title has template-specific visual treatment (accent line, ribbon, underline, serif treatment, circle detail, etc.).
- Body text and five content cards use high-contrast typography.
- Canvas: 800×1000 CSS pixels.
- Rendering: 1600×2000 PNG at device scale factor 2.

## JSON placeholders

Every template supports:
- `{{category}}`
- `{{title}}`
- `{{description}}`
- `{{hero_image_url}}`
- `{{hero_image_alt}}` (renderer support)
- `{{points[0..4].title}}`
- `{{points[0..4].description}}`
- `{{points[0..4].items[0..1]}}`

The renderer injects the correct local hero image for the selected template.

## Selection

The project uses one random unused template per run. A template is not repeated until all 10 templates have been used; then the template cycle resets.

Topics are independently rotated through the supplied JSON.

## Facebook workflow

The existing workflow is retained:
- one topic per run
- one image per run
- one Facebook Page post per run
- manual workflow dispatch
- six scheduled runs per day
- persistent topic/template history


## v12:10 update

- Set 1 + Set 2 are merged: 2,000 topics in `data/blogs.json`.
- The theme engine now has 12 predefined light themes.
- Theme selection is hero-aware: each template has a curated compatible palette list.
- The project can use any unused compatible theme and reset the theme cycle after all themes are used.
- Template design remains independent from the theme.
- Titles use a WordArt-inspired gradient, strong weight, shadow and template-specific accent treatment.
- Output supports both 12:10 orientations:
  - horizontal: 1200 × 1000
  - vertical: 1000 × 1200
- One topic still produces one image per workflow run.
