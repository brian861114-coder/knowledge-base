import {
  SEMANTIC_EDGE_TYPES,
  buildGraphIndex,
  collectDirectionalRelations,
  detailFileNameForNodeId,
  validateDetailPayload,
  validateGraphPayload,
} from "./logic.mjs";
import { createDetailStore } from "./detail-store.mjs";
import {
  buildEmptyDetailView,
  buildNodeDetailView,
  buildNoteSectionHtml,
} from "./detail-renderer.mjs";
import {
  buildMetaItemsHtml,
  buildPillListHtml,
  buildSearchResultsHtml,
  buildStatCardsHtml,
} from "./detail-panel.mjs";
import {
  createFocusState,
  createOverviewState,
  stepBrowseHistory,
} from "./navigation-state.mjs";
import { buildFocusSceneData, buildOverviewSceneData } from "./scene-builder.mjs";
import { buildBreadcrumbHtml, createModeUiState } from "./ui-state.mjs";
import { escapeHtml, renderMarkdown } from "./markdown.mjs";
import { scheduleMathTypeset } from "./mathjax.mjs";
import {
  clamp,
  clampNodesToViewport,
  clientToSvgPoint,
  getNavigationBounds,
  projectMiniMapClick,
  updateMiniMapViewport,
  updateViewportTransform,
} from "./viewport.mjs";
import {
  collisionHalfHeight as baseCollisionHalfHeight,
  collisionHalfWidth as baseCollisionHalfWidth,
  collisionRadius as baseCollisionRadius,
  relaxLayout as runRelaxLayout,
} from "./layout-solver.mjs";
import {
  buildEdgePath,
  convexHull,
  focusTypeOrder,
  offsetPolygon,
  positionRing,
  rankFocusNodes,
  smoothClosedPath,
} from "./scene-geometry.mjs";

const GRAPH_URL = "../physics_graph.json";
const DETAIL_INDEX_URL = "./data/detail-index.json";
const DETAIL_BASE_URL = "./data/details";
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

const DOMAIN_REGION_STYLES = {
  mechanics: { fill: "rgba(232, 240, 254, 0.95)", stroke: "rgba(168, 199, 250, 0.95)" },
  electromagnetism: { fill: "rgba(255, 243, 224, 0.95)", stroke: "rgba(255, 204, 128, 0.95)" },
  waves_optics: { fill: "rgba(224, 247, 250, 0.95)", stroke: "rgba(128, 222, 234, 0.95)" },
  foundations: { fill: "rgba(242, 242, 247, 0.95)", stroke: "rgba(199, 199, 204, 0.95)" },
  thermo_fluids: { fill: "rgba(232, 245, 233, 0.95)", stroke: "rgba(165, 214, 167, 0.95)" },
  modern_physics: { fill: "rgba(237, 231, 246, 0.95)", stroke: "rgba(179, 157, 219, 0.95)" },
  analytical_dynamics: { fill: "rgba(227, 242, 253, 0.95)", stroke: "rgba(144, 202, 249, 0.95)" },
  uncategorized: { fill: "rgba(229, 229, 234, 0.95)", stroke: "rgba(199, 199, 204, 0.95)" },
};

function computeOverviewQuotas(taxonomy, poolSize) {
  return { law: 999, concept: 999, map: 6, quantity: 3, mathematical_tool: 3, experiment: 1 };
}

function selectOverviewNodesForTaxonomy(pool) {
  const selected = [];
  const quotas = computeOverviewQuotas(pool[0]?.taxonomy, pool.length);

  // Laws: all
  const laws = pool.filter((n) => n.type === "law").sort((a, b) => b.degree - a.degree);
  selected.push(...laws);

  // Concepts: bridge (degree>=30) OR standalone (degree>=50)
  const lawIds = new Set(pool.filter((n) => n.type === "law").map((n) => n.id));
  const bridgeSet = new Set();
  for (const edge of state.graph.edges) {
    if (edge.type !== "requires" && edge.type !== "derives_to" && edge.type !== "formalized_by") continue;
    if (lawIds.has(edge.source) && !lawIds.has(edge.target)) bridgeSet.add(edge.target);
    if (lawIds.has(edge.target) && !lawIds.has(edge.source)) bridgeSet.add(edge.source);
  }
  const concepts = pool
    .filter((n) => n.type === "concept")
    .filter((n) => bridgeSet.has(n.id) ? n.degree >= 30 : n.degree >= 50)
    .sort((a, b) => b.degree - a.degree);
  selected.push(...concepts);

  // Quantities: degree >= 25
  const quantities = pool
    .filter((n) => n.type === "quantity" && n.degree >= 25)
    .sort((a, b) => b.degree - a.degree);
  selected.push(...quantities);

  // Maps: use quotas
  for (const type of ["map"]) {
    const quota = quotas[type] || 0;
    const matches = pool
      .filter((node) => node.type === type)
      .sort((a, b) => b.degree - a.degree)
      .slice(0, quota);
    selected.push(...matches);
  }
  return dedupeNodes(selected);
}

