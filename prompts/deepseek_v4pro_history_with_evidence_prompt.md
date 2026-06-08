Use the system rules exactly.

You are repairing one `歷史背景` section for issue category `history_not_concrete`.

This category is evidence-gated. You must not guess.

Rules:

1. Use only person names, years, experiments, and facts explicitly present in the task input.
2. If the input does not provide at least one concrete anchor such as a person, year, experiment, or cited fact, return `blocked`.
3. Do not invent historical details.
4. Do not turn the section into generic praise or broad cultural commentary.
5. Explain the historical motivation or role of the concept/tool/experiment using the provided anchors.
6. Do not edit any section other than the target section.

What good output looks like:

- contains at least one person, year, experiment name, or source-backed anchor
- explains why that development mattered
- stays concise and specific

Your `content` field must contain only the replacement body for the target section.

Return JSON only.

Task JSON:

```json
{{TASK_JSON}}
```
