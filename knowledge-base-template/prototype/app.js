// ============================================================
// 知識庫資料來源 — 修改這兩個路徑以指向你的匯出檔案
// ============================================================
// 若將 graph.json 與 note_details.json 放在同目錄：
const graphUrl = "./graph.json";
const noteDetailsUrl = "./note_details.json";
// 若使用 standalone 模式（嵌入 JS），註解上面兩行，取消下面兩行：
// const graphUrl = null;
// const noteDetailsUrl = null;
const primaryEdgeTypes = new Set([
  "organized_by",
  "requires",
  "formalized_by",
  "derives_to",
  "uses",
  "verified_by",
  "explains",
  "measures",
  "related_to",
]);
const structuralEdgeTypes = new Set(["organized_by", "requires"]);
const overviewNodeTypes = new Set(["map"]);
const overviewSearchLimit = 14;
const domainSeedLimit = 16;
const domainSupportLimit = 6;
const localPrimaryLimit = 10;
const localSupportLimit = 4;
const wikilinkPattern = /\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|([^\]]+))?\]\]/g;

const state = {
  graph: null,
  noteDetails: {},
  nodeMap: new Map(),
  incomingMap: new Map(),
  domainMeta: [],
  visibleNodes: [],
  visibleEdges: [],
  domainSelection: new Set(),
  typeSelection: new Set(),
  filterMode: localStorage.getItem("kb_filterMode") || "taxonomy",
  viewMode: "overview",
  focusedDomain: null,
  searchTerm: "",
  selectedNodeId: null,
  noteViewMode: "preview",
  draggingNodeId: null,
  suppressNodeClickUntil: 0,
  mentionPattern: null,
  mentionTargets: new Map(),
  pointerOffset: { x: 0, y: 0 },
  viewport: {
    scale: 1,
    offsetX: 0,
    offsetY: 0,
    panning: false,
    startX: 0,
    startY: 0,
    baseOffsetX: 0,
    baseOffsetY: 0,
  },
  layoutFrame: null,
};

const els = {
  heroStats: document.getElementById("heroStats"),
  searchInput: document.getElementById("searchInput"),
  viewModeButtons: document.getElementById("viewModeButtons"),
  focusBanner: document.getElementById("focusBanner"),
  domainFilters: document.getElementById("domainFilters"),
  filterModeToggle: document.getElementById("filterModeToggle"),
  domainSectionTitle: document.getElementById("domainSectionTitle"),
  typeFilters: document.getElementById("typeFilters"),
  typeLegend: document.getElementById("typeLegend"),
  domainOverview: document.getElementById("domainOverview"),
  graphFrame: document.getElementById("graphFrame"),
  graphCanvas: document.getElementById("graphCanvas"),
  nodesLayer: document.getElementById("nodesLayer"),
  workspace: document.querySelector(".workspace-shell"),
  graphPanel: document.querySelector(".graph-panel"),
  detailPanel: document.querySelector(".detail-panel"),
  detailCard: document.getElementById("detailCard"),
  zoomOutButton: document.getElementById("zoomOutButton"),
  zoomInButton: document.getElementById("zoomInButton"),
  fitViewButton: document.getElementById("fitViewButton"),
  backToOverviewToolbarButton: document.getElementById("backToOverviewToolbarButton"),
  resetViewButton: document.getElementById("resetViewButton"),
  graphHint: document.getElementById("graphHint"),
  topnavButtons: document.querySelectorAll(".topnav-item"),
  brandLink: document.querySelector(".brand-link"),
};

const typeLabel = {
  map: "Map",
  concept: "Concept",
  principle: "Principle",
  entity: "Entity",
  procedure: "Procedure",
  case_study: "Case Study",
  law: "Principle",
  quantity: "Entity",
  mathematical_tool: "Procedure",
  experiment: "Case Study",
  domain: "Domain",
};

const relationLabel = {
  organized_by: "Organized By",
  requires: "Prerequisite",
  formalized_by: "Formalized By",
  derives_to: "Derives To",
  uses: "Uses",
  verified_by: "Verified By",
  explains: "Extends To",
  measures: "Measures",
  related_to: "Related To",
  illustrated_by: "Illustrated By",
  used_in: "Used In",
  wikilink: "In-Body Link",
};

const domainDescriptions = {
  core: "Foundational notes that define the central ideas and entities of the project.",
  methods: "Procedures, representations, and analysis methods used across the project.",
  applications: "Examples, case studies, and downstream applications.",
  uncategorized: "Notes that have not yet been assigned to a stable domain.",
  未分類: "Notes that have not yet been assigned to a stable domain.",
};

const taxonomyLabels = {
  core: "Core",
  methods: "Methods",
  applications: "Applications",
};

const taxonomyDescriptions = {
  core: "Foundational structures and concepts that define the subject area.",
  methods: "Methods, procedures, and formal tools used to work inside the subject area.",
  applications: "Applied, illustrative, or case-based parts of the knowledge base.",
};

const taxonomyColorPalette = {
  core: "#315f98",
  methods: "#648356",
  applications: "#ae5a31",
};

const domainColorPalette = {
  core: "#315f98",
  methods: "#648356",
  applications: "#ae5a31",
  uncategorized: "#a1a6b1",
  未分類: "#a1a6b1",
};

init().catch((error) => {
  console.error(error);
  els.detailCard.classList.remove("empty");
  els.detailCard.innerHTML = `
    <p class="detail-kicker">Load Error</p>
    <h2>Could not load knowledge-base data</h2>
    <p class="detail-summary">${escapeHtml(String(error.message || error))}</p>
  `;
});

function getActiveDomain(node) {
  if (state.filterMode === "taxonomy") {
    return node.taxonomy_domain || "未分類";
  }
  return node.domain || "未分類";
}

function getActiveDomainDescriptions() {
  return state.filterMode === "taxonomy" ? taxonomyDescriptions : domainDescriptions;
}

function getActiveColorPalette() {
  return state.filterMode === "taxonomy" ? taxonomyColorPalette : domainColorPalette;
}

function getDomainLabel(domain) {
  if (state.filterMode === "taxonomy") {
    return taxonomyLabels[domain] || domain;
  }
  return domain;
}

function humanizeTypeId(type) {
  return String(type || "")
    .replaceAll("_", " ")
    .replaceAll("-", " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function getTypeLabel(type) {
  return typeLabel[type] || humanizeTypeId(type);
}

function buildTypeLegend(graph) {
  if (!els.typeLegend) return;
  els.typeLegend.innerHTML = graph.types
    .map(
      (type) => `<span><i class="swatch type-${escapeHtml(type)}"></i>${escapeHtml(getTypeLabel(type))}</span>`
    )
    .join("");
}

function switchFilterMode() {
  state.filterMode = state.filterMode === "taxonomy" ? "domain" : "taxonomy";
  localStorage.setItem("kb_filterMode", state.filterMode);
  state.focusedDomain = null;
  state.viewMode = "overview";
  // Rebuild domain layer with new grouping
  const g = state.graph;
  const newGraph = rebuildDomainLayer(g.noteNodes, g.edges, state.nodeMap, state.incomingMap);
  state.graph = newGraph;
  // Update UI
  els.domainSectionTitle.textContent = state.filterMode === "taxonomy" ? "Taxonomy" : "Domain";
  syncModeButtons();
  buildFilters(newGraph);
  buildDomainOverview();
  buildStats(newGraph);
  layoutVisibleGraph(true);
}

function getNoteDetail(nodeId) {
  return (
    state.noteDetails[nodeId] ||
    state.noteDetails[String(nodeId).toLowerCase()] ||
    state.noteDetails[String(nodeId).replaceAll(" ", "-")] ||
    null
  );
}

async function init() {
  const [graphResponse, detailResponse] = await Promise.all([fetch(graphUrl), fetch(noteDetailsUrl)]);
  if (!graphResponse.ok) {
    throw new Error(`HTTP ${graphResponse.status} while loading ${graphUrl}`);
  }
  if (!detailResponse.ok) {
    throw new Error(`HTTP ${detailResponse.status} while loading ${noteDetailsUrl}`);
  }

  const [rawGraph, rawNoteDetails] = await Promise.all([graphResponse.json(), detailResponse.json()]);
  const graph = normalizeGraph(rawGraph);
  state.graph = graph;
  state.noteDetails = rawNoteDetails;

  buildStats(graph);
  buildMentionIndex(graph);
  buildModeButtons();
  buildFilters(graph);
  buildTypeLegend(graph);
  buildDomainOverview();
  els.domainSectionTitle.textContent = state.filterMode === "taxonomy" ? "Taxonomy" : "Domain";
  bindEvents();
  resetViewport();
  layoutVisibleGraph(true);
}

function normalizeGraph(rawGraph) {
  const baseNodes = rawGraph.nodes.map((node, index) => ({
    ...node,
    domain: node.domain || inferDomainFromTags(node.tags || []),
    taxonomy_domain: node.taxonomy_domain || "",
    tags: node.tags || [],
    x: 0,
    y: 0,
    vx: 0,
    vy: 0,
    degree: 0,
    support: false,
    kind: "note",
    searchText: [node.title, node.summary, node.type, node.domain, node.taxonomy_domain, ...(node.tags || [])]
      .filter(Boolean)
      .join(" ")
      .toLowerCase(),
    _order: index,
  }));

  const nodeMap = new Map(baseNodes.map((node) => [node.id, node]));
  const edges = [];
  const edgeSeen = new Set();

  for (const edge of rawGraph.edges) {
    const source = nodeMap.get(edge.source);
    const target = nodeMap.get(edge.target);
    if (!source || !target) continue;
    const key = `${edge.source}|${edge.target}|${edge.type}`;
    if (edgeSeen.has(key)) continue;
    edgeSeen.add(key);
    edges.push({ ...edge });
  }

  const incomingMap = new Map();
  for (const node of baseNodes) incomingMap.set(node.id, []);

  for (const edge of edges) {
    nodeMap.get(edge.source).degree += 1;
    nodeMap.get(edge.target).degree += 1;
    incomingMap.get(edge.target).push(edge);
  }

  return rebuildDomainLayer(baseNodes, edges, nodeMap, incomingMap);
}

function rebuildDomainLayer(baseNodes, edges, nodeMap, incomingMap) {
  // Remove old domain nodes from maps
  for (const [key, val] of nodeMap) {
    if (key.startsWith("domain::")) nodeMap.delete(key);
  }
  for (const [key, val] of incomingMap) {
    if (key.startsWith("domain::")) incomingMap.delete(key);
  }

  const descs = getActiveDomainDescriptions();
  const domains = unique(baseNodes.map((node) => getActiveDomain(node))).sort(localeCompareZh);
  const domainNodes = domains.map((domain, index) => {
    const domainMembers = baseNodes.filter((node) => getActiveDomain(node) === domain);
    const edgeCount = edges.filter((edge) => {
      const source = nodeMap.get(edge.source);
      const target = nodeMap.get(edge.target);
      if (!source || !target) return false;
      return getActiveDomain(source) === domain || getActiveDomain(target) === domain;
    }).length;
    return {
      id: `domain::${domain}`,
      title: getDomainLabel(domain),
      type: "domain",
      kind: "domain",
      domain,
      summary: descs[domain] || "No overview description has been written for this group yet.",
      tags: ["domain-hub"],
      path: "",
      degree: edgeCount,
      memberCount: domainMembers.length,
      x: 0,
      y: 0,
      vx: 0,
      vy: 0,
      support: false,
      searchText: `${getDomainLabel(domain)} ${(descs[domain] || "").toLowerCase()}`,
      _order: 1000 + index,
    };
  });

  const fullNodes = [...baseNodes, ...domainNodes];
  for (const domainNode of domainNodes) nodeMap.set(domainNode.id, domainNode);
  for (const domainNode of domainNodes) incomingMap.set(domainNode.id, []);

  const domainEdgeMap = new Map();
  for (const edge of edges) {
    const source = nodeMap.get(edge.source);
    const target = nodeMap.get(edge.target);
    if (!source || !target) continue;
    const sourceDomain = getActiveDomain(source);
    const targetDomain = getActiveDomain(target);
    if (sourceDomain === targetDomain) continue;
    const key = [sourceDomain, targetDomain].sort(localeCompareZh).join("|");
    const current = domainEdgeMap.get(key) || {
      source: `domain::${sourceDomain}`,
      target: `domain::${targetDomain}`,
      type: "related_to",
      weight: 0,
    };
    current.weight += edge.type === "wikilink" ? 1 : 3;
    domainEdgeMap.set(key, current);
  }

  const domainEdges = [...domainEdgeMap.values()];

  state.nodeMap = nodeMap;
  state.incomingMap = incomingMap;
  state.domainMeta = domainNodes.map((domainNode) => {
    const typeCounts = countBy(
      baseNodes.filter((node) => getActiveDomain(node) === domainNode.domain),
      (node) => getTypeLabel(node.type)
    );
    return {
      id: domainNode.id,
      domain: domainNode.domain,
      count: domainNode.memberCount,
      typeCounts,
      description: domainNode.summary,
    };
  });

  return {
    nodes: fullNodes,
    noteNodes: baseNodes,
    domainNodes,
    edges,
    domainEdges,
    domains,
    types: unique(baseNodes.map((node) => node.type)).sort(),
  };
}

function buildStats(graph) {
  const stats = [
    { label: "節點", value: graph.noteNodes.length },
    { label: "關係", value: graph.edges.filter((edge) => primaryEdgeTypes.has(edge.type)).length },
    { label: "Domains", value: graph.domains.length },
    { label: "Types", value: graph.types.length },
  ];

  const domainBreakdown = graph.domains
    .map((domain) => {
      const count = graph.noteNodes.filter((node) => getActiveDomain(node) === domain).length;
      return `${getDomainLabel(domain)} ${count}`;
    })
    .join(" / ");

  els.heroStats.innerHTML = `
    <div class="stat-grid">
      ${stats
        .map(
          (stat) => `
            <div class="stat-box">
              <div class="stat-label">${stat.label}</div>
              <div class="stat-value">${stat.value}</div>
            </div>`
        )
        .join("")}
    </div>
    <div class="stat-box">
      <div class="stat-label">Domain Distribution</div>
      <div class="detail-summary">${escapeHtml(domainBreakdown)}</div>
    </div>
  `;
}

function buildModeButtons() {
  const modes = [
    { value: "overview", label: "Overview" },
    { value: "domain", label: "Domain Focus" },
  ];
  els.viewModeButtons.innerHTML = "";
  for (const mode of modes) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `chip ${state.viewMode === mode.value ? "active" : ""}`;
    button.textContent = mode.label;
    button.dataset.value = mode.value;
    button.addEventListener("click", () => {
      state.viewMode = mode.value;
      if (mode.value === "overview") state.focusedDomain = null;
      syncModeButtons();
      layoutVisibleGraph(true);
    });
    els.viewModeButtons.appendChild(button);
  }
}

