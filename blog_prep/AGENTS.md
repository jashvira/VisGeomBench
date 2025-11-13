# Blog Prep Workflow

This directory stores the assets that feed the external blog/paper bundle. When
new evaluation runs land (new results JSON + figures), follow the steps below to
keep everything in sync.

## Refreshing a Task After New Model Results

1. **Copy the latest run into `blog_prep/…/<dataset>`**
   ```bash
   python scripts/update_latest_runs.py <model_dir> <run_id>
   ```
   Use the repo root (`outputs/evals/...`) to pick the newest run per model. The
   script overwrites `metadata.json` and `results.jsonl` under
   `blog_prep/<model_dir>/<dataset>`.

2. **Regenerate question + answer spot-check figures**
   ```bash
   UV_CACHE_DIR=.uv-cache uv run python scripts/render_spotcheck_visuals.py \
     blog_prep/<model_dir>/<dataset>/results.jsonl \
     data/<dataset>.jsonl \
     blog_prep/<model_dir>/<dataset>/questions_gt \
     --indices 1-5 --mode ground_truth

   UV_CACHE_DIR=.uv-cache uv run python scripts/render_spotcheck_visuals.py \
     blog_prep/<model_dir>/<dataset>/results.jsonl \
     data/<dataset>.jsonl \
     blog_prep/<model_dir>/<dataset>/model_answers \
     --indices 1-5 --mode model_answer
   ```
   Adjust indices/counts to match however many samples the blog showcases.

3. **Rebuild the per-question gallery (`blog_prep/model_visuals`)**
   ```bash
   UV_CACHE_DIR=.uv-cache uv run python scripts/render_all_model_visuals.py
   ```
   This re-renders every question for every stored run and keeps the `model_visuals`
   tree consistent with the new results.

4. **Refresh the prompt reference JSON**
   ```bash
   python scripts/update_blog_prompts.py
   ```
   The script infers which datasets appear in `paper_package/blog.md` and rewrites
   `blog_prompts.json` directly from `data/<dataset>.jsonl`.

5. **Sync the shipping bundle**
   ```bash
   python scripts/refresh_blog_assets.py
   ```
   Copies all referenced images into `paper_package/assets/...`, ensuring the bundle
   is self-contained before distribution.

## When to Update `blog.md`

Edit `blog_prep/paper_package/blog.md` only when one of the following is true:

- The set of featured tasks, questions, or model pairs changes.
- Prompt copy needs to be refreshed (after running `update_blog_prompts.py`).
- Layout/styling or explanatory text requires an update.

Whenever you change the samples/prompts:

1. Run `python scripts/update_blog_prompts.py` to pull the latest text.
2. Apply the prompt text to the relevant `<pre>` blocks (use
   the helper script if already available).
3. Re-run `python scripts/refresh_blog_assets.py` so the packaged assets align
   with the markdown.

Keeping this order prevents stale prompts or missing figures from slipping into
production bundles.
