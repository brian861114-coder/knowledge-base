import test from "node:test";
import assert from "node:assert/strict";

import { escapeHtml, renderMarkdown } from "../src/markdown.mjs";

test("escapeHtml escapes unsafe markup", () => {
  assert.equal(escapeHtml('<tag attr="x">'), "&lt;tag attr=&quot;x&quot;&gt;");
});

test("renderMarkdown resolves wikilinks through injected lookup", () => {
  const html = renderMarkdown("[[Hooke's law|虎克定律]]", {}, {
    findNodeByTitle(title) {
      if (title === "Hooke's law") return { id: "hooke_law" };
      return null;
    },
  });
  assert.match(html, /data-node-id="hooke_law"/);
  assert.match(html, /虎克定律/);
});

test("renderMarkdown leaves unresolved wikilinks as non-clickable spans", () => {
  const html = renderMarkdown("[[Ghost]]");
  assert.match(html, /inline-note-link unresolved/);
});
