# knowledge-base

Interactive university-level physics knowledge base backed by an Obsidian vault, with a local graph-reading prototype and generation/export tooling.

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

The project is no longer just a seed prototype. It currently includes:

- A physics knowledge base covering:
  - mathematical tools
  - mechanics
  - vibrations and waves
  - thermodynamics
  - electromagnetism
  - optics
  - modern physics
  - fluid mechanics
- `255` notes exported into the frontend dataset
- a graph export and note-detail export used by the prototype
- full-page reading mode in the frontend
- full-note export support, not only previews
- HTML math rendering support for Obsidian-style `$...$` and `$$...$$`
- expanded concept and law pages with stronger university-level explanations
- step-by-step derivation sections added to core concept and core law notes
- bridge-note and method-page batches added to reduce isolated concept pages and turn the vault into a more connected analysis system
- recent expansion batches closed major coverage gaps in circuits, induction, rotational dynamics, equilibrium, elasticity, and introductory thermodynamics

## Current Incomplete List

The previously documented high-priority gaps have now been filled:

- thermodynamics follow-up pages
  - `熱膨脹`
  - `熱機`
  - `效率`
- AC / resonance cleanup
  - `RLC電路`
- wave and optics bridge pages
  - `波速`
  - `波長`
  - `頻率`
  - `折射率`
  - `薄膜干涉`
  - `單縫繞射`
  - `雙縫干涉`

Areas that now have a usable backbone but may still need density and refinement:

- rotational dynamics
  - now includes `轉動版牛頓第二定律`, `平行軸定理`, `角動量守恆`, `進動`, `陀螺`
- equilibrium and elasticity
  - now includes `機械平衡`, `靜力平衡`, `彈性`, `應力`, `應變`, `楊氏模數`, `剪切模數`, `體積彈性模數`
- circuits through induction and AC foundations
  - now includes `電流`, `電阻`, `電動勢`, `直流電路`, `基爾霍夫` laws, `自感`, `互感`, `阻抗`, `感抗`, `電容抗`, `變壓器`
- introductory thermodynamics
  - now includes `比熱`, `潛熱`, `理想氣體`, `狀態方程`, `分子運動論`
- wave and optics bridge layer
  - now includes `波速`, `波長`, `頻率`, `折射率`, `薄膜干涉`, `單縫繞射`, `雙縫干涉`

Current work is therefore less about obvious missing cornerstone pages and more about:

- deepening existing note bodies
- adding targeted reverse links from older core pages into the new bridge pages
- increasing density in waves, optics, and thermodynamics where the skeleton now exists but many notes are still shorter than the mechanics and electromagnetism core

## Export Id Policy

The export layer now keeps note ids in their canonical mixed-case form instead of forcing everything to lowercase slugs.

Examples:

- `RC電路`
- `RL電路`
- `RLC電路`

This applies to:

- `physics_note_details.json` keys
- `physics_graph.json` node ids

Link resolution and validation still use normalized matching internally, so existing `[[wikilink]]` and frontmatter relation targets remain tolerant to case and spacing differences.

Completion standard remains unchanged:

- broken `[[wikilink]]` targets = `0`
- broken frontmatter relation targets = `0`
- math issues = `0`

## Current Architecture

```text
Obsidian vault Markdown notes
  -> note types
     - laws
     - concepts
     - quantities
     - experiments
     - mathematical tools
  -> bridge / method layer
     - cross-topic concept bridges
     - analysis-method pages
     - quantity pages used as flow or state discriminators
  -> generation / enrichment scripts
  -> structured notes with frontmatter + sectioned bodies
  -> JSON exports
     - physics_graph.json
     - physics_note_details.json
  -> validation
     - frontmatter, link, math, and export consistency checks
  -> prototype frontend
     - graph exploration
     - side-panel preview
     - full-page reader mode
     - MathJax formula rendering
```

## Bridge And Method Progress

The vault is no longer being expanded only by adding isolated definition pages.  
Recent work focused on high-value bridge pages and method pages that multiple core notes can point back to.

Completed priority batches:

- quantum and wave bridge pages
  - `相位`
  - `算符`
  - `期望值`
  - `穿隧`
  - `散射`
  - `繞射`
  - `解析度`
