# AI Handoff

This file is for the next AI agent that takes over the project.

## What This Project Is

This workspace builds a physics knowledge-base system around an Obsidian vault.

There are two distinct locations:

- Workspace repo:
  `C:\Users\brian\Downloads\vibe_coding\knowledge database`
- Obsidian vault output:
  `C:\Users\brian\OneDrive\文件\Obsidian Vault\Project\knowledge database`

Do not confuse them.

- Code, docs, prototype, exports, and skill files stay in the repo.
- Generated Obsidian markdown pages go to the vault path.

## Current State

The project already has:

- A structured physics encyclopedia schema
- A demo agent skill for Obsidian generation/export
- A working frontend prototype
- First batch and second batch note generation scripts
- Exported graph JSON and note detail JSON

The frontend prototype currently reads:

- `physics_graph.json`
- `physics_note_details.json`

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

- Domain overview
- Domain focus mode
- Ring-based focused layout
- Node collision avoidance
- Zoom and pan
- Back-to-overview control
- Scrollable right-hand detail panel
- Obsidian note preview in the detail panel
- Section table of contents with jump navigation

Do not accidentally regress these.

## Current Note Batches

### First batch

- 8 map pages
- Initial mechanics, math, thermodynamics, electromagnetism, optics, and fluid entries

### Second batch

Focused on:

- Mechanics
- Mathematical tools
- Electromagnetism

Added items such as:

- `牛頓第一定律`
- `牛頓第三定律`
- `機械能守恆`
- `自由體圖`
- `重力`
- `摩擦力`
- `速度`
- `高斯定律`
- `電位`
- `電通量`
- `內積`
- `外積`
- `偏導數`
- `梯度`

## How To Continue Safely

### When generating more content

1. Keep the existing frontmatter shape.
2. Keep fixed section headings by page type.
3. Prefer adding new notes over rewriting working notes unless the user asks.
4. Update related `map` pages when a new cluster becomes important.

### When updating the frontend

1. Refresh JSON exports after vault content changes.
2. Keep HTTP serving; do not rely on local file loading.
3. Verify focused-domain views still avoid overlap.
4. Verify the right-hand panel still renders note previews and jump links.

### When touching exports

The exporter relation mapping is important. If you change frontmatter fields, also update:

- `obsidian-knowledge-map-demo/scripts/export_graph.py`
- any note-generation scripts that populate those fields

## Recommended Next Step

The most valuable next move is not micro-polish on the frontend.

It is to generate the third batch of notes:

- 力學: `萬有引力定律`, `位能`, `保守力`
- 電磁學: `等位面`, `平行板電容器`, `電場能量`
- 波動: `簡諧運動`, `駐波`, `共振`

That will improve the graph more than another round of UI tweaks.

## Quick Commands

Start prototype:

```powershell
.\start_prototype.cmd
```

Export graph:

```powershell
& 'C:\Users\brian\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  '.\obsidian-knowledge-map-demo\scripts\export_graph.py' `
  --vault 'C:\Users\brian\OneDrive\文件\Obsidian Vault\Project\knowledge database' `
  --out '.\physics_graph.json'
```

Export detail previews:

```powershell
& 'C:\Users\brian\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  '.\tools\export_note_details.py' `
  --vault 'C:\Users\brian\OneDrive\文件\Obsidian Vault\Project\knowledge database' `
  --out '.\physics_note_details.json'
```

Generate second batch again:

```powershell
& 'C:\Users\brian\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  '.\tools\generate_physics_second_batch.py' `
  --vault 'C:\Users\brian\OneDrive\文件\Obsidian Vault\Project\knowledge database'
```

## Final Warning

This project only works cleanly because the structure is currently disciplined.

If a future agent starts free-writing notes without respecting the schema, the graph quality will collapse fast.