function syncModeButtons() {
  for (const button of els.viewModeButtons.querySelectorAll(".chip")) {
    button.classList.toggle("active", button.dataset.value === state.viewMode);
  }
}

function buildFilters(graph) {
  state.domainSelection = new Set(graph.domains);
  state.typeSelection = new Set(graph.types);
  const domainItems = graph.domains.map((domain) => ({
    value: domain,
    label: getDomainLabel(domain),
    count: graph.noteNodes.filter((node) => getActiveDomain(node) === domain).length,
    color: filterSwatchColor("domain", domain),
  }));
  const typeItems = graph.types.map((type) => ({
    value: type,
    label: getTypeLabel(type),
    count: graph.noteNodes.filter((node) => node.type === type).length,
    color: filterSwatchColor("type", type),
  }));

  renderSidebarFilterGroup(els.domainFilters, domainItems, state.domainSelection, () => {
    if (state.focusedDomain && !state.domainSelection.has(state.focusedDomain)) {
      state.focusedDomain = null;
      state.viewMode = "overview";
      syncModeButtons();
    }
    buildDomainOverview();
    layoutVisibleGraph(true);
  });
  renderSidebarFilterGroup(els.typeFilters, typeItems, state.typeSelection, () => layoutVisibleGraph(true));
}

function renderChipGroup(container, values, selection, onChange, labeler = (value) => value) {
  container.innerHTML = "";
  for (const value of values) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `chip ${selection.has(value) ? "active" : ""}`;
    button.textContent = labeler(value);
    button.dataset.value = value;
    button.addEventListener("click", () => {
      if (selection.has(value) && selection.size > 1) selection.delete(value);
      else if (!selection.has(value)) selection.add(value);
      button.classList.toggle("active", selection.has(value));
      onChange();
    });
    container.appendChild(button);
  }
}

function buildDomainOverview() {
  const visibleDomains = state.domainMeta.filter((meta) => state.domainSelection.has(meta.domain));
  els.domainOverview.classList.toggle("collapsed", state.viewMode === "domain");
  els.domainOverview.innerHTML = "";
  for (const meta of visibleDomains) {
    const card = document.createElement("button");
    card.type = "button";
    card.className = `domain-card ${state.focusedDomain === meta.domain ? "active" : ""}`;
    const label = getDomainLabel(meta.domain);
    const kicker = state.filterMode === "taxonomy" ? "taxonomy group" : "domain group";
    const topTypes = Object.entries(meta.typeCounts || {})
      .sort((a, b) => b[1] - a[1] || localeCompareZh(a[0], b[0]))
      .slice(0, 2);
    card.innerHTML = `
      <div class="domain-card-kicker">${kicker}</div>
      <div class="domain-card-count">${meta.count}</div>
      <h3>${escapeHtml(label)}</h3>
      <p>${escapeHtml(meta.description)}</p>
      <div class="domain-card-meta">
        ${topTypes.map(([type, count]) => `<span class="domain-metric">${escapeHtml(type)} ${count}</span>`).join("")}
      </div>
      <div class="domain-card-footer">Click to focus</div>
    `;
    card.addEventListener("click", () => focusDomain(meta.domain));
    els.domainOverview.appendChild(card);
  }
}

function bindEvents() {
  els.searchInput.addEventListener("input", () => {
    state.searchTerm = els.searchInput.value.trim().toLowerCase();
    layoutVisibleGraph(true);
  });

  els.filterModeToggle?.addEventListener("click", () => {
    switchFilterMode();
  });

  els.resetViewButton.addEventListener("click", () => {
    state.searchTerm = "";
    els.searchInput.value = "";
    state.selectedNodeId = null;
    state.focusedDomain = null;
    state.viewMode = "overview";
    state.domainSelection = new Set(state.graph.domains);
    state.typeSelection = new Set(state.graph.types);
    buildModeButtons();
    buildFilters(state.graph);
    buildDomainOverview();
    resetViewport();
    layoutVisibleGraph(true);
    renderDetail(null);
  });

  els.backToOverviewToolbarButton.addEventListener("click", () => {
    state.viewMode = "overview";
    state.focusedDomain = null;
    syncModeButtons();
    buildDomainOverview();
    resetViewport();
    layoutVisibleGraph(true);
  });

  els.zoomInButton.addEventListener("click", () => zoomViewport(1.15));
  els.zoomOutButton.addEventListener("click", () => zoomViewport(1 / 1.15));
  els.fitViewButton.addEventListener("click", () => resetViewport());

  els.graphFrame.addEventListener("wheel", (event) => {
    event.preventDefault();
    const factor = event.deltaY < 0 ? 1.08 : 1 / 1.08;
    zoomViewport(factor, event.offsetX, event.offsetY);
  }, { passive: false });

  els.graphFrame.addEventListener("pointerdown", (event) => {
    if (event.target.closest(".node")) return;
    startPan(event);
  });

  window.addEventListener("resize", () => layoutVisibleGraph());

  // Brand click → reset to homepage
  els.brandLink?.addEventListener("click", (event) => {
    event.preventDefault();
    // Reset all state
    state.searchTerm = "";
    els.searchInput.value = "";
    state.selectedNodeId = null;
    state.focusedDomain = null;
    state.viewMode = "overview";
    state.domainSelection = new Set(state.graph?.domains || []);
    state.typeSelection = new Set(state.graph?.types || []);
    state.noteViewMode = "preview";
    buildModeButtons();
    buildFilters(state.graph);
    buildDomainOverview();
    resetViewport();
    layoutVisibleGraph(true);
    renderDetail(null);
    // Reset topnav to graph
    for (const btn of els.topnavButtons) btn.classList.remove("is-active");
    const graphBtn = document.querySelector('[data-view="graph"]');
    if (graphBtn) graphBtn.classList.add("is-active");
  });

  // Topnav view switching
  for (const btn of els.topnavButtons) {
    btn.addEventListener("click", () => {
      const view = btn.dataset.view;
      for (const other of els.topnavButtons) other.classList.remove("is-active");
      btn.classList.add("is-active");

      if (view === "search") {
        renderSearchView();
      } else if (view === "notes") {
        renderNotesListView();
      } else if (view === "settings") {
        renderSettingsView();
      } else if (view === "graph") {
        // Return to graph view
        state.selectedNodeId = null;
        state.focusedDomain = null;
        state.viewMode = "overview";
        syncModeButtons();
        buildDomainOverview();
        resetViewport();
        layoutVisibleGraph(true);
        renderDetail(null);
      }
    });
  }
}

function focusDomain(domain) {
  state.focusedDomain = domain;
  state.viewMode = "domain";
  state.domainSelection.add(domain);
  syncModeButtons();
  buildDomainOverview();
  resetViewport();
  layoutVisibleGraph(true);
}

