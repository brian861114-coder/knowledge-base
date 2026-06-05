# Materials Science and Engineering Knowledge Base

This folder is a specialized starter knowledge base for materials science and engineering.

It is built for an Obsidian-style Markdown vault plus export scripts that generate:

- `graph.json` for graph navigation
- `note_details.json` for reader mode

## Folder Layout

```text
materials-science-engineering-kb/
  vault/
    00_maps/
    01_principles/
    02_concepts/
    03_properties/
    04_processes/
    05_characterization/
    06_failures/
    07_applications/
  schema/
  tools/
  prototype/
  docs/
```

## What This Starter Includes

- Domain schema for materials science and engineering
- Reframed note types for principles, concepts, properties, processes, and characterization
- Seed map pages that organize the field
- Seed notes covering structure, processing, properties, characterization, failures, and applications

## Domain Model

Taxonomy domains:

- `fundamentals`
- `material_classes`
- `structure`
- `properties`
- `processing`
- `characterization`
- `failure`
- `applications`

Operational domains:

- `Foundations`
- `Material Classes`
- `Structure and Defects`
- `Properties`
- `Processing`
- `Characterization`
- `Failure Analysis`
- `Applications`

## Note Type Model

- `map`: navigation and curriculum pages
- `law`: foundational mechanisms and governing principles
- `concept`: entities, classes, and interpretive concepts
- `quantity`: property-oriented notes
- `experiment`: processes, manufacturing routes, and test workflows
- `mathematical_tool`: characterization and analysis methods

The type IDs stay compatible with the existing exporter and frontend, but the labels and folders are specialized for materials science.

## Quick Start

1. Point the local config at the included seed vault or your own vault.
2. Run exports.
3. Open the prototype.

Example:

```bash
python tools/run_exports.py --vault ./vault --out-dir ./prototype
python -m http.server 4173
```

Then open `http://127.0.0.1:4173/prototype/`.

## Local Config

Copy `.knowledge-base.local.example.json` to `.knowledge-base.local.json` and set:

- `vault_path`
- `python_path` if needed
- `out_dir` if you want exports somewhere other than the repo root

## Recommended Build Order

1. Expand the map pages first.
2. Add missing bridge notes between structure, processing, and properties.
3. Deepen characterization notes so they connect directly to target microstructures and failure modes.
4. Add domain-specific application clusters such as batteries, semiconductors, or biomaterials.

## Seed Vault Coverage

The starter vault already includes:

- core maps
- atomic bonding, diffusion, phase diagrams, and transformation kinetics
- crystal structure, crystal defects, microstructure, major material classes
- mechanical, electrical, and thermal properties
- heat treatment, sintering, thin film deposition, additive manufacturing
- XRD, SEM, TEM, and EBSD
- corrosion, fracture mechanisms, battery materials, biomaterials, and semiconductor materials

## Next Good Expansions

- creep
- fatigue
- polymers processing
- composite toughening
- corrosion testing
- electrochemistry for batteries
- magnetic materials
- dielectric and ferroelectric materials
- high-entropy alloys
- computational materials science
