# knowledge_map Agent Guide

This file is for future agents picking up work in `C:\Users\brian\Downloads\vibe_coding\knowledge_map`.
It is intentionally practical. The goal is to reduce time wasted on false assumptions about where the real data lives, what the entrypoints are, and which parts of the repo are currently drifting from reality.

## 1. What this project actually is

This is not just a frontend app and not just a Markdown repo.
It is a four-layer system:

1. An external Obsidian vault
   - This is the real source of truth.
   - The actual knowledge content lives there as Markdown notes with frontmatter, wikilinks, and math.
2. A Python export and validation toolchain in this repo
   - Exports the vault into JSON artifacts.
   - Validates frontmatter, links, relations, math delimiters, and export consistency.
3. A local prototype frontend in this repo
   - Reads exported JSON.
   - Renders the graph, side-panel preview, and reader mode.
4. A deployment layer under `docs/`
   - GitHub Pages serves from here.
   - `docs/` must be kept in sync with exported JSON and `prototype/`.

Rule that matters most:

- `physics_graph.json` and `physics_note_details.json` are derived artifacts.
- The external vault is the authoritative content database.

If content is wrong, inspect the vault first.
If export output is wrong, inspect the export scripts.
If the UI is wrong, inspect `prototype/`.

## 2. Important directories

### Core repo directories

- `prototype/`
  - Local frontend source.
  - Main files: `index.html`, `app.js`, `styles.css`.
- `docs/`
  - GitHub Pages deployment output.
- `tools/`
  - Main project scripts: export, validation, taxonomy, map-page expansion, batch content work.
- `obsidian-knowledge-map-demo/scripts/`
  - Contains `export_graph.py`, the graph exporter.
- `scripts/`
  - Contains deployment helpers such as `deploy.sh`.
- `assets/`
  - Frontend-served static images and diagrams.
- `knowledge-base-template/`
  - Extracted reusable template version of this architecture.
- `materials-science-engineering-kb/`
  - A second knowledge-base project using the same architecture.
  - This is not noise. Deployment flow explicitly references it.

### Core documentation

- `README.md`
  - Project overview, but some status details are stale.
- `AI_HANDOFF.md`
  - Prior agent handoff document, also drift-prone.
- `PROJECT_ARCHITECTURE.md`
  - High-level architecture notes.
- `MAINTENANCE.md`
  - Operator manual.
- `agent.md`
  - This file. Use it as the fast operational map, not as marketing copy.

## 3. Real entrypoints

### Start the local prototype

- `start_prototype.cmd`
  - Thin wrapper that calls PowerShell.
- `start_prototype.ps1`
  - Real startup entrypoint.
  - Reads `.knowledge-base.local.json`.
  - Supports environment overrides:
    - `KB_PYTHON_PATH`
    - `KB_PROTOTYPE_HOST`
    - `KB_PROTOTYPE_PORT`
  - If no server is listening on the configured host and port, it starts a Python `http.server`.

### Export and validate

- `tools/run_exports.py`
  - Main operator entrypoint.
  - Runs:
    1. `tools/export_note_details.py`
    2. `obsidian-knowledge-map-demo/scripts/export_graph.py`
    3. `tools/validate_knowledge_base.py`
- `tools/kb_paths.py`
  - Central vault-path resolution logic.
  - Resolution order:
    1. CLI `--vault`
    2. `KB_VAULT_PATH`
    3. `.knowledge-base.local.json` -> `vaultPath`
- `tools/validate_knowledge_base.py`
  - Validates:
    - required frontmatter
    - broken `[[wikilink]]` targets
    - broken frontmatter relation targets
    - duplicate titles
    - unmatched `$` and `$$`
    - consistency between vault note count and exported JSON files

### Deploy

- `scripts/deploy.sh`
  - Runs `python tools/run_exports.py`
  - Copies main project export and frontend artifacts into `docs/`
  - Copies `materials-science-engineering-kb` deployment artifacts into `docs/materials-science-engineering/`
  - Stages selected files, commits, and pushes