const state = {
  graph: null,
  detailStore: null,
  nodeMap: new Map(),
  graphIndex: null,
  zoom: 1,
  panX: 0,
  panY: 0,
  mode: "overview",
  query: "",
  selectedNodeId: null,
  browseHistory: [],
  browseIndex: -1,
  noteViewMode: "preview",
  domainSelection: null,
  typeSelection: null,
  overviewNodes: [],
  overviewEdges: [],
  focusNodes: [],
  focusEdges: [],
  focusSceneNodeId: null,
  domainRegions: new Map(),
  miniMapBounds: null,
  lastSemanticTier: 0,
  searchDebounceId: null,
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
  labelLayer: document.getElementById("labelLayer"),
  searchInput: document.getElementById("searchInput"),
  zoomSlider: document.getElementById("zoomSlider"),
  zoomLabel: document.getElementById("zoomLabel"),
  zoomInButton: document.getElementById("zoomInButton"),
  zoomOutButton: document.getElementById("zoomOutButton"),
  fitButton: document.getElementById("fitButton"),
  browseNav: document.getElementById("browseNav"),
  browseBack: document.getElementById("browseBack"),
  browseForward: document.getElementById("browseForward"),
  backButton: document.getElementById("backButton"),
  overviewModeButton: document.getElementById("overviewModeButton"),
  focusModeButton: document.getElementById("focusModeButton"),
  breadcrumb: document.getElementById("breadcrumb"),
  graphHint: document.getElementById("graphHint"),
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
  const rawGraph = await fetchJson(GRAPH_URL);
  validateGraphPayload(rawGraph);

  state.graph = normalizeGraph(rawGraph);
  state.detailStore = createDetailStore({
    detailIndexUrl: DETAIL_INDEX_URL,
    detailBaseUrl: DETAIL_BASE_URL,
    detailFileNameForNodeId,
    validateDetailPayload,
  });
  await state.detailStore.loadIndex(state.graph.nodes.map((node) => node.id));
  buildOverviewScene();
  buildDomainOverview();
  buildFilters();
  bindEvents();
  setZoom(1);
  render();
}

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`${url} 載入失敗：HTTP ${response.status}`);
  }
  return response.json();
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
  state.graphIndex = buildGraphIndex(nodes, semanticEdges);

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

function buildDomainOverview() {
  const container = document.getElementById("domainOverview");
  if (!container) return;
  container.innerHTML = "";
  const domainMeta = [];
  for (const taxonomy of TAXONOMY_ORDER) {
    const label = TAXONOMY_LABELS[taxonomy] || taxonomy;
    const nodes = state.graph.nodes.filter((n) => n.taxonomy === taxonomy && n.type !== "domain");
    if (!nodes.length) continue;
    const typeCounts = {};
    for (const n of nodes) {
      const t = TYPE_LABELS[n.type] || n.type;
      typeCounts[t] = (typeCounts[t] || 0) + 1;
    }
    domainMeta.push({
      taxonomy,
      label,
      count: nodes.length,
      description: Object.entries(typeCounts).map(([t, c]) => `${t} ${c}`).join("、"),
    });
  }
  for (const meta of domainMeta) {
    const card = document.createElement("button");
    card.type = "button";
    card.className = "domain-card";
    card.innerHTML = `
      <div class="domain-card-count">${meta.count}</div>
      <h3>${escapeHtml(meta.label)}</h3>
      <p>${escapeHtml(meta.description)}</p>
    `;
    card.addEventListener("click", () => goToOverviewAndCenterTaxonomy(meta.taxonomy));
    container.appendChild(card);
  }
}

