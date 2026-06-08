Use the system rules exactly.

You are being given one repair task for one section only.

Task handling rules:

1. Read the JSON task carefully.
2. Repair only the requested target section.
3. Reuse existing formulas and links when provided.
4. Do not add new facts unless they are already present in `provided_evidence`.
5. If the task asks for a derivation improvement without enough math steps or formulas, return `blocked`.
6. If the task asks for historical concreteness without enough evidence, return `blocked`.
7. Your `content` field must contain only the replacement body for the section, not the heading and not the full note.

Return JSON only.

Task JSON:

```json
{{TASK_JSON}}
```
