# knowledge_map Agent Guide

This file is for future agents picking up work in `C:\Users\brian\Downloads\vibe_coding\knowledge_map`.
It is intentionally practical.

## 1. What this project actually is

This repo is a four-layer system:

1. An external Obsidian vault
   - This is the source of truth.
   - Real content lives there as Markdown notes with frontmatter, wikilinks, and math.
2. A Python export and validation toolchain in this repo
   - Exports the vault into JSON artifacts.
   - Validates links, relations, math delimiters, structure, and export consistency.
3. A local prototype frontend in this repo
   - Reads exported JSON.
   - Renders graph, preview panel, and reader mode.
4. A deployment layer under `docs/`
   - GitHub Pages serves from here.

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
  - Export, validation, schema migration, taxonomy, and content-maintenance scripts.
- `schema/`
  - Active structure rules for note types, section order, rename rules, and content rules.
- `obsidian-knowledge-map-demo/scripts/`
  - Contains `export_graph.py`, the graph exporter.
- `assets/`
  - Frontend-served static images and diagrams.
- `knowledge-base-template/`
  - Reusable template version of this architecture.
- `materials-science-engineering-kb/`
  - Separate knowledge-base project sharing the same architecture.
  - Deployment flow explicitly references it.

### Core documentation

- `README.md`
  - Repo overview and current verified status.
- `MAINTENANCE.md`
  - Operator-oriented maintenance notes.
- `agent.md`
  - This file. Use it as the fast operational map.

## 3. Real entrypoints

### Start the local prototype

- `start_prototype.cmd`
  - Wrapper that calls PowerShell.
- `start_prototype.ps1`
  - Real startup entrypoint.
  - Reads `.knowledge-base.local.json`.
  - Supports:
    - `KB_PYTHON_PATH`
    - `KB_PROTOTYPE_HOST`
    - `KB_PROTOTYPE_PORT`

### Export and validate

- `tools/run_exports.py`
  - Main operator entrypoint.
  - Runs:
    1. `tools/export_note_details.py`
    2. `obsidian-knowledge-map-demo/scripts/export_graph.py`
    3. `tools/validate_knowledge_base.py`
- `tools/validate_knowledge_base.py`
  - Validates:
    - required frontmatter
    - broken `[[wikilink]]` targets
    - broken frontmatter relation targets
    - duplicate titles and paths
    - unmatched `$` and `$$`
    - consistency between vault note count and exported JSON files
- `tools/validate_structure.py`
  - Validates:
    - required sections
    - required section order
    - conditional section rules
    - `map` optional section placement

### Path resolution

- `tools/kb_paths.py`
  - Central vault-path resolution logic.
  - Resolution order:
    1. CLI `--vault`
    2. `KB_VAULT_PATH`
    3. `.knowledge-base.local.json` -> `vaultPath`

## 4. Current Verified Status (as of 2026-06-08)

The active source vault, exports, and both validators agree on the current state:

- vault notes: `417`
- exported note details: `417`
- graph nodes: `417`
- graph edges: `7170`
- broken wikilinks: `0`
- broken frontmatter relations: `0`
- math issues: `0`
- duplicate titles: `0`
- duplicate paths: `0`
- structure validation issues: `0`

This was verified in this repo by:

- `tools/validate_structure.py`
- `tools/run_exports.py`
- `tools/validate_knowledge_base.py`

## 5. Current Schema Baseline

The active schema lives under `schema/`:

- `schema/note_types.yaml`
- `schema/sections.yaml`
- `schema/renaming_rules.yaml`
- `schema/content_rules.yaml`

Important implementation note:

- these files currently use JSON syntax even though the extension is `.yaml`
- current consumers use `json.loads`
- do not silently convert them to real YAML unless you update every loader

### Active section rules

- `concept`
  - required: `概念摘要`, `嚴格定義`, `先備知識`, `物理意義`, `典型應用`, `常見誤解`, `歷史背景`, `現代理論視角`, `相關連結`
  - optional: `核心公式`, `符號與單位`, `推導`
  - conditional:
    - if formula exists, require `符號與單位`
    - if formula exists, require `推導`
- `law`
  - `定律摘要`, `數學表述`, `符號與單位`, `物理意義`, `推導`, `適用條件`, `典型應用`, `常見誤解`, `歷史背景`, `現代理論視角`, `相關連結`
- `quantity`
  - `定義`, `數學表達`, `符號與單位`, `維度與量綱`, `物理意義`, `量測方式`, `出現於哪些定律`, `歷史背景`, `現代理論視角`, `相關連結`
- `mathematical_tool`
  - `工具摘要`, `數學定義`, `推導`, `幾何意義`, `為什麼物理需要它`, `在哪些主題中出現`, `典型操作`, `解題框架`, `歷史背景`, `常見誤解`, `現代理論視角`, `相關工具`
- `experiment`
  - `實驗摘要`, `問題背景`, `裝置與方法`, `可觀測量`, `實驗結果`, `誤差與限制`, `歷史背景`, `歷史影響`, `現代理論視角`, `相關連結`, `延伸價值`
