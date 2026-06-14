import test from "node:test";
import assert from "node:assert/strict";

import {
  buildMetaItemsHtml,
  buildPillListHtml,
  buildSearchResultsHtml,
  buildStatCardsHtml,
} from "./detail-panel.mjs";

const helpers = {
  escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  },
};

test("buildMetaItemsHtml escapes labels and values", () => {
  const html = buildMetaItemsHtml([["<type>", "\"law\""]], helpers);
  assert.match(html, /&lt;type&gt;/);
  assert.match(html, /&quot;law&quot;/);
});

test("buildStatCardsHtml renders each stat entry", () => {
  const html = buildStatCardsHtml([["Requires", "4"]], helpers);
  assert.match(html, /Requires/);
  assert.match(html, />4</);
});

test("buildPillListHtml returns clickable node-id buttons", () => {
  const html = buildPillListHtml([{ id: "node-1", title: "Alpha" }], "related", helpers);
  assert.match(html, /data-node-id="node-1"/);
  assert.match(html, /data-family="related"/);
});

test("buildSearchResultsHtml renders empty-state query safely", () => {
  const html = buildSearchResultsHtml("<unsafe>", [], {
    ...helpers,
    messages: {
      emptyPrefix: "No result for ",
      emptySuffix: ".",
      resultCountPrefix: "",
      resultCountSuffix: "",
    },
  });
  assert.match(html, /No result for &lt;unsafe&gt;\./);
});

test("buildSearchResultsHtml renders result count and matches", () => {
  const html = buildSearchResultsHtml("alpha", [{ id: "n1", title: "Alpha" }], {
    ...helpers,
    messages: {
      emptyPrefix: "",
      emptySuffix: "",
      resultCountPrefix: "Matches: ",
      resultCountSuffix: "",
    },
  });
  assert.match(html, /Matches: 1/);
  assert.match(html, /Alpha/);
});