## 4. Data flow

### Main content flow

External vault Markdown
-> `tools/export_note_details.py`
-> `physics_note_details.json`
-> consumed by `prototype/app.js` for side panel and reader mode

External vault Markdown
-> `obsidian-knowledge-map-demo/scripts/export_graph.py`
-> `physics_graph.json`
-> consumed by `prototype/app.js` for graph rendering

### Relation model

`export_graph.py` maps frontmatter fields into edge types:

- `prerequisites` -> `requires`
- `related_concepts` -> `related_to`
- `related_quantities` -> `related_to`
- `related_laws` -> `related_to`
- `experiments` -> `verified_by`
- `math_tools` -> `formalized_by`
- `derived_results` -> `derives_to`
- `modern_connections` -> `explains`
- `tested_laws` -> `verified_by`
- `measured_quantities` -> `measures`
- `measurement_methods` -> `measures`
- `used_in` -> `uses`
- `includes` -> `organized_by`
- `recommended_order` -> `requires`
- body `[[wikilink]]` -> `wikilink`

If note schema or field naming drifts, graph semantics drift immediately.

## 5. Frontend structure

This is a large plain HTML/CSS/JS prototype, not a formal app framework.

### File responsibilities

- `prototype/index.html`
  - Page shell.
  - Loads MathJax.
  - Declares the containers for sidebar, graph area, and detail panel.
- `prototype/app.js`
  - Almost all frontend logic lives here.
  - Data loading, graph rendering, interactions, filters, reader mode, markdown rendering, and internal-link behavior.
- `prototype/styles.css`
  - All styles.

### Known frontend characteristics

- The frontend does not read raw vault Markdown directly.
- It depends on exported JSON artifacts.
- It supports graph view, notes view, search view, and settings view.
- It supports taxonomy/domain filter mode.
- It supports Markdown image rendering.
- It uses MathJax for equations.

### Known frontend issue

- `prototype/index.html` currently shows visible mojibake in terminal output and likely contains encoding damage in displayed copy.

Do not assume visible UI text is healthy just because the app loads.

## 6. Local config and environment assumptions

### Local config file

- `.knowledge-base.local.json`
  - Machine-local settings.
  - Includes:
    - `pythonPath`
    - `prototypeHost`
    - `prototypePort`
    - `vaultPath`

### Critical path drift

Repo docs mention a vault path under something like `Obsidian Vault...`.
Actual validation in this session resolved the live vault path as:

- `C:\Users\brian\Downloads\Obsidian Vault備份\obsidian\Project\knowledge database`

That matters because it proves at least one thing:

- documented vault path and active vault path have drifted

Never trust README path examples without checking `.knowledge-base.local.json` or `KB_VAULT_PATH`.

## 7. Verified current state in this session

The validator was run directly with the configured Python runtime:

```powershell
& 'C:\Users\brian\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\tools\validate_knowledge_base.py
```

Result: validation passed after two cleanup changes:

- `_bak_*` backup directories are now ignored by the export and validation pipeline
- broken links and broken frontmatter relations in the affected `05_mathematical_tools/` notes were cleaned up

Observed summary:

Active validator path on `2026-06-07`:

`C:\Users\brian\Downloads\Obsidian Vault備份\obsidian\Project\knowledge database`

- vault: `C:\Users\brian\Downloads\Obsidian Vault備份\obsidian\Project\knowledge database`
- notes: `330`
- note details: `330`
- graph nodes: `330`
- graph edges: `7473`
- missing required fields: `0`
- broken wikilinks: `0`
- broken frontmatter relations: `0`
- math issues: `0`
- duplicate titles: `0`

Implications:

- the active vault and exported JSON are currently aligned again
- `_bak_*` folders exist inside the vault tree but are intentionally treated as backup data, not live notes
- future status claims should still be treated as stale unless validation has just been rerun

