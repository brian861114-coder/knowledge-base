Read and obey these files first:

- `prompts/deepseek_v4pro_system_prompt.md`
- `prompts/deepseek_v4pro_task_prompt.md`
- `docs/DEEPSEEK_V4PRO_OPERATOR_GUIDE.md`

You will receive a directory of task JSON files.

Rules:

1. Process tasks one by one.
2. For each task, output one JSON response file.
3. The response filename must exactly match the task filename.
4. The response content must follow the required JSON contract.
5. Do not combine multiple tasks into one file.
6. Do not rewrite whole notes.
7. Do not modify frontmatter.
8. Do not invent links, formulas, or historical facts.
9. If a task cannot be completed safely, still output a JSON file with `status: "blocked"`.

Expected directory behavior:

- input task file: `001-example.json`
- output response file: `001-example.json`

Do not change filenames.
