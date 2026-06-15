export function collisionHalfHeight(node) {
  return (node.r || 0) + 12;
}

export function collisionHalfWidth(node, { visibleTitle }) {
  if (!visibleTitle) return (node.r || 0) + 6;
  const estimatedHalfWidth = Math.min(118, Math.max(0, Array.from(visibleTitle).length * 9.5));
  return Math.max((node.r || 0) + 6, estimatedHalfWidth + 14);
}

export function collisionRadius(node, { getCollisionHalfWidth, getCollisionHalfHeight = collisionHalfHeight }) {
  return Math.max(getCollisionHalfWidth(node), getCollisionHalfHeight(node));
}

export function relaxLayout(nodes, options = {}) {
  const iterations = options.iterations || 40;
  const padding = options.padding || 10;
  const lockDomains = Boolean(options.lockDomains);
  const lockFocal = Boolean(options.lockFocal);
  const enforceBounds = Boolean(options.enforceBounds);
  const getCollisionHalfWidth = options.getCollisionHalfWidth;
  const getCollisionHalfHeight = options.getCollisionHalfHeight || collisionHalfHeight;
  const clampNodes = options.clampNodes;

  for (let step = 0; step < iterations; step += 1) {
    for (let i = 0; i < nodes.length; i += 1) {
      for (let j = i + 1; j < nodes.length; j += 1) {
        const a = nodes[i];
        const b = nodes[j];
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        const overlapX = getCollisionHalfWidth(a) + getCollisionHalfWidth(b) + padding - Math.abs(dx);
        const overlapY = getCollisionHalfHeight(a) + getCollisionHalfHeight(b) + padding - Math.abs(dy);
        if (overlapX <= 0 || overlapY <= 0) continue;

        const aLocked = (lockDomains && a.type === "domain") || (lockFocal && a.focal);
        const bLocked = (lockDomains && b.type === "domain") || (lockFocal && b.focal);
        const movableCount = Number(!aLocked) + Number(!bLocked);
        if (!movableCount) continue;

        if (overlapX < overlapY) {
          const direction = dx === 0 ? (i % 2 === 0 ? 1 : -1) : Math.sign(dx);
          const push = overlapX / movableCount;
          if (!aLocked) a.x -= direction * push;
          if (!bLocked) b.x += direction * push;
        } else {
          const direction = dy === 0 ? (j % 2 === 0 ? 1 : -1) : Math.sign(dy);
          const push = overlapY / movableCount;
          if (!aLocked) a.y -= direction * push;
          if (!bLocked) b.y += direction * push;
        }
      }
    }

    if (enforceBounds && clampNodes) {
      clampNodes(nodes, { preserveFocus: lockFocal });
    }
  }
}
