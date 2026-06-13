const GRAPH_URL = "../physics_graph.json";
const DETAILS_URL = "../physics_note_details.json";
const CANVAS_WIDTH = 1440;
const CANVAS_HEIGHT = 960;
const CENTER_X = 720;
const CENTER_Y = 480;

const TAXONOMY_LABELS = {
  mechanics: "力學",
  electromagnetism: "電磁學",
  waves_optics: "波動與光學",
  foundations: "基礎總論",
  thermo_fluids: "熱學與流體",
  modern_physics: "近代物理",
  analytical_dynamics: "解析動力學",
  uncategorized: "未分類",
};

const TAXONOMY_ORDER = [
  "foundations",
  "mechanics",
  "analytical_dynamics",
  "electromagnetism",
  "waves_optics",
  "thermo_fluids",
  "modern_physics",
  "uncategorized",
];

const TYPE_LABELS = {
  root: "知識圖譜",
  domain: "領域",
  map: "導覽頁",
  law: "定律",
  concept: "概念",
  quantity: "物理量",
  mathematical_tool: "數學工具",
  experiment: "實驗",
};

const RELATION_LABELS = {
  requires: "先備關係",
  derives_to: "可推導出",
  formalized_by: "數學支撐",
  related_to: "相關概念",
  organized_by: "主題收納",
  verified_by: "驗證實驗",
  measures: "量測對應",
  uses: "直接使用",
  explains: "延伸視角",
};

const SEMANTIC_EDGE_TYPES = new Set([
  "requires",
  "derives_to",
  "formalized_by",
  "related_to",
  "organized_by",
  "verified_by",
  "measures",
  "uses",
  "explains",
]);

const FOCUS_INNER_TYPES = new Set(["requires", "formalized_by"]);
const FOCUS_OUTER_TYPES = new Set(["derives_to", "verified_by", "measures", "uses", "explains"]);
const FOCUS_RELATED_TYPES = new Set(["related_to", "organized_by"]);
const OVERVIEW_QUOTAS = {
  map: 2,
  law: 3,
  concept: 4,
  quantity: 2,
  mathematical_tool: 2,
  experiment: 1,
};

const state = {
  graph: null,
  details: {},
  nodeMap: new Map(),
  zoom: 1,
  panX: 0,
  panY: 0,
  mode: "overview",
  query: "",
  selectedNodeId: null,
  overviewNodes: [],
  overviewEdges: [],
  focusNodes: [],
  focusEdges: [],
  miniMapBounds: null,
  dragging: {
    active: false,
    pointerId: null,
    startX: 0,
    startY: 0,
    basePanX: 0,
    basePanY: 0,
  },
};

const els = {
  graphFrame: document.getElementById("graphFrame"),
  minimapSvg: document.getElementById("minimapSvg"),
  viewport: document.getElementById("viewport"),
  ringLayer: document.getElementById("ringLayer"),
  edgeLayer: document.getElementById("edgeLayer"),
  nodeLayer: document.getElementById("nodeLayer"),
  searchInput: document.getElementById("searchInput"),
  zoomSlider: document.getElementById("zoomSlider"),
  zoomLabel: document.getElementById("zoomLabel"),
  zoomInButton: document.getElementById("zoomInButton"),
  zoomOutButton: document.getElementById("zoomOutButton"),
  fitButton: document.getElementById("fitButton"),
  backButton: document.getElementById("backButton"),
  overviewModeButton: document.getElementById("overviewModeButton"),
  focusModeButton: document.getElementById("focusModeButton"),
  breadcrumb: document.getElementById("breadcrumb"),
  graphHint: document.getElementById("graphHint"),
  overviewBadgeText: document.getElementById("overviewBadgeText"),
  minimapLayer: document.getElementById("minimapLayer"),
  minimapViewport: document.getElementById("minimapViewport"),
  minimapModeLabel: document.getElementById("minimapModeLabel"),
  detailType: document.getElementById("detailType"),
  detailTitle: document.getElementById("detailTitle"),
  detailSummary: document.getElementById("detailSummary"),
  detailMeta: document.getElementById("detailMeta"),
  detailTaxonomyBadge: document.getElementById("detailTaxonomyBadge"),
  prereqList: document.getElementById("prereqList"),
  extensionList: document.getElementById("extensionList"),
  relatedList: document.getElementById("relatedList"),
  prereqCount: document.getElementById("prereqCount"),
  extensionCount: document.getElementById("extensionCount"),
  relatedCount: document.getElementById("relatedCount"),
  detailPath: document.getElementById("detailPath"),
  statsStrip: document.getElementById("statsStrip"),
  focusActionButton: document.getElementById("focusActionButton"),
};

init().catch((error) => {
  console.error(error);
  els.detailTitle.textContent = "載入失敗";
  els.detailSummary.textContent = String(error.message || error);
});

async function init() {
  const [graphResponse, detailResponse] = await Promise.all([fetch(GRAPH_URL), fetch(DETAILS_URL)]);
  const rawGraph = await graphResponse.json();
  const rawDetails = await detailResponse.json();

  state.details = rawDetails;
  state.graph = normalizeGraph(rawGraph);
  buildOverviewScene();
  bindEvents();
  setZoom(1);
  render();
}

