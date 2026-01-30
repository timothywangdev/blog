Publish a blog post to Substack. This command orchestrates the full workflow.

## Usage

`/substack <path-to-qmd-file>`

Example: `/substack posts/diffusion/12-why-diffusion/index.qmd`

## Workflow

Run these steps **sequentially** (each depends on the previous):

### Step 1: Rewrite for Substack

Run `/substack-rewrite` on the input file to create `_substack.qmd`:
- Converts inline LaTeX → Unicode/prose
- Converts tables → bullet lists
- Adds `substack_url: ""` placeholder to frontmatter

**Output**: `_substack.qmd` in the same directory as the input file

### Step 2: Publish to Substack

Run `/substack-publish` on the generated `_substack.qmd`:
- Generates HTML for copy-paste
- Guides through Substack editor workflow
- Handles paste limitation workarounds
- Handles image upload issues

**Output**: Published post on Substack

### Step 3: Validate

Run `/substack-validate` on the `_substack.qmd` file:
- Verifies all content transferred correctly
- Checks images uploaded successfully
- Verifies callout content not stripped
- Confirms equations rendered

**Output**: Validation report (PASS/FAIL)

### Step 4: Cleanup

After validation passes:
- Delete the generated HTML file
- Update `substack_url` in frontmatter with the published URL

## Error Handling

If any step fails:
- **Step 1 fails**: Fix the source QMD and retry
- **Step 2 fails**: Follow the troubleshooting in `/substack-publish`
- **Step 3 fails**: Fix the identified issues and re-validate

Do NOT proceed to the next step if the current step fails.
