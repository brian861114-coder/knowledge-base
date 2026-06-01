# Maintenance Guide

This document is the operator manual for maintaining the `knowledge-base` project after the initial setup is complete.

Use [README.md](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\README.md) for project overview.  
Use this file for day-to-day maintenance, export, verification, and troubleshooting.

## Scope

This guide covers:

- where the source of truth lives
- how to update content safely
- how to re-export frontend data
- how to verify the prototype after changes
- what to check when moving to another machine
- common failure cases

## Source of Truth

There are two layers in this project:

1. Obsidian vault
   - real note content
   - formulas
   - wikilinks
   - note frontmatter
2. Git repo
   - generation and enrichment scripts
   - frontend prototype
   - exported JSON used by the frontend
   - architecture and handoff docs

Rule of thumb:

- if a note reads incorrectly, fix the vault
- if exported content is wrong, inspect the export scripts
- if the reader UI is wrong, inspect the frontend

## Local Paths

Current workspace:

`C:\Users\brian\Downloads\vibe_coding\knowledge database`

Current vault root:

`C:\Users\brian\OneDrive\[Documents]\Obsidian Vault`

Current knowledge-base folder inside the vault:

`C:\Users\brian\OneDrive\[Documents]\Obsidian Vault\Project\knowledge database`

If working on another machine:

1. locate the vault first
2. confirm the repo checkout path
3. update any path assumptions before running exports

Recommended local config file:

- copy [C:\Users\brian\Downloads\vibe_coding\knowledge database\.knowledge-base.local.example.json](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\.knowledge-base.local.example.json)
  to `.knowledge-base.local.json`
- this local file is ignored by Git
- use it for machine-specific values instead of editing shared scripts when possible

## Files To Reconfigure On Another Machine

These are the main machine-specific files to check after moving the repo:

1. [start_prototype.ps1](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\start_prototype.ps1)
   - reads `.knowledge-base.local.json`
   - supports `KB_PYTHON_PATH`, `KB_PROTOTYPE_HOST`, and `KB_PROTOTYPE_PORT`
   - this is the main startup file most likely to need adjustment only if config support is insufficient
2. [start_prototype.cmd](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\start_prototype.cmd)
   - usually portable
   - confirm it still calls the local PowerShell script correctly
3. `.knowledge-base.local.json`
   - set the local Python path
   - set the local prototype host and port
   - optionally store the local vault path for operator reference
4. [README.md](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\README.md)
   - update any path examples shown to future users
5. [MAINTENANCE.md](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\MAINTENANCE.md)
   - update the recorded local paths and example commands
6. [AI_HANDOFF.md](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\AI_HANDOFF.md)
   - update the repo path
   - update the vault path
   - update command examples if they include absolute paths
7. [PROJECT_ARCHITECTURE.md](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\PROJECT_ARCHITECTURE.md)
   - update the external vault path reference
8. [physics_database_build_manifest.md](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\physics_database_build_manifest.md)
   - update the recorded build environment paths

Usually not machine-specific:

- [prototype/app.js](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\prototype\app.js)
- [prototype/index.html](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\prototype\index.html)
- [prototype/styles.css](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\prototype\styles.css)
- generation and enrichment scripts in `tools/`, unless a script is later changed to hardcode a path

## Normal Maintenance Flow

Use this sequence for most work:

1. Update notes in the Obsidian vault
2. Run generation or enrichment scripts if the change is script-driven
3. Re-export `physics_note_details.json`
4. Re-export `physics_graph.json` if links, note titles, note count, or graph structure changed
5. Start the prototype
6. Verify representative pages
7. Commit the related script, frontend, and export updates together

## Common Commands

### Start the prototype

```powershell
.\start_prototype.cmd
```

Expected local URL:

