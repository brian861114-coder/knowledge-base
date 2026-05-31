---
name: obsidian-knowledge-map-demo
description: Use this skill when the user wants to build an AI-friendly Obsidian knowledge base, especially a structured physics encyclopedia with fixed page types, explicit note relations, and frontend-ready knowledge map exports.
---

# Obsidian Knowledge Map Demo

This skill treats an Obsidian vault as a semi-structured knowledge base for both AI authoring and frontend rendering.

This demo is now specialized for a university-level general physics encyclopedia, but the workflow still applies to other structured domains.

Use this skill when the task is one of:

- Create a new Obsidian note from a fixed note type template
- Rewrite a messy note into a normalized structure
- Enrich notes with summary, relations, or parent topics
- Export a vault into JSON for a knowledge map frontend
- Build or maintain a physics knowledge graph with encyclopedia-style pages

## Workflow

1. Identify the task mode: `author`, `normalize`, `enrich`, or `export`.
2. Identify the page type: `law`, `concept`, `quantity`, `experiment`, `mathematical_tool`, or `map`.
3. Read [references/page_types.md](references/page_types.md) and [references/frontmatter_schema.md](references/frontmatter_schema.md) before creating or rewriting content.
4. If the task is physics-specific, also read [references/physics_structure.md](references/physics_structure.md).
5. For note authoring, copy the matching template from [assets/templates](assets/templates).
6. For JSON export, run `scripts/export_graph.py` against the target vault path.

## Task Modes

### `author`

- Create a new page from the correct template
- Fill frontmatter first
- Keep the fixed section order
- Use explicit `[[wikilinks]]` for prerequisites, related concepts, derived results, and experiments

### `normalize`

- Convert a messy note into one canonical page type
- Preserve valid content, but move it into the defined sections
- If content belongs to another page type, split it instead of cramming everything into one page

### `enrich`

- Add missing summary, relations, or prerequisite links
- Improve weak sections such as `物理直觀` or `常見誤解`
- Do not invent historical facts, experimental claims, or citations

### `export`

- Parse note metadata and wiki links
- Build node and edge payloads for the frontend
- Preserve page type and relation semantics whenever possible

## Guardrails

- Prefer deterministic parsing for paths, frontmatter, wiki links, and headings.
- Do not invent sources. If a source is missing, leave an explicit placeholder.
- Keep one note focused on one core idea unless the user explicitly wants a map page.
- Preserve existing wiki links when they are valid.
- If the vault already has a schema, adapt to it instead of forcing this demo schema blindly.
- For physics pages, separate `law`, `concept`, and `quantity` instead of mixing them casually.
- Treat `適用條件`, `常見誤解`, and `現代理論視角` as first-class sections, not optional filler.

## Files To Read On Demand

- [references/page_types.md](references/page_types.md): page responsibilities and when to use each type
- [references/frontmatter_schema.md](references/frontmatter_schema.md): required metadata fields
- [references/relation_types.md](references/relation_types.md): allowed note relations and intended meaning
- [references/physics_structure.md](references/physics_structure.md): domain structure for a general physics encyclopedia
- [references/frontend_schema.md](references/frontend_schema.md): output JSON shape for frontend use
- [assets/templates/law.md](assets/templates/law.md): law page template
- [assets/templates/concept.md](assets/templates/concept.md): concept note template
- [assets/templates/quantity.md](assets/templates/quantity.md): quantity page template
- [assets/templates/experiment.md](assets/templates/experiment.md): experiment page template
- [assets/templates/mathematical_tool.md](assets/templates/mathematical_tool.md): mathematical tool template
- [assets/templates/map.md](assets/templates/map.md): map note template
- [scripts/create_note.py](scripts/create_note.py): create a page from a named template
- [scripts/export_graph.py](scripts/export_graph.py): export vault graph JSON

## Physics Authoring Rules

- `law` pages are encyclopedia hubs, not random lecture notes.
- `concept` pages define ideas such as force, field, energy, and entropy.
- `quantity` pages define measurable quantities such as mass, acceleration, charge, and pressure.
- `experiment` pages link theory to evidence.
- `mathematical_tool` pages provide reusable formal support for physics pages.
- `map` pages organize learning order and cluster navigation.

## Create Example

```text
python scripts/create_note.py --type law --title "牛頓第二定律" --out "C:\path\to\vault\laws\newton_second_law.md"
```

## Export Example

```text
python scripts/export_graph.py --vault "C:\path\to\vault" --out "C:\path\to\graph.json"
```
