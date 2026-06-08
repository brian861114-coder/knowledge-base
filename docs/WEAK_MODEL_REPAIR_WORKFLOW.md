# Weak Model Repair Workflow

This workflow is for using weaker models such as DeepSeek v4 Pro without letting them damage the vault.

## Core rule

Do not let a weak model rewrite a full note.

The weak model is only allowed to repair one target section at a time and must return a structured payload. A local tool or operator should then decide whether to write that payload back into the source vault.

## What this workflow is for

Use this workflow for low-risk content fixes detected by `tools/audit_content_quality.py`.

Good candidates:

- `meaning_too_short`
- `ungrouped_related_links`
- `banned_pattern`
- `history_not_concrete` only when evidence is already provided

Bad candidates:

- `derivation_missing_formula`
- `derivation_too_short`
- `missing_symbol_section`
- anything that requires new equations, new notation decisions, or cross-note graph decisions

## Required files

- `llm_configs/deepseek_v4pro_repair_profile.json`
- `llm_configs/issue_routing_rules.json`
- `task_templates/section_repair_task_template.json`
- `prompts/deepseek_v4pro_system_prompt.md`
- `prompts/deepseek_v4pro_task_prompt.md`

## Recommended operator loop

1. Run `tools/audit_content_quality.py`.
2. Select only issue categories routed to the weak model.
3. Build one task per note per target section.
4. Give the weak model:
   - the system prompt
   - the task prompt
   - one task JSON
5. Validate the model response:
   - response must be valid JSON
   - response must touch one section only
   - response must not invent links, facts, formulas, or section names
6. Apply the approved section payload back into the source vault.
7. Rerun:
   - `tools/validate_structure.py`
   - `tools/audit_content_quality.py`
   - `tools/run_exports.py`
8. If the issue remains or a new problem appears, escalate that note to a stronger model or human review.

## Minimum task package

Every weak-model task should include:

- note path
- note type
- issue category
- target section
- exact length or semantic constraints
- existing section content that matters
- known formulas that must be preserved
- known links that may be reused
- evidence snippets if the task is about history

If any of those are missing, the task quality drops fast.

## Hard safety boundaries

The weak model must not:

- rewrite full Markdown files
- add or remove headings
- touch frontmatter
- rename notes
- choose wikilink targets on its own
- invent historical names, dates, or experiments
- invent derivation steps when the math is not already supplied

## Escalation rule

If a task asks for new derivation math, new formula selection, or new historical facts, the weak model should return `status: "blocked"` instead of guessing.
