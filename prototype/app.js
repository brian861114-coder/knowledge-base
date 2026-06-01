const graphUrl = "../physics_graph.json";
const noteDetailsUrl = "../physics_note_details.json";
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
  viewMode: "overview",
  focusedDomain: null,
  searchTerm: "",
  selectedNodeId: null,
  noteViewMode: "preview",
  draggingNodeId: null,
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
  typeFilters: document.getElementById("typeFilters"),
  domainOverview: document.getElementById("domainOverview"),
  graphFrame: document.getElementById("graphFrame"),
  graphCanvas: document.getElementById("graphCanvas"),
  nodesLayer: document.getElementById("nodesLayer"),
  workspace: document.querySelector(".workspace"),
  graphPanel: document.querySelector(".graph-panel"),
  detailPanel: document.querySelector(".detail-panel"),
  detailCard: document.getElementById("detailCard"),
  zoomOutButton: document.getElementById("zoomOutButton"),
  zoomInButton: document.getElementById("zoomInButton"),
  fitViewButton: document.getElementById("fitViewButton"),
  backToOverviewToolbarButton: document.getElementById("backToOverviewToolbarButton"),
  resetViewButton: document.getElementById("resetViewButton"),
  graphHint: document.getElementById("graphHint"),
};

const typeLabel = {
  map: "導覽頁",
  law: "定律",
  concept: "概念",
  quantity: "物理量",
  mathematical_tool: "數學工具",
  domain: "領域",
};

const relationLabel = {
  organized_by: "主題收納",
  requires: "先備關係",
  formalized_by: "數學支撐",
  derives_to: "可推出",
  uses: "直接使用",
  verified_by: "實驗驗證",
  explains: "進階視角",
  measures: "量測對應",
  related_to: "相關概念",
  wikilink: "文內連結",
};

const domainDescriptions = {
  力學: "從運動、力、能量與動量開始，是整張地圖的骨架。",
  振動與波動: "把粒子運動延伸成週期振盪與波的傳播。",
  熱學與熱力學: "聚焦巨觀系統中的熱、內能、熵與循環。",
  電磁學: "從電荷與電場出發，擴展到磁、感應與電磁波。",
  光學: "在幾何光學與波動光學之間切換視角。",
  近代物理: "經典理論失效後，往相對論與量子入門展開。",
  流體力學: "將力學延伸到液體與氣體的連續介質。",
  數學工具: "不是完整數學百科，而是解釋數學在物理裡拿來做什麼。",
  未分類: "尚未歸入正式領域的節點或過渡內容。",
};

init().catch((error) => {
  console.error(error);
  els.detailCard.classList.remove("empty");
  els.detailCard.innerHTML = `
    <p class="detail-kicker">Load Error</p>
    <h2>無法載入 graph 資料</h2>
    <p class="detail-summary">${escapeHtml(String(error.message || error))}</p>
  `;
});

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
  buildModeButtons();
  buildFilters(graph);
  buildDomainOverview();
  bindEvents();
  resetViewport();
  layoutVisibleGraph(true);
}

