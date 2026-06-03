# Diagram Assets

Use this folder for frontend-facing static images that are referenced by exported note content.

Recommended usage:

- keep explanatory diagrams, figures, and schematic images here
- prefer ASCII filenames with hyphens, for example `newton-second-law-free-body.png`
- use relative paths from note content, for example `![Free-body diagram](../assets/newton-second-law-free-body.png "Force analysis schematic")`
- keep the original source file elsewhere if you need editable design formats such as `.pptx`, `.drawio`, or `.svg` working files

Supported by the current prototype renderer:

- block image syntax: `![alt text](../assets/example.png "Optional caption")`
- inline image syntax inside a paragraph with the same Markdown image form

Notes:

- the prototype serves this folder over HTTP when the repo root is the server root
- external `http://` and `https://` image URLs also work, but local checked-in assets are more stable
- avoid spaces and machine-specific absolute paths in image URLs
