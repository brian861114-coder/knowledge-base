# knowledge-base

Interactive university-level physics knowledge base backed by an Obsidian vault, with a local graph-reading prototype and generation/export tooling.

**Live Demo**: https://brian861114-coder.github.io/knowledge-base/

## What This Repo Is

This project has two connected parts:

1. This Git repo:
   - tooling
   - schema and planning docs
   - frontend prototype
   - exported JSON artifacts
2. An external Obsidian vault:
   - the actual physics notes in Markdown
   - the source of truth for the knowledge base

The repo is the workspace and toolchain.  
The Obsidian vault is the content database.

## Current Status

The physics knowledge base is in active structure-hardening and taxonomy cleanup, not just raw content expansion.

- `318` notes exported
- `6376` graph edges (relationships)
- `0` broken wikilinks
- `0` broken frontmatter relations
- `0` math issues

Recent progress:

- expanded the source vault substantially across mechanics, optics, electromagnetism, analytical mechanics, nonlinear dynamics, and supporting bridge pages
- added second-layer taxonomy metadata to all `02_concepts` notes:
  - `taxonomy_domain`
  - `cluster`
  - `level`
- added six secondary navigation maps in `00_maps/`
- completed the first structural split of `02_concepts/` into real subfolders for:
  - `analytical_dynamics`
  - `modern_physics`
  - `thermo_fluids`

The repo is now beyond “content exists”; the main work has shifted to keeping the growing vault navigable and structurally coherent.

### Domains

| Domain | Notes | Description |
|--------|------:|-------------|
| 力學 | 82 | 運動、力、能量、動量 |
| 電磁學 | 67 | 電荷、電場、磁、感應 |
| 近代物理 | 21 | 相對論、量子入門 |
| 熱學與熱力學 | 17 | 熱、內能、熵、循環 |
| 光學 | 17 | 幾何光學、波動光學 |
| 數學工具 | 16 | 物理中使用的數學方法 |
| 振動與波動 | 13 | 週期振盪、波的傳播 |
| 流體力學 | 13 | 液體與氣體的連續介質 |
| 熱力學 | 8 | 熱力學專題 |
| 未分類 | 1 | 過渡內容 |

### Note Types

| Type | Label | Description |
|------|-------|-------------|
| concept | 概念 | 核心概念與定義 |
| law | 定律 | 物理定律與定理 |
| quantity | 物理量 | 可量測的物理量 |
| experiment | 實驗 | 經典實驗與量測方法 |
| mathematical_tool | 數學工具 | 數學在物理中的應用 |
| map | 導覽頁 | 領域總覽與知識地圖入口 |

## Frontend Features

- Graph exploration with force-directed layout
- Domain overview with card-based navigation
- Domain focus mode with local subgraph
- Side-panel note preview with MathJax rendering
- Full-page reader mode with table of contents and IntersectionObserver highlighting
- Topnav with 4 views: Search (live filtering), Notes (browsable list), Graph, Settings
- Brand title click resets to homepage
- Responsive design with mobile breakpoints

## Architecture

```text
Obsidian vault Markdown notes
  → note types (defined in schema/)
     - laws, concepts, quantities, experiments, mathematical tools, maps
  → bridge / method layer
     - cross-topic concept bridges
     - analysis-method pages
  → generation / enrichment scripts
  → structured notes with frontmatter + sectioned bodies
  → JSON exports
     - physics_graph.json (nodes + edges)
     - physics_note_details.json (sections + frontmatter)
  → validation
     - frontmatter, link, math, and export consistency checks
  → prototype frontend
     - graph exploration
     - side-panel preview
     - full-page reader mode
     - MathJax formula rendering
```

## Repo Layout

```text
knowledge-base/
  assets/                         Frontend-served static diagrams and figures
  docs/                           GitHub Pages deployment (prototype + data)
  prototype/                      Frontend prototype (local dev)
  tools/                          Note generation / enrichment / export scripts
  obsidian-knowledge-map-demo/    Graph export demo script source
  knowledge-base-template/        Reusable template for other knowledge bases
  physics_graph.json              Exported graph for frontend
  physics_note_details.json       Exported note details for frontend
  AI_HANDOFF.md                   Handoff context for future continuation
  MAINTENANCE.md                  Day-to-day operations and troubleshooting
  README.md                       This file
```

## Key Docs

- [README.md](README.md): project overview and current status
- [AI_HANDOFF.md](AI_HANDOFF.md): handoff context for future continuation
- [MAINTENANCE.md](MAINTENANCE.md): day-to-day operations, export flow, and troubleshooting
- [knowledge-base-template/README.md](knowledge-base-template/README.md): reusable template for other knowledge bases

## Important Paths

Project workspace:

`C:\Users\brian\Downloads\vibe_coding\knowledge_map`

Obsidian vault root:

`C:\Users\brian\Downloads\Obsidian Vault備份\obsidian`

Knowledge-base vault folder used by this project:

`C:\Users\brian\Downloads\Obsidian Vault備份\obsidian\Project\knowledge database`

## Quick Start

### Local Development

```powershell
# Start prototype with the repo's local wrapper
.\start_prototype.cmd

# Export + validate
python .\tools\run_exports.py

# Validate only
python .\tools\validate_knowledge_base.py
```

Expected local URL:

