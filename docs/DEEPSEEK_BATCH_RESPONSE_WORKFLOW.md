# DeepSeek Batch Response Workflow

This is the workflow for cases where DeepSeek should repair many tasks and save all outputs as files.

## Goal

Do not paste one response at a time into chat if the batch is large.

Instead:

1. generate a task directory locally
2. let DeepSeek produce one response JSON per task
3. store those response files in a response directory
4. use a local batch apply tool to validate and apply them

## Required layout

Example:

```text
batch_tasks/
  deepseek_v4pro/
    meaning_too_short/
      001-example.json
      002-example.json
      manifest.json

batch_responses/
  deepseek_v4pro/
    meaning_too_short/
      001-example.json
      002-example.json
```

The response filenames should match the task filenames exactly.

## What to tell DeepSeek

Do not tell it to rewrite notes directly.

Tell it:

- read the system prompt
- read the task prompt
- process tasks one by one
- save one JSON response per task
- use the same filename as the task file
- if blocked, still save a JSON file with `status: "blocked"`

## Local apply step

Dry-run:

```powershell
python .\tools\apply_weak_model_batch.py `
  --task-dir .\batch_tasks\deepseek_v4pro\meaning_too_short `
  --response-dir .\batch_responses\deepseek_v4pro\meaning_too_short
```

Write back:

```powershell
python .\tools\apply_weak_model_batch.py `
  --task-dir .\batch_tasks\deepseek_v4pro\meaning_too_short `
  --response-dir .\batch_responses\deepseek_v4pro\meaning_too_short `
  --write `
  --report-out .\tmp\deepseek_batch_apply_report.json
```

## After apply

Always rerun:

1. `tools/validate_structure.py`
2. `tools/audit_content_quality.py`
3. `tools/run_exports.py`

## Hard rule

Do not trust a response file just because it exists.

The batch apply tool is the gate. It rejects mismatched note paths, target sections, empty content, and malformed responses.