function normalizeGraph(rawGraph) {
  const degreeMap = new Map();
  const semanticEdges = rawGraph.edges.filter((edge) => SEMANTIC_EDGE_TYPES.has(edge.type));
  for (const edge of semanticEdges) {
    degreeMap.set(edge.source, (degreeMap.get(edge.source) || 0) + 1);
    degreeMap.set(edge.target, (degreeMap.get(edge.target) || 0) + 1);
  }

  const nodes = rawGraph.nodes.map((node) => {
    const taxonomy = node.taxonomy_domain || "uncategorized";
    const degree = degreeMap.get(node.id) || 0;
    const tier = inferTier(node, degree);
    return {
      ...node,
      taxonomy,
      degree,
      tier,
      shortTitle: shorten(node.title, 12),
      searchText: [node.title, node.summary, node.type, node.domain, taxonomy, ...(node.tags || [])]
        .filter(Boolean)
        .join(" ")
        .toLowerCase(),
    };
  });

  const nodeMap = new Map(nodes.map((node) => [node.id, node]));
  state.nodeMap = nodeMap;

  const domainHubs = TAXONOMY_ORDER.map((taxonomy) => ({
    id: `domain::${taxonomy}`,
    title: TAXONOMY_LABELS[taxonomy],
    shortTitle: TAXONOMY_LABELS[taxonomy],
    summary: `${TAXONOMY_LABELS[taxonomy]} 的總覽樞紐。`,
    type: "domain",
    taxonomy,
    tier: 0,
    degree: 0,
    domain: "",
    tags: [],
    searchText: `${TAXONOMY_LABELS[taxonomy]} ${taxonomy}`.toLowerCase(),
  }));

  for (const hub of domainHubs) {
    nodeMap.set(hub.id, hub);
  }

  const overviewRoot = {
    id: "root::physics",
    title: "物理知識圖譜",
    shortTitle: "物理知識圖譜",
    summary: "從領域總覽進入概念、定律與推導關係。",
    type: "root",
    taxonomy: "all",
    tier: 0,
    degree: domainHubs.length,
    domain: "",
    tags: [],
    searchText: "物理 知識圖譜 總覽 physics knowledge map",
  };
  nodeMap.set(overviewRoot.id, overviewRoot);

  return { nodes, domainHubs, overviewRoot, edges: semanticEdges };
}

function inferTier(node, degree) {
  if (node.type === "map") return 0;
  if (node.type === "law" || degree >= 24) return 1;
  if (node.type === "quantity" || node.type === "mathematical_tool" || node.type === "experiment") return 2;
  return degree >= 10 ? 1 : 2;
}

function buildOverviewScene() {
  const sceneNodes = [];
  const sceneEdges = [];
  const chosenIds = new Set();
  const hubByTaxonomy = new Map();
  const overviewRoot = {
    ...state.graph.overviewRoot,
    x: CENTER_X,
    y: CENTER_Y,
    r: 76,
    focal: true,
  };
  sceneNodes.push(overviewRoot);

  state.graph.domainHubs.forEach((hub, index) => {
    const angle = (-Math.PI / 2) + (index / state.graph.domainHubs.length) * Math.PI * 2;
    const placed = {
      ...hub,
      x: CENTER_X + Math.cos(angle) * 350,
      y: CENTER_Y + Math.sin(angle) * 276,
      r: 56,
      sectorAngle: angle,
    };
    hubByTaxonomy.set(hub.taxonomy, placed);
    sceneNodes.push(placed);
    sceneEdges.push({
      source: overviewRoot.id,
      target: hub.id,
      type: "organized_by",
      family: "organized_by",
    });
  });

  for (const taxonomy of TAXONOMY_ORDER) {
    const hub = hubByTaxonomy.get(taxonomy);
    if (!hub) continue;
    const pool = state.graph.nodes.filter((node) => node.taxonomy === taxonomy);
    const selected = selectOverviewNodesForTaxonomy(pool);
    const bandWidth = 0.84;

    selected.forEach((node, index) => {
      const ratio = selected.length <= 1 ? 0.5 : index / (selected.length - 1);
      const angle = hub.sectorAngle - bandWidth / 2 + ratio * bandWidth;
      const localRadiusX = node.tier === 0 ? 68 : node.tier === 1 ? 126 : 182;
      const localRadiusY = node.tier === 0 ? 52 : node.tier === 1 ? 94 : 140;
      const placed = {
        ...node,
        x: hub.x + Math.cos(angle) * localRadiusX,
        y: hub.y + Math.sin(angle) * localRadiusY,
        r: node.type === "map" ? 38 : node.tier === 1 ? 28 : 22,
      };
      chosenIds.add(node.id);
      sceneNodes.push(placed);
      sceneEdges.push({
        source: hub.id,
        target: node.id,
        type: "organized_by",
        family: "organized_by",
      });
    });
  }

  for (const edge of state.graph.edges) {
    if (!chosenIds.has(edge.source) || !chosenIds.has(edge.target)) continue;
    if (edge.type === "organized_by") continue;
    if (edge.type === "related_to" && weakLink(edge)) continue;
    if ((edge.type === "uses" || edge.type === "explains") && weakUse(edge)) continue;
    sceneEdges.push({ ...edge, family: edge.type });
  }

  relaxLayout(sceneNodes, { iterations: 220, padding: 18, lockDomains: false, lockFocal: true, enforceBounds: true });
  clampNodesToViewport(sceneNodes, { padding: 72, preserveFocus: false });
  state.overviewNodes = sceneNodes;
  state.overviewEdges = dedupeEdges(sceneEdges);
}

