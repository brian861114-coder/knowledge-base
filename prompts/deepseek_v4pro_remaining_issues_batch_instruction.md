Read and obey these files first:

- `prompts/deepseek_v4pro_system_prompt.md`
- one issue-specific prompt chosen from:
  - `prompts/deepseek_v4pro_banned_pattern_prompt.md`
  - `prompts/deepseek_v4pro_ungrouped_related_links_prompt.md`
  - `prompts/deepseek_v4pro_history_with_evidence_prompt.md`
- `docs/DEEPSEEK_V4PRO_OPERATOR_GUIDE.md`

You will receive a directory of task JSON files for one issue category only.

Rules:

1. Process tasks one by one.
2. For each task, output one JSON response file.
3. The response filename must exactly match the task filename.
4. The response content must follow the required JSON contract.
5. Do not combine multiple tasks into one file.
6. Do not rewrite whole notes.
7. Do not modify frontmatter.
8. For `ungrouped_related_links`, do not invent wikilinks.
9. For `banned_pattern`, rewrite only the flagged local text.
10. For `history_not_concrete`, do not invent names, dates, or experiments.
11. If a task cannot be completed safely, still output a JSON file with `status: "blocked"`.

Expected directory behavior:

- input task file: `001-example.json`
- output response file: `001-example.json`

Do not change filenames.
