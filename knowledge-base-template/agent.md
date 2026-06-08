# knowledge-base-template Agent Guide

This file is for future agents working in `C:\Users\brian\Downloads\vibe_coding\knowledge_map\knowledge-base-template`.

This directory is a starter architecture, not a live knowledge base.

## 1. What This Template Is

This template packages the reusable methods extracted from the parent project:

1. schema-first note modeling
2. export pipeline
3. structure validation
4. content-quality auditing
5. note-section normalization
6. schema-first note skeleton generation
7. section-level AI repair scaffolding

It does not include:

- a populated vault
- validated live counts
- project-specific content
- project-specific repair scripts

If you treat this directory as if it were a complete knowledge base, you are using it incorrectly.

## 2. Source-Of-Truth Boundary

For any derived project:

- the target Markdown vault is the source of truth
- `graph.json` and `note_details.json` are derived artifacts
- the frontend is a reader, not an authoring system

Never patch exported JSON as the canonical content fix.

## 3. Important Directories

- `schema/`
  - note types
  - domains
  - section rules
  - rename rules
  - content rules
- `tools/`
  - exporters
  - validators
  - skeleton generator
  - normalizer
- `prototype/`
  - generic graph-reading frontend
- `docs/`
  - operator workflow
  - new-topic guide
  - frontend customization notes
- `llm_configs/`
  - issue routing and repair profiles
- `task_templates/`
  - JSON task contract examples
- `prompts/`
  - system/task prompt baselines for section-level repair

## 4. Main Entrypoints

### Generate a new note from schema

```powershell
python .\tools\generate_note_skeleton.py --type concept --title "New Topic" --summary "One-line summary" --domain "core"
```

### Normalize legacy headings and section order

```powershell
python .\tools\normalize_sections.py --vault C:\path\to\vault
```

### Validate section structure

```powershell
python .\tools\validate_structure.py --vault C:\path\to\vault
```

### Audit content quality

```powershell
python .\tools\audit_content_quality.py --vault C:\path\to\vault
```

### Export plus validate

```powershell
python .\tools\run_exports.py --vault C:\path\to\vault --out-dir .\docs
```

### Full validator only

```powershell
python .\tools\validate.py --vault C:\path\to\vault --graph .\docs\graph.json --details .\docs\note_details.json
```

## 5. Current Template Contract

The template is schema-first.

That means:

- note type decides section structure
- section names come from schema, not from the model
- required vs optional sections are contract rules
- rename rules are the migration path
- content rules describe what quality checks should enforce

Do not let a model invent headings, reshuffle sections, or decide that required sections are optional.

## 6. Schema Files

Primary schema files:

- `schema/note_types.yaml`
- `schema/domains.yaml`
- `schema/sections.yaml`
- `schema/renaming_rules.yaml`
- `schema/content_rules.yaml`

Important implementation detail:

- these files use JSON syntax inside `.yaml` files
- validators and generators currently load them with `json.loads`

Do not silently convert them unless you update all loaders.

## 7. Validator Layers

The template now has two separate validator layers.

### Structure validator

`tools/validate_structure.py`

Checks:

- missing required sections
- required section order
- conditional section requirements
- optional section placement rules
- legacy heading hits from rename rules

### Content-quality auditor

`tools/audit_content_quality.py`

Checks:

- banned filler phrases
- too-short meaning sections
- too-short derivations
- history sections with no concrete anchor
- formulas with missing symbol sections
- related-links sections that contain links but no groups

### Full export validator

`tools/validate.py`

Checks:

- required frontmatter
- broken wikilinks
- broken frontmatter relation targets
- duplicate titles and paths
- basic math delimiter health
- export consistency

## 8. Recommended Workflow

When creating or modifying a derived project:

1. Adapt the schema first
2. Point the template at a real vault
3. Generate new notes from skeletons, not blank files
4. Fill content only inside schema-defined sections
5. Run structure validation
6. Run content-quality audit
7. Run export and full validation
8. Publish only after the validators are green

## 9. LLM Workflow

This template includes a generic section-repair workflow.

The intended pattern is:

1. validator or audit finds a specific issue
2. build a section-level task JSON
3. model returns only the target section payload
4. a local tool applies the payload back into the note
5. validators rerun

Do not use a weak model as an unrestricted whole-note editor.

## 10. Common Failure Modes

1. Treating the template as if it already has a real vault
2. Patching exported JSON instead of the vault
3. Letting AI improvise note structure
4. Hardcoding domain-specific logic into generic scripts
5. Skipping revalidation after repair

## 11. One-Line Summary

This directory is a reusable schema-first starter kit; keep it generic, keep the vault as source of truth, and keep every repair inside a validation loop.
