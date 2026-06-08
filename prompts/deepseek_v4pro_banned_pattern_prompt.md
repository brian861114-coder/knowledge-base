Use the system rules exactly.

You are repairing a single flagged section for issue category `banned_pattern`.

Your job is narrow:

1. Rewrite only the flagged sentence or short paragraph.
2. Keep the original physics meaning.
3. Remove template-like contrast phrasing such as `不是 A，而是 B`.
4. Do not broaden scope.
5. Do not add new facts, formulas, links, names, or dates.
6. If the flagged text cannot be safely rewritten from the provided input, return `blocked`.

What good output looks like:

- shorter or similarly sized rewrite
- more direct definition or explanation
- no rhetorical contrast template
- no extra claims

Your `content` field must contain only the replacement body for the target section.

Return JSON only.

Task JSON:

```json
{{TASK_JSON}}
```
