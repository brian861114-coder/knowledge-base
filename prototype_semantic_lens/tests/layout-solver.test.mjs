import test from "node:test";
import assert from "node:assert/strict";

import {
  collisionHalfHeight,
  collisionHalfWidth,
  collisionRadius,
  relaxLayout,
} from "../src/layout-solver.mjs";

test("collisionHalfWidth falls back to node radius", () => {
  assert.equal(collisionHalfWidth({ r: 10 }, { visibleTitle: "" }), 16);
});

test("collisionHalfWidth expands for visible labels", () => {
  assert.ok(collisionHalfWidth({ r: 10 }, { visibleTitle: "Long Visible Title" }) > 16);
});

test("collisionRadius uses the larger axis", () => {
  const value = collisionRadius(
    { r: 10 },
    {
      getCollisionHalfWidth(node) {
        return collisionHalfWidth(node, { visibleTitle: "Label" });
      },
      getCollisionHalfHeight: collisionHalfHeight,
    }
  );
  assert.ok(value >= collisionHalfHeight({ r: 10 }));
});

test("relaxLayout separates overlapping nodes", () => {
  const nodes = [
    { id: "a", x: 0, y: 0, r: 10 },
    { id: "b", x: 0, y: 0, r: 10 },
  ];
  relaxLayout(nodes, {
    iterations: 4,
    padding: 4,
    getCollisionHalfWidth(node) {
      return collisionHalfWidth(node, { visibleTitle: "" });
    },
    getCollisionHalfHeight: collisionHalfHeight,
  });
  assert.ok(nodes[0].x !== nodes[1].x || nodes[0].y !== nodes[1].y);
});

test("relaxLayout keeps focal nodes fixed when requested", () => {
  const nodes = [
    { id: "focal", x: 0, y: 0, r: 10, focal: true },
    { id: "other", x: 0, y: 0, r: 10 },
  ];
  relaxLayout(nodes, {
    iterations: 4,
    padding: 4,
    lockFocal: true,
    getCollisionHalfWidth(node) {
      return collisionHalfWidth(node, { visibleTitle: "" });
    },
    getCollisionHalfHeight: collisionHalfHeight,
  });
  assert.equal(nodes[0].x, 0);
  assert.equal(nodes[0].y, 0);
});