function buildFilters() {
  const domainContainer = document.getElementById("domainFilters");
  const typeContainer = document.getElementById("typeFilters");
  if (!domainContainer || !typeContainer) return;

  // Domain filters
  state.domainSelection = new Set(TAXONOMY_ORDER);
  domainContainer.innerHTML = "";
  for (const taxonomy of TAXONOMY_ORDER) {
    const label = TAXONOMY_LABELS[taxonomy] || taxonomy;
    const count = state.graph.nodes.filter((n) => n.taxonomy === taxonomy && n.type !== "domain").length;
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "filter-chip active";
    chip.textContent = `${label} ${count}`;
    chip.dataset.value = taxonomy;
    chip.addEventListener("click", () => {
      if (state.domainSelection.has(taxonomy) && state.domainSelection.size > 1) {
        state.domainSelection.delete(taxonomy);
        chip.classList.remove("active");
      } else if (!state.domainSelection.has(taxonomy)) {
        state.domainSelection.add(taxonomy);
        chip.classList.add("active");
      }
      render();
    });
    domainContainer.appendChild(chip);
  }

  // Type filters
  const types = ["map", "law", "concept", "quantity", "mathematical_tool", "experiment"];
  state.typeSelection = new Set(types);
  typeContainer.innerHTML = "";
  for (const type of types) {
    const label = TYPE_LABELS[type] || type;
    const count = state.graph.nodes.filter((n) => n.type === type).length;
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "filter-chip active";
    chip.textContent = `${label} ${count}`;
    chip.dataset.value = type;
    chip.addEventListener("click", () => {
      if (state.typeSelection.has(type) && state.typeSelection.size > 1) {
        state.typeSelection.delete(type);
        chip.classList.remove("active");
      } else if (!state.typeSelection.has(type)) {
        state.typeSelection.add(type);
        chip.classList.add("active");
      }
      render();
    });
    typeContainer.appendChild(chip);
  }
}

function buildOverviewScene() {
  const scene = buildOverviewSceneData(
    {
      graph: state.graph,
      nodeMap: state.nodeMap,
      taxonomyOrder: TAXONOMY_ORDER,
      centerX: CENTER_X,
      centerY: CENTER_Y,
    },
    {
      selectOverviewNodesForTaxonomy,
      weakLink,
      weakUse,
      relaxLayout,
      clampNodesToViewport,
      dedupeEdges,
      smoothClosedPath,
    }
  );
  state.overviewNodes = scene.overviewNodes;
  state.overviewEdges = scene.overviewEdges;
  state.domainRegions = scene.domainRegions;
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
  const scene = buildFocusSceneData(
    {
      nodeId,
      graph: state.graph,
      nodeMap: state.nodeMap,
      graphIndex: state.graphIndex,
      overviewNodes: state.overviewNodes,
      taxonomyLabels: TAXONOMY_LABELS,
    },
    {
      collectDirectionalRelations,
      rankFocusNodes: (nodes) => rankFocusNodes(nodes, { dedupeNodes }),
      dedupeNodes,
      dedupeEdges,
      positionRing,
      relaxLayout,
      clampNodesToViewport,
    }
  );
  if (!scene) return;
  state.focusSceneNodeId = scene.focusSceneNodeId;
  state.focusNodes = scene.focusNodes;
  state.focusEdges = scene.focusEdges;
}

