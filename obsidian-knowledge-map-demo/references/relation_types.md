# Relation Types

Prefer explicit relation semantics instead of one generic "related" bucket.

## Core Relations

- `requires`
  - A requires understanding B first
- `defines`
  - A defines B or gives a formal meaning to B
- `uses`
  - A uses B in its formulation or application
- `derives_to`
  - A can be used to derive B
- `explains`
  - A helps explain B
- `verified_by`
  - A is supported or tested by experiment B
- `measures`
  - experiment A measures quantity B
- `formalized_by`
  - A relies on mathematical tool B
- `organized_by`
  - A is grouped or sequenced by map B
- `related_to`
  - weak fallback relation only when a more precise edge is not available

## Display Guidance

- `requires`: learning path edge
- `derives_to`: derivation tree edge
- `verified_by`: theory-to-experiment edge
- `formalized_by`: math-support edge
- `related_to`: weak semantic edge
