# knowledge-base-template Agent Guide

This file is for future agents working in `C:\Users\brian\Downloads\vibe_coding\knowledge_map\knowledge-base-template`.

This directory is not a finished knowledge base. It is a reusable starter architecture for building new knowledge-base projects.

## 1. What this template is

This template packages the general system used by the parent project into a reusable skeleton:

1. schema-driven note model
2. export scripts
3. validation scripts
4. lightweight frontend prototype
5. GitHub Pages deployment helper

Important difference from a real project:

- this template does not include a real vault with live content

That means you should treat it as scaffolding. Validation and export behavior are meaningful, but only after the user or another agent points it at a real vault or creates one.

## 2. Core structure

Important directories:

- `schema/`
  - YAML definitions for note types, domains, and section requirements.
- `tools/`
  - Generic exporter, validator, config, and orchestration scripts.
- `prototype/`
  - Frontend source.
  - Unlike the materials-science subproject, this folder does not ship with populated `graph.json` and `note_details.json`.
- `docs/`
  - Guidance docs for using the template:
    - `NEW_TOPIC_GUIDE.md`
    - `CONTENT_WORKFLOW.md`
    - `FRONTEND_CUSTOMIZATION.md`
- `scripts/`
  - Deployment helper.
- `standalone_html_app/`
  - Alternate static packaging layer.

There is no in-repo `vault/` here by default.

## 3. Source-of-truth boundary

For any project created from this template:

- the target Obsidian vault is the source of truth
- exported `graph.json` and `note_details.json` are derived artifacts
- the frontend is a viewer, not the authoring system

If someone starts editing exported JSON directly as if it were the database, they are misusing the template.

## 4. Main entrypoints

### Export and validate

Primary operator entrypoint:

- `tools/run_exports.py`

It runs:

1. `tools/export_note_details.py`
2. `tools/export_graph.py`
3. `tools/validate.py` unless `--skip-validate` is passed

Supported flags:

- `--vault`
- `--out-dir`
- `--skip-validate`

Typical example:

```powershell
python .\tools\run_exports.py --vault C:\path\to\your\vault --out-dir .\docs
```

### Validate only

```powershell
python .\tools\validate.py --vault C:\path\to\your\vault --graph .\docs\graph.json --details .\docs\note_details.json
```

### Deploy

- `scripts/deploy.sh`

Important warning:

- this script uses `git add -A`

That is acceptable only if you deliberately want all current changes. In a real derived project, narrow staging is usually safer.

## 5. Config model

Config resolution is handled in `tools/kb_config.py`.

Vault resolution order:

1. CLI `--vault`
2. `KB_VAULT_PATH`
3. `.knowledge-base.local.json`

The example config file is:

- `.knowledge-base.local.example.json`

Relevant fields:

- `vault_path`
- `python_path`
- `out_dir`

The example file is only a placeholder. It is not proof that any local vault exists.

## 6. Schema model

This template is schema-first.

Important files:

- `schema/note_types.yaml`
  - type IDs, labels, folders, colors
- `schema/domains.yaml`
  - taxonomy domains plus display domains
- `schema/sections.yaml`
  - required and optional sections by note type

The template's main value is that these files let a new topic area be reshaped without rewriting the whole stack from scratch.

If you change schema semantics, inspect all of these together:

- `tools/kb_config.py`
- `tools/export_graph.py`
- `tools/export_note_details.py`
- `tools/validate.py`
- `prototype/app.js`

## 7. Tooling layout

Important scripts under `tools/`:

- `kb_config.py`
  - schema loading
  - vault path resolution
  - common parsing helpers
- `export_graph.py`
  - exports nodes and edges
- `export_note_details.py`
  - exports note detail payload
- `validate.py`
  - validates vault structure and export consistency
- `run_exports.py`
  - orchestration wrapper

The entire template assumes the project remains structured and schema-compatible. If note format degenerates into free-form Markdown with no stable frontmatter discipline, the template loses most of its value.

## 8. Frontend role

The frontend under `prototype/` is a thin viewer layer:

- `index.html`
- `app.js`
- `styles.css`

Its job is to consume exported JSON and render:

- graph exploration
- note browsing
- side-panel reading
- reader mode

It is not designed to parse arbitrary raw vault files directly in the browser.

## 9. Documentation role

The `docs/` folder here is not a deployment output folder in the same sense as the parent project's root `docs/`.
Inside this template, `docs/` is mostly instructional content for people adapting the starter kit.

Key files:

- `NEW_TOPIC_GUIDE.md`
  - how to create a new domain-specific knowledge base from this template
- `CONTENT_WORKFLOW.md`
  - content authoring and export workflow
- `FRONTEND_CUSTOMIZATION.md`
  - frontend adjustment guidance

If an agent ignores these and starts reinventing the template structure manually, that is wasted effort.

## 10. What this template is not

It is not:

- a complete knowledge base
- a guarantee that the target vault exists
- proof that current output JSON is valid
- a substitute for project-specific handoff documentation once a derived project becomes real

Once a clone of this template grows into a real project, it should get its own `agent.md`, operational docs, and validated current-state notes.

## 11. Recommended agent workflow

If the task is to start a new knowledge base from this template:

1. define schema in `schema/`
2. prepare or point to a real vault
3. set `.knowledge-base.local.json`
4. run `tools/run_exports.py`
5. inspect frontend output
6. write project-specific docs instead of relying forever on template-level assumptions

If the task is to modify the template itself:

1. preserve genericity
2. avoid baking in topic-specific assumptions unless explicitly requested
3. verify all schema-driven paths still agree
4. treat deploy script broad staging as a documented risk

## 12. Common failure modes

1. Treating the template as if it were already a populated project.
   - Wrong. It is scaffolding.
2. Hardcoding topic-specific logic into the generic scripts without being asked.
   - Wrong. That corrupts the template.
3. Forgetting that frontend expects exported JSON, not raw vault files.
   - Wrong. The architecture is export-first.
4. Using `git add -A` deployment behavior casually in a future derived project.
   - Wrong. That is often too broad.

## 13. One-line summary

This directory is a schema-driven starter kit for building JSON-exported, vault-backed knowledge bases; it is useful only if you preserve the source-of-truth boundary and keep the template generic.