function layoutVisibleGraph(resetPositions = false) {
  cancelAnimationFrame(state.layoutFrame);
  if (resetPositions) resetViewport();
  const previousSelectedNodeId = state.selectedNodeId;

  const prepared = state.viewMode === "overview" ? prepareOverviewGraph() : prepareDomainGraph();
  state.visibleNodes = prepared.nodes;
  state.visibleEdges = prepared.edges;
  syncVisibleNodeRefs(prepared.nodes);

  updateGraphHint();
  updateFocusBanner();

  if (!prepared.nodes.some((node) => node.id === state.selectedNodeId)) {
    // Only reset if selectedNodeId is truly not in the visible set
    // Check if it's a note node that exists but isn't rendered yet
    const existingNode = state.nodeMap.get(state.selectedNodeId);
    if (existingNode && existingNode.kind !== "domain") {
      // Keep the selected note node even if not in visible set
    } else {
      state.selectedNodeId = prepared.nodes[0]?.id ?? null;
    }
  }

  ensureNodeElements(prepared.nodes);

  const frameRect = els.graphFrame.getBoundingClientRect();
  const width = Math.max(frameRect.width, 320);
  const height = Math.max(frameRect.height, 320);
  const anchors =
    prepared.anchors ||
    (state.viewMode === "domain"
      ? buildFocusAnchors(width, height, prepared.nodes, state.focusedDomain)
      : buildDomainAnchors(width, height, prepared.nodes));

  for (const node of prepared.nodes) {
    if (resetPositions || !Number.isFinite(node.x) || !Number.isFinite(node.y) || node.x === 0) {
      const anchor = anchors.get(node.anchorKey || getActiveDomain(node)) || { x: width / 2, y: height / 2 };
      const radius =
        state.viewMode === "domain"
          ? node.kind === "domain"
            ? 12
            : 0
          : node.kind === "domain"
            ? 12
            : node.support
              ? 118
              : 86;
      const seed = hashString(node.id);
      node.x = anchor.x + Math.cos(seed) * radius;
      node.y = anchor.y + Math.sin(seed * 0.7) * radius * 0.72;
      node.vx = 0;
      node.vy = 0;
    }
  }

  runSimulation(prepared.nodes, prepared.edges, anchors, width, height);
  applyViewportTransform();
  drawGraph(width, height);
  renderDetail(state.nodeMap.get(state.selectedNodeId) || null);
  if (state.selectedNodeId !== previousSelectedNodeId) {
    scrollReadingToTop();
  }
}

function renderSidebarFilterGroup(container, items, selection, onChange) {
  container.innerHTML = "";
  for (const item of items) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `chip filter-item ${selection.has(item.value) ? "active" : ""}`;
    button.dataset.value = item.value;
    button.innerHTML = `
      <span class="filter-item-main">
        <span class="filter-dot" style="--filter-dot:${escapeAttribute(item.color)}"></span>
        <span class="filter-item-label">${escapeHtml(item.label)}</span>
      </span>
      <span class="filter-item-count">${escapeHtml(String(item.count))}</span>
    `;
    button.addEventListener("click", () => {
      if (selection.has(item.value) && selection.size > 1) selection.delete(item.value);
      else if (!selection.has(item.value)) selection.add(item.value);
      button.classList.toggle("active", selection.has(item.value));
      onChange();
    });
    container.appendChild(button);
  }
}

function filterSwatchColor(kind, value) {
  if (kind === "type") {
    const typePalette = {
      map: "var(--type-map)",
      principle: "var(--type-principle)",
      law: "var(--type-law)",
      concept: "var(--type-concept)",
      entity: "var(--type-entity)",
      quantity: "var(--type-quantity)",
      procedure: "var(--type-procedure)",
      mathematical_tool: "var(--type-mathematical_tool)",
      case_study: "var(--type-case_study)",
      experiment: "var(--type-case_study)",
      domain: "var(--accent)",
    };
    return typePalette[value] || "var(--accent)";
  }

  const palette = getActiveColorPalette();
  return palette[value] || "#7b8797";
}

function buildDomainAnchors(width, height, nodes) {
  const domainKeys = unique(nodes.map((node) => node.anchorKey || getActiveDomain(node))).sort(localeCompareZh);
  const anchors = new Map();
  const cx = width / 2;
  const cy = height / 2;
  const radiusX = Math.max(width * 0.32, 140);
  const radiusY = Math.max(height * 0.24, 110);

  domainKeys.forEach((domain, index) => {
    const angle = -Math.PI / 2 + (index / Math.max(domainKeys.length, 1)) * Math.PI * 2;
    anchors.set(domain, {
      x: cx + Math.cos(angle) * radiusX,
      y: cy + Math.sin(angle) * radiusY,
    });
  });

  return anchors;
}

function buildFocusAnchors(width, height, nodes, domain) {
  const anchors = new Map();
  const primary = nodes
    .filter((node) => !node.support && node.kind !== "domain")
    .sort(compareFocusNodes);
  const support = nodes
    .filter((node) => node.support && node.kind !== "domain")
    .sort(compareFocusNodes);

  const cx = width * 0.4;
  const cy = height * 0.56;
  const innerRadiusX = Math.max(180, Math.min(width * 0.22, 260));
  const innerRadiusY = Math.max(145, Math.min(height * 0.18, 210));
  const outerRadiusX = innerRadiusX + 220;
  const outerRadiusY = innerRadiusY + 110;

  primary.forEach((node, index) => {
    const angle = -Math.PI / 2 + (index / Math.max(primary.length, 1)) * Math.PI * 2;
    anchors.set(node.id, {
      x: cx + Math.cos(angle) * innerRadiusX,
      y: cy + Math.sin(angle) * innerRadiusY,
    });
  });

  support.forEach((node, index) => {
    const angle = -Math.PI / 2 + (index / Math.max(support.length, 1)) * Math.PI * 2;
    anchors.set(node.id, {
      x: cx + Math.cos(angle) * outerRadiusX,
      y: cy + Math.sin(angle) * outerRadiusY,
    });
  });

  anchors.set(domain, { x: cx, y: cy });
  return anchors;
}

function runSimulation(nodes, edges, anchors, width, height) {
  cancelAnimationFrame(state.layoutFrame);
  const visibleSet = new Set(nodes.map((node) => node.id));
  let tickCount = 0;
  let stableFrames = 0;
  const maxTicks = state.viewMode === "domain" ? 240 : 180;
  const stableFrameTarget = 16;

  const tick = () => {
    tickCount += 1;
    const selectedConnections = state.selectedNodeId ? new Set(connectedNodeIds(state.selectedNodeId)) : null;

    for (const node of nodes) {
      const anchor = anchors.get(node.anchorKey || getActiveDomain(node));
      if (!anchor || node.kind === "domain") continue;
      const tension =
        state.viewMode === "domain"
          ? node.id === state.selectedNodeId
            ? 0.06
            : node.support
              ? 0.042
              : 0.05
          : node.id === state.selectedNodeId
            ? 0.034
            : node.support
              ? 0.013
              : 0.019;
      node.vx += (anchor.x - node.x) * tension;
      node.vy += (anchor.y - node.y) * tension;
    }

    for (let i = 0; i < nodes.length; i += 1) {
      for (let j = i + 1; j < nodes.length; j += 1) {
        const a = nodes[i];
        const b = nodes[j];
        let dx = a.x - b.x;
        let dy = a.y - b.y;
        let distSq = dx * dx + dy * dy;
        if (distSq < 1) {
          dx = Math.random() - 0.5;
          dy = Math.random() - 0.5;
          distSq = dx * dx + dy * dy;
        }
        const force =
          a.kind === "domain" || b.kind === "domain"
            ? 600 / distSq
            : state.viewMode === "domain"
              ? 1680 / distSq
              : 1180 / distSq;
        const dist = Math.sqrt(distSq);
        const nx = dx / dist;
        const ny = dy / dist;
        a.vx += nx * force;
        a.vy += ny * force;
        b.vx -= nx * force;
        b.vy -= ny * force;
      }
    }

    resolveCollisions(nodes);

    for (const edge of edges) {
      const source = state.nodeMap.get(edge.source);
      const target = state.nodeMap.get(edge.target);
      if (!source || !target || !visibleSet.has(source.id) || !visibleSet.has(target.id)) continue;
      const dx = target.x - source.x;
      const dy = target.y - source.y;
      const dist = Math.max(Math.sqrt(dx * dx + dy * dy), 1);
      const preferred =
        source.kind === "domain" || target.kind === "domain"
          ? 210
          : state.viewMode === "domain"
            ? source.support || target.support
              ? 190
              : 150
            : source.anchorKey === target.anchorKey
              ? 100
              : 150;
      const stretch = dist - preferred;
      const strength =
        edge.type === "organized_by"
          ? 0.012
          : edge.type === "requires"
            ? 0.009
            : state.viewMode === "domain"
              ? 0.004
              : 0.006;
      const fx = (dx / dist) * stretch * strength;
      const fy = (dy / dist) * stretch * strength;
      source.vx += fx;
      source.vy += fy;
      target.vx -= fx;
      target.vy -= fy;
    }

    let totalMotion = 0;
    let maxSpeed = 0;
    for (const node of nodes) {
      if (state.draggingNodeId === node.id) continue;
      const connectionBoost = selectedConnections && selectedConnections.has(node.id) ? 1.05 : 1;
      const friction = node.kind === "domain" ? 0.68 : state.viewMode === "domain" ? 0.7 : 0.78;
      node.vx *= friction * connectionBoost;
      node.vy *= friction * connectionBoost;
      const speed = Math.hypot(node.vx, node.vy);
      totalMotion += speed;
      maxSpeed = Math.max(maxSpeed, speed);
      const halfW = Math.max((node.boxWidth || 120) / 2 + 14, node.kind === "domain" ? 94 : 54);
      const halfH = Math.max((node.boxHeight || 72) / 2 + 14, node.kind === "domain" ? 94 : 54);
      node.x = clamp(node.x + node.vx, halfW, width - halfW);
      node.y = clamp(node.y + node.vy, halfH, height - halfH);
      node.element.style.left = `${node.x}px`;
      node.element.style.top = `${node.y}px`;
    }

    drawGraph(width, height);
    const averageMotion = nodes.length ? totalMotion / nodes.length : 0;
    const settled = maxSpeed < 0.08 && averageMotion < 0.035;
    stableFrames = settled ? stableFrames + 1 : 0;

    if (stableFrames >= stableFrameTarget || tickCount >= maxTicks) {
      state.layoutFrame = null;
      return;
    }

    state.layoutFrame = requestAnimationFrame(tick);
  };

  state.layoutFrame = requestAnimationFrame(tick);
}

function resolveCollisions(nodes) {
  const gap = state.viewMode === "domain" ? 28 : 18;
  for (let i = 0; i < nodes.length; i += 1) {
    for (let j = i + 1; j < nodes.length; j += 1) {
      const a = nodes[i];
      const b = nodes[j];
      const aHalfW = (a.boxWidth || 120) / 2 + gap;
      const aHalfH = (a.boxHeight || 72) / 2 + gap;
      const bHalfW = (b.boxWidth || 120) / 2 + gap;
      const bHalfH = (b.boxHeight || 72) / 2 + gap;
      const dx = b.x - a.x;
      const dy = b.y - a.y;
      const overlapX = aHalfW + bHalfW - Math.abs(dx);
      const overlapY = aHalfH + bHalfH - Math.abs(dy);

      if (overlapX <= 0 || overlapY <= 0) continue;

      if (overlapX < overlapY) {
        const push = overlapX / 2;
        const dir = dx === 0 ? (i % 2 === 0 ? -1 : 1) : Math.sign(dx);
        if (a.kind !== "domain") a.x -= dir * push;
        if (b.kind !== "domain") b.x += dir * push;
        a.vx -= dir * 0.16;
        b.vx += dir * 0.16;
      } else {
        const push = overlapY / 2;
        const dir = dy === 0 ? (i % 2 === 0 ? -1 : 1) : Math.sign(dy);
        if (a.kind !== "domain") a.y -= dir * push;
        if (b.kind !== "domain") b.y += dir * push;
        a.vy -= dir * 0.16;
        b.vy += dir * 0.16;
      }
    }
  }
}

