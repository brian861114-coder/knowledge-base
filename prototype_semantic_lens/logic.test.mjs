import test from "node:test";
import assert from "node:assert/strict";

import {
  buildGraphIndex,
  collectDirectionalRelations,
  relationBucketForEdge,
  validateDetailPayload,
  validateGraphPayload,
} from "./logic.mjs";

test("validateGraphPayload accepts a minimal valid graph", () => {
  assert.doesNotThrow(() => {
    validateGraphPayload({
      nodes: [
        { id: "map", title: "Map", type: "map" },
        { id: "law", title: "Law", type: "law" },
      ],
      edges: [{ source: "map", target: "law", type: "requires" }],
    });
  });
});

test("validateGraphPayload rejects duplicate node ids", () => {
  assert.throws(() => {
    validateGraphPayload({
      nodes: [
        { id: "dup", title: "One", type: "concept" },
        { id: "dup", title: "Two", type: "concept" },
      ],
      edges: [],
    });
  }, /重複的 node id/);
});

test("validateDetailPayload rejects unknown detail ids", () => {
  assert.throws(() => {
    validateDetailPayload({ ghost: { summary: "?" } }, ["known"]);
  }, /未知節點/);
});

test("relationBucketForEdge preserves directional semantics", () => {
  assert.equal(relationBucketForEdge("requires", "source"), "requires");
  assert.equal(relationBucketForEdge("requires", "target"), "extension");
  assert.equal(relationBucketForEdge("derives_to", "source"), "extension");
  assert.equal(relationBucketForEdge("derives_to", "target"), "requires");
});

test("collectDirectionalRelations separates prerequisite and extension correctly", () => {
  const nodes = [
    { id: "map", title: "Map", type: "map" },
    { id: "law", title: "Law", type: "law" },
    { id: "math", title: "Math", type: "mathematical_tool" },
    { id: "derived", title: "Derived", type: "concept" },
  ];
  const edges = [
    { source: "map", target: "law", type: "requires" },
    { source: "law", target: "math", type: "formalized_by" },
    { source: "law", target: "derived", type: "derives_to" },
  ];
  const nodeMap = new Map(nodes.map((node) => [node.id, node]));
  const graphIndex = buildGraphIndex(nodes, edges);

  const lawRelations = collectDirectionalRelations("law", graphIndex, nodeMap);
  const grouped = Object.groupBy(lawRelations, (entry) => entry.bucket);

  assert.deepEqual(
    (grouped.requires || []).map((entry) => entry.node.id).sort(),
    ["math"]
  );
  assert.deepEqual(
    (grouped.extension || []).map((entry) => entry.node.id).sort(),
    ["derived", "map"]
  );
});

test("buildGraphIndex rejects semantic edges that point to missing nodes", () => {
  assert.throws(() => {
    buildGraphIndex(
      [{ id: "only", title: "Only", type: "concept" }],
      [{ source: "only", target: "missing", type: "requires" }]
    );
  }, /找不到 target 節點/);
});