function selectOverviewNodesForTaxonomy(pool) {
  const selected = [];
  for (const type of ["map", "law", "concept", "quantity", "mathematical_tool", "experiment"]) {
    const quota = OVERVIEW_QUOTAS[type] || 0;
    const matches = pool
      .filter((node) => node.type === type)
      .sort((a, b) => b.degree - a.degree)
      .slice(0, quota);
    selected.push(...matches);
  }
  return dedupeNodes(selected);
}

function weakLink(edge) {
  const a = state.nodeMap.get(edge.source);
  const b = state.nodeMap.get(edge.target);
  return (a?.degree || 0) < 14 && (b?.degree || 0) < 14;
}

function weakUse(edge) {
  const a = state.nodeMap.get(edge.source);
  const b = state.nodeMap.get(edge.target);
  return Math.min(a?.degree || 0, b?.degree || 0) < 10;
}

function buildFocusScene(nodeId) {
  const focalSource = state.nodeMap.get(nodeId);
  if (!focalSource) return;

  const focal = { ...focalSource, x: 670, y: 470, r: 68, focal: true };
  const edges = [];
  const inner = [];
  const outer = [];
  const related = [];

  for (const edge of state.graph.edges) {
    if (edge.source !== nodeId && edge.target !== nodeId) continue;
    const otherId = edge.source === nodeId ? edge.target : edge.source;
    const other = state.nodeMap.get(otherId);
    if (!other || other.type === "domain") continue;
    const copy = { ...other };
    if (FOCUS_INNER_TYPES.has(edge.type)) inner.push(copy);
    else if (FOCUS_OUTER_TYPES.has(edge.type)) outer.push(copy);
    else if (FOCUS_RELATED_TYPES.has(edge.type)) related.push(copy);
    edges.push({ ...edge, family: edge.type });
  }

  const innerNodes = rankFocusNodes(inner).slice(0, 6);
  const outerNodes = rankFocusNodes(outer).slice(0, 8);
  const relatedNodes = rankFocusNodes(related).slice(0, 6);
  const sceneNodes = [focal];

  positionRing(innerNodes, focal, 254, 194, 34, 0);
  positionRing(outerNodes, focal, 430, 336, 30, 0);
  positionRing(relatedNodes, focal, 334, 262, 24, Math.PI / 7);

  sceneNodes.push(...dedupeNodes([...innerNodes, ...outerNodes, ...relatedNodes]));
  relaxLayout(sceneNodes, { iterations: 100, padding: 16, lockDomains: false, lockFocal: true, enforceBounds: true });
  clampNodesToViewport(sceneNodes, { padding: 84, preserveFocus: true });
  state.focusNodes = sceneNodes;
  state.focusEdges = dedupeEdges(
    edges.filter((edge) => sceneNodes.some((node) => node.id === edge.source) && sceneNodes.some((node) => node.id === edge.target))
  );
}

function positionRing(items, focal, radiusX, radiusY, r, angleOffset = 0) {
  items.forEach((node, index) => {
    const angle = angleOffset - Math.PI / 2 + (index / Math.max(items.length, 1)) * Math.PI * 2;
    node.x = focal.x + Math.cos(angle) * radiusX;
    node.y = focal.y + Math.sin(angle) * radiusY;
    node.r = r;
  });
}

function rankFocusNodes(nodes) {
  return dedupeNodes(nodes).sort((a, b) => {
    const typeOrder = focusTypeOrder(a.type) - focusTypeOrder(b.type);
    if (typeOrder !== 0) return typeOrder;
    return b.degree - a.degree;
  });
}

function focusTypeOrder(type) {
  const order = { law: 0, concept: 1, quantity: 2, mathematical_tool: 3, experiment: 4, map: 5 };
  return order[type] ?? 99;
}

