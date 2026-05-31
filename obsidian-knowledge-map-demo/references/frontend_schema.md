# Frontend Export Schema

The export target is a frontend-ready graph payload with deterministic note metadata.

## Output Shape

```json
{
  "nodes": [
    {
      "id": "gradient-descent",
      "title": "梯度下降",
      "type": "law",
      "summary": "用局部斜率逐步逼近最小值的最佳化方法。",
      "path": "physics/laws/newton_second_law.md",
      "domain": "力學",
      "tags": ["mechanics", "law"]
    }
  ],
  "edges": [
    {
      "source": "newton-second-law",
      "target": "acceleration",
      "type": "uses"
    }
  ]
}
```

## Field Notes

- `id`: slug derived from file name
- `title`: frontmatter title, fallback to first heading, fallback to file stem
- `type`: frontmatter type, fallback to `note`
- `summary`: frontmatter summary when present
- `path`: vault-relative path
- `domain`: frontmatter domain when present
- `tags`: frontmatter tags only in this demo exporter
- `edges`: extracted from explicit relation fields first, then from Obsidian wiki links in body content
