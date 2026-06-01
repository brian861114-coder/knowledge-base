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
- `136` notes exported into the frontend dataset
- a graph export and note-detail export used by the prototype
- full-page reading mode in the frontend
- full-note export support, not only previews
- HTML math rendering support for Obsidian-style `$...$` and `$$...$$`
- expanded concept and law pages with stronger university-level explanations
- step-by-step derivation sections added to core concept and core law notes

## Current Architecture

```text
Obsidian vault Markdown notes
  -> generation / enrichment scripts
  -> structured notes with frontmatter + sectioned bodies
  -> JSON exports
     - physics_graph.json
     - physics_note_details.json
  -> prototype frontend
     - graph exploration
     - side-panel preview
     - full-page reader mode
     - MathJax formula rendering
```

## Repo Layout

```text
knowledge-base/
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

- [README.md](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\README.md): project overview and current status
- [MAINTENANCE.md](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\MAINTENANCE.md): day-to-day operations, export flow, and troubleshooting
- [PROJECT_ARCHITECTURE.md](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\PROJECT_ARCHITECTURE.md): architecture notes
- [AI_HANDOFF.md](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\AI_HANDOFF.md): handoff context for future continuation

## Important Paths

Project workspace:

`C:\Users\brian\Downloads\vibe_coding\knowledge database`

Obsidian vault root:

`C:\Users\brian\OneDrive\[Documents]\Obsidian Vault`

Knowledge-base vault folder used by this project:

`C:\Users\brian\OneDrive\[Documents]\Obsidian Vault\Project\knowledge database`

Note:

- On this machine, `[Documents]` is the Windows user Documents folder name shown in Chinese in Explorer.
- If the vault path changes on another machine, update the export commands and startup assumptions before working further.

## Machine-Specific Settings

When syncing this repo to another computer, check these files first:

- [start_prototype.ps1](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\start_prototype.ps1)
  - verify `$preferredPython`
  - verify the default port `4173` is still appropriate
- [start_prototype.cmd](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\start_prototype.cmd)
  - usually portable now, but verify it still launches the local `.ps1` correctly
- [README.md](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\README.md)
  - update example vault paths if the local machine uses a different location
- [MAINTENANCE.md](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\MAINTENANCE.md)
  - update the local path examples and migration checklist if needed
- [AI_HANDOFF.md](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\AI_HANDOFF.md)
  - update repo and vault paths before handing off to another agent
- [PROJECT_ARCHITECTURE.md](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\PROJECT_ARCHITECTURE.md)
  - update the external vault path reference if it changes
- [physics_database_build_manifest.md](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\physics_database_build_manifest.md)
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

- [tools/generate_physics_third_batch.py](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\tools\generate_physics_third_batch.py)
- [tools/enrich_concept_pages.py](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\tools\enrich_concept_pages.py)
- [tools/enrich_concept_pages_derivations.py](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\tools\enrich_concept_pages_derivations.py)
- [tools/enrich_remaining_pages.py](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\tools\enrich_remaining_pages.py)

Export:

- [tools/export_note_details.py](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\tools\export_note_details.py)
- [obsidian-knowledge-map-demo/scripts/export_graph.py](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\obsidian-knowledge-map-demo\scripts\export_graph.py)

Frontend:

- [prototype/index.html](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\prototype\index.html)
- [prototype/app.js](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\prototype\app.js)
- [prototype/styles.css](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\prototype\styles.css)

## Frontend State

The prototype currently supports:

- graph exploration
- note preview in the side panel
- full-note reading mode as a main-page reader
- Markdown-like rendering for exported note content
- clickable Obsidian-style internal links inside note content
- MathJax rendering for:
  - inline math `$...$`
  - display math `$$...$$`

The frontend should be opened over HTTP, not `file://`.

## Running the Prototype

Start the local server with:

```powershell
.\start_prototype.cmd
```

Then open:

[http://127.0.0.1:4173/prototype/](http://127.0.0.1:4173/prototype/)

## Export Workflow

Re-export graph JSON:

```powershell
python .\obsidian-knowledge-map-demo\scripts\export_graph.py `
  --vault 'C:\Users\brian\OneDrive\[Documents]\Obsidian Vault\Project\knowledge database' `
  --out '.\physics_graph.json'
```

Re-export note details JSON:

```powershell
python .\tools\export_note_details.py `
  --vault 'C:\Users\brian\OneDrive\[Documents]\Obsidian Vault\Project\knowledge database' `
  --out '.\physics_note_details.json'
```

Important:

- `physics_graph.json` is the graph dataset
- `physics_note_details.json` is the reading dataset
- after note rewrites finish, export JSON in a separate step so the frontend gets the final note state

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