function bindEvents() {
  els.searchInput.addEventListener("input", () => {
    state.query = els.searchInput.value.trim().toLowerCase();
    render();
  });

  els.zoomSlider.addEventListener("input", () => {
    setZoom(Number(els.zoomSlider.value) / 100);
    render();
  });

  els.zoomInButton.addEventListener("click", () => {
    setZoom(state.zoom * 1.15);
    render();
  });

  els.zoomOutButton.addEventListener("click", () => {
    setZoom(state.zoom / 1.15);
    render();
  });

  els.fitButton.addEventListener("click", () => {
    state.panX = 0;
    state.panY = 0;
    setZoom(state.mode === "overview" ? 1 : 0.98);
    render();
  });

  els.backButton.addEventListener("click", goToOverview);
  els.overviewModeButton.addEventListener("click", goToOverview);

  els.focusModeButton.addEventListener("click", () => {
    if (state.selectedNodeId) {
      state.mode = "focus";
      buildFocusScene(state.selectedNodeId);
      render();
    }
  });

  els.focusActionButton.addEventListener("click", () => {
    if (state.selectedNodeId) {
      state.mode = "focus";
      buildFocusScene(state.selectedNodeId);
      render();
    }
  });

  els.graphFrame.addEventListener("pointerdown", onPointerDown);
  els.graphFrame.addEventListener("wheel", onWheel, { passive: false });
  els.minimapSvg.addEventListener("click", onMiniMapClick);
  window.addEventListener("pointermove", onPointerMove);
  window.addEventListener("pointerup", onPointerUp);
  window.addEventListener("pointercancel", onPointerUp);
}

function goToOverview() {
  state.mode = "overview";
  state.selectedNodeId = null;
  state.panX = 0;
  state.panY = 0;
  setZoom(1);
  render();
}

function onPointerDown(event) {
  if (event.button !== 0) return;
  if (
    typeof event.target.closest === "function" &&
    event.target.closest(".node, button, input, a, .minimap-card")
  ) return;
  state.dragging.active = true;
  state.dragging.pointerId = event.pointerId;
  const point = clientToSvgPoint(event.clientX, event.clientY);
  state.dragging.startX = point.x;
  state.dragging.startY = point.y;
  state.dragging.basePanX = state.panX;
  state.dragging.basePanY = state.panY;
  els.graphFrame.setPointerCapture?.(event.pointerId);
  els.graphFrame.classList.add("is-panning");
  event.preventDefault();
}

function onPointerMove(event) {
  if (!state.dragging.active || event.pointerId !== state.dragging.pointerId) return;
  const point = clientToSvgPoint(event.clientX, event.clientY);
  const deltaX = point.x - state.dragging.startX;
  const deltaY = point.y - state.dragging.startY;
  state.panX = state.dragging.basePanX + deltaX;
  state.panY = state.dragging.basePanY + deltaY;
  updateViewportTransform();
  updateMiniMapViewport();
}

function onPointerUp(event) {
  if (!state.dragging.active || event.pointerId !== state.dragging.pointerId) return;
  els.graphFrame.releasePointerCapture?.(event.pointerId);
  state.dragging.active = false;
  state.dragging.pointerId = null;
  els.graphFrame.classList.remove("is-panning");
}

function onWheel(event) {
  if (typeof event.target.closest === "function" && event.target.closest(".zoom-card, .minimap-card")) return;
  event.preventDefault();

  const pointer = clientToSvgPoint(event.clientX, event.clientY);
  const worldX = (pointer.x - state.panX) / state.zoom;
  const worldY = (pointer.y - state.panY) / state.zoom;
  const factor = Math.exp(-event.deltaY * 0.0015);
  const nextZoom = clamp(state.zoom * factor, 0.55, 2.6);

  state.panX = pointer.x - worldX * nextZoom;
  state.panY = pointer.y - worldY * nextZoom;
  setZoom(nextZoom);
  render();
}

function setZoom(value) {
  state.zoom = clamp(value, 0.55, 2.6);
  els.zoomSlider.value = String(Math.round(state.zoom * 100));
  els.zoomLabel.textContent = `${Math.round(state.zoom * 100)}%`;
  updateViewportTransform();
}

function updateViewportTransform() {
  els.viewport.setAttribute("transform", `translate(${state.panX} ${state.panY}) scale(${state.zoom})`);
}

function clientToSvgPoint(clientX, clientY) {
  const svg = els.graphFrame.querySelector(".graph-svg");
  const point = svg.createSVGPoint();
  point.x = clientX;
  point.y = clientY;
  const matrix = svg.getScreenCTM();
  return matrix ? point.matrixTransform(matrix.inverse()) : { x: clientX, y: clientY };
}

function render() {
  updateViewportTransform();
  const scene = state.mode === "focus" && state.selectedNodeId
    ? ensureFocusScene()
    : {
        nodes: filterOverviewNodes(state.overviewNodes),
        edges: filterOverviewEdges(state.overviewEdges),
      };

  relaxLayout(scene.nodes, {
    iterations: 240,
    padding: state.mode === "focus" ? 14 : 18,
    lockFocal: true,
    enforceBounds: state.mode === "focus",
  });
  renderRings(scene.nodes);
  renderEdges(scene.edges, scene.nodes);
  renderNodes(scene.nodes);
  renderMiniMap(scene.nodes);
  renderDetail();
  updateModeUI(scene.nodes);
}

function ensureFocusScene() {
  buildFocusScene(state.selectedNodeId);
  return { nodes: state.focusNodes, edges: state.focusEdges };
}

