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

## 7. Current Project Status (as of 2026-06-07)

### Validation Snapshot

vault: 355 notes (excluding _bak_ backup directory), 7423 graph edges
0 broken wikilinks, 0 broken relations, 0 math issues, 0 duplicate titles

### Content Quality Audit (10 Rules)

10-rule content quality audit performed on 2026-06-07. Rules: (1) No "不是A而是B", (2) Definition-first summary, (3) Concrete history, (4) Multi-aspect intuition, (5) Complete symbols, (6) Derivation with formulas, (7) Modern theory, (8) All sections substantive, (9) Wikilinks exist, (10) Related links grouped.

**Pass rate: 234/355 (65%)** — up from 56/355 (15%) at start of session.

| Score | Count | Description |
|-------|-------|-------------|
| 0 (pass) | 234 | All 10 rules satisfied |
| 1 | 0 | Single failure — cleared |
| 2 | 0 | Double failure — cleared |
| 3 | 77 | Triple failure (mostly 直覺+推導+符號) |
| 4 | 32 | Quadruple failure |
| 5 | 12 | Five failures |

Remaining 121 notes fail on:
- 直覺 (物理直覺 < 100 chars): 92 notes
- 推導 (no LaTeX or < 80 chars): 75 notes
- 符號 (no table or no $): 36 notes
- 現代理論 (generic template): 12 notes
- 歷史 (no names/dates): 1 note

### Content Rewrite Progress (2026-06-07 session)

| Batch | Notes | Scope | Status |
|-------|-------|-------|--------|
| Score-6 rewrite | 8 notes | Full rewrite (波粒二象性, 離散能階, 偏振, 共振, 散射, 繞射, 解析度, 密度) | ✅ Done |
| 不是A而是B cleanup | 208 instances across 95 files | All instances removed | ✅ Done |
| 現代理論 (domain-specific) | 206 notes | Replaced template text with specific content | ✅ Done |
| 歷史背景 (domain-specific) | 204 notes | Added specific names/dates by domain | ✅ Done |
| 符號表 (auto-extract) | 145 notes | Extracted symbols from formulas | ✅ Done |
| 推導 (manual) | 76 notes | Wrote specific derivations with LaTeX | ✅ Done |
| 物理直覺 (manual) | 15 notes | Wrote mechanism+analogy+blind spots | ✅ Done |
| Remaining | 121 notes | Mostly 直覺+推導 | In progress |

### Key Lesson

Automated scripts can fix structural issues (template removal, section stubs, symbol extraction) but CANNOT generate actual physics content (formulas, historical figures, multi-aspect intuition). Content quality requires per-note domain knowledge writing.

### Standard Section Structure by Note Type

All new pages MUST follow these section standards. Existing pages will be migrated in phases.

| Type | Standard Section Order |
|------|-----------------------|
| **concept** | 概念摘要 → 嚴格定義 → **先備知識** → 核心公式 → 符號說明與單位 → 物理直覺 → 物理意義 → 推導 → 典型應用 → 常見誤解 → 歷史背景 → 現代理論視角 → 相關連結(含相關概念/物理量/實驗/衍生結果) |
| **law** | 定律摘要 → 數學表述 → 符號說明與單位 → 物理直覺 → 物理意義 → 推導 → 適用條件 → 典型應用 → 常見誤解 → 歷史背景 → 現代理論視角 → 相關連結(含相關概念/物理量/實驗/衍生結果) |
| **quantity** | 定義 → 數學表達 → 符號與單位 → 維度與量綱 → 物理直覺 → 物理意義 → 量測方式 → 出現於哪些定律 → 歷史背景 → 相關連結(含相關概念/物理量/實驗) |
| **mathematical_tool** | 工具摘要 → 數學定義 → 幾何意義 → 為什麼物理需要它 → 在哪些主題中出現 → 典型操作 → 解題框架 → 物理直覺 → 歷史背景 → 常見誤解 → 相關工具 → 進一步視角 |
| **experiment** | 實驗摘要 → 問題背景 → 裝置與方法 → 可觀測量 → 實驗結果 → 誤差與限制 → 物理直覺 → 歷史背景 → 歷史影響 → 相關概念 → 延伸價值 |
| **map** | 地圖摘要 → 主要主題 → 關鍵概念 → 關鍵定律 → 典型問題類型 → 建議學習順序 → 先備知識 → 與其他領域的橋接 → 延伸方向 |

### Renaming Rules (for migration)

| Type | Old Name(s) | Standard Name |
|------|-------------|---------------|
| concept | 核心想法 | → 概念摘要 |
| concept/law/quantity | 物理解讀 | → merge into 物理直覺 |
| concept | 它在衡量什麼 / 這個概念在衡量什麼 | → 物理意義 |
| concept | 先備與延伸連結 / 先備知識與延伸 | → 先備知識 |
| concept/law | 與延伸定理的連接 / 與上下游概念的連接 | → 相關連結 |
| law | 敘述 | → 定律摘要 |
| law | 推導思路 / 逐步數學推導 | → 推導 |
| quantity | 物理量摘要 / 為什麼需要這個物理量 / 這個物理量在衡量什麼 | → 定義 |
| quantity | 數學表述 | → 數學表達 |
| concept/law | 進一步視角 | → 現代理論視角 |
| quantity | 出現於哪些定律 / 與下游定律的連接 | → 出現於哪些定律 |
| all | 和既有節點的關係 / 同域參考 / 與某某的連接 | → 相關連結 |

### Content Quality Rules

1. **No "不是A而是B" pattern** — Direct definition first, not negation then assertion.
2. **物理解讀 merged into 物理直覺** — Single rich intuition section instead of two thin ones.
3. **Definition-first summaries** — State what it is, then where it's used.
4. **Historical background must be concrete** — Include specific people, dates, experiments.
5. **Physics intuition must be multi-aspect** — Mechanism, analogy, and common blind spots.
6. **符號說明與單位 required** for any note containing formulas — Every variable must have name and SI unit.
7. **推導 required** — Even a brief derivation chain. Not just a statement of the formula.
8. **現代理論視角** for concept and law — How this concept is extended or reinterpreted in modern physics.

### Known Content Issues

1. **Section structure inconsistency** — Different note types (law, concept, quantity, mathematical_tool) use different section names. Many concept notes have 核心想法/概念摘要/物理解讀 overlapping sections. Laws lack standardized structure.
2. **Formula completeness** — Many formulas presented without derivation steps, symbol explanations, or SI units. Mathematical_tool type needs: 定義→公式→推導→物理意義.
3. **Missing 符號說明 in many notes** — Variables used in formulas are not listed with their meanings and units.
4. **Review HTML accessibility snapshot** may show incomplete content due to `<div class="diff-*">` wrappers. Actual content is present — verify with `innerText` in console.

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

### If the task is to continue the Wikipedia-assisted cleanup flow

- Use `tmp/review_sessions/wiki-pilot-20260607-120602/review.html` as the primary review artifact.
- Do not assume the local review server is stable.
- The current blocker is not candidate generation.
- The current blocker is the final reviewed-change import/apply step.

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
