# materials-science-engineering-kb Agent Guide

This file is for future agents working in `C:\Users\brian\Downloads\vibe_coding\knowledge_map\materials-science-engineering-kb`.

This subproject is a real, usable knowledge base, not just a template. It has its own vault, toolchain, prototype, docs output, and deployment flow.

## 1. What this subproject is

This is a materials science and engineering knowledge base built on the same general architecture as the parent physics project, but with one major difference:

- this subproject includes an in-repo `vault/`

That means content, export scripts, frontend, and deploy artifacts all live under this subproject directory. You do not need to rely on an external vault just to inspect or validate the baseline state.

## 2. Core structure

Important directories:

- `vault/`
  - Source of truth for this subproject.
  - Markdown notes are organized by domain folders:
    - `00_maps/`
    - `01_principles/`
    - `02_concepts/`
    - `03_properties/`
    - `04_processes/`
    - `05_characterization/`
    - `06_failures/`
    - `07_applications/`
- `schema/`
  - YAML schema defining note types, domains, and required section structure.
- `tools/`
  - Export, validation, config, translation, and snapshot scripts.
- `prototype/`
  - Local frontend source plus current exported JSON artifacts.
- `docs/`
  - Documentation guides for using and extending this subproject.
- `scripts/`
  - Deployment helper script.
- `standalone_html_app/`
  - Alternate static-app packaging layer.

## 3. Source-of-truth boundary

For this subproject:

- `vault/` is the source of truth
- `prototype/graph.json`, `prototype/note_details.json`, `prototype/graph_en.json`, and `prototype/note_details_en.json` are derived artifacts

If note content is wrong, fix `vault/`.
If export output is wrong, inspect `tools/`.
If rendering is wrong, inspect `prototype/`.

Do not patch exported JSON directly unless you are debugging the exporter.

## 4. Main entrypoints

### Export and validate

Primary operator entrypoint:

- `tools/run_exports.py`

It runs:

1. `tools/export_note_details.py`
2. `tools/export_graph.py`
3. `tools/export_english_snapshot.py`
4. `tools/validate.py` unless `--skip-validate` is passed

Key behavior:

- accepts `--vault`
- accepts `--out-dir`
- defaults output to the repo root if `--out-dir` is omitted

Typical useful command inside this folder:

```powershell
python .\tools\run_exports.py --vault .\vault --out-dir .\prototype
```

### Validate only

```powershell
python .\tools\validate.py --vault .\vault --graph .\prototype\graph.json --details .\prototype\note_details.json
```

### Deploy

- `scripts/deploy.sh`

Important warning:

- this script uses `git add -A`

That is dangerous in a dirty tree. If you only want to commit a narrow change, do not blindly run this script without first understanding the current working tree.

## 5. Tooling layout

Important scripts under `tools/`:

- `kb_config.py`
  - central config and schema loading
  - resolves vault path from CLI, env var, or local config
- `export_graph.py`
  - exports node/edge graph JSON
- `export_note_details.py`
  - exports note detail JSON for reader mode
- `validate.py`
  - validates vault structure and exported JSON consistency
- `export_english_snapshot.py`
  - generates English snapshot artifacts
- `fix_zh_translation.py`
  - translation/cleanup utility for Chinese content

This means the subproject is bilingual-aware in a way the generic template is not.

## 6. Config model

Example local config file:

- `.knowledge-base.local.example.json`

Relevant fields:

- `vault_path`
- `python_path`
- `out_dir`

The example points at:

- `vault_path: "./vault"`
- `out_dir: "./prototype"`

That is the intended default local workflow for this subproject.

## 7. Export outputs

Current prototype directory includes:

- `app.js`
- `index.html`
- `styles.css`
- `graph.json`
- `note_details.json`
- `graph_en.json`
- `note_details_en.json`

The `_en` files are not accidental. They are part of the English snapshot workflow and should not be deleted casually.

## 8. Schema model

This subproject uses schema-driven configuration from `schema/`:

- `note_types.yaml`
  - type IDs, labels, folders, colors
- `domains.yaml`
  - taxonomy domains and operational domains
- `sections.yaml`
  - required and optional section layouts by note type

This is the structural backbone of the project. If you change folder conventions, note types, or frontmatter semantics, you need to confirm the exporter, validator, and frontend still agree.

## 9. Verified state from this session

The subproject was directly validated in this session with:

```powershell
& 'C:\Users\brian\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\tools\validate.py --vault .\vault --graph .\prototype\graph.json --details .\prototype\note_details.json
```

Observed result:

- validation passed
- notes: `151`
- note details: `151`
- graph nodes: `151`
- graph edges: `1658`
- broken wikilinks: `0`
- broken frontmatter relations: `0`
- math issues: `0`
- duplicate titles: `0`

This is much more trustworthy than any stale README claim because it was checked live.

## 10. Current working tree risk

At the time this file was created, this subproject had many uncommitted changes in:

- `vault/*`
- `prototype/graph.json`
- `prototype/note_details.json`

There was also one untracked file:

- `vault/05_characterization/Dynamic Mechanical Analysis.md`

Implication:

- do not assume the subproject is clean
- do not use broad staging unless the user explicitly wants everything staged

## 11. Recommended agent workflow

If the task is content work:

1. edit notes in `vault/`
2. run `tools/run_exports.py --vault .\vault --out-dir .\prototype`
3. rerun validation if needed
4. inspect `git status --short` before staging

If the task is frontend work:

1. inspect `prototype/app.js` first
2. confirm whether JSON outputs need regeneration
3. keep `_en` export artifacts in mind

If the task is schema work:

1. update YAML in `schema/`
2. inspect `kb_config.py`, `export_*`, and `validate.py` expectations
3. verify the vault and exports still match the new schema

## 12. Common failure modes

1. Treating `prototype/*.json` as editable source content.
   - Wrong. `vault/` is the source of truth.
2. Ignoring `_en` artifacts.
   - Wrong. English snapshot export is part of the workflow.
3. Running `scripts/deploy.sh` in a dirty tree without checking what will be staged.
   - Wrong. It uses `git add -A`.
4. Assuming this subproject is just a demo folder.
   - Wrong. It is a real, validated knowledge base with active content changes.

## 13. One-line summary

This subproject is a self-contained materials science knowledge base with an in-repo vault, schema-driven export pipeline, bilingual snapshot outputs, and a dirty-tree deployment risk because the deploy script stages everything.