function filterOverviewNodes(nodes) {
  return nodes.filter((node) => {
    if (state.query && !node.searchText?.includes(state.query) && node.type !== "domain" && node.type !== "root") return false;
    return true;
  });
}

function filterOverviewEdges(edges) {
  const visibleIds = new Set(filterOverviewNodes(state.overviewNodes).map((node) => node.id));
  return edges.filter((edge) => visibleIds.has(edge.source) && visibleIds.has(edge.target));
}

function semanticTierFromZoom(zoom) {
  if (zoom < 1.15) return 0;
  if (zoom < 1.55) return 1;
  if (zoom < 2) return 2;
  return 3;
}

function renderRings(nodes) {
  if (state.mode === "overview") {
    els.ringLayer.innerHTML = `
      <circle class="overview-halo" cx="${CENTER_X}" cy="${CENTER_Y}" r="118"></circle>
      <text class="overview-caption" x="${CENTER_X}" y="${CENTER_Y + 112}" text-anchor="middle">選擇領域或概念以進入焦點視圖</text>
    `;
    return;
  }

  const focal = nodes[0];
  if (!focal) {
    els.ringLayer.innerHTML = "";
    return;
  }
  els.ringLayer.innerHTML = [
    `<circle class="ring-circle inner" cx="${focal.x}" cy="${focal.y}" r="250"></circle>`,
    `<circle class="ring-circle outer" cx="${focal.x}" cy="${focal.y}" r="430"></circle>`,
    `<text class="ring-label" x="${focal.x}" y="${focal.y - 258}" text-anchor="middle">先備</text>`,
    `<text class="ring-label" x="${focal.x}" y="${focal.y + 440}" text-anchor="middle">延伸</text>`,
  ].join("");
}

function renderEdges(edges, nodes) {
  const sceneNodeMap = new Map(nodes.map((node) => [node.id, node]));
  const visibleIds = new Set(nodes.map((node) => node.id));
  const markup = edges
    .filter((edge) => visibleIds.has(edge.source) && visibleIds.has(edge.target))
    .map((edge) => {
      const source = sceneNodeMap.get(edge.source) || state.nodeMap.get(edge.source);
      const target = sceneNodeMap.get(edge.target) || state.nodeMap.get(edge.target);
      if (!source || !target) return "";
      const highlighted = state.selectedNodeId && (edge.source === state.selectedNodeId || edge.target === state.selectedNodeId);
      return `<path class="edge ${edge.family} ${highlighted ? "is-highlighted" : "is-muted"}" d="${buildEdgePath(source, target)}"></path>`;
    })
    .join("");
  els.edgeLayer.innerHTML = markup;
}

function renderNodes(nodes) {
  const labelTier = semanticTierFromZoom(state.zoom);
  const markup = nodes
    .map((node) => {
      const selected = node.id === state.selectedNodeId;
      const dimmed = state.selectedNodeId && !selected && !isConnectedToSelected(node.id);
      const title = resolveVisibleTitle(node, labelTier, selected);
      return `
        <g class="node ${node.type} ${selected ? "is-selected" : ""} ${node.focal ? "focal" : ""} ${dimmed ? "is-dimmed" : ""}" data-node-id="${escapeHtml(node.id)}" transform="translate(${node.x} ${node.y})" role="button" tabindex="0" aria-label="${escapeHtml(`開啟 ${node.title}`)}">
          <circle class="node-hit" r="${Math.max(node.r + 14, 28)}"></circle>
          <circle class="node-circle" r="${node.r}"></circle>
          ${title ? `<text class="node-title" y="0">${escapeHtml(title)}</text>` : ""}
        </g>
      `;
    })
    .join("");

  els.nodeLayer.innerHTML = markup;
  for (const element of els.nodeLayer.querySelectorAll(".node")) {
    element.addEventListener("click", (event) => handleNodeSelect(event.currentTarget.dataset.nodeId));
    element.addEventListener("keydown", (event) => {
      if (event.key !== "Enter" && event.key !== " ") return;
      event.preventDefault();
      handleNodeSelect(event.currentTarget.dataset.nodeId);
    });
  }
}

function renderMiniMap(nodes) {
  const width = 220;
  const height = 140;
  const padding = 10;
  const bounds = getNavigationBounds(nodes);
  state.miniMapBounds = bounds;
  const scaleX = (width - padding * 2) / Math.max(bounds.maxX - bounds.minX, 1);
  const scaleY = (height - padding * 2) / Math.max(bounds.maxY - bounds.minY, 1);
  const sceneMarkup = nodes.map((node) => {
    const x = padding + (node.x - bounds.minX) * scaleX;
    const y = padding + (node.y - bounds.minY) * scaleY;
    const r = Math.max(node.type === "domain" ? 4.2 : node.focal ? 4 : 2.4, node.r * 0.05);
    return `<circle class="minimap-node ${node.id === state.selectedNodeId ? "focus" : ""}" cx="${x}" cy="${y}" r="${r}"></circle>`;
  }).join("");
  els.minimapLayer.innerHTML = sceneMarkup;
  updateMiniMapViewport(bounds);
  els.minimapModeLabel.textContent = state.mode;
}

