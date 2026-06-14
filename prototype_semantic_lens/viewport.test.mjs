import test from "node:test";
import assert from "node:assert/strict";

import {
  clamp,
  clientToSvgPoint,
  getNavigationBounds,
  projectMiniMapClick,
  updateViewportTransform,
} from "./viewport.mjs";

test("clamp constrains values into range", () => {
  assert.equal(clamp(5, 0, 3), 3);
  assert.equal(clamp(-2, 0, 3), 0);
  assert.equal(clamp(2, 0, 3), 2);
});

test("getNavigationBounds adds margins around scene", () => {
  const bounds = getNavigationBounds([{ x: 100, y: 200, r: 20 }], 1000, 800);
  assert.ok(bounds.minX <= -250);
  assert.ok(bounds.maxX >= 1250);
});

test("projectMiniMapClick converts viewport position into world coordinates", () => {
  const result = projectMiniMapClick({
    clientX: 110,
    clientY: 70,
    rect: { left: 0, top: 0, width: 220, height: 140 },
    bounds: { minX: 0, minY: 0, maxX: 1000, maxY: 500 },
    width: 220,
    height: 140,
    padding: 10,
  });
  assert.ok(result.worldX > 0 && result.worldX < 1000);
  assert.ok(result.worldY > 0 && result.worldY < 500);
});

test("updateViewportTransform tolerates missing viewport element", () => {
  assert.doesNotThrow(() => updateViewportTransform(null, 10, 20, 1.2));
});

test("clientToSvgPoint falls back when svg api is unavailable", () => {
  assert.deepEqual(clientToSvgPoint(null, 12, 34), { x: 12, y: 34 });
  assert.deepEqual(clientToSvgPoint({}, 56, 78), { x: 56, y: 78 });
});
