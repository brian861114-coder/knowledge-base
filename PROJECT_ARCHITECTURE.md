# Project Architecture

## Purpose

This project is building a structured physics encyclopedia on top of Obsidian content, then rendering that content as an interactive knowledge map in the browser.

This is not just a visual graph demo. The real system has three layers:

1. Obsidian note system
2. Export / transformation layer
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

Each page uses structured frontmatter plus fixed sections so agents and scripts can parse it reliably.

### Core Principle

The vault is authoritative.

- Markdown note pages are the canonical knowledge base.
- Exported JSON is derived data.
- The frontend should not invent structure that the vault does not encode.

## Layer 2: Export / Transformation

### Scripts

`tools/generate_physics_seed_notes.py`

- Generates the first batch of physics encyclopedia notes.

`tools/generate_physics_second_batch.py`

- Generates the second batch of notes focused on mechanics, math tools, and electromagnetism.

`tools/export_note_details.py`

- Exports note preview content and section snippets into `physics_note_details.json`.

`obsidian-knowledge-map-demo/scripts/export_graph.py`

- Exports node-edge graph JSON into `physics_graph.json`.

### Export Outputs

`physics_graph.json`

- Nodes
- Typed edges
- Domain metadata embedded per node
- Used by the graph prototype

`physics_note_details.json`

- Body preview
- Section preview blocks
- Used by the right-hand reading panel

## Layer 3: Frontend Prototype

Frontend files:

- `prototype/index.html`
- `prototype/styles.css`
- `prototype/app.js`

### Current frontend capabilities

- Overview mode and focused-domain mode
- Domain cards and domain hubs
- Ring layout for focused views
- Zoom / pan / fit view
- Back-to-overview controls
- Right-side detail panel
- Scrollable detail panel
- Section table of contents with jump navigation
- Live reading from exported note preview JSON

### Current frontend limitation

The frontend is still a prototype.

- It does not parse raw vault markdown directly.
- It depends on pre-exported JSON.
- It is single-page and stateful, not yet a formal app with routing or build tooling.

## Domain Strategy

The physics encyclopedia is organized by top-level domains for readers:

- 數學工具
- 力學
- 振動與波動
- 熱學與熱力學
- 電磁學
- 光學
- 近代物理
- 流體力學

Internally, the graph is organized by page type plus typed relations.

That distinction matters:

- Reader navigation is domain-centric.
- System structure is page-type-centric.

## Relation Model

The graph exporter currently maps frontmatter fields to edge types:

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
- Skills
- Scripts
- Exported JSON
- Design source files in the workspace

### Outside repo

The external Obsidian vault path stores the actual encyclopedia pages:

`C:\Users\brian\Downloads\Obsidian Vault備份\obsidian\Project\knowledge database`

This split is intentional.

- Repo = tooling and project logic
- Vault = encyclopedia content

## Recommended Future Structure

The next durable upgrade should be:

1. Add a single orchestrator script that runs note generation, graph export, and detail export in one command.
2. Introduce a real frontend build system if the prototype grows.
3. Continue increasing note density before large UI refactors.

## What Not To Break

- Do not replace the structured note model with freeform notes.
- Do not make the frontend the source of truth.
- Do not let agent-generated pages drift away from the current page-type schema.
- Do not rely on `file://` for frontend loading.

