# DeepSeek Remaining Issues Playbook

This note defines exactly how to send the remaining lower-risk content-audit categories to DeepSeek v4 Pro.

## Current intended categories

Send these categories to DeepSeek:

1. `banned_pattern`
2. `ungrouped_related_links`
3. `history_not_concrete` only when task input includes concrete evidence

Do not mix categories in one batch.

## Prompt selection

Always provide:

- `prompts/deepseek_v4pro_system_prompt.md`
- `docs/DEEPSEEK_V4PRO_OPERATOR_GUIDE.md`

Then choose exactly one issue-specific prompt:

- `banned_pattern`
  - use `prompts/deepseek_v4pro_banned_pattern_prompt.md`
- `ungrouped_related_links`
  - use `prompts/deepseek_v4pro_ungrouped_related_links_prompt.md`
- `history_not_concrete`
  - use `prompts/deepseek_v4pro_history_with_evidence_prompt.md`

For batch mode, also provide:

- `prompts/deepseek_v4pro_remaining_issues_batch_instruction.md`

## Exact operator wording

### Single task

```text
請先閱讀並嚴格遵守：
- prompts/deepseek_v4pro_system_prompt.md
- prompts/<ISSUE_SPECIFIC_PROMPT>.md
- docs/DEEPSEEK_V4PRO_OPERATOR_GUIDE.md

現在只處理我提供的單一 task JSON。
你只能輸出 JSON。
你只能修一個 note 的一個 target section。
不可修改 frontmatter，不可修改其他 section，不可輸出整篇 note。
若資訊不足，回傳 status="blocked"。

以下是 task JSON：
[貼上 task JSON]
```

### Batch mode

```text
請先閱讀並嚴格遵守：
- prompts/deepseek_v4pro_system_prompt.md
- prompts/<ISSUE_SPECIFIC_PROMPT>.md
- prompts/deepseek_v4pro_remaining_issues_batch_instruction.md
- docs/DEEPSEEK_V4PRO_OPERATOR_GUIDE.md

現在請處理這個 task 目錄：
[TASK_DIR]

並把每個 task 的回應各自存成同名 JSON 到：
[RESPONSE_DIR]

必須遵守：
1. 一個 task 對應一個 response JSON。
2. response 檔名必須和 task 檔名完全一致。
3. 若無法安全完成，仍要輸出同名 JSON，但 status 必須是 "blocked"。
4. 不可輸出整篇 note，不可修改 frontmatter，不可改 section 順序。
```

## Routing intent

### `banned_pattern`

Use when the audit only flags template-like contrast phrasing.

Expected behavior:

- local rewrite only
- same meaning
- no padding

### `ungrouped_related_links`

Use when links already exist but are not grouped under `###` subsections.

Expected behavior:

- regroup existing links
- add one short explanation sentence per group
- no new links

### `history_not_concrete`

Use only when the task package includes concrete anchors.

Expected behavior:

- include explicit person, year, experiment, or source-backed anchor
- connect the anchor to the note topic
- no fabricated history
