import test from "node:test";
import assert from "node:assert/strict";

import {
  createFocusState,
  createOverviewState,
  stepBrowseHistory,
} from "../src/navigation-state.mjs";

test("createOverviewState resets browse and focus state", () => {
  const state = createOverviewState();
  assert.equal(state.mode, "overview");
  assert.equal(state.selectedNodeId, null);
  assert.deepEqual(state.browseHistory, []);
  assert.equal(state.browseIndex, -1);
  assert.equal(state.zoom, 1);
});

test("createFocusState pushes node into browse history by default", () => {
  const state = createFocusState(
    {
      browseHistory: ["a"],
      browseIndex: 0,
    },
    "b"
  );
  assert.equal(state.selectedNodeId, "b");
  assert.deepEqual(state.browseHistory, ["a", "b"]);
  assert.equal(state.browseIndex, 1);
  assert.equal(state.zoom, 0.98);
});

test("createFocusState can skip history push", () => {
  const state = createFocusState(
    {
      browseHistory: ["a", "b"],
      browseIndex: 1,
    },
    "b",
    { pushHistory: false }
  );
  assert.equal(state.selectedNodeId, "b");
  assert.equal("browseHistory" in state, false);
  assert.equal("browseIndex" in state, false);
});

test("stepBrowseHistory moves backward and forward inside bounds", () => {
  const currentState = {
    browseHistory: ["a", "b", "c"],
    browseIndex: 1,
  };
  assert.deepEqual(stepBrowseHistory(currentState, "back"), { nodeId: "a", browseIndex: 0 });
  assert.deepEqual(stepBrowseHistory(currentState, "forward"), { nodeId: "c", browseIndex: 2 });
});

test("stepBrowseHistory returns null when already out of bounds", () => {
  assert.equal(
    stepBrowseHistory({ browseHistory: ["a"], browseIndex: 0 }, "back"),
    null
  );
  assert.equal(
    stepBrowseHistory({ browseHistory: ["a"], browseIndex: 0 }, "forward"),
    null
  );
});
