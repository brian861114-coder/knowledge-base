import test from "node:test";
import assert from "node:assert/strict";

import {
  buildGraphIndex,
  collectDirectionalRelations,
  detailFileNameForNodeId,
  findSearchMatches,
  groupDirectionalRelations,
  relationBucketForEdge,
  validateDetailPayload,
  validateGraphPayload,
} from "../src/logic.mjs";

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

test("groupDirectionalRelations ranks and slices each bucket", () => {
  const grouped = groupDirectionalRelations(
    [
      { bucket: "requires", node: { id: "r2", score: 2 } },
      { bucket: "requires", node: { id: "r1", score: 1 } },
      { bucket: "extension", node: { id: "e1", score: 1 } },
      { bucket: "related", node: { id: "x2", score: 2 } },
      { bucket: "related", node: { id: "x1", score: 1 } },
    ],
    {
      rankNodes(nodes) {
        return nodes.slice().sort((a, b) => b.score - a.score);
      },
      limit: 1,
    }
  );

  assert.deepEqual(grouped, {
    requires: [{ id: "r2", score: 2 }],
    extension: [{ id: "e1", score: 1 }],
    related: [{ id: "x2", score: 2 }],
  });
});

test("findSearchMatches filters non-content nodes and respects limit", () => {
  const matches = findSearchMatches(
    [
      { id: "root", type: "root", searchText: "energy" },
      { id: "domain", type: "domain", searchText: "energy" },
      { id: "law-1", type: "law", searchText: "energy conservation" },
      { id: "concept-1", type: "concept", searchText: "energy transfer" },
    ],
    "energy",
    { limit: 1 }
  );

  assert.deepEqual(matches, [
    { id: "law-1", type: "law", searchText: "energy conservation" },
  ]);
});

test("buildGraphIndex rejects semantic edges that point to missing nodes", () => {
  assert.throws(() => {
    buildGraphIndex(
      [{ id: "only", title: "Only", type: "concept" }],
      [{ source: "only", target: "missing", type: "requires" }]
    );
  }, /找不到 target 節點/);
});

test("detailFileNameForNodeId uses URL-safe encoding", () => {
  assert.match(detailFileNameForNodeId("A/B test"), /^detail-[0-9a-f]{8}\.json$/);
  assert.equal(detailFileNameForNodeId("A/B test"), detailFileNameForNodeId("A/B test"));
  assert.notEqual(detailFileNameForNodeId("A/B test"), detailFileNameForNodeId("A/B test 2"));
});
