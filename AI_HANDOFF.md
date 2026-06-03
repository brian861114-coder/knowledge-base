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

The project already has:

- A structured physics encyclopedia schema
- Seed, second-batch, and third-batch generation scripts
- Enrichment scripts for concept pages and remaining page types
- Exported graph JSON and note detail JSON
- A working frontend prototype with reader mode and math rendering

The frontend currently reads:

- `physics_graph.json`
- `physics_note_details.json`

Export ids now preserve canonical mixed-case note names such as:

- `RC電路`
- `RL電路`
- `RLC電路`

Do not assume exported ids are always lowercase slugs anymore.

## Current Page Types

- `map`
- `law`
- `concept`
- `quantity`
- `experiment`
- `mathematical_tool`

Treat these as stable unless the user explicitly wants schema changes.

## Current Frontend Behavior

Key prototype behaviors already implemented:

- Graph exploration
- Side-panel note preview
- Full-page reader mode
- Section table of contents with jump navigation
- Clickable internal note links
- MathJax support for `$...$` and `$$...$$`

Do not regress these accidentally.

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

If id-generation rules change, update all three:

- `tools/export_note_details.py`
- `obsidian-knowledge-map-demo/scripts/export_graph.py`
- `tools/validate_knowledge_base.py`

The current strategy is:

- exported ids keep the original note stem casing
- relation and wikilink resolution still normalize targets for tolerant matching
- the frontend has a small compatibility fallback while old and new exports coexist

## Recommended Next Step

The highest-value next step is still content depth and reverse-link density, not ornamental UI work:

1. Increase coverage in underdeveloped physics areas.
2. Add more worked examples and derivations.
3. Add targeted reverse links from older core pages into the newer bridge pages.
4. Add stronger validation for broken links and malformed math.

## Quick Commands

Start prototype:

```powershell
.\start_prototype.cmd
```

Export graph:

```powershell
& 'C:\Users\brian\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  '.\obsidian-knowledge-map-demo\scripts\export_graph.py' `
  --vault 'C:\Users\brian\Downloads\Obsidian Vault備份\obsidian\Project\knowledge database' `
  --out '.\physics_graph.json'
```

Export note details:

```powershell
& 'C:\Users\brian\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  '.\tools\export_note_details.py' `
  --vault 'C:\Users\brian\Downloads\Obsidian Vault備份\obsidian\Project\knowledge database' `
  --out '.\physics_note_details.json'
```

Generate second batch again:

```powershell
& 'C:\Users\brian\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  '.\tools\generate_physics_second_batch.py' `
  --vault 'C:\Users\brian\Downloads\Obsidian Vault備份\obsidian\Project\knowledge database'
```

Generate third batch again:

```powershell
& 'C:\Users\brian\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  '.\tools\generate_physics_third_batch.py' `
  --vault 'C:\Users\brian\Downloads\Obsidian Vault備份\obsidian\Project\knowledge database'
```

## Final Warning

This project works because the note structure is disciplined.

If a future agent ignores the schema and starts free-writing notes, export quality and graph quality will degrade quickly.