- `map`
  - `地圖摘要`, `主要主題`, `關鍵概念`, `關鍵定律`, `典型問題類型`, `建議學習順序`, `先備知識`, `與其他領域的橋接`, `延伸方向`
  - optional: `關鍵實驗`
  - placement rule: `關鍵實驗` must appear immediately after `關鍵定律`

### Active rename baseline

Representative normalizations:

- `物理直覺` -> `物理意義`
- `物理解讀` -> `物理意義`
- `符號說明與單位` -> `符號與單位`
- `進一步視角` -> `現代理論視角`
- `相關概念` -> `相關連結` for experiment notes

Use `schema/renaming_rules.yaml` for the full mapping, not memory.

## 6. Current structure tooling

These scripts are now part of the real operator path:

- `tools/validate_structure.py`
  - structure contract validator
- `tools/normalize_sections.py`
  - heading normalization, merge, dedupe, reorder
- `tools/fill_quantity_modern_perspectives.py`
  - fills missing `現代理論視角` for quantity notes
- `tools/fill_experiment_modern_perspectives.py`
  - fills missing `現代理論視角` for experiment notes
- `tools/fill_mathematical_tool_derivations.py`
  - fills missing `推導` for mathematical tool notes
- `tools/fill_final_structure_gaps.py`
  - final small-batch patcher for map/law edge cases

These were used to migrate the live vault into structure compliance.

## 7. Data flow

External vault Markdown
-> `tools/export_note_details.py`
-> `physics_note_details.json`
-> consumed by `prototype/app.js`

External vault Markdown
-> `obsidian-knowledge-map-demo/scripts/export_graph.py`
-> `physics_graph.json`
-> consumed by `prototype/app.js`

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

If field naming drifts, graph semantics drift immediately.

## 8. Frontend structure

This is a large plain HTML/CSS/JS prototype, not a formal app framework.

- `prototype/index.html`
  - page shell
  - loads MathJax
- `prototype/app.js`
  - almost all frontend logic
  - data loading, rendering, interactions, markdown rendering
- `prototype/styles.css`
  - all styles

The frontend does not read raw vault Markdown directly.
It depends on exported JSON artifacts.

## 9. Local config and path discipline

- `.knowledge-base.local.json`
  - machine-local settings
  - includes:
    - `pythonPath`
    - `prototypeHost`
    - `prototypePort`
    - `vaultPath`

Never trust README path examples without checking `.knowledge-base.local.json` or `KB_VAULT_PATH`.

## 10. Recommended agent strategy

### If the task is structure or schema work

1. Inspect `schema/`
2. Run `tools/validate_structure.py`
3. If the issue is mechanical, use `tools/normalize_sections.py`
4. If the issue is real missing content, patch the source vault and rerun structure validation
5. After structure changes, rerun `tools/run_exports.py`

### If the task is content repair or expansion

- Edit the external vault Markdown, not exported JSON.
- Re-export afterward.
- Run both validators if structure or links changed.

### If the task is graph behavior or relation correctness

- Inspect frontmatter fields and `export_graph.py` mapping first.
- Do not patch only the frontend unless the bug is purely presentational.

### If the task is frontend work

- Most logic is in `prototype/app.js`.
- Deployment requires syncing `docs/`.

### If the task is documentation

- Re-run validation before writing counts or status claims.
- Do not copy stale numbers from older docs.

## 11. Current limitations

Structure compliance is green.
Content quality auditing is not.

What still does not exist yet:

- a semantic/content-quality validator that can reliably detect vague filler
- an automatic score for weak historical sections, shallow derivations, or low-information modern-theory sections

Do not confuse “schema valid” with “content excellent.”

## 12. Role of `materials-science-engineering-kb/`

Do not ignore this directory.

It is a separate knowledge-base project using the same architecture, and deployment explicitly depends on it.

Practical consequence:

- changes to deployment flow must consider both the main physics project and this subproject
- a large share of the dirty working tree may live there
- if your task is only about the main project, do not accidentally stage unrelated material-science files

## 13. Working tree discipline

The repo may be dirty.

Operational rules:

- do not use broad staging like `git add .` unless the user explicitly wants that risk
- if you only touch main-project files, stage explicitly
- never treat exported JSON as canonical content

## 14. Minimum handoff checklist

Before doing real work, do these:

1. Read `.knowledge-base.local.json`
2. Confirm `vaultPath` and Python path
3. Run `git status --short`
4. Run `tools/validate_structure.py`
5. Run `tools/validate_knowledge_base.py`
6. Decide whether the task belongs to the main physics system or `materials-science-engineering-kb`
7. If deployment is involved, verify whether `prototype/` and `docs/` are in sync

## 15. One-line summary

This project is an external Obsidian knowledge base plus a strict schema, export, and validation pipeline. If you get the source-of-truth boundary wrong, you will break the project.
