Use the system rules exactly.

You are repairing one `相關連結` section for issue category `ungrouped_related_links`.

Your job is narrow:

1. Reorganize only the links already present in the input.
2. Group them under `###` subsection headings.
3. Add one short explanatory sentence per group.
4. Do not invent new wikilinks.
5. Do not delete links unless the task explicitly marks them invalid.
6. Do not edit any section other than the target section.
7. If the provided links are too incomplete to group safely, return `blocked`.

Minimum output shape:

- `### 群組名稱`
- one short sentence explaining the relationship
- the existing wikilinks listed under that group

Your `content` field must contain only the replacement body for the target section.

Return JSON only.

Task JSON:

```json
{{TASK_JSON}}
```
