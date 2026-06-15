import test from "node:test";
import assert from "node:assert/strict";

import { buildBreadcrumbHtml, createModeUiState } from "../src/ui-state.mjs";

test("buildBreadcrumbHtml escapes labels and adds separators", () => {
  const html = buildBreadcrumbHtml(
    [{ label: "<Home>", action: "overview" }, { label: "Node" }],
    {
      escapeHtml(value) {
        return String(value).replace(/</g, "&lt;").replace(/>/g, "&gt;");
      },
    }
  );
  assert.match(html, /&lt;Home&gt;/);
  assert.match(html, /breadcrumb-separator/);
});

test("createModeUiState returns focus breadcrumb state", () => {
  const result = createModeUiState(
    { mode: "focus", selectedNodeId: "n1" },
    { id: "n1", title: "Node" },
    "Mechanics"
  );
  assert.equal(result.isFocus, true);
  assert.equal(result.breadcrumbItems[1].label, "Mechanics");
});

test("createModeUiState returns overview breadcrumb state", () => {
  const result = createModeUiState(
    { mode: "overview", selectedNodeId: null },
    null,
    ""
  );
  assert.equal(result.isFocus, false);
  assert.equal(result.breadcrumbItems[1].label, "taxonomy domains");
});