function updateMiniMapViewport(bounds = state.miniMapBounds) {
  if (!bounds) return;
  const width = 220;
  const height = 140;
  const padding = 10;
  const availableWidth = width - padding * 2;
  const availableHeight = height - padding * 2;
  const sceneWidth = Math.max(bounds.maxX - bounds.minX, 1);
  const sceneHeight = Math.max(bounds.maxY - bounds.minY, 1);
  const viewWorldWidth = CANVAS_WIDTH / state.zoom;
  const viewWorldHeight = CANVAS_HEIGHT / state.zoom;
  const viewWidth = clamp((viewWorldWidth / sceneWidth) * availableWidth, 32, availableWidth);
  const viewHeight = clamp((viewWorldHeight / sceneHeight) * availableHeight, 24, availableHeight);
  const visibleLeft = (-state.panX) / state.zoom;
  const visibleTop = (-state.panY) / state.zoom;
  const x = clamp(padding + ((visibleLeft - bounds.minX) / sceneWidth) * availableWidth, padding, width - padding - viewWidth);
  const y = clamp(padding + ((visibleTop - bounds.minY) / sceneHeight) * availableHeight, padding, height - padding - viewHeight);
  els.minimapViewport.setAttribute("x", String(x));
  els.minimapViewport.setAttribute("y", String(y));
  els.minimapViewport.setAttribute("width", String(viewWidth));
  els.minimapViewport.setAttribute("height", String(viewHeight));
}

function resolveVisibleTitle(node, tier, selected) {
  if (node.type === "domain" || node.type === "root") return node.title;
  if (state.mode === "focus") return tier >= 1 ? node.title : node.shortTitle;
  if (tier === 0) return node.type === "map" || selected ? node.shortTitle : "";
  if (tier === 1) return node.shortTitle;
  return node.title;
}

function handleNodeSelect(nodeId) {
  const node = state.nodeMap.get(nodeId);
  if (!node) return;
  if (node.type === "root") {
    goToOverview();
    return;
  }
  if (node.type === "domain") {
    goToOverviewAndCenterTaxonomy(node.taxonomy);
    return;
  }
  state.selectedNodeId = nodeId;
  state.mode = "focus";
  state.panX = 0;
  state.panY = 0;
  setZoom(0.98);
  buildFocusScene(nodeId);
  render();
}

function onMiniMapClick(event) {
  const rect = els.minimapSvg.getBoundingClientRect();
  const localX = ((event.clientX - rect.left) / rect.width) * 220;
  const localY = ((event.clientY - rect.top) / rect.height) * 140;
  const padding = 10;
  const bounds = state.miniMapBounds || { minX: 0, minY: 0, maxX: CANVAS_WIDTH, maxY: CANVAS_HEIGHT };
  const worldX = bounds.minX + ((localX - padding) / (220 - padding * 2)) * (bounds.maxX - bounds.minX);
  const worldY = bounds.minY + ((localY - padding) / (140 - padding * 2)) * (bounds.maxY - bounds.minY);
  state.panX = CANVAS_WIDTH / 2 - worldX * state.zoom;
  state.panY = CANVAS_HEIGHT / 2 - worldY * state.zoom;
  updateViewportTransform();
  updateMiniMapViewport();
}

function getSceneBounds(nodes) {
  if (!nodes.length) return { minX: 0, minY: 0, maxX: CANVAS_WIDTH, maxY: CANVAS_HEIGHT };
  const xs = nodes.map((node) => [node.x - node.r, node.x + node.r]).flat();
  const ys = nodes.map((node) => [node.y - node.r, node.y + node.r]).flat();
  return {
    minX: Math.min(...xs) - 24,
    maxX: Math.max(...xs) + 24,
    minY: Math.min(...ys) - 24,
    maxY: Math.max(...ys) + 24,
  };
}

function getNavigationBounds(nodes) {
  const scene = getSceneBounds(nodes);
  const horizontalMargin = CANVAS_WIDTH * 0.25;
  const verticalMargin = CANVAS_HEIGHT * 0.25;
  return {
    minX: Math.min(scene.minX, -horizontalMargin),
    maxX: Math.max(scene.maxX, CANVAS_WIDTH + horizontalMargin),
    minY: Math.min(scene.minY, -verticalMargin),
    maxY: Math.max(scene.maxY, CANVAS_HEIGHT + verticalMargin),
  };
}

function clampNodesToViewport(nodes, options = {}) {
  const padding = options.padding || 64;
  const preserveFocus = Boolean(options.preserveFocus);
  const useCollisionRadius = Boolean(options.useCollisionRadius);
  for (const node of nodes) {
    if (preserveFocus && node.focal) continue;
    const radius = useCollisionRadius ? collisionRadius(node) : node.r;
    const minX = padding + radius;
    const maxX = CANVAS_WIDTH - padding - radius;
    const minY = padding + node.r;
    const maxY = CANVAS_HEIGHT - padding - node.r;
    node.x = clamp(node.x, minX, maxX);
    node.y = clamp(node.y, minY, maxY);
  }
}