- [http://127.0.0.1:4173/prototype/](http://127.0.0.1:4173/prototype/)

### GitHub Pages

The `docs/` folder is deployed to GitHub Pages.
To update it after content changes:

```powershell
# Re-export
python .\tools\run_exports.py

# Copy deploy artifacts to docs/
Copy-Item .\physics_graph.json .\docs\physics_graph.json -Force
Copy-Item .\physics_note_details.json .\docs\physics_note_details.json -Force
Copy-Item .\prototype\app.js .\docs\app.js -Force
Copy-Item .\prototype\index.html .\docs\index.html -Force
Copy-Item .\prototype\styles.css .\docs\styles.css -Force

# Commit and push
git add .\docs
git commit -m "Update docs deploy artifacts"
git push
```

## Export Workflow

Recommended default command:

```bash
python tools/run_exports.py
```

This runs both exports and then validates:

- note count consistency
- graph count consistency
- required frontmatter
- broken `[[wikilink]]` targets
- broken frontmatter relation targets
- basic `$` / `$$` delimiter balance

## Export Id Policy

The export layer keeps note ids in their canonical mixed-case form.

Examples:

- `RC電路`
- `RL電路`
- `RLC電路`

Completion standard:

- broken `[[wikilink]]` targets = `0`
- broken frontmatter relation targets = `0`
- math issues = `0`

## Vault Structure

The vault is organized by note type:

- `00_maps/`
- `01_laws/`
- `02_concepts/`
- `03_quantities/`
- `04_experiments/`
- `05_mathematical_tools/`

### Current Concept Taxonomy Progress

`02_concepts/` is no longer treated as a flat bucket.

Completed so far:

- all concept notes now have `taxonomy_domain`, `cluster`, and `level` frontmatter
- new secondary map pages were added for:
  - mechanics
  - waves/optics
  - electromagnetism
  - thermo/fluids
  - modern physics
  - analytical mechanics and nonlinear dynamics
- these concept subfolders are already live in the source vault:
  - `02_concepts/analytical_dynamics/`
  - `02_concepts/modern_physics/`
  - `02_concepts/thermo_fluids/`
  - `02_concepts/waves_optics/` *(26 notes, migrated 2026-06-04)*
  - `02_concepts/foundations/` *(25 notes, migrated 2026-06-04)*
  - `02_concepts/mechanics/` *(31 notes, migrated 2026-06-04)*
  - `02_concepts/electromagnetism/` *(40 notes, migrated 2026-06-04)*

Planned target taxonomy for concepts:

- `02_concepts/foundations/`
- `02_concepts/mechanics/`
- `02_concepts/waves_optics/`
- `02_concepts/electromagnetism/`
- `02_concepts/thermo_fluids/`
- `02_concepts/modern_physics/`
- `02_concepts/analytical_dynamics/`

## Main Scripts

Generation / enrichment:

- `tools/generate_physics_third_batch.py`
- `tools/enrich_concept_pages.py`
- `tools/enrich_concept_pages_derivations.py`
- `tools/enrich_remaining_pages.py`

Export:

- `tools/export_note_details.py`
- `obsidian-knowledge-map-demo/scripts/export_graph.py`
- `tools/run_exports.py`
- `tools/validate_knowledge_base.py`

Structure / links:

- `tools/fill_missing_map_experiment_sections.py`
- `tools/integrate_bridge_links.py`
- `tools/enrich_intuition_history_sections.py`

Frontend:

- `prototype/index.html`
- `prototype/app.js`
- `prototype/styles.css`

## Reusable Template

A reusable knowledge-base template has been extracted to [`knowledge-base-template/`](knowledge-base-template/).

It includes:
- YAML-driven note types, domains, and section structures
- Configurable export/validate scripts
- Frontend prototype with all UX improvements
- Documentation for building knowledge bases on other topics

See [knowledge-base-template/README.md](knowledge-base-template/README.md) for details.

## Content Update Workflow

1. Update notes in the vault
2. Run enrichment / generation scripts if needed
3. Re-export `physics_note_details.json`
4. Re-export `physics_graph.json` if graph structure changed
5. Refresh the prototype
6. Copy updated JSON to `docs/` and push for GitHub Pages

## Current Follow-Up Work

Open structure and maintenance work worth tracking right now:

- move the remaining flat `02_concepts/*.md` pages into taxonomy subfolders in controlled batches
  - ~~`waves_optics`~~ ✅ done (2026-06-04)
  - ~~`foundations`~~ ✅ done (2026-06-04)
  - ~~`mechanics`~~ ✅ done (2026-06-04)
  - ~~`electromagnetism`~~ ✅ done (2026-06-04)
  - **All concept notes are now in taxonomy subfolders. No flat `.md` files remain in `02_concepts/`.**
- decide whether to keep the legacy `domain` field as-is or gradually align it with `taxonomy_domain` *(both fields now coexist; frontend toggle switches between them)*
- ~~update the frontend and any downstream tooling to expose taxonomy-based browsing and filtering~~ ✅ done (2026-06-04)
- keep `README.md`, `AI_HANDOFF.md`, and `MAINTENANCE.md` aligned with the new structure and migration state
- keep `docs/` deploy files synchronized with `prototype/` after frontend changes
- keep treating the external Obsidian vault as source of truth; never patch exported JSON as if it were canonical content
- rerun export plus validation after every vault batch

### Recommended Next Step

If continuing the taxonomy rollout, use this order:

1. ~~move `02_concepts/waves_optics`~~ ✅
2. ~~move `02_concepts/foundations`~~ ✅
3. ~~move `02_concepts/mechanics`~~ ✅
4. ~~move `02_concepts/electromagnetism`~~ ✅

All four batches are complete. `02_concepts/` is now fully organized into taxonomy subfolders.

## Maintainer Workflow

When continuing work after a long break:

1. Confirm the Obsidian vault path
2. Open a few notes in Obsidian and verify formulas render
3. Re-run `python tools/run_exports.py`
4. Start the prototype and test key interactions
5. Commit the export changes
