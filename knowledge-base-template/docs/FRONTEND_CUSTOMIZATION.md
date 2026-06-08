# Frontend Customization

The frontend in `prototype/` is intentionally lightweight.

Its job is to read exported JSON and render:

- graph exploration
- note detail panel
- reader mode

## Files

- `prototype/index.html`
- `prototype/app.js`
- `prototype/styles.css`

## What To Change First

If you adapt the template to a new domain, the usual frontend changes are:

1. note-type labels
2. note-type color palette
3. domain descriptions
4. taxonomy descriptions
5. landing-copy text

Do not start frontend work before the exported data contract is stable.

If note types, relation fields, or section shapes are still moving, frontend polish is premature.

## Data Contract

The frontend expects:

- `graph.json`
- `note_details.json`

It does not read raw Markdown files directly.

So if the UI looks wrong, first ask:

1. is the source vault correct?
2. are the exports current?
3. is the schema aligned with the data?

Only after that should you debug `prototype/app.js`.
