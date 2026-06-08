# Content Workflow

This template assumes a schema-first content workflow.

## The Correct Order

1. Decide the note type
2. Generate a skeleton from schema
3. Fill only the defined sections
4. Run structure validation
5. Run content-quality audit
6. Run export and full validation

## Do Not Start From Blank Files

Use:

```powershell
python .\tools\generate_note_skeleton.py --type concept --title "New Topic" --summary "One-line summary" --domain "core"
```

This prevents heading drift from the beginning.

## Why This Matters

If you let content grow from arbitrary blank Markdown files:

- headings drift
- section order drifts
- required sections disappear
- AI fills pages with filler instead of structure

That is exactly the failure mode this template is designed to avoid.

## Content Audit Role

The content audit is not a truth engine.

It cannot guarantee excellent prose.

What it can do is catch predictable failure modes:

- filler phrases
- shallow meaning sections
- empty derivations
- vague history blocks
- ungrouped related links

That is enough to keep the baseline from collapsing.