[http://127.0.0.1:4173/prototype/](http://127.0.0.1:4173/prototype/)

Optional environment-variable override:

```powershell
$env:KB_PYTHON_PATH = "C:\Python311\python.exe"
$env:KB_PROTOTYPE_PORT = "4174"
.\start_prototype.cmd
```

### Re-export note details

```powershell
python .\tools\export_note_details.py `
  --vault 'C:\Users\brian\OneDrive\[Documents]\Obsidian Vault\Project\knowledge database' `
  --out '.\physics_note_details.json'
```

### Re-export graph data

```powershell
python .\obsidian-knowledge-map-demo\scripts\export_graph.py `
  --vault 'C:\Users\brian\OneDrive\[Documents]\Obsidian Vault\Project\knowledge database' `
  --out '.\physics_graph.json'
```

### Check working tree

```powershell
git status --short
```

### Review changed files quickly

```powershell
git diff --stat
```

## When To Re-Export Which File

Re-export `physics_note_details.json` when:

- note body text changed
- formulas changed
- section structure changed
- preview text changed
- full reader content changed

Re-export `physics_graph.json` when:

- note titles changed
- `[[wikilink]]` structure changed
- note count changed
- frontmatter relationships changed
- a new note type page was added or removed

Re-export both when unsure.

## Frontend Verification Checklist

After exports or frontend changes, verify all of the following:

1. The graph loads successfully
2. Clicking a node opens the side panel
3. Full-page reader mode opens correctly
4. A concept page renders normal paragraphs correctly
5. A law page renders display equations correctly
6. A page with inline math renders `$...$` correctly
7. A page with `[[wikilink]]` content shows clickable internal links
8. The page can switch between graph exploration and reading without layout breakage

Suggested representative pages:

- one concept page
- one law page
- one page with dense equations
- one page with many internal links

## Content Maintenance Guidance

When editing notes, keep these priorities:

1. Use valid Obsidian math formatting
   - inline math: `$...$`
   - display math: `$$...$$`
2. Keep the frontmatter schema intact
3. Preserve note-type folder conventions
4. Prefer meaningful section headings over giant undifferentiated text blocks
5. Keep wikilinks consistent with actual note titles

For university-level quality, content should aim to include:

- why the concept or law is needed
- what the quantity or concept measures
- physical interpretation
- governing equations
- assumptions and scope
- step-by-step derivation where appropriate
- common misconceptions
- connections to downstream laws or applications

## Script Ownership Map

Use these files depending on the kind of change:

- [tools/generate_physics_third_batch.py](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\tools\generate_physics_third_batch.py)
  - batch note creation
- [tools/enrich_concept_pages.py](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\tools\enrich_concept_pages.py)
  - broad concept-page enrichment
- [tools/enrich_concept_pages_derivations.py](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\tools\enrich_concept_pages_derivations.py)
  - concept-page derivation and deeper teaching structure
- [tools/enrich_remaining_pages.py](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\tools\enrich_remaining_pages.py)
  - law, quantity, experiment, map, and mathematical-tool enrichment
- [tools/export_note_details.py](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\tools\export_note_details.py)
  - note-detail export used by the reader
- [obsidian-knowledge-map-demo/scripts/export_graph.py](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\obsidian-knowledge-map-demo\scripts\export_graph.py)
  - graph export used by node-link exploration

## Move-To-New-Machine Checklist

When moving the project to another computer:

1. Clone the repo
2. Confirm the vault exists locally
3. Confirm the knowledge-base vault folder path
4. Update path assumptions in commands or local scripts if needed
5. Run both exports once
6. Start the prototype
7. Verify math rendering and reader mode

If something looks wrong after migration, the most likely causes are:

- vault path mismatch
- exports were not rerun
- old JSON is still being served
- note titles changed without matching links

## Troubleshooting

### Problem: The prototype only shows old content

Check:

1. Did `physics_note_details.json` get re-exported after the note edits?
2. Did the local server restart or refresh?
3. Are you looking at the correct repo folder?

### Problem: The graph does not reflect new notes or links

Check:

1. Did `physics_graph.json` get re-exported?
2. Were note titles changed without updating `[[wikilink]]` references?
3. Did the new notes land in the correct vault folder?

### Problem: Equations render in Obsidian but not in the browser

Check:

1. Is the note using `$...$` for inline math?
2. Is the note using `$$...$$` for display math?
3. Is the page being served over HTTP rather than `file://`?
4. Did the frontend load MathJax successfully?

### Problem: Full-page reader mode looks broken

Check:

1. Was `physics_note_details.json` exported after the note-structure change?
2. Did the frontend rendering logic change in [prototype/app.js](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\prototype\app.js)?
3. Did a CSS change in [prototype/styles.css](C:\Users\brian\Downloads\vibe_coding\knowledge%20database\prototype\styles.css) affect layout width, spacing, or overflow?

### Problem: A script runs but the output looks half-old and half-new

This usually means note rewrites and export were done in overlapping steps.

Safer pattern:

1. finish note generation or enrichment first
2. verify the vault files are final
3. export JSON in a separate step
4. then refresh the frontend

## Commit Guidance

Try to keep these grouped together in the same commit:

- note-generation script changes
- note-detail export changes caused by those scripts
- frontend changes needed to render the new structure
- README or maintenance-doc updates that explain the new workflow

That makes future debugging much easier.

## Recommended Next Improvements

The highest-value future work is likely:

1. add more worked examples to core concept and law pages
2. deepen step-by-step mathematical derivations in the central physics spine
3. add stronger maintenance automation for validation, especially broken-link and formula checks