- mechanics method and reduction pages
  - `自由度`
  - `約束`
  - `中心力`
  - `有效位能`
  - `可逆過程`
  - `不可逆過程`
- fluid-analysis bridge pages
  - `理想流體近似`
  - `黏滯力`
  - `層流`
  - `紊流`
  - `雷諾數`

What those batches changed structurally:

- quantum notes now have a clearer bridge from `波函數 / 機率振幅 / 本徵態 / 可觀測量 / 薛丁格方程` into measurement language and barrier / scattering analysis
- optics notes now have an explicit bridge from `干涉 / 惠更斯原理 / 顯微鏡 / 光線模型` into diffraction-limited resolution analysis
- mechanics notes now have an explicit bridge from `廣義座標 / 拉格朗日力學 / 角動量 / 位能` into constrained-system and orbital analysis
- thermodynamics notes now have an explicit bridge from `熱平衡 / 熵 / 熱力學第二定律` into process-direction and reversibility analysis
- fluid mechanics notes now have an explicit bridge from `連續方程 / 伯努力方程 / 文氏管` into approximation limits, viscous effects, and flow-regime classification

Status against the original bridge-page priority list:

- completed: all items from the original priority list have now been created
- not yet done: systematic back-linking from older core pages into these new bridge pages is still incomplete
- ongoing standard: after each content batch, rerun export and validation until
  - broken `[[wikilink]]` targets = `0`
  - broken frontmatter relation targets = `0`
  - math issues = `0`

Current next-step priority:

- add targeted reverse links from older core pages to the new bridge and method pages where the connection is conceptually central
- keep avoiding isolated new notes
- continue using `02_concepts/` and `03_quantities/` as the default home unless a topic is clearly a law or mathematical tool

## Repo Layout

```text
knowledge-base/
  assets/                         Frontend-served static diagrams and figures
  prototype/                      Frontend prototype
  tools/                          Note generation / enrichment / export scripts
  obsidian-knowledge-map-demo/    Graph export demo script source
  physics_graph.json              Exported graph for frontend
  physics_note_details.json       Exported note details for frontend
  physics_encyclopedia_schema.md  Core encyclopedia schema
  physics_database_build_manifest.md
  physics_second_batch_manifest.md
  MAINTENANCE.md
  PROJECT_ARCHITECTURE.md
  AI_HANDOFF.md
  start_prototype.cmd
  start_prototype.ps1
```

## Key Docs

- [README.md](C:\Users\brian\Downloads\vibe_coding\knowledge_map\README.md): project overview and current status
- [MAINTENANCE.md](C:\Users\brian\Downloads\vibe_coding\knowledge_map\MAINTENANCE.md): day-to-day operations, export flow, and troubleshooting
- [PROJECT_ARCHITECTURE.md](C:\Users\brian\Downloads\vibe_coding\knowledge_map\PROJECT_ARCHITECTURE.md): architecture notes
- [AI_HANDOFF.md](C:\Users\brian\Downloads\vibe_coding\knowledge_map\AI_HANDOFF.md): handoff context for future continuation

## Important Paths

Project workspace:

`C:\Users\brian\Downloads\vibe_coding\knowledge_map`

Obsidian vault root:

`C:\Users\brian\Downloads\Obsidian Vault備份\obsidian`

Knowledge-base vault folder used by this project:

`C:\Users\brian\Downloads\Obsidian Vault備份\obsidian\Project\knowledge database`

Note:

- On this machine, `[Documents]` is the Windows user Documents folder name shown in Chinese in Explorer.
- If the vault path changes on another machine, update the export commands and startup assumptions before working further.

## Machine-Specific Settings

When syncing this repo to another computer, check these files first:

- [.knowledge-base.local.example.json](C:\Users\brian\Downloads\vibe_coding\knowledge_map\.knowledge-base.local.example.json)
  - copy this to `.knowledge-base.local.json`
  - set the local Python path
  - set the local prototype host and port
  - record the local vault path for operator reference
- `.knowledge-base.local.json`
  - this file is intentionally local-only and ignored by Git
  - use it instead of editing shared scripts when possible

