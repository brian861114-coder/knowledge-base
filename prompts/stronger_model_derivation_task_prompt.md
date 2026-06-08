Use the system rules exactly.

You are being given one derivation-repair task for one section only.

Task handling rules:

1. Repair only the `推導` section from the task JSON.
2. Keep the repaired derivation consistent with the surrounding definitions and formulas.
3. Use at least one explicit LaTeX equation.
4. Explain why each step follows, not just the final result.
5. Do not invent unrelated notation or rewrite other sections.
6. If the task context is insufficient for a reliable derivation, return `blocked`.

Return JSON only.

Task JSON:

```json
{{TASK_JSON}}
```