function drawGraph(width, height) {
  const canvas = els.graphCanvas;
  const frameRect = els.graphFrame.getBoundingClientRect();
  const drawWidth = Math.round(width || frameRect.width || 1);
  const drawHeight = Math.round(height || frameRect.height || 1);
  const ratio = window.devicePixelRatio || 1;
  canvas.width = drawWidth * ratio;
  canvas.height = drawHeight * ratio;
  canvas.style.width = `${drawWidth}px`;
  canvas.style.height = `${drawHeight}px`;

  const ctx = canvas.getContext("2d");
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  ctx.clearRect(0, 0, drawWidth, drawHeight);

  const selectedId = state.selectedNodeId;
  const highlightedIds = selectedId ? new Set(connectedNodeIds(selectedId)) : new Set();

  for (const edge of state.visibleEdges) {
    const source = state.nodeMap.get(edge.source);
    const target = state.nodeMap.get(edge.target);
    if (!source || !target) continue;

    const isHighlighted =
      selectedId &&
      (edge.source === selectedId ||
        edge.target === selectedId ||
        (highlightedIds.has(edge.source) && highlightedIds.has(edge.target)));

    ctx.beginPath();
    ctx.moveTo(source.x, source.y);
    const controlX = (source.x + target.x) / 2;
    const verticalBias = source.anchorKey === target.anchorKey ? -14 : 18;
    const controlY = (source.y + target.y) / 2 + verticalBias;
    ctx.quadraticCurveTo(controlX, controlY, target.x, target.y);
    ctx.lineWidth =
      state.viewMode === "overview"
        ? isHighlighted ? 2.4 : 1.8
        : isHighlighted ? 2 : edge.type === "organized_by" ? 1.4 : 1;
    ctx.strokeStyle = edgeStroke(edge.type, isHighlighted);
    ctx.stroke();
  }
}

function startPan(event) {
  event.preventDefault();
  state.viewport.panning = true;
  state.viewport.startX = event.clientX;
  state.viewport.startY = event.clientY;
  state.viewport.baseOffsetX = state.viewport.offsetX;
  state.viewport.baseOffsetY = state.viewport.offsetY;
  els.graphFrame.classList.add("panning");

  const onMove = (moveEvent) => {
    state.viewport.offsetX = state.viewport.baseOffsetX + (moveEvent.clientX - state.viewport.startX);
    state.viewport.offsetY = state.viewport.baseOffsetY + (moveEvent.clientY - state.viewport.startY);
    applyViewportTransform();
  };

  const onUp = () => {
    state.viewport.panning = false;
    els.graphFrame.classList.remove("panning");
    window.removeEventListener("pointermove", onMove);
    window.removeEventListener("pointerup", onUp);
  };

  window.addEventListener("pointermove", onMove);
  window.addEventListener("pointerup", onUp);
}

function zoomViewport(factor, pivotX = null, pivotY = null) {
  const frameRect = els.graphFrame.getBoundingClientRect();
  const px = pivotX ?? frameRect.width / 2;
  const py = pivotY ?? frameRect.height / 2;
  const oldScale = state.viewport.scale;
  const nextScale = clamp(oldScale * factor, 0.62, 2.1);
  const scaleRatio = nextScale / oldScale;
  state.viewport.offsetX = px - (px - state.viewport.offsetX) * scaleRatio;
  state.viewport.offsetY = py - (py - state.viewport.offsetY) * scaleRatio;
  state.viewport.scale = nextScale;
  applyViewportTransform();
}

function resetViewport() {
  state.viewport.scale = 1;
  state.viewport.offsetX = 0;
  state.viewport.offsetY = 0;
  applyViewportTransform();
}

function applyViewportTransform() {
  const transform = `translate(${state.viewport.offsetX}px, ${state.viewport.offsetY}px) scale(${state.viewport.scale})`;
  els.graphCanvas.style.transform = transform;
  els.nodesLayer.style.transform = transform;
}

function renderDetail(node) {
  const isReaderMode = Boolean(node && node.kind !== "domain" && state.noteViewMode === "full");
  syncReadingLayout(isReaderMode);

  if (!isReaderMode && activeSectionObserver) {
    activeSectionObserver.disconnect();
    activeSectionObserver = null;
  }

  if (!node) {
    els.detailCard.className = "detail-card empty";
    els.detailCard.innerHTML = `
      <p class="detail-kicker">Node Detail</p>
      <h2>Select a node</h2>
      <p class="detail-summary">This panel shows the selected note summary, grouping, type, and relation context.</p>
      <div class="detail-empty-note">Start from overview or click any node in the graph.</div>
    `;
    return;
  }

  if (node.kind === "domain") {
    const members = state.graph.noteNodes.filter((candidate) => getActiveDomain(candidate) === node.domain);
    const byType = countBy(members, (item) => getTypeLabel(item.type));
    els.detailCard.className = "detail-card";
    els.detailCard.innerHTML = `
      <p class="detail-kicker">Domain Hub</p>
      <h2>${escapeHtml(node.title)}</h2>
      <p class="detail-summary">${escapeHtml(node.summary)}</p>
      <div class="detail-meta">
        ${detailMetaBox("Members", String(node.memberCount))}
        ${detailMetaBox("Cross-Domain Links", String(node.degree))}
        ${detailMetaBox("Types Included", escapeHtml(Object.keys(byType).join(" / ")))}
        ${detailMetaBox("Role", "Domain hub and navigation entry")}
      </div>
      <div class="detail-grid">
        <section class="detail-section">
          <h3>Type Distribution</h3>
          <div class="detail-tags">${renderPills(Object.entries(byType).map(([label, count]) => `${label} ${count}`))}</div>
        </section>
        <section class="detail-section">
          <h3>Action</h3>
          <div class="focus-actions">
            <button id="detailFocusButton" class="ghost-button" type="button">Focus ${escapeHtml(node.title)}</button>
          </div>
        </section>
      </div>
    `;
    els.detailCard.querySelector("#detailFocusButton").addEventListener("click", () => focusDomain(node.domain));
    return;
  }

  const noteDetail = getNoteDetail(node.id);
  const outgoing = state.graph.edges.filter((edge) => edge.source === node.id && primaryEdgeTypes.has(edge.type));
  const incoming = (state.incomingMap.get(node.id) || []).filter((edge) => primaryEdgeTypes.has(edge.type));
  const outgoingGroups = groupRelations(outgoing, "target");
  const incomingGroups = groupRelations(incoming, "source");
  const resolvedSummary =
    node.summary ||
    noteDetail?.summary ||
    noteDetail?.body_preview ||
    "This node does not have a polished summary yet. Inspect related links or the full note body.";
  const resolvedPath = node.path || noteDetail?.path || "";

  if (isReaderMode) {
    els.detailCard.className = "detail-card reader";
    els.detailCard.innerHTML = renderReaderMode(node, noteDetail, resolvedSummary, resolvedPath, outgoingGroups, incomingGroups);
    scheduleMathTypeset(els.detailCard);
    setupSectionObserver(node.id);
    return;
  }

  els.detailCard.className = "detail-card";
  els.detailCard.innerHTML = `
    <p class="detail-kicker">${escapeHtml(getTypeLabel(node.type))}</p>
    <h2>${escapeHtml(node.title)}</h2>
    <div class="detail-summary rich-summary">${renderMarkdown(resolvedSummary, { compact: true })}</div>
    <div class="detail-meta">
      ${detailMetaBox("Domain", getDomainLabel(getActiveDomain(node)))}
      ${detailMetaBox("Type", getTypeLabel(node.type))}
      ${detailMetaBox("Links", String(node.degree))}
      ${detailMetaBox("Path", resolvedPath)}
    </div>
    <div class="detail-grid">
      ${renderNotePreview(node, noteDetail)}
      <section class="detail-section">
        <h3>Tags</h3>
        <div class="detail-tags">${renderPills(node.tags)}</div>
      </section>
      <section class="detail-section">
        <h3>Outgoing Relations</h3>
        ${renderRelationGroups(outgoingGroups)}
      </section>
      <section class="detail-section">
        <h3>Incoming Relations</h3>
        ${renderRelationGroups(incomingGroups)}
      </section>
    </div>
  `;
  scheduleMathTypeset(els.detailCard);
}

function renderReaderMode(node, detail, resolvedSummary, resolvedPath, outgoingGroups, incomingGroups) {
  const sections = detail?.sections || [];
  const outline = sections
    .map(
      (section, index) => `
        <button
          class="reader-outline-button"
          type="button"
          data-section-target="${escapeHtml(buildSectionTargetId(node.id, index))}"
        >
          <span class="reader-outline-index">${index + 1}</span>
          <span class="reader-outline-title">${escapeHtml(section.title)}</span>
        </button>
      `
    )
    .join("");

  const articleSections = sections
    .map(
      (section, index) => `
        <section class="reader-section-block" id="${escapeHtml(buildSectionTargetId(node.id, index))}">
          <h2>${escapeHtml(section.title)}</h2>
          <div class="reader-prose">${renderProse(section.content || section.preview || "")}</div>
        </section>
      `
    )
    .join("");

  const fallbackBody = detail?.body_full || detail?.body_preview || detail?.summary || resolvedSummary;

  return `
    <div class="reader-shell">
      <div class="reader-toolbar">
        <div class="detail-view-toggle" role="tablist" aria-label="筆記檢視模式">
          <button class="detail-view-button" type="button" data-note-view-mode="preview">預覽模式</button>
          <button class="detail-view-button active" type="button" data-note-view-mode="full">全文模式</button>
        </div>
        <button class="ghost-button" type="button" data-note-view-mode="preview">返回預覽</button>
      </div>

        <article class="reader-article">
          <div class="reader-layout ${outline ? "has-outline" : ""}">
            ${
              outline
                ? `
            <aside class="reader-outline-panel">
              <div class="reader-outline-header">
                <p class="detail-kicker">Outline</p>
                <p class="reader-outline-caption">Jump directly to the section you need.</p>
              </div>
              <div class="reader-outline-list">${outline}</div>
            </aside>
            `
                : ""
            }

            <div class="reader-main">
              <header class="reader-header">
                <p class="detail-kicker">${escapeHtml(getTypeLabel(node.type))}</p>
                <h1>${escapeHtml(node.title)}</h1>
                <div class="reader-summary rich-summary">${renderMarkdown(resolvedSummary, { compact: true })}</div>
                <div class="reader-meta-grid">
                  ${detailMetaBox("Domain", getDomainLabel(getActiveDomain(node)))}
                  ${detailMetaBox("Type", getTypeLabel(node.type))}
                  ${detailMetaBox("Links", String(node.degree))}
                  ${detailMetaBox("Path", resolvedPath)}
                </div>
              </header>

              <div class="reader-body-shell">
                <section class="reader-content">
                  ${
                    articleSections ||
                    `<div class="reader-prose">${renderProse(fallbackBody)}</div>`
                  }
                </section>
              </div>

              <footer class="reader-footer-grid">
                <section class="reader-footer-panel">
                  <p class="detail-kicker">Tags</p>
                  <div class="detail-tags">${renderPills(node.tags)}</div>
                </section>
                <section class="reader-footer-panel">
                  <p class="detail-kicker">Outgoing Relations</p>
                  ${renderRelationGroups(outgoingGroups)}
                </section>
                <section class="reader-footer-panel">
                  <p class="detail-kicker">Incoming Relations</p>
                  ${renderRelationGroups(incomingGroups)}
                </section>
              </footer>
            </div>
          </div>
        </article>
      </div>
    `;
  }