- [start_prototype.ps1](C:\Users\brian\Downloads\vibe_coding\knowledge_map\start_prototype.ps1)
  - now reads `.knowledge-base.local.json` first
  - also supports `KB_PYTHON_PATH`, `KB_PROTOTYPE_HOST`, and `KB_PROTOTYPE_PORT`
- [start_prototype.cmd](C:\Users\brian\Downloads\vibe_coding\knowledge_map\start_prototype.cmd)
  - usually portable now, but verify it still launches the local `.ps1` correctly
- [README.md](C:\Users\brian\Downloads\vibe_coding\knowledge_map\README.md)
  - update example vault paths if the local machine uses a different location
- [MAINTENANCE.md](C:\Users\brian\Downloads\vibe_coding\knowledge_map\MAINTENANCE.md)
  - update the local path examples and migration checklist if needed
- [AI_HANDOFF.md](C:\Users\brian\Downloads\vibe_coding\knowledge_map\AI_HANDOFF.md)
  - update repo and vault paths before handing off to another agent
- [PROJECT_ARCHITECTURE.md](C:\Users\brian\Downloads\vibe_coding\knowledge_map\PROJECT_ARCHITECTURE.md)
  - update the external vault path reference if it changes
- [physics_database_build_manifest.md](C:\Users\brian\Downloads\vibe_coding\knowledge_map\physics_database_build_manifest.md)
  - update the recorded repo path and vault path if the environment changes

Files that usually do not need path edits:

- frontend files in `prototype/`
- enrichment scripts in `tools/`
- export scripts, as long as the vault path is passed in through the command line

## Vault Structure

The vault is organized by note type:

- `00_maps/`
- `01_laws/`
- `02_concepts/`
- `03_quantities/`
- `04_experiments/`
- `05_mathematical_tools/`

Those note types are what the generators and exports expect.

## Main Scripts

Generation / enrichment:

- [tools/generate_physics_third_batch.py](C:\Users\brian\Downloads\vibe_coding\knowledge_map\tools\generate_physics_third_batch.py)
- [tools/enrich_concept_pages.py](C:\Users\brian\Downloads\vibe_coding\knowledge_map\tools\enrich_concept_pages.py)
- [tools/enrich_concept_pages_derivations.py](C:\Users\brian\Downloads\vibe_coding\knowledge_map\tools\enrich_concept_pages_derivations.py)
- [tools/enrich_remaining_pages.py](C:\Users\brian\Downloads\vibe_coding\knowledge_map\tools\enrich_remaining_pages.py)

Export:

- [tools/export_note_details.py](C:\Users\brian\Downloads\vibe_coding\knowledge_map\tools\export_note_details.py)
- [obsidian-knowledge-map-demo/scripts/export_graph.py](C:\Users\brian\Downloads\vibe_coding\knowledge_map\obsidian-knowledge-map-demo\scripts\export_graph.py)
- [tools/run_exports.py](C:\Users\brian\Downloads\vibe_coding\knowledge_map\tools\run_exports.py)
- [tools/validate_knowledge_base.py](C:\Users\brian\Downloads\vibe_coding\knowledge_map\tools\validate_knowledge_base.py)

Frontend:

- [prototype/index.html](C:\Users\brian\Downloads\vibe_coding\knowledge_map\prototype\index.html)
- [prototype/app.js](C:\Users\brian\Downloads\vibe_coding\knowledge_map\prototype\app.js)
- [prototype/styles.css](C:\Users\brian\Downloads\vibe_coding\knowledge_map\prototype\styles.css)

## Frontend State

The prototype currently supports:

- graph exploration
- note preview in the side panel
- full-note reading mode as a main-page reader
- Markdown-like rendering for exported note content
- clickable Obsidian-style internal links inside note content
- Markdown image rendering for explanatory diagrams
- MathJax rendering for:
  - inline math `$...$`
  - display math `$$...$$`

The frontend should be opened over HTTP, not `file://`.

## Diagram Assets

If you want to embed explanatory diagrams in note content, use repo-served image assets rather than machine-specific absolute file paths.

Recommended location:

