# Wikipedia Enrichment Spec

This document defines the first safe version of Wikipedia-assisted note enrichment for the `knowledge_map` project.

The goal is to improve vague or imprecise AI-generated note content without directly copying Wikipedia text into the vault.

## 1. Core principle

Wikipedia is an evidence and structure source, not the final source of truth for note wording.

The enrichment pipeline should use Wikipedia to:

- sharpen definitions
- identify missing key terms
- suggest missing related notes
- suggest missing prerequisite notes
- suggest missing section topics
- point to better source material for human or model-assisted rewriting

The enrichment pipeline should not:

- directly overwrite the vault on first pass
- bulk-import Wikipedia prose into the knowledge base
- create wikilinks that do not already resolve to real notes without explicit review
- silently modify frontmatter relation lists

## 2. First-version scope

Version 1 is `report-only`.

It produces a structured enrichment report for one note at a time.
It does not:

- modify the source vault
- modify exported JSON
- open pull requests
- invoke the review UI yet

## 3. Inputs

The report generator receives:

- a note path inside the active vault
- optionally a manually supplied Wikipedia title
- optionally a manually supplied Wikipedia language

If a note already contains frontmatter fields such as:

- `wikipedia_title`
- `wikipedia_lang`

those values take precedence over naive search.

## 4. Matching strategy

The pipeline must not assume that a note title always maps cleanly to one Wikipedia page.

Matching order:

1. explicit CLI override
2. frontmatter `wikipedia_title`
3. title search in requested language
4. fallback title search in the alternate language set

Version 1 language policy:

- default primary language: `zh`
- default fallback language: `en`

The report must emit:

- `match_status`
- `match_confidence`
- `selected_page`
- `alternatives`

If confidence is low, the tool should still emit a report but mark the note as `manual_match_required`.

## 5. Wikipedia evidence to extract

Version 1 should extract only high-value structured evidence:

- canonical page title
- canonical URL
- page revision id
- lead extract
- section headings
- internal links

This is enough to build a useful enrichment plan without dumping whole encyclopedia pages into the workflow.

## 6. Note analysis

The pipeline should analyze the original note before making suggestions.

Version 1 heuristics:

- summary missing or too short
- summary contains vague language
- first body section lacks a concrete definition
- few or no related links
- few or no frontmatter relation targets
- missing standard note sections

This stage must produce:

- `weaknesses`
- `strengths`
- `current_sections`
- `current_links`
- `current_relations`

## 7. Candidate generation philosophy

Version 1 does not produce a final rewrite.
It produces a `revision_plan` and a `prompt_packet`.

### revision_plan

The revision plan should include:

- `definition_gaps`
- `missing_key_terms`
- `missing_section_topics`
- `recommended_related_notes`
- `recommended_prerequisites`
- `phrases_to_replace`
- `keep_sections`
- `rewrite_sections`

### prompt_packet

The prompt packet is the structured input for a later LLM rewrite step.
It should include:

- original note content
- original frontmatter
- note type and taxonomy
- matched Wikipedia evidence
- allowed related-note targets that actually exist in the vault
- rewrite constraints

The later LLM rewrite step should be able to generate:

- `minimal_revision`
- `full_revision`

but Version 1 stops before that.

## 8. Rewrite constraints for the later LLM stage

These constraints define how candidate revised text must be produced in the future:

- preserve note type
- preserve taxonomy domain unless explicitly changed by a human
- do not invent physics claims not supported by the original note or the matched evidence
- do not directly copy long Wikipedia passages
- prefer original phrasing only when it is already correct and specific
- prefer rewriting vague sentences into concrete statements
- do not add invalid wikilinks
- do not add invalid frontmatter relation targets
- keep the knowledge-base tone instructional and precise rather than encyclopedic filler

## 9. Review-session data contract

The future review UI will need per-note artifacts in a stable format.
Version 1 should already emit data shaped for later review tooling.

Recommended output file:

- `tmp/wikipedia_enrichment/<note-id>.json`

Recommended top-level structure:

```json
{
  "note": {},
  "match": {},
  "wikipedia_evidence": {},
  "vault_context": {},
  "analysis": {},
  "revision_plan": {},
  "prompt_packet": {}
}
```

## 10. Existing-vault safety rule

The enrichment tool is advisory until a later explicit apply step exists.

That means:

- no writes to the vault
- no auto-updates to relation fields
- no auto-commits

The first write-capable stage should be the later review-apply pipeline, not the enrichment report stage.

## 11. Pilot recommendation

Start with a narrow pilot of 5 to 10 notes, ideally in:

- `05_mathematical_tools/`

Good pilot characteristics:

- vague wording
- mature Wikipedia coverage
- enough related note candidates already exist in the vault
- low ambiguity in topic identity

## 12. Definition of success

The Wikipedia-assisted workflow is successful only if:

- matched pages are usually correct
- suggested related notes actually resolve
- suggested rewrite targets are concrete and useful
- review remains human-controlled
- final exported knowledge-base quality improves without link regressions