function bindEvents() {
  els.searchInput.addEventListener("input", () => {
    if (state.searchDebounceId) {
      window.clearTimeout(state.searchDebounceId);
    }
    state.searchDebounceId = window.setTimeout(() => {
      state.query = els.searchInput.value.trim().toLowerCase();
      state.searchDebounceId = null;
      render();
    }, 150);
  });

  els.zoomSlider.addEventListener("input", () => {
    setZoom(Number(els.zoomSlider.value) / 100);
    renderForZoomChange();
  });

  els.zoomInButton.addEventListener("click", () => {
    setZoom(state.zoom * 1.15);
    renderForZoomChange();
  });

  els.zoomOutButton.addEventListener("click", () => {
    setZoom(state.zoom / 1.15);
    renderForZoomChange();
  });

  els.fitButton.addEventListener("click", () => {
    state.panX = 0;
    state.panY = 0;
    setZoom(state.mode === "overview" ? 1 : 0.98);
    renderForZoomChange({ forceLayout: true, refreshDetail: false, refreshSearch: false });
  });

  els.backButton.addEventListener("click", goToOverview);
  els.browseBack.addEventListener("click", goBack);
  els.browseForward.addEventListener("click", goForward);

  // Note view toggle (top buttons)
  document.getElementById("noteViewToggle")?.addEventListener("click", (event) => {
    const btn = event.target.closest(".note-view-btn");
    if (!btn) return;
    const mode = btn.dataset.noteMode;
    if (mode && mode !== state.noteViewMode) {
      state.noteViewMode = mode;
      render();
    }
  });

  // Global click handler for wikilinks and relation pills
  document.addEventListener("click", (event) => {
    const nodePill = event.target.closest("[data-node-id]");
    if (nodePill) {
      handleNodeSelect(nodePill.dataset.nodeId);
      return;
    }
    const inlineLink = event.target.closest(".inline-note-link[data-node-id]");
    if (inlineLink) {
      handleNodeSelect(inlineLink.dataset.nodeId);
      return;
    }
    const sectionJump = event.target.closest(".section-jump-button");
    if (sectionJump) {
      const target = document.getElementById(sectionJump.dataset.sectionTarget || "");
      if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
      return;
    }
    const retryDetail = event.target.closest("[data-retry-detail]");
    if (retryDetail) {
      state.detailStore.clearError(retryDetail.dataset.retryDetail);
      void loadDetail(retryDetail.dataset.retryDetail);
    }
  });
  els.overviewModeButton.addEventListener("click", goToOverview);

    els.focusModeButton.addEventListener("click", () => {
      if (state.selectedNodeId) {
        activateFocusNode(state.selectedNodeId, { pushHistory: false });
      }
    });
  
    els.focusActionButton.addEventListener("click", () => {
      if (state.selectedNodeId) {
        activateFocusNode(state.selectedNodeId, { pushHistory: false });
      }
    });

  els.graphFrame.addEventListener("pointerdown", onPointerDown);
  els.graphFrame.addEventListener("wheel", onWheel, { passive: false });
  els.minimapSvg.addEventListener("click", onMiniMapClick);
  window.addEventListener("pointermove", onPointerMove);
  window.addEventListener("pointerup", onPointerUp);
  window.addEventListener("pointercancel", onPointerUp);
}

function applyStatePatch(patch) {
  for (const [key, value] of Object.entries(patch)) {
    if (key === "zoom") {
      setZoom(value);
      continue;
    }
    state[key] = value;
  }
}

function activateFocusNode(nodeId, options = {}) {
  const { pushHistory = true } = options;
  const node = state.nodeMap.get(nodeId);
  if (!node) return;
  applyStatePatch(createFocusState(state, nodeId, { pushHistory }));
  buildFocusScene(nodeId);
  render();
}

function resetOverviewState() {
  applyStatePatch(createOverviewState());
  document.querySelector(".app-shell")?.classList.remove("reader-mode");
}

function goToOverview() {
  resetOverviewState();
  render();
}

function goBack() {
  const next = stepBrowseHistory(state, "back");
  if (!next) return;
  state.browseIndex = next.browseIndex;
  activateFocusNode(next.nodeId, { pushHistory: false });
}

function goForward() {
  const next = stepBrowseHistory(state, "forward");
  if (!next) return;
  state.browseIndex = next.browseIndex;
  activateFocusNode(next.nodeId, { pushHistory: false });
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
  const point = clientToSvgPoint(els.graphFrame.querySelector(".graph-svg"), event.clientX, event.clientY);
  const deltaX = point.x - state.dragging.startX;
  const deltaY = point.y - state.dragging.startY;
  state.panX = state.dragging.basePanX + deltaX;
  state.panY = state.dragging.basePanY + deltaY;
  syncViewportTransform();
  syncMiniMapViewport();
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

  const pointer = clientToSvgPoint(els.graphFrame.querySelector(".graph-svg"), event.clientX, event.clientY);
  const worldX = (pointer.x - state.panX) / state.zoom;
  const worldY = (pointer.y - state.panY) / state.zoom;
  const factor = Math.exp(-event.deltaY * 0.0015);
  const nextZoom = clamp(state.zoom * factor, 0.55, 2.6);

  state.panX = pointer.x - worldX * nextZoom;
  state.panY = pointer.y - worldY * nextZoom;
  setZoom(nextZoom);
  renderForZoomChange();
}

function setZoom(value) {
  state.zoom = clamp(value, 0.55, 2.6);
  els.zoomSlider.value = String(Math.round(state.zoom * 100));
  els.zoomLabel.textContent = `${Math.round(state.zoom * 100)}%`;
  syncViewportTransform();
}

