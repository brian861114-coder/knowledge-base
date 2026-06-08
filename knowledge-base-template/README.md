# Knowledge Base Template v2

This directory is a reusable starter kit for building vault-backed knowledge bases with a schema-first workflow.

It is not a populated project. It is the generic architecture extracted from the parent repository after the physics vault was migrated to:

- strict section schema compliance
- structure validation
- content-quality auditing
- schema-first note creation
- section-level AI repair workflows

## What Is Included

- `schema/`
  - active template schema
  - note types
  - domains
  - section rules
  - rename rules
  - content-audit rules
- `tools/`
  - export tools
  - full validator
  - structure validator
  - content-quality auditor
  - section normalizer
  - schema-first note skeleton generator
- `prototype/`
  - lightweight graph and reading frontend
- `docs/`
  - operator workflow and customization guides
- `llm_configs/`, `task_templates/`, `prompts/`
  - generic section-repair workflow assets for weaker or stronger models

## Source Of Truth Rule

For any project created from this template:

- the external Markdown vault is the source of truth
- exported JSON is derived output
- the frontend is only a viewer

Do not treat `graph.json` or `note_details.json` as the database.

## Template v2 Upgrades

Compared with the old template, this version adds the reusable concepts that proved necessary in the parent project:

1. Schema-first note creation
2. Separate structure and content validation layers
3. Rename-rule driven migration support
4. Section normalization tooling
5. Section-level AI repair workflow scaffolding
6. Definition-of-done discipline around export and validation

## Core Workflow

1. Define or adapt the schema under `schema/`
2. Point the template at a real vault
3. Generate new notes from the schema skeleton, not blank files
4. Run structure validation
5. Run content-quality audit
6. Run export and full validation
7. Publish or inspect the frontend

## Main Commands

Generate a new schema-first note skeleton:

```powershell
python .\tools\generate_note_skeleton.py --type concept --title "New Topic" --summary "One-line summary" --domain "core"
```

Run structure validation:

```powershell
python .\tools\validate_structure.py --vault C:\path\to\vault
```

Run content-quality audit:

```powershell
python .\tools\audit_content_quality.py --vault C:\path\to\vault
```

Run export plus full validation:

```powershell
python .\tools\run_exports.py --vault C:\path\to\vault --out-dir .\docs
```

Run full vault/export validation directly:

```powershell
python .\tools\validate.py --vault C:\path\to\vault --graph .\docs\graph.json --details .\docs\note_details.json
```

## Schema Notes

The template uses `.yaml` filenames, but the shipped files are JSON-syntax payloads for deterministic loading.

That is deliberate.

- `tools/validate_structure.py`
- `tools/audit_content_quality.py`
- `tools/generate_note_skeleton.py`
- `tools/normalize_sections.py`

all currently read them with `json.loads`.

If you convert these files to real YAML, update every loader first.

## Generic Concepts Worth Reusing

This template deliberately preserves the following reusable patterns from the parent project:

- schema-first contract
- source-of-truth boundary
- dual validator layers
- migration via rename rules
- section-only AI repair tasks
- blocked-task handling
- weak-model / strong-model routing
- post-repair revalidation

These are template-level patterns.

The topic-specific repair scripts from the parent project are intentionally not copied here.

## Files To Read First

- [agent.md](/C:/Users/brian/Downloads/vibe_coding/knowledge_map/knowledge-base-template/agent.md)
- [docs/SCHEMA_FIRST_WORKFLOW.md](/C:/Users/brian/Downloads/vibe_coding/knowledge_map/knowledge-base-template/docs/SCHEMA_FIRST_WORKFLOW.md)
- [docs/LLM_REPAIR_WORKFLOW.md](/C:/Users/brian/Downloads/vibe_coding/knowledge_map/knowledge-base-template/docs/LLM_REPAIR_WORKFLOW.md)
- [docs/NEW_TOPIC_GUIDE.md](/C:/Users/brian/Downloads/vibe_coding/knowledge_map/knowledge-base-template/docs/NEW_TOPIC_GUIDE.md)

## One-Line Summary

This template is a schema-first, vault-backed knowledge-base starter kit with export, structure validation, content auditing, and section-level AI repair scaffolding.
