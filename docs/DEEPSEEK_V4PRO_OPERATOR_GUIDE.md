# DeepSeek v4 Pro Operator Guide

This note is for the human or orchestration layer that sends tasks to DeepSeek v4 Pro.

## Purpose

DeepSeek v4 Pro is being used here as a constrained section repair worker, not as an autonomous note author.

Its job is to patch small, explicit content problems.

## Priority order

Send these first:

1. `meaning_too_short`
2. `ungrouped_related_links`
3. `banned_pattern`
4. `history_not_concrete` only with supplied evidence

Do not send these first:

1. `derivation_missing_formula`
2. `derivation_too_short`
3. `missing_symbol_section`

## How to package a task

Use one JSON task per repair.

Good:

- one note
- one target section
- one issue category

Bad:

- multiple sections in one request
- a whole note rewrite
- "please improve this page" without exact constraints

## Response acceptance checklist

Accept a DeepSeek response only if all are true:

- valid JSON
- `status` is `ok`
- `note_path` matches the input task
- `target_section` matches the input task
- `content` contains only the replacement body, not a heading or full note
- no invented wikilinks
- no invented facts
- no banned `不是A而是B` style phrasing
- no frontmatter text

Reject or escalate if any fail.

## Practical notes by issue type

### `meaning_too_short`

Give DeepSeek:

- title
- summary
- current `物理意義`
- one or two surrounding sections such as `定義` or `數學表達`

Expected output:

- a tighter and longer `物理意義`
- concrete explanation of what the note describes and why it matters

### `ungrouped_related_links`

Give DeepSeek:

- current `相關連結`
- list of links already present
- expected grouping labels if you already have them

Expected output:

- same links regrouped under `###` subsections
- one short sentence per group explaining the relationship

### `banned_pattern`

Give DeepSeek:

- exact sentence or paragraph that triggered the audit

Expected output:

- local rewrite only
- same meaning, less template-like phrasing

### `history_not_concrete`

Give DeepSeek:

- current `歷史背景`
- at least one explicit person, year, experiment, or cited fact from a trusted source package

Expected output:

- history paragraph with concrete anchor points

If that evidence is not provided, DeepSeek should be told to return `blocked`.

## Final gate

Even a good-looking response is not done until the repaired note passes:

- `tools/validate_structure.py`
- `tools/audit_content_quality.py`
- `tools/run_exports.py`
