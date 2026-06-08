# knowledge-base

Interactive university-level physics knowledge base backed by an external Obsidian vault, with a local graph-reading prototype and an export/validation toolchain.

**Live Demo**: [knowledge-base](https://brian861114-coder.github.io/knowledge-base/)  
**Materials Science Subpage**: [materials-science-engineering](https://brian861114-coder.github.io/knowledge-base/materials-science-engineering/)

## What This Repo Is

This project has two connected parts:

1. This Git repo
   - tooling
   - schema and workflow docs
   - frontend prototype
   - exported JSON artifacts
2. An external Obsidian vault
   - the actual physics notes in Markdown
   - the source of truth for the knowledge base

The repo is the workspace and toolchain.  
The Obsidian vault is the content database.

## Current Verified Status

Latest verified snapshot from `2026-06-08` against the active vault configured for this checkout:

- `417` vault notes
- `417` exported note details
- `417` graph nodes
- `7170` graph edges
- `0` broken wikilinks
- `0` broken frontmatter relations
- `0` math issues
- `0` duplicate titles
- `0` duplicate paths
- `0` structure validation issues

This means:

- the live source vault is aligned with the current schema
- exports are in sync with the source vault again
- both structure validation and full export validation pass

## What Was Completed In This Migration

The repo now has a real schema-first maintenance workflow:

1. Active schema files were defined under `schema/`
2. A structure validator was added
3. The external vault was normalized and migrated to the current section standard
4. Missing required sections were filled across quantities, experiments, mathematical tools, maps, and laws
5. Exports were rerun and full vault validation passed

This is not just a documentation update. The source vault was actually rewritten to comply with the current schema.

## Active Schema

The active schema lives under:

- `schema/note_types.yaml`
- `schema/sections.yaml`
- `schema/renaming_rules.yaml`
- `schema/content_rules.yaml`

Important implementation note:

- these files currently use JSON syntax even though the extension is `.yaml`
- current scripts load them with `json.loads`

### Active note structure

- `concept`
  - required: `概念摘要`, `嚴格定義`, `先備知識`, `物理意義`, `典型應用`, `常見誤解`, `歷史背景`, `現代理論視角`, `相關連結`
  - optional: `核心公式`, `符號與單位`, `推導`
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
  - rule: `關鍵實驗` can exist, but only immediately after `關鍵定律`

## Validator Layers

There are now two separate validation layers:

### 1. Structure validator

`tools/validate_structure.py`

Checks:

- required sections
- section order
- conditional section rules
- map optional-section placement
- legacy heading normalization against rename rules

### 2. Knowledge-base validator

`tools/validate_knowledge_base.py`

Checks:

- required frontmatter
- broken `[[wikilink]]` targets
- broken frontmatter relation targets
- duplicate titles and paths
- basic math delimiter health
- consistency between vault notes and exported JSON

## Repo Layout

```text
knowledge-base/
  assets/                         Frontend-served static diagrams and figures
  docs/                           GitHub Pages deployment
  prototype/                      Frontend prototype
  schema/                         Active note schema, rename rules, content rules
  tools/                          Export / validation / migration scripts
  obsidian-knowledge-map-demo/    Graph export script source
  knowledge-base-template/        Reusable template
  materials-science-engineering-kb/
  physics_graph.json              Exported graph for frontend
  physics_note_details.json       Exported note details for frontend
  MAINTENANCE.md
  README.md
  agent.md
```

## Important Paths

Project workspace:

`C:\Users\brian\Downloads\vibe_coding\knowledge_map`

Do not hardcode the vault path from this README.
Always confirm the active path from:

- `.knowledge-base.local.json`, or
- `KB_VAULT_PATH`, or
- `tools/kb_paths.py` resolution through the validators

## Quick Start

### Local development

```powershell
.\start_prototype.cmd
```

### Export + full validation

```powershell
python .\tools\run_exports.py
```

### Structure validation only

```powershell
python .\tools\validate_structure.py
```

### Export validation only

```powershell
python .\tools\validate_knowledge_base.py
```

Expected local URL:

- [http://127.0.0.1:4173/prototype/](http://127.0.0.1:4173/prototype/)

## Content Update Workflow

Recommended operator loop:

1. Edit notes in the external vault
2. If structure changed, run `python .\tools\validate_structure.py`
3. Run `python .\tools\run_exports.py`
4. Refresh the prototype
5. Copy updated deploy artifacts to `docs/` if publishing

## GitHub Pages Deploy

After content changes:

```powershell
python .\tools\run_exports.py
Copy-Item .\physics_graph.json .\docs\physics_graph.json -Force
Copy-Item .\physics_note_details.json .\docs\physics_note_details.json -Force
Copy-Item .\prototype\app.js .\docs\app.js -Force
Copy-Item .\prototype\index.html .\docs\index.html -Force
Copy-Item .\prototype\styles.css .\docs\styles.css -Force
```

If the materials-science project also changed, sync `docs/materials-science-engineering/` as well.

## Main Scripts

Structure / migration:

- `tools/validate_structure.py`
- `tools/normalize_sections.py`
- `tools/fill_quantity_modern_perspectives.py`
- `tools/fill_experiment_modern_perspectives.py`
- `tools/fill_mathematical_tool_derivations.py`
- `tools/fill_final_structure_gaps.py`

Export / validation:

- `tools/export_note_details.py`
- `obsidian-knowledge-map-demo/scripts/export_graph.py`
- `tools/run_exports.py`
- `tools/validate_knowledge_base.py`

Wikipedia-assisted review:

- `tools/enrich_from_wikipedia.py`
- `tools/build_review_session.py`
- `tools/build_standalone_review_html.py`
- `tools/review_server.py`
- `tools/apply_review_decisions.py`

## Current Limitation

Structure compliance is now green.
Content quality auditing is not yet formalized.

That means:

- the vault now obeys the current section schema
- this does not guarantee every section is equally rich or non-generic

The next layer of work, if needed, is semantic/content-quality auditing rather than more structure cleanup.