function renderNotePreview(node, detail) {
  if (!detail) {
    return `
      <section class="detail-section">
        <h3>筆記預覽</h3>
        <p class="detail-summary">這個節點還沒有對應的 Obsidian 匯出內容。</p>
      </section>
    `;
  }

  const isFullMode = state.noteViewMode === "full";
  const sectionItems = isFullMode ? detail.sections || [] : (detail.sections || []).slice(0, 6);
  const outline = sectionItems
    .map(
      (section, index) => `
        <button
          class="section-jump-button"
          type="button"
          data-section-target="${escapeHtml(buildSectionTargetId(node.id, index))}"
        >
          <span class="reader-outline-index">${index + 1}</span>
          <span class="reader-outline-title">${escapeHtml(section.title)}</span>
        </button>
      `
    )
    .join("");

  const sectionCards = sectionItems
    .map(
      (section, index) => `
        <article class="section-preview-card" id="${escapeHtml(buildSectionTargetId(node.id, index))}">
          <p class="detail-kicker">章節</p>
          <h4>${escapeHtml(section.title)}</h4>
          <div class="reader-prose compact-prose">${renderMarkdown(
            isFullMode ? section.content || section.preview || "" : section.preview || "",
            { compact: !isFullMode }
          )}</div>
        </article>
      `
    )
    .join("");

  return `
    <section class="detail-section">
      <div class="detail-section-heading">
        <h3>${isFullMode ? "筆記全文" : "筆記預覽"}</h3>
        <div class="detail-view-toggle" role="tablist" aria-label="筆記檢視模式">
          <button class="detail-view-button ${!isFullMode ? "active" : ""}" type="button" data-note-view-mode="preview">預覽</button>
          <button class="detail-view-button ${isFullMode ? "active" : ""}" type="button" data-note-view-mode="full">全文</button>
        </div>
      </div>
      <div class="detail-summary detail-body-copy reader-prose">${renderMarkdown(
        isFullMode ? detail.body_full || detail.body_preview || detail.summary || "" : detail.body_preview || detail.summary || "",
        { stripLeadingTitle: true, compact: !isFullMode, title: node.title }
      )}</div>
    </section>
    ${
      outline
        ? `
    <section class="detail-section preview-outline-panel">
      <div class="detail-section-heading">
        <h3>文章目錄</h3>
        <p class="detail-section-caption">點選章節直接跳到對應段落。</p>
      </div>
      <div class="detail-outline">${outline}</div>
    </section>`
        : ""
    }
    <section class="detail-section preview-sections-panel">
      <h3>${isFullMode ? "章節全文" : "章節預覽"}</h3>
      <div class="preview-sections-grid">
        ${
          sectionCards ||
          `<p class="detail-summary">這份筆記還沒有切分好的章節內容。</p>`
        }
      </div>
    </section>
  `;
}

function buildSectionTargetId(nodeId, index) {
  return `section-${nodeId}-${index}`.replaceAll(" ", "-");
}

let activeSectionObserver = null;

function setupSectionObserver(nodeId) {
  if (activeSectionObserver) {
    activeSectionObserver.disconnect();
    activeSectionObserver = null;
  }

  const sections = els.detailCard.querySelectorAll(".reader-section-block");
  const buttons = els.detailCard.querySelectorAll(".reader-outline-button");
  if (!sections.length || !buttons.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          const targetId = entry.target.id;
          for (const btn of buttons) {
            btn.classList.toggle("is-active", btn.dataset.sectionTarget === targetId);
          }
        }
      }
    },
    { rootMargin: "-10% 0px -60% 0px", threshold: 0 }
  );

  for (const section of sections) observer.observe(section);
  activeSectionObserver = observer;
}

function renderRelationGroups(groups) {
  if (groups.length === 0) {
    return `<p class="detail-summary">目前沒有可顯示的關聯節點。</p>`;
  }
  return groups
    .map(
      (group) => `
        <div class="relation-group">
          <p class="detail-kicker">${escapeHtml(relationLabel[group.type] || group.type)}</p>
          <div class="relation-list">
            ${group.items
              .map(
                (item) => `<button class="relation-pill" type="button" data-node-id="${escapeHtml(item.id)}">${escapeHtml(item.title)}</button>`
              )
              .join("")}
          </div>
        </div>`
    )
    .join("");
}

function renderNotesListView() {
  if (!state.graph) return;
  const notes = [...state.graph.noteNodes].sort((a, b) =>
    (a.domain || "").localeCompare(b.domain || "") || a.title.localeCompare(b.title, "zh-Hant")
  );

  const grouped = {};
  for (const note of notes) {
    const domain = note.domain || "未分類";
    if (!grouped[domain]) grouped[domain] = [];
    grouped[domain].push(note);
  }

  let html = `<p class="detail-kicker">Notes</p>
    <h2>All Notes (${notes.length})</h2>
    <p class="detail-summary">Grouped by domain. Click any note to focus it in the graph.</p>
    <div class="detail-grid">`;

  for (const [domain, domainNotes] of Object.entries(grouped)) {
    html += `<section class="detail-section">
      <h3>${escapeHtml(domain)}（${domainNotes.length}）</h3>
      <div class="detail-tags">${domainNotes.map(
        (n) => `<button class="pill note-pill" type="button" data-node-id="${escapeHtml(n.id)}">${escapeHtml(n.title)}</button>`
      ).join("")}</div>
    </section>`;
  }

  html += `</div>`;

  els.detailCard.className = "detail-card";
  els.detailCard.innerHTML = html;
}

function renderSettingsView() {
  const noteCount = state.graph?.noteNodes.length || 0;
  const edgeCount = state.graph?.edges.length || 0;
  const domainCount = state.graph?.domains.length || 0;

  els.detailCard.className = "detail-card";
  els.detailCard.innerHTML = `
    <p class="detail-kicker">About</p>
    <h2>Knowledge Base Viewer</h2>
    <p class="detail-summary">A generic graph-reading frontend for schema-first, vault-backed knowledge bases.</p>
    <div class="detail-meta">
      ${detailMetaBox("Notes", String(noteCount))}
      ${detailMetaBox("Relations", String(edgeCount))}
      ${detailMetaBox("Domains", String(domainCount))}
      ${detailMetaBox("Version", "prototype")}
    </div>
    <div class="detail-grid">
      <section class="detail-section">
        <h3>About</h3>
        <div class="detail-summary rich-summary">
          <p>This template frontend reads exported note and graph JSON generated from an external Markdown vault.</p>
          <p>It is meant to be reused across domains, not tied to any single subject such as physics.</p>
        </div>
      </section>
      <section class="detail-section">
        <h3>Stack</h3>
        <div class="detail-tags">${renderPills(["Obsidian", "Python", "Vanilla JS", "Canvas", "MathJax"])}</div>
      </section>
    </div>
  `;
}

function renderSearchView() {
  els.detailCard.className = "detail-card";
  els.detailCard.innerHTML = `
    <p class="detail-kicker">Search</p>
    <h2>Search the knowledge base</h2>
    <p class="detail-summary">Search notes by title, summary, type, domain, or tags.</p>
    <label class="search search-view-input">
      <input id="searchViewInput" type="search" placeholder="Example: causal graph, sampling, pricing model..." autofocus>
    </label>
    <div id="searchViewResults" class="detail-grid"></div>
  `;

  const input = document.getElementById("searchViewInput");
  const results = document.getElementById("searchViewResults");

  if (!input || !results) return;

  input.focus();

  input.addEventListener("input", () => {
    const query = input.value.trim().toLowerCase();
    if (!query) {
      results.innerHTML = `<p class="detail-summary">Results appear as you type.</p>`;
      return;
    }

    const matches = state.graph.noteNodes.filter((n) => n.searchText.includes(query)).slice(0, 50);

    if (!matches.length) {
      results.innerHTML = `<p class="detail-summary">No notes matched "${escapeHtml(input.value.trim())}".</p>`;
      return;
    }

    // Group by domain
    const grouped = {};
    for (const note of matches) {
      const domain = note.domain || "未分類";
      if (!grouped[domain]) grouped[domain] = [];
      grouped[domain].push(note);
    }

    let html = `<p class="detail-summary">Found ${matches.length} result${matches.length === 1 ? "" : "s"}${matches.length === 50 ? " (showing the first 50)" : ""}.</p>`;
    for (const [domain, notes] of Object.entries(grouped)) {
      html += `<section class="detail-section">
        <h3>${escapeHtml(domain)}（${notes.length}）</h3>
        <div class="detail-tags">${notes.map(
          (n) => `<button class="pill note-pill" type="button" data-node-id="${escapeHtml(n.id)}">${escapeHtml(n.title)}</button>`
        ).join("")}</div>
      </section>`;
    }
    results.innerHTML = html;

    // Wire up result pills
    for (const pill of results.querySelectorAll(".note-pill")) {
      pill.addEventListener("click", () => {
        const nodeId = pill.dataset.nodeId;
        const node = state.nodeMap.get(nodeId);
        if (!node) return;
        for (const btn of els.topnavButtons) btn.classList.remove("is-active");
        const graphBtn = document.querySelector('[data-view="graph"]');
        if (graphBtn) graphBtn.classList.add("is-active");

        state.selectedNodeId = node.id;
        renderDetail(node);
        layoutVisibleGraph(true);
      });
    }
  });
}

