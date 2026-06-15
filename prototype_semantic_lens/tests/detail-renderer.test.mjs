import test from "node:test";
import assert from "node:assert/strict";

import { buildEmptyDetailView, buildNoteSectionHtml } from "../src/detail-renderer.mjs";

const baseOptions = {
  escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  },
  renderMarkdown(value) {
    return String(value || "");
  },
  findNodeByTitle() {
    return null;
  },
  loadError: null,
  isLoaded: true,
};

test("full note view prefers body_full without duplicating section cards", () => {
  const html = buildNoteSectionHtml(
    { id: "n1", title: "Node" },
    {
      body_full: "Full body text",
      body_preview: "Preview text",
      sections: [
        { title: "Section A", content: "Full body text" },
      ],
    },
    {
      ...baseOptions,
      noteViewMode: "full",
    }
  );

  assert.match(html, /Full body text/);
  assert.doesNotMatch(html, /Section A/);
  assert.doesNotMatch(html, /note-sections-grid/);
  assert.doesNotMatch(html, /section-head/);
});

test("full note view falls back to sections when body_full is absent", () => {
  const html = buildNoteSectionHtml(
    { id: "n1", title: "Node" },
    {
      sections: [
        { title: "Section A", content: "Section content" },
      ],
    },
    {
      ...baseOptions,
      noteViewMode: "full",
    }
  );

  assert.doesNotMatch(html, /Section A/);
  assert.doesNotMatch(html, /note-sections-grid/);
  assert.doesNotMatch(html, /section-head/);
});

test("buildEmptyDetailView includes overview stats from options", () => {
  const view = buildEmptyDetailView({
    overviewNodeCount: 12,
    overviewEdgeCount: 34,
  });

  assert.deepEqual(view.statsEntries, [
    ["顯示節點", "12"],
    ["顯示關係", "34"],
    ["已隱藏", "wikilink"],
    ["總層級", "3"],
  ]);
});
