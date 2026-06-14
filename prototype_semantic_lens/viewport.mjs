export function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

export function updateViewportTransform(viewportEl, panX, panY, zoom) {
  viewportEl.setAttribute("transform", `translate(${panX} ${panY}) scale(${zoom})`);
}

export function clientToSvgPoint(svg, clientX, clientY) {
  const point = svg.createSVGPoint();
  point.x = clientX;
  point.y = clientY;
  const matrix = svg.getScreenCTM();
  return matrix ? point.matrixTransform(matrix.inverse()) : { x: clientX, y: clientY };
}

export function getSceneBounds(nodes, canvasWidth, canvasHeight) {
  if (!nodes.length) return { minX: 0, minY: 0, maxX: canvasWidth, maxY: canvasHeight };
  const xs = nodes.map((node) => [node.x - node.r, node.x + node.r]).flat();
  const ys = nodes.map((node) => [node.y - node.r, node.y + node.r]).flat();
  return {
    minX: Math.min(...xs) - 24,
    maxX: Math.max(...xs) + 24,
    minY: Math.min(...ys) - 24,
    maxY: Math.max(...ys) + 24,
  };
}

export function getNavigationBounds(nodes, canvasWidth, canvasHeight) {
  const scene = getSceneBounds(nodes, canvasWidth, canvasHeight);
  const horizontalMargin = canvasWidth * 0.25;
  const verticalMargin = canvasHeight * 0.25;
  return {
    minX: Math.min(scene.minX, -horizontalMargin),
    maxX: Math.max(scene.maxX, canvasWidth + horizontalMargin),
    minY: Math.min(scene.minY, -verticalMargin),
    maxY: Math.max(scene.maxY, canvasHeight + verticalMargin),
  };
}

export function updateMiniMapViewport(minimapViewportEl, bounds, viewportState) {
  if (!bounds) return;
  const { width, height, padding, panX, panY, zoom, canvasWidth, canvasHeight } = viewportState;
  const availableWidth = width - padding * 2;
  const availableHeight = height - padding * 2;
  const sceneWidth = Math.max(bounds.maxX - bounds.minX, 1);
  const sceneHeight = Math.max(bounds.maxY - bounds.minY, 1);
  const viewWorldWidth = canvasWidth / zoom;
  const viewWorldHeight = canvasHeight / zoom;
  const viewWidth = clamp((viewWorldWidth / sceneWidth) * availableWidth, 32, availableWidth);
  const viewHeight = clamp((viewWorldHeight / sceneHeight) * availableHeight, 24, availableHeight);
  const visibleLeft = (-panX) / zoom;
  const visibleTop = (-panY) / zoom;
  const x = clamp(padding + ((visibleLeft - bounds.minX) / sceneWidth) * availableWidth, padding, width - padding - viewWidth);
  const y = clamp(padding + ((visibleTop - bounds.minY) / sceneHeight) * availableHeight, padding, height - padding - viewHeight);
  minimapViewportEl.setAttribute("x", String(x));
  minimapViewportEl.setAttribute("y", String(y));
  minimapViewportEl.setAttribute("width", String(viewWidth));
  minimapViewportEl.setAttribute("height", String(viewHeight));
}

export function projectMiniMapClick({ clientX, clientY, rect, bounds, width, height, padding }) {
  const localX = ((clientX - rect.left) / rect.width) * width;
  const localY = ((clientY - rect.top) / rect.height) * height;
  return {
    worldX: bounds.minX + ((localX - padding) / (width - padding * 2)) * (bounds.maxX - bounds.minX),
    worldY: bounds.minY + ((localY - padding) / (height - padding * 2)) * (bounds.maxY - bounds.minY),
  };
}

export function clampNodesToViewport(nodes, options = {}) {
  const {
    padding = 64,
    preserveFocus = false,
    useCollisionRadius = false,
    collisionRadius = (node) => node.r,
    canvasWidth,
    canvasHeight,
  } = options;
  for (const node of nodes) {
    if (preserveFocus && node.focal) continue;
    const radius = useCollisionRadius ? collisionRadius(node) : node.r;
    const minX = padding + radius;
    const maxX = canvasWidth - padding - radius;
    const minY = padding + node.r;
    const maxY = canvasHeight - padding - node.r;
    node.x = clamp(node.x, minX, maxX);
    node.y = clamp(node.y, minY, maxY);
  }
}
