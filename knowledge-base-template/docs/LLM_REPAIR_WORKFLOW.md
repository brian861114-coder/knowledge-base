# LLM Repair Workflow

This template ships a section-level LLM repair pattern.

## Scope Discipline

The model should repair:

- one note
- one target section
- one issue category

It should not rewrite the whole note.

## Intended Flow

1. validator or audit identifies a concrete issue
2. build a task JSON
3. model returns a section payload JSON
4. local tool or operator applies only that section
5. rerun validators

## Why Section-Level Only

Weak models are acceptable for:

- expanding a short section
- replacing filler phrases
- grouping existing links

Weak models are not acceptable for:

- free-form whole-note rewrites
- frontmatter changes
- schema changes
- uncontrolled derivations

## Blocked Is A Feature

If the model lacks enough evidence, it should return `blocked`.

That is healthier than hallucinating.
