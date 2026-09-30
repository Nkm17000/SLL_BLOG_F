# Smart Learning Lab — Dynamic Technical Blog Publisher

## 10 fixed templates — no theme concept
This version uses exactly **10 HTML templates**, each paired with its own hero image. The template layout/design is fixed; only the JSON placeholders are populated at runtime.

### Input
Edit only:

`data/blogs.json`

Each blog must contain:
- `id`
- `category`
- `title`
- `description`
- exactly 5 `points`
- exactly 2 `items` inside every point

### Template selection
- 10 templates total.
- One template is selected randomly per workflow run.
- A template is not repeated until all 10 templates have been used.
- After all 10 are used, the template cycle resets and random selection starts again.
- There is **no theme ID, theme engine, or template×theme combination logic**.

### Topic selection
- One topic is selected randomly per workflow run.
- A topic is not repeated until every topic in `data/blogs.json` has been generated.
- After all topics are generated, the topic cycle resets.
- Full generation/publishing history is stored in `data/blog_history.json`.

### Image behavior
- Each template has its own local hero image: `assets/images/template-01-hero.png` through `template-10-hero.png`.
- The matching hero image is automatically inserted into the matching template.
- No external image download is required.
- HTML is rendered at 800×1000 CSS pixels with a 2× device scale factor, producing a 1600×2000 PNG.

### Workflow
- One workflow run creates exactly one blog image.
- Manual `workflow_dispatch` and scheduled runs use the same selection/history logic.
- Schedule: `0 0,4,8,12,16,20 * * *` UTC — six runs per day.

### Facebook
Set repository secrets:
- `FACEBOOK_PAGE_ID`
- `FACEBOOK_PAGE_TOKEN`

The workflow renders one PNG and publishes it through the existing Facebook Page service.
