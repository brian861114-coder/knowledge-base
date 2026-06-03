# Physics Database Build Manifest

This document records the expected environment and scope for rebuilding the exported physics knowledge-base dataset.

## Paths On This Machine

Obsidian vault content:

`C:\Users\brian\Downloads\Obsidian Vault備份\obsidian\Project\knowledge database`

Repo workspace:

`C:\Users\brian\Downloads\vibe_coding\knowledge_map`

Vault root:

`C:\Users\brian\Downloads\Obsidian Vault備份\obsidian`

## Expected Vault Structure

```text
knowledge database/
  00_maps/
  01_laws/
  02_concepts/
  03_quantities/
  04_experiments/
  05_mathematical_tools/
```

The generators and exporters assume this folder structure.

## Build Inputs

Main content source:

- Obsidian Markdown notes in the vault

Main scripts:

- `tools/generate_physics_seed_notes.py`
- `tools/generate_physics_second_batch.py`
- `tools/generate_physics_third_batch.py`
- `tools/enrich_concept_pages.py`
- `tools/enrich_concept_pages_derivations.py`
- `tools/enrich_remaining_pages.py`
- `tools/export_note_details.py`
- `obsidian-knowledge-map-demo/scripts/export_graph.py`

## Build Outputs

- `physics_graph.json`
- `physics_note_details.json`

These are derived artifacts used by the frontend prototype.

## Normal Rebuild Flow

1. Update notes in the vault.
2. Run any required generation or enrichment script.
3. Export `physics_note_details.json`.
4. Export `physics_graph.json` if titles, links, relationships, or note count changed.
5. Start the prototype and verify representative pages.

## Commands

Export note details:

```powershell
& 'C:\Users\brian\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  '.\tools\export_note_details.py' `
  --vault 'C:\Users\brian\Downloads\Obsidian Vault備份\obsidian\Project\knowledge database' `
  --out '.\physics_note_details.json'
```

Export graph:

```powershell
& 'C:\Users\brian\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  '.\obsidian-knowledge-map-demo\scripts\export_graph.py' `
  --vault 'C:\Users\brian\Downloads\Obsidian Vault備份\obsidian\Project\knowledge database' `
  --out '.\physics_graph.json'
```

## Validation Checklist

- Vault path is correct on the current machine.
- Generated notes remain inside the expected page-type folders.
- `physics_note_details.json` reflects latest note content.
- `physics_graph.json` reflects latest relationships and wikilinks.
- Prototype loads over HTTP and renders math correctly.