function render() {
  const scene = getCurrentScene();
  renderScene(scene, {
    forceLayout: false,
    refreshGraph: true,
    refreshDetail: true,
    refreshSearch: true,
    refreshModeUI: true,
  });
}

function getCurrentScene() {
  syncViewportTransform();
  return state.mode === "focus" && state.selectedNodeId
    ? ensureFocusScene()
    : {
        nodes: filterOverviewNodes(state.overviewNodes),
        edges: filterOverviewEdges(state.overviewEdges),
      };
}

function renderScene(scene, options = {}) {
  const {
    forceLayout = false,
    refreshGraph = false,
    refreshDetail = true,
    refreshSearch = true,
    refreshModeUI = true,
  } = options;
  updateViewportTransform();
  const tier = semanticTierFromZoom(state.zoom);
  const shouldLayout = forceLayout || state.lastSemanticTier !== tier;
  if (shouldLayout) {
    relaxLayout(scene.nodes, {
      iterations: state.mode === "focus" ? 100 : 120,
      padding: state.mode === "focus" ? 14 : 2,
      lockFocal: true,
      enforceBounds: state.mode === "focus",
    });
    state.lastSemanticTier = tier;
  }

  renderRings(scene.nodes);
  if (shouldLayout || refreshGraph) {
    renderEdges(scene.edges, scene.nodes);
    renderMiniMap(scene.nodes);
  } else {
    updateMiniMapViewport();
  }
  renderNodes(scene.nodes);
  if (refreshDetail) {
    try { renderDetail(); } catch (e) { console.error("renderDetail error:", e); }
  }
  if (refreshSearch) {
    try { renderSearchResults(); } catch (e) { console.error("renderSearchResults error:", e); }
  }
  syncNoteViewToggle();
  if (refreshModeUI) {
    updateModeUI(scene.nodes);
  }
}

function renderForZoomChange(options = {}) {
  const scene = getCurrentScene();
  renderScene(scene, {
    forceLayout: Boolean(options.forceLayout),
    refreshGraph: false,
    refreshDetail: Boolean(options.refreshDetail),
    refreshSearch: Boolean(options.refreshSearch),
    refreshModeUI: true,
  });
}

function ensureFocusScene() {
  if (!state.focusNodes.length || state.focusSceneNodeId !== state.selectedNodeId) {
    buildFocusScene(state.selectedNodeId);
  }
  return { nodes: state.focusNodes, edges: state.focusEdges };
}

