# Frontmatter Schema

All pages should prefer explicit frontmatter over inferred metadata.

## Common Fields

```yaml
---
type:
title:
summary:
tags: []
updated:
---
```

## `law`

```yaml
---
type: law
title:
domain:
summary:
applicability:
prerequisites: []
related_concepts: []
related_quantities: []
related_laws: []
experiments: []
math_tools: []
derived_results: []
modern_connections: []
tags: []
updated:
---
```

## `concept`

```yaml
---
type: concept
title:
domain:
summary:
prerequisites: []
related_laws: []
related_quantities: []
related_concepts: []
math_tools: []
tags: []
updated:
---
```

## `quantity`

```yaml
---
type: quantity
title:
symbol:
unit:
dimension:
domain:
summary:
related_concepts: []
related_laws: []
measurement_methods: []
tags: []
updated:
---
```

## `experiment`

```yaml
---
type: experiment
title:
summary:
domain:
tested_laws: []
measured_quantities: []
related_concepts: []
historical_period:
tags: []
updated:
---
```

## `mathematical_tool`

```yaml
---
type: mathematical_tool
title:
summary:
used_in: []
prerequisites: []
related_concepts: []
tags: []
updated:
---
```

## `map`

```yaml
---
type: map
title:
summary:
focus_domain:
includes: []
recommended_order: []
tags: []
updated:
---
```
