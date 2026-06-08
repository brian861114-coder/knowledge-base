# Stronger Model Derivation Workflow

This workflow is for derivation repairs that should not be assigned to a weak model.

## Use this for

- `derivation_too_short`
- `derivation_missing_formula`

## Do not use this for

- full-note rewrites
- frontmatter changes
- section reordering
- arbitrary cross-note rewiring

## Core rule

Even a stronger model still only repairs one target section at a time.

The model returns a JSON payload for the `推導` section only. A local tool applies that payload back into the source vault.

## Required files

- `llm_configs/stronger_model_derivation_profile.json`
- `prompts/stronger_model_derivation_system_prompt.md`
- `prompts/stronger_model_derivation_task_prompt.md`
- `tools/build_stronger_model_tasks.py`
- `tools/apply_weak_model_response.py`
- `tools/apply_weak_model_batch.py`

## Recommended loop

1. Run `tools/audit_content_quality.py`.
2. Generate derivation tasks with `tools/build_stronger_model_tasks.py`.
3. Give the stronger model one task per response file or a batch directory of task files.
4. Validate responses locally.
5. Apply responses back into the source vault.
6. Rerun:
   - `tools/validate_structure.py`
   - `tools/audit_content_quality.py`
   - `tools/run_exports.py`

## Acceptance criteria for a derivation response

- valid JSON
- status is `ok`
- target section matches the task
- contains at least one explicit LaTeX equation
- explains the transition between steps
- uses existing notation unless clearly grounded
- does not touch any section outside `推導`

## Escalation

If the model cannot derive safely from the supplied context, it must return `blocked`.
