import test from "node:test";
import assert from "node:assert/strict";

import { buildFocusSceneData, buildOverviewSceneData } from "../src/scene-builder.mjs";

test("buildOverviewSceneData returns overview nodes, edges, and regions", () => {
  const graph = {
    overviewRoot: { id: "root::physics", type: "root", taxonomy: "all" },
    domainHubs: [{ id: "domain::mechanics", type: "domain", taxonomy: "mechanics", title: "Mechanics" }],
    nodes: [
      { id: "law-1", type: "law", taxonomy: "mechanics", tier: 1, degree: 10 },
      { id: "concept-1", type: "concept", taxonomy: "mechanics", tier: 2, degree: 8 },
    ],
    edges: [{ source: "law-1", target: "concept-1", type: "requires" }],
  };
  const result = buildOverviewSceneData(
    {
      graph,
      nodeMap: new Map(graph.nodes.map((node) => [node.id, node])),
      taxonomyOrder: ["mechanics"],
      centerX: 720,
      centerY: 480,
    },
    {
      selectOverviewNodesForTaxonomy(pool) {
        return pool;
      },
      weakLink() {
        return false;
      },
      weakUse() {
        return false;
      },
      relaxLayout() {},
      clampNodesToViewport() {},
      dedupeEdges(edges) {
        return edges;
      },
      smoothClosedPath() {
        return "M 0 0 Z";
      },
    }
  );
  assert.ok(result.overviewNodes.length >= 2);
  assert.equal(result.overviewEdges.length, 1);
  assert.equal(result.domainRegions.has("mechanics"), true);
});

test("buildFocusSceneData returns root-centered focus scene", () => {
  const graph = {
    domainHubs: [{ id: "domain::mechanics", type: "domain", taxonomy: "mechanics", title: "Mechanics" }],
  };
  const nodeMap = new Map([
    ["root::physics", { id: "root::physics", type: "root", title: "Physics" }],
  ]);
  const result = buildFocusSceneData(
    {
      nodeId: "root::physics",
      graph,
      nodeMap,
      graphIndex: null,
      overviewNodes: [],
      taxonomyLabels: { mechanics: "Mechanics" },
    },
    {
      collectDirectionalRelations() {
        return [];
      },
      rankFocusNodes(nodes) {
        return nodes;
      },
      dedupeNodes(nodes) {
        return nodes;
      },
      dedupeEdges(edges) {
        return edges;
      },
      positionRing(nodes) {
        nodes.forEach((node, index) => {
          node.x = index * 10;
          node.y = index * 10;
        });
      },
      relaxLayout() {},
      clampNodesToViewport() {},
    }
  );
  assert.equal(result.focusSceneNodeId, "root::physics");
  assert.equal(result.focusEdges.length, 1);
});

test("buildFocusSceneData builds related node scene for regular nodes", () => {
  const graph = { domainHubs: [] };
  const sourceNode = { id: "law-1", type: "law", title: "Law" };
  const relatedNode = { id: "concept-1", type: "concept", title: "Concept" };
  const nodeMap = new Map([
    [sourceNode.id, sourceNode],
    [relatedNode.id, relatedNode],
  ]);
  const result = buildFocusSceneData(
    {
      nodeId: sourceNode.id,
      graph,
      nodeMap,
      graphIndex: {},
      overviewNodes: [],
      taxonomyLabels: {},
    },
    {
      collectDirectionalRelations() {
        return [{
          bucket: "requires",
          node: relatedNode,
          edge: { source: sourceNode.id, target: relatedNode.id, type: "requires" },
        }];
      },
      rankFocusNodes(nodes) {
        return nodes;
      },
      dedupeNodes(nodes) {
        return nodes;
      },
      dedupeEdges(edges) {
        return edges;
      },
      positionRing(nodes, focal) {
        nodes.forEach((node) => {
          node.x = focal.x + 1;
          node.y = focal.y + 1;
        });
      },
      relaxLayout() {},
      clampNodesToViewport() {},
    }
  );
  assert.equal(result.focusSceneNodeId, sourceNode.id);
  assert.equal(result.focusNodes.length, 2);
  assert.equal(result.focusEdges.length, 1);
});