- [assets/README.md](C:\Users\brian\Downloads\vibe_coding\knowledge_map\assets\README.md)

Recommended Markdown syntax:

```md
![Free-body diagram](../assets/newton-second-law-free-body.png "Force analysis schematic")
```

Current frontend behavior:

- a standalone image line renders as a figure block
- the optional quoted title becomes the visible caption
- inline image syntax inside a paragraph is also supported
- local relative paths and external `http://` / `https://` image URLs work

Avoid:

- Windows absolute paths such as `C:\...`
- spaces in image filenames when a simpler hyphenated name is available
- relying on `file://` page loads

## Running the Prototype

Start the local server with:

```powershell
.\start_prototype.cmd
```

Then open:

[http://127.0.0.1:4173/prototype/](http://127.0.0.1:4173/prototype/)

If another machine uses a different Python install or port:

1. Copy `.knowledge-base.local.example.json` to `.knowledge-base.local.json`
2. Update the local values there
3. Run `.\start_prototype.cmd`

## Export Workflow

Recommended default command:

```powershell
python .\tools\run_exports.py
```

This runs both exports and then validates:

- note count consistency
- graph count consistency
- required frontmatter
- broken `[[wikilink]]` targets
- broken frontmatter relation targets
- basic `$` / `$$` delimiter balance

Validation only:

```powershell
python .\tools\validate_knowledge_base.py
```

Re-export graph JSON:

```powershell
python .\obsidian-knowledge-map-demo\scripts\export_graph.py `
  --vault 'C:\Users\brian\Downloads\Obsidian Vault備份\obsidian\Project\knowledge database' `
  --out '.\physics_graph.json'
```

Re-export note details JSON:

```powershell
python .\tools\export_note_details.py `
  --vault 'C:\Users\brian\Downloads\Obsidian Vault備份\obsidian\Project\knowledge database' `
  --out '.\physics_note_details.json'
```

Important:

- `physics_graph.json` is the graph dataset
- `physics_note_details.json` is the reading dataset
- after note rewrites finish, export JSON in a separate step so the frontend gets the final note state
- use `tools/run_exports.py` as the normal operator path; use the individual commands only when isolating a problem

## Content Update Workflow

Typical content workflow:

1. Update notes in the vault
2. Run enrichment / generation scripts if needed
3. Re-export `physics_note_details.json`
4. Re-export `physics_graph.json` if graph structure changed
5. Refresh the prototype

## Maintainer Workflow

When continuing work on another machine or after a long break, use this order:

1. Confirm the Obsidian vault path used on the current machine
2. Confirm the repo path and that `start_prototype.cmd` still points to the local setup
3. Open a few representative notes in Obsidian and verify formulas render correctly
4. If content scripts were changed, re-run the relevant generation or enrichment scripts
5. Re-export `physics_note_details.json`
6. Re-export `physics_graph.json` when links, note names, or note count changed
7. Start the prototype and test:
   - one concept page
   - one law page
   - one page with inline math
   - one page with display math
   - one page containing Obsidian internal links
8. Commit the export changes together with the script or frontend changes that produced them

Suggested quick sanity check after major updates:

- note count still matches expectations
- no broken `[[wikilink]]` targets remain
- MathJax renders both `$...$` and `$$...$$`
- full-page reader mode still opens and scrolls correctly
- graph and note detail JSON are both freshly exported

## Current Content Direction

Recent work has focused on:

- deepening concept pages to a stronger university level
- adding clearer answers to:
  - why the concept is needed
  - what the concept measures
  - how it connects to downstream theorems
- adding step-by-step derivations to core concept pages such as:
  - `potential energy`
  - `conservative force`
  - `simple harmonic motion`
  - `electric potential`
- deepening core law pages such as:
  - `Newton's second law`
  - `work-energy theorem`
  - `mechanical energy conservation`
  - `Gauss's law`
  - `Faraday's law`
  - `ideal gas equation`
  - `first law of thermodynamics`
  - `thin lens equation`

## Source of Truth

Keep these responsibilities separate:

- Obsidian vault:
  - real content
  - note structure
  - formulas
  - links
- Git repo:
  - scripts
  - prototype
  - docs
  - exported frontend data
