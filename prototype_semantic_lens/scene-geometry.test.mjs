import test from "node:test";
import assert from "node:assert/strict";

import {
  buildEdgePath,
  convexHull,
  focusTypeOrder,
  offsetPolygon,
  positionRing,
  rankFocusNodes,
  smoothClosedPath,
} from "./scene-geometry.mjs";

test("convexHull removes interior points", () => {
  const hull = convexHull([
    { x: 0, y: 0 },
    { x: 4, y: 0 },
    { x: 4, y: 4 },
    { x: 0, y: 4 },
    { x: 2, y: 2 },
  ]);
  assert.equal(hull.length, 4);
});

test("offsetPolygon preserves polygon size", () => {
  const polygon = [
    { x: 0, y: 0 },
    { x: 4, y: 0 },
    { x: 4, y: 4 },
    { x: 0, y: 4 },
  ];
  const expanded = offsetPolygon(polygon, 2);
  assert.equal(expanded.length, polygon.length);
});

test("smoothClosedPath emits a closed cubic path", () => {
  const path = smoothClosedPath([
    { x: 0, y: 0 },
    { x: 3, y: 0 },
    { x: 3, y: 3 },
    { x: 0, y: 3 },
  ]);
  assert.match(path, /^M /);
  assert.match(path, / C /);
  assert.match(path, / Z$/);
});

test("positionRing places nodes around the focal point", () => {
  const nodes = [{}, {}, {}];
  positionRing(nodes, { x: 10, y: 20 }, 30, 40, 12);
  assert.equal(nodes.every((node) => typeof node.x === "number" && typeof node.y === "number" && node.r === 12), true);
});

test("focusTypeOrder keeps law nodes ahead of concepts", () => {
  assert.ok(focusTypeOrder("law") < focusTypeOrder("concept"));
});

test("rankFocusNodes sorts by type order then degree", () => {
  const nodes = [
    { id: "c-1", type: "concept", degree: 5 },
    { id: "l-1", type: "law", degree: 1 },
    { id: "c-2", type: "concept", degree: 9 },
    { id: "l-1", type: "law", degree: 10 },
  ];
  const ranked = rankFocusNodes(nodes, {
    dedupeNodes(items) {
      const seen = new Set();
      return items.filter((item) => {
        if (seen.has(item.id)) return false;
        seen.add(item.id);
        return true;
      });
    },
  });
  assert.deepEqual(ranked.map((node) => node.id), ["l-1", "c-2", "c-1"]);
});

test("buildEdgePath creates a quadratic curve command", () => {
  const path = buildEdgePath({ x: 0, y: 0 }, { x: 10, y: 0 });
  assert.match(path, /^M 0 0 Q /);
  assert.match(path, / 10 0$/);
});