function normalizeGraph(rawGraph) {
  const baseNodes = rawGraph.nodes.map((node, index) => ({
    ...node,
    domain: node.domain || inferDomainFromTags(node.tags || []),
    tags: node.tags || [],
    x: 0,
    y: 0,
    vx: 0,
    vy: 0,
    degree: 0,
    support: false,
    kind: "note",
    searchText: [node.title, node.summary, node.type, node.domain, ...(node.tags || [])]
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

  const domains = unique(baseNodes.map((node) => node.domain || "未分類")).sort(localeCompareZh);
  const domainNodes = domains.map((domain, index) => {
    const domainMembers = baseNodes.filter((node) => (node.domain || "未分類") === domain);
    const edgeCount = edges.filter((edge) => {
      const source = nodeMap.get(edge.source);
      const target = nodeMap.get(edge.target);
      if (!source || !target) return false;
      return source.domain === domain || target.domain === domain;
    }).length;
    return {
      id: `domain::${domain}`,
      title: domain,
      type: "domain",
      kind: "domain",
      domain,
      summary: domainDescriptions[domain] || "以該領域為核心的主題群。",
      tags: ["domain-hub"],
      path: "",
      degree: edgeCount,
      memberCount: domainMembers.length,
      x: 0,
      y: 0,
      vx: 0,
      vy: 0,
      support: false,
      searchText: `${domain} ${(domainDescriptions[domain] || "").toLowerCase()}`,
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
    const sourceDomain = source.domain || "未分類";
    const targetDomain = target.domain || "未分類";
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
    const maps = baseNodes.filter((node) => node.domain === domainNode.domain && node.type === "map").length;
    const laws = baseNodes.filter((node) => node.domain === domainNode.domain && node.type === "law").length;
    return {
      id: domainNode.id,
      domain: domainNode.domain,
      count: domainNode.memberCount,
      maps,
      laws,
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
    { label: "關聯", value: graph.edges.filter((edge) => primaryEdgeTypes.has(edge.type)).length },
    { label: "領域", value: graph.domains.length },
    { label: "頁型", value: graph.types.length },
  ];

  const domainBreakdown = graph.domains
    .map((domain) => {
      const count = graph.noteNodes.filter((node) => (node.domain || "未分類") === domain).length;
      return `${domain} ${count}`;
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
      <div class="stat-label">領域分布</div>
      <div class="detail-summary">${escapeHtml(domainBreakdown)}</div>
    </div>
  `;
}

function buildModeButtons() {
  const modes = [
    { value: "overview", label: "總覽" },
    { value: "domain", label: "領域聚焦" },
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
  renderChipGroup(els.domainFilters, graph.domains, state.domainSelection, () => {
    if (state.focusedDomain && !state.domainSelection.has(state.focusedDomain)) {
      state.focusedDomain = null;
      state.viewMode = "overview";
      syncModeButtons();
    }
    buildDomainOverview();
    layoutVisibleGraph(true);
  });
  renderChipGroup(
    els.typeFilters,
    graph.types,
    state.typeSelection,
    () => layoutVisibleGraph(true),
    (value) => typeLabel[value] || value
  );
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
    card.innerHTML = `
      <div class="domain-card-kicker">Domain Cluster</div>
      <h3>${escapeHtml(meta.domain)}</h3>
      <p>${escapeHtml(meta.description)}</p>
      <div class="domain-card-meta">
        <span class="domain-metric">${meta.count} 節點</span>
        <span class="domain-metric">${meta.maps} 導覽頁</span>
        <span class="domain-metric">${meta.laws} 定律</span>
      </div>
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

  const prepared = state.viewMode === "overview" ? prepareOverviewGraph() : prepareDomainGraph();
  state.visibleNodes = prepared.nodes;
  state.visibleEdges = prepared.edges;

  updateGraphHint();
  updateFocusBanner();

  if (!prepared.nodes.some((node) => node.id === state.selectedNodeId)) {
    state.selectedNodeId = prepared.nodes[0]?.id ?? null;
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
      const anchor = anchors.get(node.anchorKey || node.domain || "未分類") || { x: width / 2, y: height / 2 };
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
}

function prepareOverviewGraph() {
  const nodes = state.graph.domainNodes.filter((node) => state.domainSelection.has(node.domain));
  const allowed = new Set(nodes.map((node) => node.id));
  const edges = state.graph.domainEdges.filter(
    (edge) => allowed.has(edge.source) && allowed.has(edge.target)
  );
  return { nodes, edges };
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
  const primaryNodes = state.graph.noteNodes.filter((node) => {
    const matchesDomain = node.domain === domain;
    const matchesType = state.typeSelection.has(node.type);
    const matchesSearch = !state.searchTerm || node.searchText.includes(state.searchTerm);
    return matchesDomain && matchesType && matchesSearch;
  });

  const supportIds = new Set();
  const primaryIds = new Set(primaryNodes.map((node) => node.id));
  for (const edge of state.graph.edges) {
    if (!primaryEdgeTypes.has(edge.type)) continue;
    if (primaryIds.has(edge.source) && !primaryIds.has(edge.target)) supportIds.add(edge.target);
    if (primaryIds.has(edge.target) && !primaryIds.has(edge.source)) supportIds.add(edge.source);
  }

  const supportNodes = [...supportIds]
    .map((id) => state.nodeMap.get(id))
    .filter(Boolean)
    .filter((node) => node.kind === "note")
    .slice(0, 10)
    .map((node) => ({ ...node, support: true }));

  const merged = dedupeNodes([...primaryNodes, ...supportNodes]);
  const visibleIds = new Set(merged.map((node) => node.id));
  const edges = state.graph.edges.filter((edge) => {
    if (!primaryEdgeTypes.has(edge.type)) return false;
    return visibleIds.has(edge.source) && visibleIds.has(edge.target);
  });

  const anchors = new Map();
  for (const node of merged) node.anchorKey = node.id;
  return { nodes: merged, edges, anchors };
}

function updateGraphHint() {
  els.backToOverviewToolbarButton.hidden = state.viewMode !== "domain";
  els.graphHint.textContent =
    state.viewMode === "overview"
      ? "先選一個領域，再展開該領域內的概念、定律與物理量。可用滑鼠滾輪縮放、拖曳空白處平移。"
      : `目前聚焦在「${state.focusedDomain}」。主節點採環狀排布，較淡的節點是跨領域支撐節點。`;
}

function updateFocusBanner() {
  if (state.viewMode !== "domain" || !state.focusedDomain) {
    els.focusBanner.hidden = true;
    els.focusBanner.innerHTML = "";
    return;
  }

  const primaryCount = state.visibleNodes.filter((node) => !node.support).length;
  const supportCount = state.visibleNodes.filter((node) => node.support).length;
  els.focusBanner.hidden = false;
  els.focusBanner.innerHTML = `
    <div>
      <p class="eyebrow">Focused Domain</p>
      <p><strong>${escapeHtml(state.focusedDomain)}</strong> 目前顯示 ${primaryCount} 個主節點，外加 ${supportCount} 個跨領域支撐節點。</p>
    </div>
    <div class="focus-actions">
      <button id="backToOverviewButton" class="ghost-button" type="button">回到總覽</button>
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
        if (node.kind === "domain") {
          focusDomain(node.domain);
          return;
        }
        state.selectedNodeId = node.id;
        drawGraph();
        renderDetail(node);
        updateNodeStates();
      });
      element.addEventListener("pointerdown", (event) => {
        if (node.kind === "domain") return;
        startDrag(event, node);
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
  if (node.kind === "domain") {
    return `
      <div class="node-badge">
        <span class="swatch type-map"></span>
        <span>${escapeHtml(typeLabel.domain)}</span>
      </div>
      <div class="node-title">${escapeHtml(node.title)}</div>
      <div class="node-meta">${node.memberCount} 個節點</div>
    `;
  }

  return `
    <div class="node-badge">
      <span class="swatch type-${escapeHtml(node.type)}"></span>
      <span>${escapeHtml(typeLabel[node.type] || node.type)}</span>
    </div>
    <div class="node-title">${escapeHtml(node.title)}</div>
    <div class="node-meta">${escapeHtml(node.support ? `支撐節點 · ${node.domain}` : node.domain || "未分類")}</div>
  `;
}

function updateNodeStates() {
  const selected = state.selectedNodeId ? state.nodeMap.get(state.selectedNodeId) : null;
  const connected = selected ? new Set(connectedNodeIds(selected.id)) : null;

  for (const node of state.visibleNodes) {
    const element = node.element;
    element.classList.toggle("selected", node.id === state.selectedNodeId);
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

function buildDomainAnchors(width, height, nodes) {
  const domainKeys = unique(nodes.map((node) => node.anchorKey || node.domain || "未分類")).sort(localeCompareZh);
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
  const selectedConnections = state.selectedNodeId ? new Set(connectedNodeIds(state.selectedNodeId)) : null;

  const tick = () => {
    for (const node of nodes) {
      const anchor = anchors.get(node.anchorKey || node.domain || "未分類");
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

    for (const node of nodes) {
      if (state.draggingNodeId === node.id) continue;
      const connectionBoost = selectedConnections && selectedConnections.has(node.id) ? 1.05 : 1;
      const friction = node.kind === "domain" ? 0.68 : state.viewMode === "domain" ? 0.7 : 0.78;
      node.vx *= friction * connectionBoost;
      node.vy *= friction * connectionBoost;
      const halfW = Math.max((node.boxWidth || 120) / 2 + 14, node.kind === "domain" ? 94 : 54);
      const halfH = Math.max((node.boxHeight || 72) / 2 + 14, node.kind === "domain" ? 94 : 54);
      node.x = clamp(node.x + node.vx, halfW, width - halfW);
      node.y = clamp(node.y + node.vy, halfH, height - halfH);
      node.element.style.left = `${node.x}px`;
      node.element.style.top = `${node.y}px`;
    }

    drawGraph(width, height);
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
        a.vx -= dir * 0.28;
        b.vx += dir * 0.28;
      } else {
        const push = overlapY / 2;
        const dir = dy === 0 ? (i % 2 === 0 ? -1 : 1) : Math.sign(dy);
        if (a.kind !== "domain") a.y -= dir * push;
        if (b.kind !== "domain") b.y += dir * push;
        a.vy -= dir * 0.28;
        b.vy += dir * 0.28;
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

  if (!node) {
    els.detailCard.className = "detail-card empty";
    els.detailCard.innerHTML = `
      <p class="detail-kicker">Node Detail</p>
      <h2>沒有可顯示的節點</h2>
      <p class="detail-summary">請調整搜尋字詞或篩選條件。</p>
    `;
    return;
  }

  if (node.kind === "domain") {
    const members = state.graph.noteNodes.filter((candidate) => candidate.domain === node.domain);
    const byType = countBy(members, (item) => typeLabel[item.type] || item.type);
    els.detailCard.className = "detail-card";
    els.detailCard.innerHTML = `
      <p class="detail-kicker">Domain Hub</p>
      <h2>${escapeHtml(node.title)}</h2>
      <p class="detail-summary">${escapeHtml(node.summary)}</p>
      <div class="detail-meta">
        ${detailMetaBox("節點數", String(node.memberCount))}
        ${detailMetaBox("跨域關聯", String(node.degree))}
        ${detailMetaBox("主要頁型", escapeHtml(Object.keys(byType).join(" / ")))}
        ${detailMetaBox("操作", "點下方按鈕進入領域聚焦")}
      </div>
      <div class="detail-grid">
        <section class="detail-section">
          <h3>頁型分布</h3>
          <div class="detail-tags">${renderPills(Object.entries(byType).map(([label, count]) => `${label} ${count}`))}</div>
        </section>
        <section class="detail-section">
          <h3>下一步</h3>
          <div class="focus-actions">
            <button id="detailFocusButton" class="ghost-button" type="button">展開 ${escapeHtml(node.title)}</button>
          </div>
        </section>
      </div>
    `;
    els.detailCard.querySelector("#detailFocusButton").addEventListener("click", () => focusDomain(node.domain));
    return;
  }

  const noteDetail = state.noteDetails[node.id] || null;
  const outgoing = state.graph.edges.filter((edge) => edge.source === node.id && primaryEdgeTypes.has(edge.type));
  const incoming = (state.incomingMap.get(node.id) || []).filter((edge) => primaryEdgeTypes.has(edge.type));
  const outgoingGroups = groupRelations(outgoing, "target");
  const incomingGroups = groupRelations(incoming, "source");
  const resolvedSummary = node.summary || noteDetail?.summary || noteDetail?.body_preview || "這個節點目前只有結構化關聯，尚未找到更完整的頁面摘要。";
  const resolvedPath = node.path || noteDetail?.path || "";

  if (isReaderMode) {
    els.detailCard.className = "detail-card reader";
    els.detailCard.innerHTML = renderReaderMode(node, noteDetail, resolvedSummary, resolvedPath, outgoingGroups, incomingGroups);
    scheduleMathTypeset(els.detailCard);
    return;
  }

  els.detailCard.className = "detail-card";
  els.detailCard.innerHTML = `
    <p class="detail-kicker">${escapeHtml(typeLabel[node.type] || node.type)}</p>
    <h2>${escapeHtml(node.title)}</h2>
    <div class="detail-summary rich-summary">${renderMarkdown(resolvedSummary, { compact: true })}</div>
    <div class="detail-meta">
      ${detailMetaBox("領域", node.domain || "未分類")}
      ${detailMetaBox("頁型", typeLabel[node.type] || node.type)}
      ${detailMetaBox("連結度", String(node.degree))}
      ${detailMetaBox("檔案路徑", resolvedPath)}
    </div>
    <div class="detail-grid">
      ${renderNotePreview(node, noteDetail)}
      <section class="detail-section">
        <h3>標籤</h3>
        <div class="detail-tags">${renderPills(node.tags)}</div>
      </section>
      <section class="detail-section">
        <h3>它連出去的關係</h3>
        ${renderRelationGroups(outgoingGroups)}
      </section>
      <section class="detail-section">
        <h3>哪些頁面連到它</h3>
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
          ${escapeHtml(section.title)}
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
        <div class="detail-view-toggle" role="tablist" aria-label="頁面閱讀模式">
          <button class="detail-view-button" type="button" data-note-view-mode="preview">回到側欄</button>
          <button class="detail-view-button active" type="button" data-note-view-mode="full">全文閱讀</button>
        </div>
        <button class="ghost-button" type="button" data-note-view-mode="preview">回到圖譜</button>
      </div>

      <article class="reader-article">
        <header class="reader-header">
          <p class="detail-kicker">${escapeHtml(typeLabel[node.type] || node.type)}</p>
          <h1>${escapeHtml(node.title)}</h1>
          <div class="reader-summary rich-summary">${renderMarkdown(resolvedSummary, { compact: true })}</div>
          <div class="reader-meta-grid">
            ${detailMetaBox("領域", node.domain || "未分類")}
            ${detailMetaBox("頁型", typeLabel[node.type] || node.type)}
            ${detailMetaBox("連結度", String(node.degree))}
            ${detailMetaBox("檔案路徑", resolvedPath)}
          </div>
        </header>

        ${
          outline
            ? `
        <section class="reader-outline-panel">
          <p class="detail-kicker">章節目錄</p>
          <div class="reader-outline-list">${outline}</div>
        </section>
        `
            : ""
        }

        <section class="reader-content">
          ${
            articleSections ||
            `<div class="reader-prose">${renderProse(fallbackBody)}</div>`
          }
        </section>

        <footer class="reader-footer-grid">
          <section class="reader-footer-panel">
            <p class="detail-kicker">標籤</p>
            <div class="detail-tags">${renderPills(node.tags)}</div>
          </section>
          <section class="reader-footer-panel">
            <p class="detail-kicker">它連出去的關係</p>
            ${renderRelationGroups(outgoingGroups)}
          </section>
          <section class="reader-footer-panel">
            <p class="detail-kicker">哪些頁面連到它</p>
            ${renderRelationGroups(incomingGroups)}
          </section>
        </footer>
      </article>
    </div>
  `;
}

function renderNotePreview(node, detail) {
  if (!detail) {
    return `
      <section class="detail-section">
        <h3>章節預覽</h3>
        <p class="detail-summary">目前沒有對應的 Obsidian 頁面預覽資料。</p>
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
          ${escapeHtml(section.title)}
        </button>
      `
    )
    .join("");

  const sectionCards = sectionItems
    .map(
      (section, index) => `
        <article class="section-preview-card" id="${escapeHtml(buildSectionTargetId(node.id, index))}">
          <p class="detail-kicker">Section</p>
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
        <h3>${isFullMode ? "頁面全文" : "頁面預覽"}</h3>
        <div class="detail-view-toggle" role="tablist" aria-label="頁面閱讀模式">
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
    <section class="detail-section">
      <h3>章節目錄</h3>
      <div class="detail-outline">${outline}</div>
    </section>`
        : ""
    }
    <section class="detail-section">
      <h3>${isFullMode ? "章節全文" : "章節預覽"}</h3>
      ${
        sectionCards ||
        `<p class="detail-summary">這篇頁面目前沒有可拆出的章節內容。</p>`
      }
    </section>
  `;
}

function buildSectionTargetId(nodeId, index) {
  return `section-${nodeId}-${index}`.replaceAll(" ", "-");
}

function renderRelationGroups(groups) {
  if (groups.length === 0) {
    return `<p class="detail-summary">目前沒有可顯示的已解析關聯。</p>`;
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

  const sectionJumpButton = event.target.closest(".section-jump-button");
  if (sectionJumpButton) {
    const target = document.getElementById(sectionJumpButton.dataset.sectionTarget || "");
    if (target) {
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    }
    return;
  }

  const pill = event.target.closest(".relation-pill");
  const inlineLink = event.target.closest(".inline-note-link[data-node-id]");
  const targetButton = pill || inlineLink;
  if (!targetButton) return;
  const node = state.nodeMap.get(targetButton.dataset.nodeId);
  if (!node) return;
  if (node.kind === "domain") {
    focusDomain(node.domain);
    return;
  }
  if (state.viewMode === "overview" && node.domain) focusDomain(node.domain);
  state.selectedNodeId = node.id;
  renderDetail(node);
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

function startDrag(event, node) {
  event.preventDefault();
  state.draggingNodeId = node.id;
  const rect = els.graphFrame.getBoundingClientRect();
  const pointerX = event.clientX - rect.left;
  const pointerY = event.clientY - rect.top;
  state.pointerOffset.x = node.x - pointerX;
  state.pointerOffset.y = node.y - pointerY;

  const onMove = (moveEvent) => {
    const moveX = moveEvent.clientX - rect.left;
    const moveY = moveEvent.clientY - rect.top;
    node.x = clamp(moveX + state.pointerOffset.x, 54, rect.width - 54);
    node.y = clamp(moveY + state.pointerOffset.y, 54, rect.height - 54);
    node.vx = 0;
    node.vy = 0;
    node.element.style.left = `${node.x}px`;
    node.element.style.top = `${node.y}px`;
    drawGraph(rect.width, rect.height);
  };

  const onUp = () => {
    state.draggingNodeId = null;
    window.removeEventListener("pointermove", onMove);
    window.removeEventListener("pointerup", onUp);
  };

  window.addEventListener("pointermove", onMove);
  window.addEventListener("pointerup", onUp);
}

function inferDomainFromTags(tags) {
  const domainTagMap = {
    mechanics: "力學",
    thermodynamics: "熱學與熱力學",
    electromagnetism: "電磁學",
    optics: "光學",
    "fluid-mechanics": "流體力學",
    waves: "振動與波動",
    mathematics: "數學工具",
  };
  for (const tag of tags) {
    if (domainTagMap[tag]) return domainTagMap[tag];
  }
  return "未分類";
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

function renderInlineMarkup(text, tokens) {
  const parts = String(text || "").split(/(@@MATH\d+@@|\[\[[^\]]+\]\]|`[^`]+`)/g);
  return parts
    .filter((part) => part !== "")
    .map((part) => {
      if (tokens.has(part)) return tokens.get(part).raw;
      if (part.startsWith("[[")) return renderWikiLink(part);
      const codeMatch = part.match(/^`([^`]+)`$/);
      if (codeMatch) return `<code>${escapeHtml(codeMatch[1])}</code>`;
      return escapeHtml(part);
    })
    .join("");
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

function findNodeByTitle(title) {
  return state.graph?.noteNodes?.find((node) => node.title === title) || null;
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

function syncReadingLayout(isReaderMode) {
  els.workspace.classList.toggle("reader-mode", isReaderMode);
  els.graphPanel.classList.toggle("reader-hidden", isReaderMode);
  els.detailPanel.classList.toggle("reader-panel", isReaderMode);
}

function cssEscape(value) {
  if (window.CSS?.escape) return window.CSS.escape(String(value));
  return String(value).replaceAll('"', '\\"');
}