document.addEventListener("click", (event) => {
  const noteViewButton = event.target.closest("[data-note-view-mode]");
  if (noteViewButton) {
    const nextMode = noteViewButton.dataset.noteViewMode;
    if (nextMode && nextMode !== state.noteViewMode) {
      state.noteViewMode = nextMode;
      renderDetail(state.nodeMap.get(state.selectedNodeId) || null);
    }
    return;
  }

  const sectionJumpButton = event.target.closest(".section-jump-button, .reader-outline-button");
  if (sectionJumpButton) {
    const target = document.getElementById(sectionJumpButton.dataset.sectionTarget || "");
    if (target) {
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    }
    return;
  }

  const pill = event.target.closest(".relation-pill, .note-pill");
  const inlineLink = event.target.closest(".inline-note-link[data-node-id]");
  const targetButton = pill || inlineLink;
  if (!targetButton) return;
  const node = state.nodeMap.get(targetButton.dataset.nodeId);
  if (!node) return;
  // Switch topnav to graph when clicking from notes/search view
  if (targetButton.classList.contains("note-pill")) {
    for (const btn of els.topnavButtons) btn.classList.remove("is-active");
    const graphBtn = document.querySelector('[data-view="graph"]');
    if (graphBtn) graphBtn.classList.add("is-active");
  }
  if (node.kind === "domain") {
    focusDomain(node.domain);
    return;
  }
  // Set selectedNodeId BEFORE focusDomain so layoutVisibleGraph doesn't reset it
  state.selectedNodeId = node.id;
  if (getActiveDomain(node) !== "未分類") focusDomain(getActiveDomain(node));
  renderDetail(node);
  scrollReadingToTop();
  updateNodeStates();
  drawGraph();
});

function groupRelations(edges, relatedKey) {
  const grouped = new Map();
  for (const edge of edges) {
    const relatedNode = state.nodeMap.get(edge[relatedKey]);
    if (!relatedNode) continue;
    if (!grouped.has(edge.type)) grouped.set(edge.type, []);
    grouped.get(edge.type).push(relatedNode);
  }
  return [...grouped.entries()].map(([type, items]) => ({
    type,
    items: dedupeNodes(items).sort((a, b) => localeCompareZh(a.title, b.title)),
  }));
}

function edgeStroke(type, isHighlighted) {
  if (isHighlighted) return "rgba(159, 71, 47, 0.68)";
  const palette = {
    organized_by: "rgba(164, 77, 48, 0.34)",
    requires: "rgba(49, 90, 142, 0.26)",
    formalized_by: "rgba(147, 100, 51, 0.26)",
    derives_to: "rgba(95, 124, 66, 0.24)",
    uses: "rgba(93, 66, 140, 0.22)",
    verified_by: "rgba(115, 86, 52, 0.24)",
    explains: "rgba(98, 83, 72, 0.22)",
    measures: "rgba(83, 112, 85, 0.22)",
    related_to: "rgba(90, 100, 115, 0.18)",
    wikilink: "rgba(90, 100, 115, 0.1)",
  };
  return palette[type] || "rgba(90, 100, 115, 0.16)";
}

function connectedNodeIds(nodeId) {
  const ids = new Set([nodeId]);
  for (const edge of state.visibleEdges) {
    if (edge.source === nodeId) ids.add(edge.target);
    if (edge.target === nodeId) ids.add(edge.source);
  }
  return ids;
}

function startDragGesture(event, node) {
  if (event.button !== 0) return;
  const rect = els.graphFrame.getBoundingClientRect();
  const originX = event.clientX;
  const originY = event.clientY;
  const dragThreshold = 6;
  let dragging = false;

  const beginDrag = (pointerX, pointerY) => {
    event.preventDefault();
    state.draggingNodeId = node.id;
    state.pointerOffset.x = node.x - pointerX;
    state.pointerOffset.y = node.y - pointerY;
    dragging = true;
  };

  const onMove = (moveEvent) => {
    const moveX = moveEvent.clientX - rect.left;
    const moveY = moveEvent.clientY - rect.top;

    if (!dragging) {
      const deltaX = moveEvent.clientX - originX;
      const deltaY = moveEvent.clientY - originY;
      if (Math.hypot(deltaX, deltaY) < dragThreshold) return;
      beginDrag(moveX, moveY);
      state.suppressNodeClickUntil = performance.now() + 250;
    }

    node.x = clamp(moveX + state.pointerOffset.x, 54, rect.width - 54);
    node.y = clamp(moveY + state.pointerOffset.y, 54, rect.height - 54);
    node.vx = 0;
    node.vy = 0;
    node.element.style.left = `${node.x}px`;
    node.element.style.top = `${node.y}px`;
    drawGraph(rect.width, rect.height);
  };

  const onUp = () => {
    window.removeEventListener("pointermove", onMove);
    window.removeEventListener("pointerup", onUp);
    if (!dragging) return;
    state.draggingNodeId = null;
    layoutVisibleGraph(false);
  };

  window.addEventListener("pointermove", onMove);
  window.addEventListener("pointerup", onUp);
}

function inferDomainFromTags(tags) {
  const domainTagMap = {
    core: "core",
    methods: "methods",
    applications: "applications",
  };
  for (const tag of tags) {
    if (domainTagMap[tag]) return domainTagMap[tag];
  }
  return "uncategorized";
}

function detailMetaBox(label, value) {
  return `
    <div class="detail-meta-box">
      <div class="detail-meta-label">${escapeHtml(label)}</div>
      <div class="detail-meta-value">${escapeHtml(value)}</div>
    </div>
  `;
}

function renderPills(values) {
  if (!values || values.length === 0) return `<span class="pill">無</span>`;
  return values.map((value) => `<span class="pill">${escapeHtml(value)}</span>`).join("");
}

function countBy(items, getter) {
  const result = {};
  for (const item of items) {
    const key = getter(item);
    result[key] = (result[key] || 0) + 1;
  }
  return result;
}

function compareFocusNodes(a, b) {
  const typeOrder = {
    map: 0,
    law: 1,
    concept: 2,
    quantity: 3,
    mathematical_tool: 4,
  };
  const orderA = typeOrder[a.type] ?? 99;
  const orderB = typeOrder[b.type] ?? 99;
  if (orderA !== orderB) return orderA - orderB;
  return localeCompareZh(a.title, b.title);
}

function dedupeNodes(nodes) {
  const seen = new Set();
  const result = [];
  for (const node of nodes) {
    if (seen.has(node.id)) continue;
    seen.add(node.id);
    result.push(node);
  }
  return result;
}

function unique(values) {
  return [...new Set(values)];
}

function hashString(text) {
  let hash = 0;
  for (let i = 0; i < text.length; i += 1) {
    hash = (hash * 31 + text.charCodeAt(i)) % 100000;
  }
  return hash / 1000;
}

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function localeCompareZh(a, b) {
  return String(a).localeCompare(String(b), "zh-Hant");
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function escapeAttribute(value) {
  return escapeHtml(value).replaceAll("`", "&#96;");
}

function formatMultilineText(value) {
  return escapeHtml(String(value || "")).replaceAll("\n", "<br>");
}

function renderProse(value) {
  return renderMarkdown(value, { stripLeadingTitle: true });
}

function renderMarkdown(value, options = {}) {
  const { compact = false, stripLeadingTitle = false, title = "" } = options;
  const normalized = String(value || "").replaceAll("\r\n", "\n").trim();
  if (!normalized) return "";

  const prepared = stripLeadingTitle ? removeLeadingTitle(normalized, title) : normalized;
  const protectedText = protectMathSegments(prepared);
  const lines = protectedText.text.split("\n");
  const blocks = [];

  for (let index = 0; index < lines.length; ) {
    const rawLine = lines[index];
    const line = rawLine.trim();

    if (!line) {
      index += 1;
      continue;
    }

    if (isMathTokenLine(line, protectedText.tokens)) {
      blocks.push(`<div class="math-block">${restoreTokens(line, protectedText.tokens)}</div>`);
      index += 1;
      continue;
    }

    const imageBlockHtml = renderImageBlock(line, protectedText.tokens);
    if (imageBlockHtml) {
      blocks.push(imageBlockHtml);
      index += 1;
      continue;
    }

    const headingMatch = line.match(/^(#{1,6})\s+(.+)$/);
    if (headingMatch) {
      const level = Math.min(6, headingMatch[1].length + 1);
      blocks.push(`<h${level}>${renderInlineMarkup(headingMatch[2], protectedText.tokens)}</h${level}>`);
      index += 1;
      continue;
    }

    if (/^- /.test(line)) {
      const items = [];
      while (index < lines.length && /^- /.test(lines[index].trim())) {
        items.push(`<li>${renderInlineMarkup(lines[index].trim().slice(2), protectedText.tokens)}</li>`);
        index += 1;
      }
      blocks.push(`<ul>${items.join("")}</ul>`);
      continue;
    }

    if (/^\d+\.\s/.test(line)) {
      const items = [];
      while (index < lines.length && /^\d+\.\s/.test(lines[index].trim())) {
        items.push(`<li>${renderInlineMarkup(lines[index].trim().replace(/^\d+\.\s/, ""), protectedText.tokens)}</li>`);
        index += 1;
      }
      blocks.push(`<ol>${items.join("")}</ol>`);
      continue;
    }

    const paragraphLines = [];
    while (index < lines.length) {
      const candidate = lines[index].trim();
      if (!candidate) break;
      if (isMathTokenLine(candidate, protectedText.tokens)) break;
      if (/^(#{1,6})\s+/.test(candidate) || /^- /.test(candidate) || /^\d+\.\s/.test(candidate)) break;
      paragraphLines.push(lines[index]);
      index += 1;
    }

    const paragraphHtml = renderInlineMarkup(paragraphLines.join(compact ? " " : "\n"), protectedText.tokens).replaceAll("\n", "<br>");
    blocks.push(`<p>${paragraphHtml}</p>`);
  }

  return blocks.join("");
}

function removeLeadingTitle(value, title) {
  const lines = value.split("\n");
  let firstContentIndex = 0;
  while (firstContentIndex < lines.length && !lines[firstContentIndex].trim()) firstContentIndex += 1;
  if (firstContentIndex >= lines.length) return value;
  const firstLine = lines[firstContentIndex].trim();
  if (!firstLine.startsWith("#")) return value;
  const normalizedTitle = firstLine.replace(/^#+\s*/, "").trim();
  if (title && normalizedTitle !== String(title).trim()) return value;
  lines.splice(firstContentIndex, 1);
  while (lines[firstContentIndex] !== undefined && !lines[firstContentIndex].trim()) {
    lines.splice(firstContentIndex, 1);
  }
  return lines.join("\n");
}

function protectMathSegments(text) {
  const tokens = new Map();
  let counter = 0;
  let protectedText = text.replace(/\$\$[\s\S]+?\$\$/g, (match) => {
    const token = `@@MATH${counter++}@@`;
    tokens.set(token, { raw: match, display: true });
    return token;
  });

  protectedText = protectedText.replace(/\$(?!\$)([^$\n]|\\\$)+?\$/g, (match) => {
    const token = `@@MATH${counter++}@@`;
    tokens.set(token, { raw: match, display: false });
    return token;
  });

  return { text: protectedText, tokens };
}

function isMathTokenLine(line, tokens) {
  return tokens.has(line) && Boolean(tokens.get(line)?.display);
}

function restoreTokens(text, tokens) {
  let restored = text;
  for (const [token, meta] of tokens.entries()) {
    restored = restored.replaceAll(token, meta.raw);
  }
  return restored;
}

function renderImageBlock(text, tokens) {
  const restored = restoreTokens(String(text || "").trim(), tokens);
  const image = parseMarkdownImage(restored);
  if (!image) return "";
  return buildImageFigure(image);
}

function renderInlineMarkup(text, tokens) {
  const parts = String(text || "").split(/(@@MATH\d+@@|!\[[^\]]*?\]\([^)\n]+?\)|\[\[[^\]]+\]\]|`[^`]+`)/g);
  return parts
    .filter((part) => part !== "")
    .map((part) => {
      if (tokens.has(part)) return tokens.get(part).raw;
      if (part.startsWith("![")) {
        const image = parseMarkdownImage(part);
        return image ? buildInlineImage(image) : escapeHtml(part);
      }
      if (part.startsWith("[[")) return renderWikiLink(part);
      const codeMatch = part.match(/^`([^`]+)`$/);
      if (codeMatch) return `<code>${escapeHtml(codeMatch[1])}</code>`;
      return autoLinkPlainMentions(part);
    })
    .join("");
}

function parseMarkdownImage(raw) {
  const match = String(raw || "").trim().match(/^!\[([^\]]*)\]\((.+)\)$/);
  if (!match) return null;

  const alt = String(match[1] || "").trim();
  const parsedDestination = parseImageDestination(match[2]);
  if (!parsedDestination || !isSafeImageUrl(parsedDestination.src)) return null;

  return {
    alt,
    src: parsedDestination.src,
    caption: parsedDestination.title || alt,
  };
}

function parseImageDestination(value) {
  const trimmed = String(value || "").trim();
  if (!trimmed) return null;

  const titledMatch = trimmed.match(/^(.+?)\s+(?:"([^"]+)"|'([^']+)')$/);
  if (titledMatch) {
    return {
      src: titledMatch[1].trim(),
      title: String(titledMatch[2] || titledMatch[3] || "").trim(),
    };
  }

  return {
    src: trimmed,
    title: "",
  };
}

function isSafeImageUrl(value) {
  const normalized = String(value || "").trim().toLowerCase();
  if (!normalized) return false;
  return !normalized.startsWith("javascript:") && !normalized.startsWith("data:text/html");
}

function buildImageFigure(image) {
  const captionHtml = image.caption
    ? `<figcaption class="content-figure-caption">${escapeHtml(image.caption)}</figcaption>`
    : "";
  return `
    <figure class="content-figure">
      <img class="content-image" src="${escapeAttribute(image.src)}" alt="${escapeAttribute(image.alt)}" loading="lazy">
      ${captionHtml}
    </figure>
  `;
}

function buildInlineImage(image) {
  return `<img class="content-image inline-image" src="${escapeAttribute(image.src)}" alt="${escapeAttribute(image.alt)}" loading="lazy">`;
}

function renderWikiLink(rawLink) {
  const match = rawLink.match(/^\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|([^\]]+))?\]\]$/);
  if (!match) return escapeHtml(rawLink);
  const targetTitle = String(match[1] || "").trim();
  const label = String(match[2] || match[1] || "").trim();
  const targetNode = findNodeByTitle(targetTitle);
  if (!targetNode) {
    return `<span class="inline-note-link unresolved">${escapeHtml(label)}</span>`;
  }
  return `<button class="inline-note-link" type="button" data-node-id="${escapeHtml(targetNode.id)}">${escapeHtml(label)}</button>`;
}

