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

The physics knowledge base is feature-complete.

- `255` notes covering 8 domains
- `5091` graph edges (relationships)
- `0` broken wikilinks
- `0` broken frontmatter relations
- `0` math issues

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

```bash
# Start prototype
python -m http.server 4173
# Open http://127.0.0.1:4173/prototype/

# Export + validate
python tools/run_exports.py

# Validate only
python tools/validate_knowledge_base.py
```

### GitHub Pages

The `docs/` folder is deployed to GitHub Pages.
To update it after content changes:

```bash
# Re-export
python tools/run_exports.py

# Copy to docs/
cp physics_graph.json docs/
cp physics_note_details.json docs/
cp prototype/app.js docs/

# Commit and push
git add docs/ && git commit -m "update docs" && git push
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

## Maintainer Workflow

When continuing work after a long break:

1. Confirm the Obsidian vault path
2. Open a few notes in Obsidian and verify formulas render
3. Re-run `python tools/run_exports.py`
4. Start the prototype and test key interactions
5. Commit the export changes
