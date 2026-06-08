Read the task JSON and repair only the target section.

Return JSON with this shape:

```json
{
  "status": "ok",
  "note_path": "...",
  "target_section": "...",
  "issue_category": "...",
  "content": "...",
  "rationale": "...",
  "self_check": [
    "..."
  ]
}
```

If the task is unsafe or underspecified, return:

```json
{
  "status": "blocked",
  "note_path": "...",
  "target_section": "...",
  "issue_category": "...",
  "content": "",
  "rationale": "Why the task is blocked.",
  "self_check": []
}
```
