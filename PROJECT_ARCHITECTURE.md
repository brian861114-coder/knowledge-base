# Project Architecture

## Purpose

This project builds a structured physics knowledge base on top of an Obsidian vault, then renders that content as an interactive knowledge map in the browser.

The system has three layers:

1. Obsidian note system
2. Export and transformation layer
3. Frontend exploration layer

## Layer 1: Obsidian Source of Truth

The Obsidian vault stores the actual encyclopedia pages.

Current page types:

- `map`
- `law`
- `concept`
- `quantity`
- `experiment`
- `mathematical_tool`

Each page is expected to use structured frontmatter plus stable section headings so scripts can parse it reliably.

### Core Principle

The vault is authoritative.

- Markdown note pages are the canonical knowledge base.
- Exported JSON is derived data.
- The frontend should not invent structure that the vault does not encode.

## Layer 2: Export and Transformation

### Scripts

`tools/generate_physics_seed_notes.py`

- Generates the first batch of seed notes.

`tools/generate_physics_second_batch.py`

- Generates the second batch focused on mechanics, mathematical tools, and electromagnetism.

`tools/generate_physics_third_batch.py`

- Generates the third batch used for broader coverage expansion.

`tools/enrich_concept_pages.py`

- Deepens concept pages.

`tools/enrich_concept_pages_derivations.py`

- Adds more explicit derivation-oriented teaching structure to concept pages.

`tools/enrich_remaining_pages.py`

- Enriches law, quantity, experiment, map, and mathematical-tool pages.

`tools/export_note_details.py`

- Exports full note-reading data into `physics_note_details.json`.

`obsidian-knowledge-map-demo/scripts/export_graph.py`

- Exports node-edge graph data into `physics_graph.json`.

`tools/validate_knowledge_base.py`

- Validates required frontmatter, wikilinks, relation targets, basic math delimiter structure, and export consistency.

`tools/run_exports.py`

- Runs both exports and then the validator as the normal operator entrypoint.

### Export Outputs

`physics_graph.json`

- Nodes
- Typed edges
- Domain metadata embedded per node
- Used by the graph prototype

`physics_note_details.json`

- Full exported note-reading content
- Section blocks for reader mode
- Used by the frontend side panel and full-page reader

## Layer 3: Frontend Prototype

Frontend files:

- `prototype/index.html`
- `prototype/styles.css`
- `prototype/app.js`

### Current frontend capabilities

- Graph exploration
- Side-panel note preview
- Full-page reader mode
- Clickable internal links
- MathJax rendering for inline and display math
- Section table of contents and jump navigation

### Current frontend limitation

The frontend is still a prototype.

- It does not parse raw vault markdown directly.
- It depends on pre-exported JSON.
- It is a single-page prototype, not yet a formal built app.

## Relation Model

The graph exporter maps frontmatter fields to edge types:

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

This mapping is the backbone of the knowledge map.

## File and Ownership Boundaries

### In repo

These belong in this Git repo:

- Docs
- Prototype
- Scripts
- Exported JSON
- Local startup helpers

Repo path on this machine:

`C:\Users\brian\Downloads\vibe_coding\knowledge_map`

### Outside repo

The external Obsidian vault stores the actual encyclopedia pages:

`C:\Users\brian\Downloads\Obsidian Vault備份\obsidian\Project\knowledge database`

This split is intentional.

- Repo = tooling and project logic
- Vault = encyclopedia content

## Recommended Future Structure

The next durable upgrade should be:

1. Extend validation beyond delimiter checks into stronger formula and schema checks.
2. Introduce a real frontend build system if the prototype grows further.
3. Continue increasing note density before large UI refactors.

## What Not To Break

- Do not replace the structured note model with freeform notes.
- Do not make the frontend the source of truth.
- Do not let generated pages drift away from the current page-type schema.
- Do not rely on `file://` for frontend loading.