function updateModeUI(sceneNodes) {
  els.backButton.hidden = state.mode !== "focus";
  els.focusActionButton.hidden = !state.selectedNodeId;
  els.overviewModeButton.classList.toggle("is-active", state.mode === "overview");
  els.focusModeButton.classList.toggle("is-active", state.mode === "focus");

  if (state.mode === "focus" && state.selectedNodeId) {
    const node = state.nodeMap.get(state.selectedNodeId);
    renderBreadcrumb([
      { label: "總覽", action: () => goToOverview() },
      { label: TAXONOMY_LABELS[node.taxonomy] || node.taxonomy, action: () => goToOverviewAndCenterTaxonomy(node.taxonomy) },
      { label: node.title },
    ]);
    els.graphHint.textContent = "中心節點固定；內圈只留先備與數學支撐，外圈只留推導、驗證、量測與應用，灰色膠囊則放弱關聯。";
    els.overviewBadgeText.textContent = "焦點模式把雜訊拿掉，只保留能解釋這個節點如何進入、如何延伸的關係。";
  } else {
    renderBreadcrumb([
      { label: "總覽", action: () => goToOverview() },
      { label: "taxonomy domains" },
    ]);
    els.graphHint.textContent = "拖曳平移、滾輪縮放；中央根節點連接各領域，放大後會依序顯示更細的節點名稱與關係。";
    els.overviewBadgeText.textContent = `目前總覽顯示 ${sceneNodes.filter((node) => node.type !== "domain").length} 個節點骨架，弱關聯與 wikilink 不進主視圖。`;
  }
}

function renderBreadcrumb(items) {
  els.breadcrumb.innerHTML = items.map((item, index) => {
    const part = item.action
      ? `<button class="breadcrumb-button" type="button" data-index="${index}">${escapeHtml(item.label)}</button>`
      : `<span>${escapeHtml(item.label)}</span>`;
    const separator = index < items.length - 1 ? `<span class="breadcrumb-separator">/</span>` : "";
    return `${part}${separator}`;
  }).join("");
  for (const button of els.breadcrumb.querySelectorAll(".breadcrumb-button")) {
    const item = items[Number(button.dataset.index)];
    button.addEventListener("click", item.action);
  }
}

function goToOverviewAndCenterTaxonomy(taxonomy) {
  goToOverview();
  const hub = state.overviewNodes.find((node) => node.id === `domain::${taxonomy}`);
  if (!hub) return;
  state.panX = CANVAS_WIDTH / 2 - hub.x * state.zoom;
  state.panY = CANVAS_HEIGHT / 2 - hub.y * state.zoom;
  updateViewportTransform();
  updateMiniMapViewport();
}

function renderDetail() {
  const node = state.selectedNodeId ? state.nodeMap.get(state.selectedNodeId) : null;
  if (!node) {
    els.detailType.textContent = "概覽";
    els.detailTitle.textContent = "請選取一個節點";
    els.detailSummary.textContent = "這個版本不動舊原型。總覽只保留每個領域的樞紐、導覽頁和高中心性節點，先把圖譜變得可讀，再進入焦點透鏡。";
    els.detailTaxonomyBadge.textContent = "overview";
    els.detailMeta.innerHTML = createMetaItems([
      ["視圖模式", "Semantic Zoom"],
      ["焦點狀態", "未選取"],
      ["關係策略", "語意邊優先"],
      ["節點標籤", "依縮放顯示"],
    ]);
    els.statsStrip.innerHTML = createStatCards([
      ["顯示節點", String(filterOverviewNodes(state.overviewNodes).length - state.graph.domainHubs.length)],
      ["顯示關係", String(filterOverviewEdges(state.overviewEdges).length)],
      ["已隱藏", "wikilink"],
      ["總層級", "3"],
    ]);
    fillRelationSection("prereq", []);
    fillRelationSection("extension", []);
    fillRelationSection("related", []);
    els.detailPath.textContent = "尚未選取節點";
    els.detailPath.removeAttribute("href");
    return;
  }

  const detail = state.details[node.id] || {};
  const relations = collectRelations(node.id);
  els.detailType.textContent = TYPE_LABELS[node.type] || node.type;
  els.detailTitle.textContent = node.title;
  els.detailSummary.textContent = detail.summary || node.summary || "這個節點目前沒有整理好的摘要。";
  els.detailTaxonomyBadge.textContent = TAXONOMY_LABELS[node.taxonomy] || node.taxonomy;
  els.detailMeta.innerHTML = createMetaItems([
    ["領域", TAXONOMY_LABELS[node.taxonomy] || node.taxonomy],
    ["類型", TYPE_LABELS[node.type] || node.type],
    ["語意連結", String(node.degree)],
    ["顯示層級", `Tier ${node.tier}`],
  ]);
  els.statsStrip.innerHTML = createStatCards([
    ["先備", String(relations.requires.length)],
    ["延伸", String(relations.extension.length)],
    ["相關", String(relations.related.length)],
    ["章節", String(detail.sections?.length || 0)],
  ]);

  fillRelationSection("prereq", relations.requires);
  fillRelationSection("extension", relations.extension);
  fillRelationSection("related", relations.related);

  const path = detail.path || node.path;
  if (path) {
    els.detailPath.textContent = path;
    els.detailPath.href = `../${encodeURI(path)}`;
  } else {
    els.detailPath.textContent = "沒有來源路徑";
    els.detailPath.removeAttribute("href");
  }
}