function buildMentionIndex(graph) {
  const mentionTargets = new Map();
  for (const node of graph.noteNodes) {
    const title = String(node.title || "").trim();
    if (!title) continue;
    const hasCjk = /[\u3400-\u9fff]/.test(title);
    const asciiLettersOnly = /^[A-Za-z0-9\s\-+*/.=()]+$/.test(title);
    if (!hasCjk && (title.length < 3 || asciiLettersOnly && title.length < 4)) continue;
    if (!mentionTargets.has(title)) mentionTargets.set(title, node);
  }

  const titles = [...mentionTargets.keys()].sort((a, b) => b.length - a.length || localeCompareZh(a, b));
  state.mentionTargets = mentionTargets;
  state.mentionPattern = titles.length
    ? new RegExp(titles.map((title) => escapeRegex(title)).join("|"), "g")
    : null;
}

function autoLinkPlainMentions(text) {
  const source = String(text || "");
  if (!source || !state.mentionPattern || !state.mentionTargets.size) return escapeHtml(source);

  const fragments = [];
  let cursor = 0;
  let matchCount = 0;
  const maxMatchesPerChunk = 8;
  state.mentionPattern.lastIndex = 0;

  for (const match of source.matchAll(state.mentionPattern)) {
    const title = match[0];
    const start = match.index ?? -1;
    if (start < 0 || start < cursor) continue;
    const targetNode = state.mentionTargets.get(title);
    if (!targetNode) continue;

    if (start > cursor) {
      fragments.push(escapeHtml(source.slice(cursor, start)));
    }

    if (matchCount >= maxMatchesPerChunk) {
      fragments.push(escapeHtml(source.slice(start)));
      cursor = source.length;
      break;
    }

    fragments.push(
      `<button class="inline-note-link auto-linked" type="button" data-node-id="${escapeHtml(targetNode.id)}">${escapeHtml(title)}</button>`
    );
    cursor = start + title.length;
    matchCount += 1;
  }

  if (cursor < source.length) {
    fragments.push(escapeHtml(source.slice(cursor)));
  }

  return fragments.join("");
}

function findNodeByTitle(title) {
  return state.graph?.noteNodes?.find((node) => node.title === title) || null;
}

