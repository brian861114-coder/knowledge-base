export function convexHull(points) {
  const pts = points.slice().sort((a, b) => a.x - b.x || a.y - b.y);
  if (pts.length <= 2) return pts;
  const cross = (o, a, b) => (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x);
  const lower = [];
  for (const p of pts) {
    while (lower.length >= 2 && cross(lower[lower.length - 2], lower[lower.length - 1], p) <= 0) lower.pop();
    lower.push(p);
  }
  const upper = [];
  for (let i = pts.length - 1; i >= 0; i -= 1) {
    const p = pts[i];
    while (upper.length >= 2 && cross(upper[upper.length - 2], upper[upper.length - 1], p) <= 0) upper.pop();
    upper.push(p);
  }
  lower.pop();
  upper.pop();
  return lower.concat(upper);
}

export function offsetPolygon(polygon, distance) {
  const n = polygon.length;
  if (n < 3) return polygon;
  const normals = [];
  for (let i = 0; i < n; i += 1) {
    const a = polygon[i];
    const b = polygon[(i + 1) % n];
    const dx = b.x - a.x;
    const dy = b.y - a.y;
    const len = Math.hypot(dx, dy) || 1;
    normals.push({ nx: dy / len, ny: -dx / len });
  }
  const expanded = [];
  for (let i = 0; i < n; i += 1) {
    const prev = normals[(i - 1 + n) % n];
    const curr = normals[i];
    const bx = prev.nx + curr.nx;
    const by = prev.ny + curr.ny;
    const dot = bx * curr.nx + by * curr.ny;
    const scale = dot > 0.01 ? distance / dot : distance;
    expanded.push({
      x: polygon[i].x + bx * scale,
      y: polygon[i].y + by * scale,
    });
  }
  return expanded;
}

export function smoothClosedPath(polygon) {
  const n = polygon.length;
  if (n < 3) return "";
  const tension = 0.22;
  let d = `M ${polygon[0].x} ${polygon[0].y}`;
  for (let i = 0; i < n; i += 1) {
    const p0 = polygon[(i - 1 + n) % n];
    const p1 = polygon[i];
    const p2 = polygon[(i + 1) % n];
    const p3 = polygon[(i + 2) % n];
    const cp1x = p1.x + (p2.x - p0.x) * tension;
    const cp1y = p1.y + (p2.y - p0.y) * tension;
    const cp2x = p2.x - (p3.x - p1.x) * tension;
    const cp2y = p2.y - (p3.y - p1.y) * tension;
    d += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${p2.x} ${p2.y}`;
  }
  d += " Z";
  return d;
}

export function positionRing(items, focal, radiusX, radiusY, r, angleOffset = 0) {
  items.forEach((node, index) => {
    const angle = angleOffset - Math.PI / 2 + (index / Math.max(items.length, 1)) * Math.PI * 2;
    node.x = focal.x + Math.cos(angle) * radiusX;
    node.y = focal.y + Math.sin(angle) * radiusY;
    node.r = r;
  });
}

export function focusTypeOrder(type) {
  const order = { law: 0, concept: 1, quantity: 2, mathematical_tool: 3, experiment: 4, map: 5 };
  return order[type] ?? 99;
}

export function rankFocusNodes(nodes, { dedupeNodes }) {
  return dedupeNodes(nodes).sort((a, b) => {
    const typeOrder = focusTypeOrder(a.type) - focusTypeOrder(b.type);
    if (typeOrder !== 0) return typeOrder;
    return b.degree - a.degree;
  });
}

export function buildEdgePath(source, target) {
  const mx = (source.x + target.x) / 2;
  const my = (source.y + target.y) / 2;
  const dx = target.x - source.x;
  const dy = target.y - source.y;
  const distance = Math.max(Math.hypot(dx, dy), 1);
  const curve = distance * 0.12;
  const nx = -dy / distance;
  const ny = dx / distance;
  return `M ${source.x} ${source.y} Q ${mx + nx * curve} ${my + ny * curve} ${target.x} ${target.y}`;
}