function filterOverviewNodes(nodes) {
  return nodes.filter((node) => {
    if (node.type === "root") return true;
    if (state.query && !node.searchText?.includes(state.query)) return false;
    if (state.domainSelection && !state.domainSelection.has(node.taxonomy)) return false;
    if (state.typeSelection && !state.typeSelection.has(node.type)) return false;
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
    const visibleTaxonomies = new Set(nodes.filter((n) => n.type !== "domain" && n.type !== "root").map((n) => n.taxonomy));
    const t = clamp((state.zoom - 0.55) / 0.9, 0, 1);
    const fillOpacity = 0.8 - t * 0.78;
    const strokeOpacity = 1.0 - t * 0.95;
    const labelOpacity = state.zoom > 1.1 ? 0 : state.zoom > 0.9 ? 1 - (state.zoom - 0.9) / 0.2 : 1;
    const regionPaths = [];
    const regionLabels = [];
    for (const [taxonomy, region] of state.domainRegions) {
      if (!visibleTaxonomies.has(taxonomy)) continue;
      const style = DOMAIN_REGION_STYLES[taxonomy] || DOMAIN_REGION_STYLES.uncategorized;
      const label = TAXONOMY_LABELS[taxonomy] || taxonomy;
      regionPaths.push(
        `<path class="domain-region" data-taxonomy="${taxonomy}" d="${region.d}" fill="${style.fill}" stroke="${style.stroke}" fill-opacity="${fillOpacity}" stroke-opacity="${strokeOpacity}"></path>`
      );
      if (labelOpacity > 0) {
        regionLabels.push(
          `<text class="domain-region-label" x="${region.cx}" y="${region.cy + 6}" text-anchor="middle" opacity="${labelOpacity}">${label}</text>`
        );
      }
    }
    els.ringLayer.innerHTML = regionPaths.join("");
    if (els.labelLayer) {
      els.labelLayer.innerHTML = regionLabels.join("");
    }
    for (const el of els.ringLayer.querySelectorAll(".domain-region")) {
      el.addEventListener("click", () => goToOverviewAndCenterTaxonomy(el.dataset.taxonomy));
    }
    return;
  }

  const focal = nodes[0];
  if (!focal) {
    els.ringLayer.innerHTML = "";
    if (els.labelLayer) els.labelLayer.innerHTML = "";
    return;
  }
  if (els.labelLayer) els.labelLayer.innerHTML = "";
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
  const bounds = getNavigationBounds(nodes, CANVAS_WIDTH, CANVAS_HEIGHT);
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
  syncMiniMapViewport(bounds);
  els.minimapModeLabel.textContent = state.mode;
}

function resolveVisibleTitle(node, tier, selected) {
  if (node.type === "root") return node.title;
  if (state.mode === "focus") return tier >= 1 ? node.title : node.shortTitle;
  if (state.zoom < 0.8) return "";
  if (tier === 0) return node.type === "map" || selected ? node.shortTitle : "";
  if (tier === 1) return node.shortTitle;
  return node.title;
}

function handleNodeSelect(nodeId) {
  const node = state.nodeMap.get(nodeId);
  if (!node) return;
  if (node.type === "domain") {
    goToOverviewAndCenterTaxonomy(node.taxonomy);
    return;
  }
  activateFocusNode(nodeId);
}

function onMiniMapClick(event) {
  const rect = els.minimapSvg.getBoundingClientRect();
  const bounds = state.miniMapBounds || { minX: 0, minY: 0, maxX: CANVAS_WIDTH, maxY: CANVAS_HEIGHT };
  const { worldX, worldY } = projectMiniMapClick({
    clientX: event.clientX,
    clientY: event.clientY,
    rect,
    bounds,
    width: 220,
    height: 140,
    padding: 10,
  });
  state.panX = CANVAS_WIDTH / 2 - worldX * state.zoom;
  state.panY = CANVAS_HEIGHT / 2 - worldY * state.zoom;
  syncViewportTransform();
  syncMiniMapViewport();
}

function updateModeUI(sceneNodes) {
  const node = state.mode === "focus" && state.selectedNodeId
    ? state.nodeMap.get(state.selectedNodeId)
    : null;
  const uiState = createModeUiState(
    state,
    node,
    node ? (TAXONOMY_LABELS[node.taxonomy] || node.taxonomy) : ""
  );
  els.backButton.hidden = !uiState.showBackButton;
  els.focusActionButton.hidden = !uiState.showFocusAction;
  els.browseNav.hidden = !uiState.showBrowseNav;
  els.browseBack.disabled = state.browseIndex <= 0;
  els.browseForward.disabled = state.browseIndex >= state.browseHistory.length - 1;
  const domainOverview = document.getElementById("domainOverview");
  if (domainOverview) domainOverview.classList.toggle("collapsed", uiState.collapseDomainOverview);
  els.overviewModeButton.classList.toggle("is-active", !uiState.isFocus);
  els.focusModeButton.classList.toggle("is-active", uiState.isFocus);

  if (uiState.isFocus && node) {
    renderBreadcrumb([
      { label: "總覽", action: () => goToOverview() },
      { label: TAXONOMY_LABELS[node.taxonomy] || node.taxonomy, action: () => goToOverviewAndCenterTaxonomy(node.taxonomy) },
      { label: node.title },
    ]);
    els.graphHint.textContent = "中心節點固定；內圈只留先備與數學支撐，外圈只留推導、驗證、量測與應用，灰色膠囊則放弱關聯。";
  } else {
    renderBreadcrumb([
      { label: "總覽", action: () => goToOverview() },
      { label: "taxonomy domains" },
    ]);
    els.graphHint.textContent = "拖曳平移、滾輪縮放；中央根節點連接各領域，放大後會依序顯示更細的節點名稱與關係。";
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
  resetOverviewState();
  render();
  const region = state.domainRegions.get(taxonomy);
  if (!region) return;
  state.panX = CANVAS_WIDTH / 2 - region.cx * state.zoom;
  state.panY = CANVAS_HEIGHT / 2 - region.cy * state.zoom;
  syncViewportTransform();
  syncMiniMapViewport();
}

function renderDetail() {
  const node = state.selectedNodeId ? state.nodeMap.get(state.selectedNodeId) : null;
  if (!node) {
    const emptyView = buildEmptyDetailView();
    emptyView.statsEntries = [
      ["顯示節點", String(filterOverviewNodes(state.overviewNodes).length)],
      ["顯示關係", String(filterOverviewEdges(state.overviewEdges).length)],
      ["已隱藏", "wikilink"],
      ["總層級", "3"],
    ];
    els.detailType.textContent = emptyView.typeText;
    els.detailTitle.textContent = emptyView.titleText;
    els.detailSummary.innerHTML = emptyView.summaryHtml;
    els.detailTaxonomyBadge.textContent = emptyView.taxonomyBadge;
      els.detailMeta.innerHTML = buildMetaItemsHtml(emptyView.metaEntries, { escapeHtml });
      els.statsStrip.innerHTML = buildStatCardsHtml(emptyView.statsEntries, { escapeHtml });
    fillRelationSection("prereq", []);
    fillRelationSection("extension", []);
    fillRelationSection("related", []);
    els.detailPath.textContent = "尚未選取節點";
    els.detailPath.removeAttribute("href");
    const noteSection = document.getElementById("noteSection");
    if (noteSection) noteSection.innerHTML = "";
    return;
  }

  const cachedDetail = state.detailStore.getCached(node.id);
  const detailIndex = state.detailStore.getIndex(node.id);
  const detail = cachedDetail || detailIndex;
  const relations = collectRelations(node.id);
  const detailView = buildNodeDetailView(node, detail, relations, {
    taxonomyLabels: TAXONOMY_LABELS,
    typeLabels: TYPE_LABELS,
    renderMarkdown,
    findNodeByTitle,
  });

  els.detailType.textContent = detailView.typeText;
  els.detailTitle.textContent = detailView.titleText;
  els.detailSummary.innerHTML = detailView.summaryHtml;
  els.detailTaxonomyBadge.textContent = detailView.taxonomyBadge;
  els.detailMeta.innerHTML = buildMetaItemsHtml(detailView.metaEntries, { escapeHtml });
  els.statsStrip.innerHTML = buildStatCardsHtml(detailView.statsEntries, { escapeHtml });

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

  // Note preview / full text
  if (!cachedDetail) {
    void loadDetail(node.id);
  }
  renderNoteSection(node, detail);
  scheduleMathTypeset(els.detailSummary);
  syncNoteViewToggle();
}

function renderNoteSection(node, detail) {
  let noteSection = document.getElementById("noteSection");
  if (!noteSection) {
    noteSection = document.createElement("div");
    noteSection.id = "noteSection";
    noteSection.className = "detail-section";
    const detailCard = document.querySelector(".detail-card");
    if (detailCard) detailCard.appendChild(noteSection);
  }

  noteSection.innerHTML = buildNoteSectionHtml(node, detail, {
    escapeHtml,
    renderMarkdown,
    findNodeByTitle,
    loadError: state.detailStore.getError(node.id),
    isLoaded: state.detailStore.hasCached(node.id),
    noteViewMode: state.noteViewMode,
  });
  scheduleMathTypeset(noteSection);
}

function syncNoteViewToggle() {
  const toggle = document.getElementById("noteViewToggle");
  if (!toggle) return;
  const hasNode = Boolean(state.selectedNodeId);
  toggle.style.display = hasNode ? "flex" : "none";
  const isFull = state.noteViewMode === "full";
  for (const btn of toggle.querySelectorAll(".note-view-btn")) {
    btn.classList.toggle("active", btn.dataset.noteMode === (isFull ? "full" : "preview"));
  }
  document.querySelector(".app-shell")?.classList.toggle("reader-mode", isFull && hasNode);
}

async function loadDetail(nodeId) {
  return state.detailStore.loadDetail(nodeId, {
    onSettled(settledNodeId) {
      if (state.selectedNodeId === settledNodeId) {
        try {
          renderDetail();
        } catch (renderError) {
          console.error("renderDetail error:", renderError);
        }
      }
    },
  });
}

function renderSearchResults() {
  let searchSection = document.getElementById("searchSection");
  if (!searchSection) {
    searchSection = document.createElement("div");
    searchSection.id = "searchSection";
    searchSection.className = "detail-section";
    const detailCard = document.querySelector(".detail-card");
    if (detailCard) detailCard.insertBefore(searchSection, detailCard.firstChild?.nextSibling);
  }
  if (!state.query) {
    searchSection.innerHTML = "";
    return;
  }
  const matches = state.graph.nodes
    .filter((n) => n.searchText?.includes(state.query))
    .filter((n) => n.type !== "domain" && n.type !== "root")
    .slice(0, 50);
  searchSection.innerHTML = buildSearchResultsHtml(state.query, matches, {
    escapeHtml,
    messages: {
      emptyPrefix: "?曆??啁泵??",
      emptySuffix: "??蝭暺?",
      resultCountPrefix: "??蝯?嚗?",
      resultCountSuffix: "嚗?",
    },
  });
  return;
  if (!matches.length) {
    searchSection.innerHTML = `<p style="color:var(--muted);font-size:0.88rem;">找不到符合「${escapeHtml(state.query)}」的節點。</p>`;
    return;
  }
  let html = `<div class="section-head"><h3>搜尋結果（${matches.length}）</h3></div><div class="pill-list">`;
  for (const n of matches) {
    html += `<button class="pill" type="button" data-node-id="${escapeHtml(n.id)}" data-family="related">${escapeHtml(n.title)}</button>`;
  }
  html += `</div>`;
  searchSection.innerHTML = html;
  for (const pill of searchSection.querySelectorAll(".pill[data-node-id]")) {
    pill.addEventListener("click", () => handleNodeSelect(pill.dataset.nodeId));
  }
}

function fillRelationSection(prefix, items) {
  const countEl = els[`${prefix}Count`];
  const listEl = els[`${prefix}List`];
  countEl.textContent = String(items.length);
  listEl.innerHTML = buildPillListHtml(
    items,
    prefix === "prereq" ? "requires" : prefix === "extension" ? "extension" : "related",
    { escapeHtml }
  );
}

function collectRelations(nodeId) {
  const entries = collectDirectionalRelations(nodeId, state.graphIndex, state.nodeMap, {
    includeNode: (node) => Boolean(node) && node.type !== "domain",
  });
  const requires = entries.filter((entry) => entry.bucket === "requires").map((entry) => entry.node);
  const extension = entries.filter((entry) => entry.bucket === "extension").map((entry) => entry.node);
  const related = entries.filter((entry) => entry.bucket === "related").map((entry) => entry.node);
  return {
    requires: rankFocusNodes(requires, { dedupeNodes }).slice(0, 8),
    extension: rankFocusNodes(extension, { dedupeNodes }).slice(0, 8),
    related: rankFocusNodes(related, { dedupeNodes }).slice(0, 8),
  };
}

function isConnectedToSelected(nodeId) {
  if (!state.selectedNodeId || nodeId === state.selectedNodeId) return true;
  return state.focusEdges.some((edge) =>
    (edge.source === state.selectedNodeId && edge.target === nodeId) ||
    (edge.target === state.selectedNodeId && edge.source === nodeId)
  );
}

function relaxLayout(nodes, options = {}) {
  runRelaxLayout(nodes, {
    ...options,
    getCollisionHalfWidth: collisionHalfWidth,
    getCollisionHalfHeight: collisionHalfHeight,
    clampNodes(sceneNodes, { preserveFocus }) {
      clampNodesToViewport(sceneNodes, {
        padding: state.mode === "focus" ? 84 : 36,
        preserveFocus,
        useCollisionRadius: true,
        collisionRadius,
        canvasWidth: CANVAS_WIDTH,
        canvasHeight: CANVAS_HEIGHT,
      });
    },
  });
}

function collisionRadius(node) {
  return baseCollisionRadius(node, {
    getCollisionHalfWidth: collisionHalfWidth,
    getCollisionHalfHeight: collisionHalfHeight,
  });
}

function collisionHalfWidth(node) {
  return baseCollisionHalfWidth(node, {
    visibleTitle: resolveVisibleTitle(
      node,
      semanticTierFromZoom(state.zoom),
      node.id === state.selectedNodeId
    ),
  });
}

function collisionHalfHeight(node) {
  return baseCollisionHalfHeight(node);
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

function syncViewportTransform() {
  updateViewportTransform(els.viewport, state.panX, state.panY, state.zoom);
}

function syncMiniMapViewport(bounds = state.miniMapBounds) {
  updateMiniMapViewport(els.minimapViewport, bounds, {
    width: 220,
    height: 140,
    padding: 10,
    panX: state.panX,
    panY: state.panY,
    zoom: state.zoom,
    canvasWidth: CANVAS_WIDTH,
    canvasHeight: CANVAS_HEIGHT,
  });
}

function findNodeByTitle(title) {
  for (const [, node] of state.nodeMap) {
    if (node.title === title) return node;
  }
  return null;
}

function escapeRegex(value) {
  return String(value || "").replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