function escapeRegex(value) {
  return String(value || "").replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function scheduleMathTypeset(container) {
  if (!container) return;
  if (window.MathJax?.typesetPromise) {
    if (typeof window.MathJax.typesetClear === "function") {
      window.MathJax.typesetClear([container]);
    }
    window.MathJax.typesetPromise([container]).catch((error) => {
      console.error("Math typeset failed", error);
    });
    return;
  }
  window.setTimeout(() => scheduleMathTypeset(container), 120);
}

function scrollReadingToTop() {
  window.requestAnimationFrame(() => {
    els.detailCard?.scrollTo({ top: 0, behavior: "auto" });
    els.detailPanel?.scrollTo?.({ top: 0, behavior: "auto" });
    if (state.noteViewMode === "full") {
      window.scrollTo({ top: 0, behavior: "auto" });
    }
  });
}

function syncReadingLayout(isReaderMode) {
  els.workspace?.classList.toggle("reader-mode", isReaderMode);
  els.graphPanel?.classList.toggle("reader-hidden", isReaderMode);
  els.detailPanel?.classList.toggle("reader-panel", isReaderMode);
}

function cssEscape(value) {
  if (window.CSS?.escape) return window.CSS.escape(String(value));
  return String(value).replaceAll('"', '\\"');
}

function syncVisibleNodeRefs(nodes) {
  for (const node of nodes) {
    state.nodeMap.set(node.id, node);
  }
}

function selectOverviewNodesForDomain(domain) {
  const domainNotes = state.graph.noteNodes.filter(
    (node) => getActiveDomain(node) === domain && state.typeSelection.has(node.type)
  );
  const maps = domainNotes
    .filter((node) => overviewNodeTypes.has(node.type))
    .sort(compareFocusNodes)
    .slice(0, 2);
  const hub = domainNotes
    .filter((node) => !overviewNodeTypes.has(node.type))
    .sort((a, b) => b.degree - a.degree || compareFocusNodes(a, b))[0];
  return hub ? [...maps, { ...hub, overviewHub: true }] : maps;
}

function collectMatchingNodes({ domains, types, searchTerm, limit, includeMapsFirst = false }) {
  const allowedDomains = new Set(domains);
  const allowedTypes = new Set(types);
  const matches = state.graph.noteNodes.filter((node) => {
    if (!allowedDomains.has(getActiveDomain(node))) return false;
    if (!allowedTypes.has(node.type)) return false;
    if (!searchTerm) return true;
    return node.searchText.includes(searchTerm);
  });
  matches.sort((a, b) => {
    const mapBoost = includeMapsFirst
      ? Number(overviewNodeTypes.has(b.type)) - Number(overviewNodeTypes.has(a.type))
      : 0;
    if (mapBoost) return mapBoost;
    return b.degree - a.degree || compareFocusNodes(a, b);
  });
  return matches.slice(0, limit).map((node) => ({ ...node }));
}

function buildDomainSeedNodes(domain, filteredNodes) {
  const ranked = [...filteredNodes].sort((a, b) => {
    const typeWeight = seedTypeWeight(a.type) - seedTypeWeight(b.type);
    if (typeWeight !== 0) return typeWeight;
    return b.degree - a.degree || compareFocusNodes(a, b);
  });
  const maps = ranked.filter((node) => node.type === "map").slice(0, 2);
  const others = ranked.filter((node) => node.type !== "map");
  const selected = dedupeNodes([...maps, ...others]).slice(0, domainSeedLimit);
  return selected.map((node) => ({ ...node }));
}

function rankRelatedNodes(nodes) {
  return dedupeNodes(nodes).sort((a, b) => {
    const typeWeight = seedTypeWeight(a.type) - seedTypeWeight(b.type);
    if (typeWeight !== 0) return typeWeight;
    return b.degree - a.degree || compareFocusNodes(a, b);
  });
}

function seedTypeWeight(type) {
  const order = {
    map: 0,
    law: 1,
    concept: 2,
    quantity: 3,
    mathematical_tool: 4,
    experiment: 5,
  };
  return order[type] ?? 99;
}

function dedupeEdges(edges) {
  const seen = new Set();
  const result = [];
  for (const edge of edges) {
    const key = `${edge.source}|${edge.target}|${edge.type}`;
    if (seen.has(key)) continue;
    seen.add(key);
    result.push(edge);
  }
  return result;
}

function describeNodeMeta(node) {
  const label = getDomainLabel(getActiveDomain(node));
  if (node.focal) return `焦點節點 · ${label}`;
  if (node.overviewHub) return `高連結樞紐 · ${label}`;
  if (node.support) return `支撐節點 · ${label}`;
  return label;
}

function collectSupportNodes(seedNodes, { limit }) {
  const primaryIds = new Set(seedNodes.map((node) => node.id));
  const supportIds = new Set();
  for (const edge of state.graph.edges) {
    if (!structuralEdgeTypes.has(edge.type)) continue;
    if (primaryIds.has(edge.source) && !primaryIds.has(edge.target)) supportIds.add(edge.target);
    if (primaryIds.has(edge.target) && !primaryIds.has(edge.source)) supportIds.add(edge.source);
  }
  return rankRelatedNodes(
    [...supportIds]
      .map((id) => state.nodeMap.get(id))
      .filter(Boolean)
      .filter((node) => node.kind === "note" && state.typeSelection.has(node.type))
  )
    .slice(0, limit)
    .map((node) => ({ ...node, support: true }));
}

function prepareLocalNeighborhood(domain, filteredNodes, selectedNode) {
  const filteredIds = new Set(filteredNodes.map((node) => node.id));
  if (!filteredIds.has(selectedNode.id)) return null;

  const directPrimary = [];
  const directSupport = [];
  for (const edge of state.graph.edges) {
    if (!primaryEdgeTypes.has(edge.type)) continue;
    const otherId =
      edge.source === selectedNode.id ? edge.target : edge.target === selectedNode.id ? edge.source : null;
    if (!otherId) continue;
    const other = state.nodeMap.get(otherId);
    if (!other || other.kind !== "note") continue;
    if (getActiveDomain(other) === domain && filteredIds.has(other.id)) directPrimary.push(other);
    else directSupport.push(other);
  }

  const rankedPrimary = rankRelatedNodes(directPrimary).slice(0, localPrimaryLimit);
  const rankedSupport = rankRelatedNodes(directSupport)
    .filter((node) => state.typeSelection.has(node.type))
    .slice(0, localSupportLimit)
    .map((node) => ({ ...node, support: true }));
  const fallbackSeed = buildDomainSeedNodes(domain, filteredNodes).slice(0, 6);
  const nodes = dedupeNodes([
    { ...selectedNode, focal: true },
    ...rankedPrimary.map((node) => ({ ...node })),
    ...rankedSupport,
    ...fallbackSeed.map((node) => ({ ...node })),
  ]).sort((a, b) => {
    const focusBoost = Number(Boolean(b.focal)) - Number(Boolean(a.focal));
    if (focusBoost) return focusBoost;
    return compareFocusNodes(a, b);
  });

  const visibleIds = new Set(nodes.map((node) => node.id));
  const edges = state.graph.edges.filter((edge) => {
    if (!visibleIds.has(edge.source) || !visibleIds.has(edge.target)) return false;
    if (edge.source === selectedNode.id || edge.target === selectedNode.id) {
      return primaryEdgeTypes.has(edge.type);
    }
    return structuralEdgeTypes.has(edge.type);
  });

  const anchors = new Map();
  for (const node of nodes) {
    if (node.focal) node.anchorKey = "focus";
    else if (node.support) node.anchorKey = "support";
    else node.anchorKey = node.type;
  }
  return { nodes, edges: dedupeEdges(edges), anchors };
}

function prepareOverviewGraph() {
  const domainNodes = state.graph.domainNodes.filter((node) => state.domainSelection.has(node.domain));
  const curatedNodes = state.searchTerm
    ? collectMatchingNodes({
        domains: [...state.domainSelection],
        types: [...state.typeSelection],
        searchTerm: state.searchTerm,
        limit: overviewSearchLimit,
        includeMapsFirst: true,
      })
    : state.graph.domains.flatMap((domain) => selectOverviewNodesForDomain(domain));
  const noteNodes = dedupeNodes(curatedNodes).map((node) => ({ ...node }));
  const visibleNodes = dedupeNodes([...domainNodes, ...noteNodes]);
  const visibleIds = new Set(visibleNodes.map((node) => node.id));
  const noteIds = new Set(noteNodes.map((node) => node.id));
  const edges = [
    ...state.graph.domainEdges.filter((edge) => visibleIds.has(edge.source) && visibleIds.has(edge.target)),
    ...noteNodes.map((node) => ({
      source: `domain::${getActiveDomain(node)}`,
      target: node.id,
      type: "organized_by",
      synthetic: true,
    })),
    ...state.graph.edges.filter((edge) => {
      if (!structuralEdgeTypes.has(edge.type)) return false;
      return noteIds.has(edge.source) && noteIds.has(edge.target);
    }),
  ];

  for (const node of noteNodes) node.anchorKey = getActiveDomain(node);
  return { nodes: visibleNodes, edges: dedupeEdges(edges) };
}

function prepareDomainGraph() {
  const domain = state.focusedDomain && state.domainSelection.has(state.focusedDomain)
    ? state.focusedDomain
    : [...state.domainSelection][0];

  if (!domain) {
    state.viewMode = "overview";
    syncModeButtons();
    return prepareOverviewGraph();
  }

  state.focusedDomain = domain;
  const filteredNodes = state.graph.noteNodes.filter((node) => {
    const matchesDomain = getActiveDomain(node) === domain;
    const matchesType = state.typeSelection.has(node.type);
    const matchesSearch = !state.searchTerm || node.searchText.includes(state.searchTerm);
    return matchesDomain && matchesType && matchesSearch;
  });

  const selectedNode = state.nodeMap.get(state.selectedNodeId);
  if (selectedNode && selectedNode.kind === "note" && getActiveDomain(selectedNode) === domain) {
    const focused = prepareLocalNeighborhood(domain, filteredNodes, selectedNode);
    if (focused) return focused;
  }

  const seedNodes = buildDomainSeedNodes(domain, filteredNodes);
  const supportNodes = collectSupportNodes(seedNodes, { limit: domainSupportLimit });
  const merged = dedupeNodes([...seedNodes, ...supportNodes]).sort(compareFocusNodes);
  const visibleIds = new Set(merged.map((node) => node.id));
  const edges = state.graph.edges.filter((edge) => {
    if (!structuralEdgeTypes.has(edge.type)) return false;
    return visibleIds.has(edge.source) && visibleIds.has(edge.target);
  });

  const anchors = new Map();
  for (const node of merged) node.anchorKey = node.support ? `${domain}-support` : node.type;
  return { nodes: merged, edges: dedupeEdges(edges), anchors };
}

function updateGraphHint() {
  els.backToOverviewToolbarButton.hidden = state.viewMode !== "domain";
  const selectedNode = state.nodeMap.get(state.selectedNodeId);
  const isLocalFocus = Boolean(
    state.viewMode === "domain" &&
      selectedNode &&
      selectedNode.kind === "note" &&
      getActiveDomain(selectedNode) === state.focusedDomain
  );
  els.graphHint.textContent =
    state.viewMode === "overview"
      ? "Overview keeps only domain hubs, map pages, and a small number of high-signal notes. Start broad, then zoom into a domain or a single note neighborhood."
      : isLocalFocus
        ? `Current local view is centered on "${selectedNode.title}" inside "${state.focusedDomain}", showing direct relations plus necessary support nodes.`
        : `Current focus is "${state.focusedDomain}". Inspect the core structure first, then click a note to switch to a local neighborhood view.`;
}

function updateFocusBanner() {
  if (state.viewMode !== "domain" || !state.focusedDomain) {
    els.focusBanner.hidden = true;
    els.focusBanner.innerHTML = "";
    return;
  }

  const primaryCount = state.visibleNodes.filter((node) => !node.support).length;
  const supportCount = state.visibleNodes.filter((node) => node.support).length;
  const selectedNode = state.nodeMap.get(state.selectedNodeId);
  const isLocalFocus = Boolean(
    selectedNode &&
      selectedNode.kind === "note" &&
      getActiveDomain(selectedNode) === state.focusedDomain &&
      state.visibleNodes.some((node) => node.id === selectedNode.id)
  );

  els.focusBanner.hidden = false;
  els.focusBanner.innerHTML = `
    <div class="focus-banner-copy">
      <p class="eyebrow">${isLocalFocus ? "Local Neighborhood" : "Domain Focus"}</p>
      <p>
        <strong>${escapeHtml(state.focusedDomain)}</strong>
        ${
          isLocalFocus
            ? ` currently shows ${primaryCount} core node(s) and ${supportCount} support node(s) around "${escapeHtml(selectedNode.title)}".`
            : ` currently shows ${primaryCount} core node(s) and ${supportCount} support node(s) to keep the graph readable.`
        }
      </p>
    </div>
    <div class="focus-banner-metrics">
      <span class="focus-banner-metric">${primaryCount} core</span>
      <span class="focus-banner-metric">${supportCount} support</span>
    </div>
    <div class="focus-actions focus-banner-actions">
      <button id="backToOverviewButton" class="ghost-button" type="button">Back to overview</button>
    </div>
  `;
  els.focusBanner.querySelector("#backToOverviewButton").addEventListener("click", () => {
    state.viewMode = "overview";
    state.focusedDomain = null;
    syncModeButtons();
    buildDomainOverview();
    layoutVisibleGraph(true);
  });
}

function ensureNodeElements(visibleNodes) {
  const activeIds = new Set(visibleNodes.map((node) => node.id));
  for (const child of [...els.nodesLayer.children]) {
    if (!activeIds.has(child.dataset.id)) child.remove();
  }

  for (const node of visibleNodes) {
    let element = els.nodesLayer.querySelector(`[data-id="${cssEscape(node.id)}"]`);
    if (!element) {
      element = document.createElement("button");
      element.type = "button";
      element.className = "node";
      element.dataset.id = node.id;
      element.addEventListener("click", () => {
        if (performance.now() < state.suppressNodeClickUntil) return;
        const liveNode = state.nodeMap.get(node.id);
        if (!liveNode) return;
        if (liveNode.kind === "domain") {
          focusDomain(liveNode.domain);
          return;
        }
        state.selectedNodeId = liveNode.id;
        drawGraph();
        renderDetail(liveNode);
        scrollReadingToTop();
        updateNodeStates();
      });
      element.addEventListener("pointerdown", (event) => {
        const liveNode = state.nodeMap.get(node.id);
        if (!liveNode || liveNode.kind === "domain") return;
        startDrag(event, liveNode);
      });
      els.nodesLayer.appendChild(element);
    }

    element.className = "node";
    if (node.kind === "domain") element.classList.add("domain-node");
    if (node.support) element.classList.add("support");
    element.dataset.id = node.id;
    element.dataset.type = node.type;
    element.innerHTML = renderNodeContent(node);
    node.element = element;
    const rect = element.getBoundingClientRect();
    node.boxWidth = Math.max(rect.width || 140, node.kind === "domain" ? 170 : 110);
    node.boxHeight = Math.max(rect.height || 68, node.kind === "domain" ? 92 : 70);
  }

  updateNodeStates();
}

function renderNodeContent(node) {
  const isMedallion = node.kind === "domain" || node.focal || node.overviewHub || node.type === "map";

  if (isMedallion) {
    return `
      <div class="node-shell node-shell-medallion">
        <div class="node-core">
          <div class="node-core-title">${escapeHtml(node.title)}</div>
        </div>
      </div>
    `;
  }

  return `
    <div class="node-shell node-shell-badge">
      <div class="node-core">
        <div class="node-title">${escapeHtml(node.title)}</div>
      </div>
    </div>
  `;
}

function updateNodeStates() {
  const selected = state.selectedNodeId ? state.nodeMap.get(state.selectedNodeId) : null;
  const connected = selected ? new Set(connectedNodeIds(selected.id)) : null;

  for (const node of state.visibleNodes) {
    const element = node.element;
    element.classList.toggle("selected", node.id === state.selectedNodeId);
    element.classList.toggle("focal", Boolean(node.focal));
    element.classList.toggle("overview-hub", Boolean(node.overviewHub));
    element.classList.toggle(
      "dimmed",
      Boolean(selected) &&
        node.kind !== "domain" &&
        node.id !== selected.id &&
        !connected.has(node.id)
    );
    if (node.kind === "domain") element.classList.remove("dimmed");
  }
}
