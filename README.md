# knowledge-base

Interactive physics knowledge-map prototype backed by an Obsidian vault.

This repo contains four things:

1. The project-level schema and planning docs for a university general physics encyclopedia.
2. A demo `agent skill` for generating and exporting structured Obsidian notes.
3. A browser prototype that renders the exported graph and note previews.
4. Python scripts that generate seed notes / second-batch notes and export frontend JSON.

## Current Scope

The current encyclopedia scope is centered on:

- Mathematical tools
- Mechanics
- Vibrations and waves
- Thermodynamics
- Electromagnetism
- Optics
- Modern physics
- Fluid mechanics

The first and second note batches have already been generated into the Obsidian vault used by this project.

## Repo Layout

```text
knowledge_map/
  prototype/                      Frontend prototype
  tools/                          Note generation and export scripts
  obsidian-knowledge-map-demo/    Demo agent skill
  physics_encyclopedia_schema.md  Core encyclopedia schema
  physics_database_build_manifest.md
  physics_second_batch_manifest.md
  physics_graph.json              Exported graph for frontend
  physics_note_details.json       Exported note previews for frontend
  新增 Microsoft PowerPoint 簡報.pdf
  新增 Microsoft PowerPoint 簡報.pptx
```

## Main Data Flow

```text
Obsidian vault markdown
  -> generation scripts
  -> structured notes with frontmatter + sections
  -> graph export JSON / detail export JSON
  -> prototype frontend
```

## Important Paths

Project workspace:

`C:\Users\brian\Downloads\vibe_coding\knowledge_map`

Obsidian content vault target:

`C:\Users\brian\Downloads\Obsidian Vault備份\obsidian\Project\knowledge database`

Only the actual Obsidian note pages live in the vault path. Tools, docs, frontend, and exports live in this repo.

## Key Files

- [physics_encyclopedia_schema.md](C:/Users/brian/Downloads/vibe_coding/knowledge_map/physics_encyclopedia_schema.md)
- [physics_database_build_manifest.md](C:/Users/brian/Downloads/vibe_coding/knowledge_map/physics_database_build_manifest.md)
- [physics_second_batch_manifest.md](C:/Users/brian/Downloads/vibe_coding/knowledge_map/physics_second_batch_manifest.md)
- [PROJECT_ARCHITECTURE.md](C:/Users/brian/Downloads/vibe_coding/knowledge_map/PROJECT_ARCHITECTURE.md)
- [AI_HANDOFF.md](C:/Users/brian/Downloads/vibe_coding/knowledge_map/AI_HANDOFF.md)

## Running the Prototype

Start the local server with:

```powershell
.\start_prototype.cmd
```

Then open:

[http://127.0.0.1:4173/prototype/](http://127.0.0.1:4173/prototype/)

Do not open `prototype/index.html` directly with `file://`; the frontend expects HTTP so it can fetch JSON.

## Regenerating Exports

Re-export graph JSON:

```powershell
& 'C:\Users\brian\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  '.\obsidian-knowledge-map-demo\scripts\export_graph.py' `
  --vault 'C:\Users\brian\Downloads\Obsidian Vault備份\obsidian\Project\knowledge database' `
  --out '.\physics_graph.json'
```

Re-export note detail JSON:

```powershell
& 'C:\Users\brian\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  '.\tools\export_note_details.py' `
  --vault 'C:\Users\brian\Downloads\Obsidian Vault備份\obsidian\Project\knowledge database' `
  --out '.\physics_note_details.json'
```

## Generating More Notes

First batch:

```powershell
& 'C:\Users\brian\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  '.\tools\generate_physics_seed_notes.py' `
  --vault 'C:\Users\brian\Downloads\Obsidian Vault備份\obsidian\Project\knowledge database'
```

Second batch:

```powershell
& 'C:\Users\brian\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  '.\tools\generate_physics_second_batch.py' `
  --vault 'C:\Users\brian\Downloads\Obsidian Vault備份\obsidian\Project\knowledge database'
```

## Next Recommended Work

1. Generate the third batch of physics notes, especially `萬有引力定律`, `位能`, `保守力`, `等位面`, `平行板電容器`, `簡諧運動`.
2. Keep treating the Obsidian vault as the source of truth.
3. Use the exported JSON only as frontend build artifacts.
4. Resist over-investing in frontend polish before the note graph is denser.

