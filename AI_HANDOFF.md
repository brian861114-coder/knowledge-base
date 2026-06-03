# AI Handoff

This file is for the next agent continuing work on this repository.

## What This Project Is

This workspace builds a physics knowledge-base system around an Obsidian vault.

There are two distinct locations on this machine:

- Workspace repo:
  `C:\Users\brian\Downloads\vibe_coding\knowledge_map`
- Obsidian vault content:
  `C:\Users\brian\Downloads\Obsidian Vault備份\obsidian\Project\knowledge database`

Do not confuse them.

- Code, docs, prototype, exports, and local config stay in the repo.
- Physics Markdown note content lives in the vault.

## Current State

The project is feature-complete for the physics knowledge base. All items in the README Agent Handoff section have been resolved.

### What's built

- A structured physics encyclopedia with 255 notes, 5091 edges
- 8 domains: mechanics, electromagnetism, optics, thermodynamics, modern physics, fluid mechanics, vibrations & waves, mathematical tools
- 6 note types: map, law, concept, quantity, experiment, mathematical_tool
- Full bridge/method page layer connecting cross-topic concepts
- Standardized section structure across all notes (物理直覺 + 歷史背景)
- Reverse links from 14 core notes to bridge pages

### Frontend features

- Graph exploration with force-directed layout
- Domain overview with card-based navigation
- Domain focus mode with local subgraph
- Side-panel note preview with MathJax rendering
- Full-page reader mode with table of contents and IntersectionObserver highlighting
- Topnav with 4 views: Search (live filtering), Notes (browsable list), Graph, Settings
- Brand title click resets to homepage
- Sidebar reordered: Search → Mode → Domain → Type → Summary
- Responsive design with mobile breakpoints

### Key files

| File | Purpose |
|------|---------|
| `prototype/index.html` | Frontend entry point |
| `prototype/app.js` | All frontend logic (~2360 lines) |
| `prototype/styles.css` | All styles (~1400 lines) |
| `physics_graph.json` | Exported graph data (nodes + edges) |
| `physics_note_details.json` | Exported note content (sections + frontmatter) |
| `tools/run_exports.py` | One-command export + validate |
| `tools/validate_knowledge_base.py` | Standalone validation |
| `tools/integrate_bridge_links.py` | Add reverse links to core notes |
| `tools/fill_missing_map_experiment_sections.py` | Fix missing standard sections |
| `knowledge-base-template/` | Reusable template for other knowledge bases |

### Validation status

```
notes: 255
note details: 255
graph nodes: 255
graph edges: 5091
broken wikilinks: 0
broken frontmatter relations: 0
math issues: 0
```

## How To Continue Safely

### When generating more content

1. Keep the existing frontmatter shape.
2. Keep stable section headings by page type.
3. Prefer adding or enriching notes over disruptive rewrites unless the user asks.
4. Re-export JSON after vault content changes.

### When updating the frontend

1. Keep HTTP serving; do not rely on local file loading.
2. Verify graph exploration still loads.
3. Verify side-panel preview still works.
4. Verify full-page reader mode still renders equations and internal links correctly.

### When touching exports

If frontmatter fields change, update both:

- `obsidian-knowledge-map-demo/scripts/export_graph.py`
- the generation or enrichment scripts that populate those fields

## Quick Commands

Start prototype:

```bash
cd C:/Users/brian/Downloads/vibe_coding/knowledge_map
python -m http.server 4173
# Open http://127.0.0.1:4173/prototype/
```

Export + validate:

```bash
cd C:/Users/brian/Downloads/vibe_coding/knowledge_map
python tools/run_exports.py
```

## Reusable Template

A reusable knowledge-base template has been extracted to `knowledge-base-template/`.
See its README for how to build knowledge bases on other topics using the same architecture.

## Final Warning

This project works because the note structure is disciplined.
If a future agent ignores the schema and starts free-writing notes, export quality and graph quality will degrade quickly.