## 8. How to think about `tools/`

`tools/` is not just export plumbing. It is the repo's content-engineering toolbox.

### Core operator scripts

- `run_exports.py`
- `export_note_details.py`
- `validate_knowledge_base.py`
- `kb_paths.py`

### Batch generation and expansion scripts

- `generate_physics_seed_notes.py`
- `generate_physics_second_batch.py`
- `generate_physics_third_batch.py`
- `expand_*`
- `add_requested_*`
- `thicken_remaining_topics_batch.py`

### Structure, taxonomy, and repair scripts

- `apply_concept_taxonomy.py`
- `add_secondary_map_pages.py`
- `move_concepts_to_taxonomy_subfolders.py`
- `expand_map_pages_with_descriptions.py`
- `integrate_bridge_links.py`
- `fill_missing_*`
- `normalize_circuit_titles.py`
- `update_law_symbol_units.py`

This repo is part viewer, part content-maintenance system, part export pipeline.

## 9. Role of `materials-science-engineering-kb/`

Do not ignore this directory.

It is a second knowledge-base project using the same architecture, and deployment explicitly depends on it.

### Why it matters

- It has its own `prototype/`
- It has its own `docs/`
- It has its own `tools/`
- It has its own `vault/`
- `scripts/deploy.sh` syncs its artifacts into `docs/materials-science-engineering/`

### Practical consequence

- Changes to deployment flow must consider both the main physics project and this subproject.
- A large share of the current dirty working tree is inside this subproject.
- If your task is only about main-project docs, do not accidentally stage or modify these unrelated files.

## 10. Working tree status at the time this file was created

The repo is not clean.
Uncommitted changes were present mainly under:

- `docs/materials-science-engineering/*`
- `materials-science-engineering-kb/prototype/*`
- `materials-science-engineering-kb/vault/*`

Operational rule:

- Never use broad staging like `git add .` unless the user explicitly wants that risk.

If you only touch main-project files, stage explicitly.

## 11. Recommended agent strategy

### If the task is content repair or content expansion

- Edit the external vault Markdown, not `physics_note_details.json`.
- Then run `tools/run_exports.py`.
- Then inspect validator output.

### If the task is graph behavior or relation correctness

- Inspect frontmatter fields and `export_graph.py` mapping first.
- Do not patch only the frontend unless the bug is purely presentational.

### If the task is frontend work

- Most logic is in `prototype/app.js`.
- `prototype/index.html` likely needs encoding scrutiny before copy edits.
- Deployment requires syncing `docs/`.

### If the task is documentation

- Do not just copy `README.md`.
- Check `.knowledge-base.local.json`.
- Re-run validation before writing counts or status claims.

## 12. Common failure modes

1. Treating repo JSON as source of truth.
   - Wrong. The external vault is the source of truth.
2. Treating README counts as current.
   - Wrong. Status docs have drift.
3. Fixing content by editing exported JSON directly.
   - Usually wrong unless you are debugging the exporter itself.
4. Ignoring `materials-science-engineering-kb/`.
   - Wrong. Deployment flow depends on it.
5. Broad staging in a dirty tree.
   - Wrong. Easy way to mix unrelated changes into one commit.
6. Assuming the documented vault path is the active one.
   - Wrong. This session already proved path drift.

## 13. Minimum handoff checklist for any future agent

Before doing real work, do these six things:

1. Read `.knowledge-base.local.json`
2. Confirm `vaultPath` and Python path
3. Run `git status --short`
4. Run `python .\tools\validate_knowledge_base.py`
5. Decide whether the task belongs to the main physics system or `materials-science-engineering-kb`
6. If deployment is involved, verify whether `prototype/` and `docs/` are in sync

## 14. One-line summary

This project is an external Obsidian knowledge base plus a strict export/validation pipeline plus a JSON-driven viewer. If you get the source-of-truth boundary wrong, you will break the project.
