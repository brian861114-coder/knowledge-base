# New Topic Guide

Use this guide when turning the template into a real project.

## 1. Copy The Template

```powershell
Copy-Item -Recurse .\knowledge-base-template .\my-new-kb
cd .\my-new-kb
```

## 2. Decide The Project Ontology

Before editing content, define:

- note types
- folder structure
- domains
- section order
- rename rules
- content-audit rules

Edit:

- `schema/note_types.yaml`
- `schema/domains.yaml`
- `schema/sections.yaml`
- `schema/renaming_rules.yaml`
- `schema/content_rules.yaml`

## 3. Point The Project At A Real Vault

Create `.knowledge-base.local.json` from the example file and set:

- `vaultPath`
- `pythonPath` if needed
- `outDir` if needed

## 4. Create Or Migrate Notes

New notes:

- generate from skeletons

Legacy notes:

- normalize with rename rules
- validate structure
- patch real gaps

## 5. Validate Before Trusting The Output

```powershell
python .\tools\validate_structure.py --vault C:\path\to\vault
python .\tools\audit_content_quality.py --vault C:\path\to\vault
python .\tools\run_exports.py --vault C:\path\to\vault --out-dir .\docs
```

If you skip this, you are guessing.

## 6. Customize The Frontend Only After The Data Contract Is Stable

Do not start by redesigning the frontend.

First make sure:

- note types are stable
- relation fields are stable
- section schema is stable
- exports are valid

Only then adjust `prototype/`.