function fillRelationSection(prefix, items) {
  const countEl = els[`${prefix}Count`];
  const listEl = els[`${prefix}List`];
  countEl.textContent = String(items.length);
  listEl.innerHTML = renderPills(items, prefix === "prereq" ? "requires" : prefix === "extension" ? "extension" : "related");
  for (const button of listEl.querySelectorAll(".pill[data-node-id]")) {
    button.addEventListener("click", () => handleNodeSelect(button.dataset.nodeId));
  }
}

function collectRelations(nodeId) {
  const requires = [];
  const extension = [];
  const related = [];
  for (const edge of state.graph.edges) {
    if (edge.source !== nodeId && edge.target !== nodeId) continue;
    const otherId = edge.source === nodeId ? edge.target : edge.source;
    const other = state.nodeMap.get(otherId);
    if (!other || other.type === "domain") continue;
    if (FOCUS_INNER_TYPES.has(edge.type)) requires.push(other);
    else if (FOCUS_OUTER_TYPES.has(edge.type)) extension.push(other);
    else related.push(other);
  }
  return {
    requires: rankFocusNodes(requires).slice(0, 8),
    extension: rankFocusNodes(extension).slice(0, 8),
    related: rankFocusNodes(related).slice(0, 8),
  };
}

function createMetaItems(entries) {
  return entries
    .map(
      ([label, value]) => `
        <div class="meta-item">
          <span class="meta-label">${escapeHtml(label)}</span>
          <span class="meta-value">${escapeHtml(value)}</span>
        </div>`
    )
    .join("");
}

function createStatCards(entries) {
  return entries
    .map(
      ([label, value]) => `
        <div class="stat-card">
          <span>${escapeHtml(label)}</span>
          <strong>${escapeHtml(value)}</strong>
        </div>`
    )
    .join("");
}

function renderPills(items, family) {
  if (!items.length) return "";
  return items
    .map((item) => `<button class="pill" type="button" data-family="${family}" data-node-id="${escapeHtml(item.id)}">${escapeHtml(item.title)}</button>`)
    .join("");
}

function isConnectedToSelected(nodeId) {
  if (!state.selectedNodeId || nodeId === state.selectedNodeId) return true;
  return state.focusEdges.some((edge) =>
    (edge.source === state.selectedNodeId && edge.target === nodeId) ||
    (edge.target === state.selectedNodeId && edge.source === nodeId)
  );
}

function buildEdgePath(source, target) {
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

function relaxLayout(nodes, options = {}) {
  const iterations = options.iterations || 40;
  const padding = options.padding || 10;
  const lockDomains = Boolean(options.lockDomains);
  const lockFocal = Boolean(options.lockFocal);
  const enforceBounds = Boolean(options.enforceBounds);

  for (let step = 0; step < iterations; step += 1) {
    for (let i = 0; i < nodes.length; i += 1) {
      for (let j = i + 1; j < nodes.length; j += 1) {
        const a = nodes[i];
        const b = nodes[j];
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        const overlapX = collisionHalfWidth(a) + collisionHalfWidth(b) + padding - Math.abs(dx);
        const overlapY = collisionHalfHeight(a) + collisionHalfHeight(b) + padding - Math.abs(dy);
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

    if (enforceBounds) {
      clampNodesToViewport(nodes, {
        padding: state.mode === "focus" ? 84 : 72,
        preserveFocus: lockFocal,
        useCollisionRadius: true,
      });
    }
  }
}

function collisionRadius(node) {
  return Math.max(collisionHalfWidth(node), collisionHalfHeight(node));
}

function collisionHalfWidth(node) {
  const label = resolveVisibleTitle(
    node,
    semanticTierFromZoom(state.zoom),
    node.id === state.selectedNodeId
  );
  if (!label) return (node.r || 0) + 6;
  const estimatedHalfWidth = Math.min(118, Math.max(0, Array.from(label).length * 9.5));
  return Math.max((node.r || 0) + 6, estimatedHalfWidth + 14);
}

function collisionHalfHeight(node) {
  return (node.r || 0) + 12;
}

function shorten(text, max) {
  return text.length > max ? `${text.slice(0, max)}…` : text;
}

function dedupeNodes(nodes) {
  const seen = new Set();
  return nodes.filter((node) => {
    if (seen.has(node.id)) return false;
    seen.add(node.id);
    return true;
  });
}

function dedupeEdges(edges) {
  const seen = new Set();
  return edges.filter((edge) => {
    const key = `${edge.source}|${edge.target}|${edge.type}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}
