// ============================================================
// 知識庫資料來源 — 修改這兩個路徑以指向你的匯出檔案
// ============================================================
// 若將 graph.json 與 note_details.json 放在同目錄：
const graphUrl = "./graph.json";
const noteDetailsUrl = "./note_details.json";
const graphEnUrl = "./graph_en.json";
const noteDetailsEnUrl = "./note_details_en.json";
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
  noteDetailsEn: {},
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
  language: localStorage.getItem("kb_language") || "zh-Hant",
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
  map: { "zh-Hant": "導覽頁", en: "Map" },
  law: { "zh-Hant": "原理", en: "Principle" },
  concept: { "zh-Hant": "概念", en: "Concept" },
  quantity: { "zh-Hant": "性質", en: "Property" },
  mathematical_tool: { "zh-Hant": "表徵", en: "Characterization" },
  experiment: { "zh-Hant": "製程", en: "Process" },
  domain: { "zh-Hant": "領域", en: "Domain" },
};

const relationLabel = {
  organized_by: { "zh-Hant": "主題收納", en: "Organized by" },
  requires: { "zh-Hant": "先備關係", en: "Prerequisite" },
  formalized_by: { "zh-Hant": "數學支撐", en: "Formalized by" },
  derives_to: { "zh-Hant": "可推出", en: "Derives to" },
  uses: { "zh-Hant": "直接使用", en: "Uses" },
  verified_by: { "zh-Hant": "實驗驗證", en: "Verified by" },
  explains: { "zh-Hant": "進階視角", en: "Explains" },
  measures: { "zh-Hant": "量測對應", en: "Measures" },
  related_to: { "zh-Hant": "相關概念", en: "Related to" },
  wikilink: { "zh-Hant": "文內連結", en: "Inline link" },
};

const domainDescriptions = {
  Foundations: {
    "zh-Hant": "鍵結、熱力學、動力學、擴散與相行為。",
    en: "Bonding, thermodynamics, kinetics, diffusion, and phase behavior.",
  },
  "Material Classes": {
    "zh-Hant": "金屬、陶瓷、高分子、複合材料、半導體等主要材料族群。",
    en: "Metals, ceramics, polymers, composites, semiconductors, and related families.",
  },
  "Structure and Defects": {
    "zh-Hant": "晶體結構、缺陷、介面、晶粒與跨尺度微觀組織。",
    en: "Crystal structure, defects, interfaces, grains, and microstructure across scales.",
  },
  Properties: {
    "zh-Hant": "機械、電、熱、光學與化學反應行為。",
    en: "Mechanical, electrical, thermal, optical, and chemical response.",
  },
  Processing: {
    "zh-Hant": "用來建立與改變結構的熱、化學、機械與增材製程。",
    en: "Thermal, chemical, mechanical, and additive routes used to build structure.",
  },
  Characterization: {
    "zh-Hant": "讓結構判斷可被驗證的繞射、顯微與分析方法。",
    en: "Diffraction, microscopy, and analysis methods that make structural claims testable.",
  },
  "Failure Analysis": {
    "zh-Hant": "斷裂、腐蝕、劣化與服役損傷判讀。",
    en: "Fracture, corrosion, degradation, and service-driven damage interpretation.",
  },
  Applications: {
    "zh-Hant": "能源、電子、生醫、結構與極端環境應用。",
    en: "Energy, electronics, biomedical, structural, and extreme-environment use cases.",
  },
  Uncategorized: {
    "zh-Hant": "尚未分配到穩定領域的節點。",
    en: "Nodes not yet assigned to a stable domain.",
  },
};

const taxonomyLabels = {
  fundamentals: { "zh-Hant": "基礎", en: "Foundations" },
  material_classes: { "zh-Hant": "材料類別", en: "Material Classes" },
  structure: { "zh-Hant": "結構與缺陷", en: "Structure" },
  properties: { "zh-Hant": "性質", en: "Properties" },
  processing: { "zh-Hant": "製程", en: "Processing" },
  characterization: { "zh-Hant": "表徵", en: "Characterization" },
  failure: { "zh-Hant": "失效", en: "Failure" },
  applications: { "zh-Hant": "應用", en: "Applications" },
};

const taxonomyDescriptions = {
  fundamentals: {
    "zh-Hant": "解釋材料為何偏好特定結構與轉變的核心原理。",
    en: "Core principles that explain why materials prefer certain structures and transformations.",
  },
  material_classes: {
    "zh-Hant": "具有典型鍵結、結構與製程窗口的常見材料家族。",
    en: "Recurring families of materials with characteristic bonding, structure, and process windows.",
  },
  structure: {
    "zh-Hant": "原子排列、缺陷、介面、晶粒與中尺度組織。",
    en: "Atomic arrangement, defects, interfaces, grains, and mesoscale organization.",
  },
  properties: {
    "zh-Hant": "材料在機械、熱、電、化學或光學上的反應方式。",
    en: "How materials respond mechanically, thermally, electrically, chemically, or optically.",
  },
  processing: {
    "zh-Hant": "改變內部結構、進而改變性能的製程路徑。",
    en: "Routes that change internal structure and therefore change performance.",
  },
  characterization: {
    "zh-Hant": "用於辨識相、缺陷、形貌與紋理的證據生成方法。",
    en: "Evidence-producing methods used to identify phases, defects, morphology, and texture.",
  },
  failure: {
    "zh-Hant": "材料在服役中開裂、腐蝕、劣化或失去功能的方式。",
    en: "Ways materials crack, corrode, degrade, or lose function in service.",
  },
  applications: {
    "zh-Hant": "性質目標與製程限制交會的應用集群。",
    en: "Application clusters where property targets and process constraints meet.",
  },
};

const uiText = {
  "zh-Hant": {
    "brand.title": "材料科學與工程知識圖譜",
    "brand.tagline": "雙語互動材料知識庫",
    "brand.homeAria": "回到知識圖譜首頁",
    "nav.search": "搜尋",
    "nav.notes": "筆記",
    "nav.graph": "圖譜",
    "nav.settings": "設定",
    "sidebar.search.title": "搜尋",
    "sidebar.search.kicker": "Query",
    "sidebar.search.label": "搜尋節點",
    "sidebar.search.placeholder": "搜尋概念、性質、製程、表徵方法…",
    "sidebar.mode.title": "檢視模式",
    "sidebar.mode.kicker": "Mode",
    "sidebar.filter.toggle": "領域 / Taxonomy",
    "sidebar.filter.title": "切換分類視角",
    "sidebar.type.title": "頁型",
    "sidebar.type.kicker": "Type",
    "sidebar.atlas.title": "圖譜摘要",
    "sidebar.atlas.kicker": "Atlas",
    "graph.title": "圖譜工作區",
    "graph.zoomOut": "縮小",
    "graph.zoomIn": "放大",
    "graph.fit": "適應畫面",
    "graph.backToOverview": "回到總覽",
    "graph.reset": "重設視圖",
    "legend.title": "圖例",
    "legend.map": "導覽頁",
    "legend.law": "原理",
    "legend.concept": "概念",
    "legend.quantity": "性質",
    "legend.characterization": "表徵",
    "detail.empty.kicker": "節點詳情",
    "detail.empty.title": "選取一個節點",
    "detail.empty.summary": "右側會顯示該頁的摘要、領域、頁型，以及它在知識地圖中的前置關係與延伸方向。",
    "detail.empty.note": "先從總覽選一個領域，或直接點擊任一節點。",
    appTitle: "材料科學與工程知識圖譜",
    loadErrorKicker: "載入錯誤",
    loadErrorTitle: "無法載入知識地圖資料",
    filterModeTaxonomy: "Taxonomy",
    filterModeDomain: "領域",
    missingDomainGuide: "尚未補上這個領域的導覽說明。",
    detailEmptyKicker: "節點詳情",
    detailEmptyTitle: "選取一個節點",
    detailEmptySummary: "右側會顯示該頁的摘要、領域、頁型，以及它在知識地圖中的前置關係與延伸方向。",
    detailEmptyNote: "先從總覽選一個領域，或直接點擊任一節點。",
    viewOverview: "總覽",
    viewGraph: "圖譜",
    viewSearch: "搜尋",
    viewNotes: "筆記",
    viewSettings: "設定",
    graphHintOverview: "總覽只保留領域樞紐、導覽頁與少量高連結節點。先選領域，再深入局部子圖。",
    graphHintDomain: "目前聚焦在「{domain}」。先看核心節點骨架，再點任一節點切換成局部子圖。",
    graphHintLocal: "目前以「{domain}」中的「{title}」為中心，只顯示直接相關與必要支撐節點。",
    focusLocalEyebrow: "局部子圖",
    focusDomainEyebrow: "領域聚焦",
    focusLocalText: "目前圍繞「{title}」顯示 {primary} 個核心節點與 {support} 個跨域支撐節點。",
    focusDomainText: "目前只顯示 {primary} 個核心節點與 {support} 個支撐節點，避免整張圖一次攤平。",
    focusPrimaryMetric: "{count} 核心節點",
    focusSupportMetric: "{count} 支撐節點",
    backToOverview: "回到總覽",
    detailDomainKicker: "領域樞紐",
    detailMembers: "成員節點",
    detailCrossLinks: "跨域連結",
    detailContainedTypes: "包含頁型",
    detailPerspective: "視角",
    detailPerspectiveValue: "領域樞紐與導覽入口",
    detailTypeDistribution: "頁型分佈",
    detailActions: "操作",
    detailFocusDomain: "聚焦 {title}",
    detailFallbackSummary: "這個節點還沒有整理好的摘要。可以先從相關連結或完整筆記內容查看。",
    metaDomain: "領域",
    metaType: "頁型",
    metaLinks: "連結數",
    metaPath: "來源路徑",
    sectionTags: "標籤",
    sectionOutgoing: "指向其他節點",
    sectionIncoming: "哪些節點連到這裡",
    readerTabPreview: "預覽模式",
    readerTabFull: "全文模式",
    readerBackPreview: "返回預覽",
    readerOutlineTitle: "文章目錄",
    readerOutlineCaption: "從定義、機制到延伸概念，直接跳到對應段落。",
    readerNoExport: "這個節點還沒有對應的 Obsidian 匯出內容。",
    previewTitle: "筆記預覽",
    fullTitle: "筆記全文",
    previewShort: "預覽",
    fullShort: "全文",
    outlineSection: "文章目錄",
    outlineCaption: "點選章節直接跳到對應段落。",
    sectionPreview: "章節預覽",
    sectionFull: "章節全文",
    sectionKicker: "章節",
    noSections: "這份筆記還沒有切分好的章節內容。",
    noRelations: "目前沒有可顯示的關聯節點。",
    notesKicker: "筆記瀏覽",
    notesTitle: "全部筆記（{count}）",
    notesSummary: "依領域分組，點選筆記可切換到圖譜檢視並聚焦該節點。",
    settingsKicker: "設定",
    settingsTitle: "材料科學與工程知識圖譜",
    settingsSummary: "可在這裡切換全中文或全英文介面與內容。",
    settingsAbout: "關於",
    settingsLanguage: "語言",
    settingsLanguageSummary: "切換後會同步更新介面文字、節點標題、摘要與筆記全文。",
    settingsLanguageZh: "全中文",
    settingsLanguageEn: "全英文",
    settingsTech: "技術",
    settingsVersion: "版本",
    statsNotes: "筆記數",
    statsEdges: "關係數",
    statsDomains: "領域數",
    aboutP1: "本專案是一個材料科學與工程知識圖譜原型，將 Obsidian Vault 中的結構化筆記匯出為 JSON，透過前端進行互動式圖譜探索與全文閱讀。",
    aboutP2: "涵蓋結構與尺度、性質、製程、表徵、失效與應用等主幹，並提供中英雙語切換。",
    searchKicker: "搜尋",
    searchTitle: "搜尋知識圖譜",
    searchSummary: "輸入關鍵字搜尋概念、性質、製程、表徵方法與應用。",
    searchPlaceholder: "例如：差排、X 光繞射、熱處理、腐蝕…",
    searchIdle: "輸入關鍵字後會即時顯示搜尋結果。",
    searchNoResults: "找不到符合「{query}」的筆記。",
    searchResults: "找到 {count} 筆結果{suffix}",
    searchResultsLimitSuffix: "（顯示前 50 筆）",
    uncategorized: "未分類",
  },
  en: {
    "brand.title": "Materials Science and Engineering Knowledge Atlas",
    "brand.tagline": "Bilingual Interactive Materials Knowledge Base",
    "brand.homeAria": "Back to atlas home",
    "nav.search": "Search",
    "nav.notes": "Notes",
    "nav.graph": "Graph",
    "nav.settings": "Settings",
    "sidebar.search.title": "Search",
    "sidebar.search.kicker": "Query",
    "sidebar.search.label": "Search nodes",
    "sidebar.search.placeholder": "Search concepts, properties, processes, methods...",
    "sidebar.mode.title": "View Mode",
    "sidebar.mode.kicker": "Mode",
    "sidebar.filter.toggle": "Domain / Taxonomy",
    "sidebar.filter.title": "Switch grouping lens",
    "sidebar.type.title": "Type",
    "sidebar.type.kicker": "Type",
    "sidebar.atlas.title": "Atlas Summary",
    "sidebar.atlas.kicker": "Atlas",
    "graph.title": "Graph Workspace",
    "graph.zoomOut": "Zoom Out",
    "graph.zoomIn": "Zoom In",
    "graph.fit": "Fit View",
    "graph.backToOverview": "Back to Overview",
    "graph.reset": "Reset View",
    "legend.title": "Legend",
    "legend.map": "Map",
    "legend.law": "Principle",
    "legend.concept": "Concept",
    "legend.quantity": "Property",
    "legend.characterization": "Characterization",
    "detail.empty.kicker": "Node Detail",
    "detail.empty.title": "Select a node",
    "detail.empty.summary": "The panel on the right shows the page summary, domain, note type, prerequisites, and outward connections.",
    "detail.empty.note": "Start from an overview domain, or click any node directly.",
    appTitle: "Materials Science and Engineering Knowledge Atlas",
    loadErrorKicker: "Load Error",
    loadErrorTitle: "Unable to load knowledge graph data",
    filterModeTaxonomy: "Taxonomy",
    filterModeDomain: "Domain",
    missingDomainGuide: "No guide text has been written for this domain yet.",
    detailEmptyKicker: "Node Detail",
    detailEmptyTitle: "Select a node",
    detailEmptySummary: "The panel on the right shows the page summary, domain, note type, prerequisites, and outward connections.",
    detailEmptyNote: "Start from an overview domain, or click any node directly.",
    viewOverview: "Overview",
    viewGraph: "Graph",
    viewSearch: "Search",
    viewNotes: "Notes",
    viewSettings: "Settings",
    graphHintOverview: "Overview keeps only domain hubs, map pages, and a small number of highly connected nodes. Pick a domain first, then drill into a local subgraph.",
    graphHintDomain: "Currently focused on “{domain}”. Start with the core skeleton, then click any node to switch to a local subgraph.",
    graphHintLocal: "Currently centered on “{title}” inside “{domain}”, showing only directly related nodes and required support nodes.",
    focusLocalEyebrow: "Local Subgraph",
    focusDomainEyebrow: "Domain Focus",
    focusLocalText: "Showing {primary} core nodes and {support} cross-domain support nodes around “{title}”.",
    focusDomainText: "Showing only {primary} core nodes and {support} support nodes to avoid flattening the whole graph at once.",
    focusPrimaryMetric: "{count} core nodes",
    focusSupportMetric: "{count} support nodes",
    backToOverview: "Back to overview",
    detailDomainKicker: "Domain Hub",
    detailMembers: "Member nodes",
    detailCrossLinks: "Cross-domain links",
    detailContainedTypes: "Included types",
    detailPerspective: "View",
    detailPerspectiveValue: "Domain hub and navigation entry",
    detailTypeDistribution: "Type distribution",
    detailActions: "Actions",
    detailFocusDomain: "Focus {title}",
    detailFallbackSummary: "This node does not have a polished summary yet. Check the linked notes or full note body first.",
    metaDomain: "Domain",
    metaType: "Type",
    metaLinks: "Links",
    metaPath: "Source path",
    sectionTags: "Tags",
    sectionOutgoing: "Outgoing links",
    sectionIncoming: "Incoming links",
    readerTabPreview: "Preview",
    readerTabFull: "Full Note",
    readerBackPreview: "Back to preview",
    readerOutlineTitle: "Outline",
    readerOutlineCaption: "Jump straight to the matching section, from definitions to mechanisms and extensions.",
    readerNoExport: "This node does not have exported Obsidian content yet.",
    previewTitle: "Note Preview",
    fullTitle: "Full Note",
    previewShort: "Preview",
    fullShort: "Full",
    outlineSection: "Outline",
    outlineCaption: "Click a section to jump to its matching block.",
    sectionPreview: "Section Preview",
    sectionFull: "Full Sections",
    sectionKicker: "Section",
    noSections: "This note does not have sectioned content yet.",
    noRelations: "No related nodes are available to show.",
    notesKicker: "Note Browser",
    notesTitle: "All Notes ({count})",
    notesSummary: "Grouped by domain. Click a note to jump back into the graph and focus that node.",
    settingsKicker: "Settings",
    settingsTitle: "Materials Science and Engineering Knowledge Atlas",
    settingsSummary: "Switch the interface and note content between full Chinese and full English here.",
    settingsAbout: "About",
    settingsLanguage: "Language",
    settingsLanguageSummary: "Switching updates UI labels, node titles, summaries, and full note content together.",
    settingsLanguageZh: "Chinese",
    settingsLanguageEn: "English",
    settingsTech: "Tech",
    settingsVersion: "Version",
    statsNotes: "Notes",
    statsEdges: "Edges",
    statsDomains: "Domains",
    aboutP1: "This project is a materials science and engineering knowledge-atlas prototype that exports structured Obsidian notes into JSON for interactive graph exploration and full-note reading.",
    aboutP2: "It covers structure and scales, properties, processing, characterization, failure, and applications, with bilingual switching across the experience.",
    searchKicker: "Search",
    searchTitle: "Search the Knowledge Atlas",
    searchSummary: "Search concepts, properties, processes, characterization methods, and applications.",
    searchPlaceholder: "For example: dislocation, X-ray diffraction, heat treatment, corrosion...",
    searchIdle: "Results will appear as you type.",
    searchNoResults: "No notes matched “{query}”.",
    searchResults: "{count} result(s){suffix}",
    searchResultsLimitSuffix: " (showing first 50)",
    uncategorized: "Uncategorized",
  },
};

const taxonomyColorPalette = {
  fundamentals: "#526c8b",
  material_classes: "#7b8751",
  structure: "#8e5f47",
  properties: "#7a5896",
  processing: "#b36a36",
  characterization: "#3d7d88",
  failure: "#a24d58",
  applications: "#4d8f73",
};

const domainColorPalette = {
  Foundations: "#526c8b",
  "Material Classes": "#7b8751",
  "Structure and Defects": "#8e5f47",
  Properties: "#7a5896",
  Processing: "#b36a36",
  Characterization: "#3d7d88",
  "Failure Analysis": "#a24d58",
  Applications: "#4d8f73",
  Uncategorized: "#a1a6b1",
};

init().catch((error) => {
  console.error(error);
  els.detailCard.classList.remove("empty");
  els.detailCard.innerHTML = `
    <p class="detail-kicker">${escapeHtml(t("loadErrorKicker"))}</p>
    <h2>${escapeHtml(t("loadErrorTitle"))}</h2>
    <p class="detail-summary">${escapeHtml(String(error.message || error))}</p>
  `;
});

function t(key, vars = {}) {
  const pack = uiText[state.language] || uiText["zh-Hant"];
  let value = pack[key] ?? uiText["zh-Hant"][key] ?? key;
  for (const [name, replacement] of Object.entries(vars)) {
    value = value.replaceAll(`{${name}}`, String(replacement));
  }
  return value;
}

function getLocalizedLabel(map, key) {
  const value = map[key];
  if (!value) return key;
  return value[state.language] || value["zh-Hant"] || key;
}

function getNodeTitle(node) {
  if (!node) return "";
  return state.language === "en"
    ? node.title_en || node.title
    : node.title_zh || node.title;
}

function getNodeSummary(node) {
  if (!node) return "";
  return state.language === "en"
    ? node.summary_en || node.summary
    : node.summary_zh || node.summary;
}

function getDetailSummary(detail) {
  if (!detail) return "";
  return state.language === "en"
    ? detail.summary_en || detail.summary
    : detail.summary_zh || detail.summary;
}

function getDetailBody(detail, mode = "full") {
  if (!detail) return "";
  const fullKey = state.language === "en" ? "body_full_en" : "body_full";
  const previewKey = state.language === "en" ? "body_preview_en" : "body_preview";
  if (mode === "preview") return detail[previewKey] || detail.body_preview || "";
  return detail[fullKey] || detail.body_full || detail[previewKey] || detail.body_preview || "";
}

function getDetailSections(detail) {
  if (!detail) return [];
  return state.language === "en"
    ? detail.sections_en || detail.sections || []
    : detail.sections || [];
}

function getTypeLabel(type) {
  return getLocalizedLabel(typeLabel, type);
}

function getRelationLabel(type) {
  return getLocalizedLabel(relationLabel, type);
}

function getLocaleCompare(a, b) {
  return String(a || "").localeCompare(String(b || ""), state.language === "en" ? "en" : "zh-Hant");
}

function applyShellI18n() {
  document.documentElement.lang = state.language === "en" ? "en" : "zh-Hant";
  document.title = t("appTitle");
  for (const element of document.querySelectorAll("[data-i18n]")) {
    element.textContent = t(element.dataset.i18n);
  }
  for (const element of document.querySelectorAll("[data-i18n-placeholder]")) {
    element.setAttribute("placeholder", t(element.dataset.i18nPlaceholder));
  }
  for (const element of document.querySelectorAll("[data-i18n-title]")) {
    element.setAttribute("title", t(element.dataset.i18nTitle));
  }
  for (const element of document.querySelectorAll("[data-i18n-aria-label]")) {
    element.setAttribute("aria-label", t(element.dataset.i18nAriaLabel));
  }
  els.domainSectionTitle.textContent = state.filterMode === "taxonomy" ? t("filterModeTaxonomy") : t("filterModeDomain");
}

function applyContentLanguage() {
  if (!state.graph) return;
  for (const node of state.graph.noteNodes || []) {
    node.title = state.language === "en" ? node.title_en || node.title_zh || node.title : node.title_zh || node.title_en || node.title;
    node.summary = state.language === "en" ? node.summary_en || node.summary_zh || node.summary : node.summary_zh || node.summary_en || node.summary;
  }

  for (const detail of Object.values(state.noteDetails || {})) {
    detail.title = state.language === "en" ? detail.title_en || detail.title_zh || detail.title : detail.title_zh || detail.title_en || detail.title;
    detail.summary = state.language === "en" ? detail.summary_en || detail.summary_zh || detail.summary : detail.summary_zh || detail.summary_en || detail.summary;
    detail.body_preview = state.language === "en"
      ? detail.body_preview_en || detail.body_preview_zh || detail.body_preview
      : detail.body_preview_zh || detail.body_preview_en || detail.body_preview;
    detail.body_full = state.language === "en"
      ? detail.body_full_en || detail.body_full_zh || detail.body_full
      : detail.body_full_zh || detail.body_full_en || detail.body_full;
    detail.sections = state.language === "en"
      ? detail.sections_en || detail.sections_zh || detail.sections
      : detail.sections_zh || detail.sections_en || detail.sections;
  }
}

function refreshLocalizedUI() {
  applyShellI18n();
  if (state.graph) {
    const refreshed = rebuildDomainLayer(state.graph.noteNodes, state.graph.edges, state.nodeMap, state.incomingMap);
    state.graph = refreshed;
    buildStats(refreshed);
    buildMentionIndex(refreshed);
    buildModeButtons();
    buildFilters(refreshed);
    buildDomainOverview();
  }
  const activeView = document.querySelector(".topnav-item.is-active")?.dataset.view || "graph";
  if (activeView === "search") {
    renderSearchView();
  } else if (activeView === "notes") {
    renderNotesListView();
  } else if (activeView === "settings") {
    renderSettingsView();
  } else {
    layoutVisibleGraph(true);
  }
}

function setLanguage(language) {
  if (!language || language === state.language) return;
  state.language = language;
  localStorage.setItem("kb_language", language);
  applyContentLanguage();
  refreshLocalizedUI();
}

function getActiveDomain(node) {
  if (state.filterMode === "taxonomy") {
    return node.taxonomy_domain || t("uncategorized");
  }
  return node.domain || t("uncategorized");
}

function getActiveDomainDescriptions() {
  return state.filterMode === "taxonomy" ? taxonomyDescriptions : domainDescriptions;
}

function getActiveColorPalette() {
  return state.filterMode === "taxonomy" ? taxonomyColorPalette : domainColorPalette;
}

function getDomainLabel(domain) {
  if (state.filterMode === "taxonomy") {
    return getLocalizedLabel(taxonomyLabels, domain);
  }
  return state.language === "en" ? domain : getLocalizedLabel(taxonomyLabels, domain) || domain;
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
  els.domainSectionTitle.textContent = state.filterMode === "taxonomy" ? t("filterModeTaxonomy") : t("filterModeDomain");
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
  applyShellI18n();
  const [graphResponse, detailResponse, graphEnResponse, detailEnResponse] = await Promise.all([
    fetch(graphUrl),
    fetch(noteDetailsUrl),
    fetch(graphEnUrl),
    fetch(noteDetailsEnUrl),
  ]);
  if (!graphResponse.ok) {
    throw new Error(`HTTP ${graphResponse.status} while loading ${graphUrl}`);
  }
  if (!detailResponse.ok) {
    throw new Error(`HTTP ${detailResponse.status} while loading ${noteDetailsUrl}`);
  }
  const [rawGraph, rawNoteDetails, rawGraphEn, rawNoteDetailsEn] = await Promise.all([
    graphResponse.json(),
    detailResponse.json(),
    graphEnResponse.ok ? graphEnResponse.json() : Promise.resolve({ nodes: [], edges: [] }),
    detailEnResponse.ok ? detailEnResponse.json() : Promise.resolve({}),
  ]);
  const graph = normalizeGraph(rawGraph, rawGraphEn);
  state.graph = graph;
  state.noteDetails = rawNoteDetails;
  state.noteDetailsEn = rawNoteDetailsEn;

  for (const [id, detail] of Object.entries(state.noteDetails)) {
    const enDetail = state.noteDetailsEn[id];
    detail.title_zh = detail.title;
    detail.summary_zh = detail.summary;
    detail.body_preview_zh = detail.body_preview;
    detail.body_full_zh = detail.body_full;
    detail.sections_zh = detail.sections;
    if (enDetail) {
      detail.title_en = enDetail.title;
      detail.summary_en = enDetail.summary;
      detail.body_preview_en = enDetail.body_preview;
      detail.body_full_en = enDetail.body_full;
      detail.sections_en = enDetail.sections;
    }
  }

  applyContentLanguage();
  buildStats(graph);
  buildMentionIndex(graph);
  buildModeButtons();
  buildFilters(graph);
  buildDomainOverview();
  els.domainSectionTitle.textContent = state.filterMode === "taxonomy" ? t("filterModeTaxonomy") : t("filterModeDomain");
  bindEvents();
  resetViewport();
  layoutVisibleGraph(true);
}

function normalizeGraph(rawGraph, rawGraphEn = { nodes: [] }) {
  const enNodes = new Map((rawGraphEn?.nodes || []).map((node) => [node.id, node]));
  const baseNodes = rawGraph.nodes.map((node, index) => ({
    ...node,
    title_zh: node.title,
    summary_zh: node.summary,
    title_en: enNodes.get(node.id)?.title || node.title,
    summary_en: enNodes.get(node.id)?.summary || node.summary,
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
    searchText: [
      node.title,
      node.summary,
      enNodes.get(node.id)?.title,
      enNodes.get(node.id)?.summary,
      node.type,
      node.domain,
      node.taxonomy_domain,
      ...(node.tags || []),
    ]
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
      title_zh: getLocalizedLabel(taxonomyLabels, domain) || domain,
      title_en: domain,
      type: "domain",
      kind: "domain",
      domain,
      summary: (descs[domain] && (descs[domain][state.language] || descs[domain]["zh-Hant"])) || t("missingDomainGuide"),
      summary_zh: (descs[domain] && descs[domain]["zh-Hant"]) || t("missingDomainGuide"),
      summary_en: (descs[domain] && descs[domain].en) || t("missingDomainGuide"),
      tags: ["domain-hub"],
      path: "",
      degree: edgeCount,
      memberCount: domainMembers.length,
      x: 0,
      y: 0,
      vx: 0,
      vy: 0,
      support: false,
      searchText: [
        getLocalizedLabel(taxonomyLabels, domain),
        domain,
        descs[domain]?.["zh-Hant"],
        descs[domain]?.en,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase(),
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
    const maps = baseNodes.filter((node) => getActiveDomain(node) === domainNode.domain && node.type === "map").length;
    const laws = baseNodes.filter((node) => getActiveDomain(node) === domainNode.domain && node.type === "law").length;
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
    { label: t("statsNotes"), value: graph.noteNodes.length },
    { label: t("statsEdges"), value: graph.edges.filter((edge) => primaryEdgeTypes.has(edge.type)).length },
    { label: t("statsDomains"), value: graph.domains.length },
    { label: t("metaType"), value: graph.types.length },
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
      <div class="stat-label">${escapeHtml(t("statsDomains"))}</div>
      <div class="detail-summary">${escapeHtml(domainBreakdown)}</div>
    </div>
  `;
}

function buildModeButtons() {
  const modes = [
    { value: "overview", label: t("viewOverview") },
    { value: "domain", label: state.language === "en" ? "Domain Focus" : "領域聚焦" },
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
    const kicker = state.filterMode === "taxonomy" ? t("filterModeTaxonomy") : t("filterModeDomain");
    card.innerHTML = `
      <div class="domain-card-kicker">${kicker}</div>
      <div class="domain-card-count">${meta.count}</div>
      <h3>${escapeHtml(label)}</h3>
      <p>${escapeHtml(meta.description)}</p>
      <div class="domain-card-meta">
        <span class="domain-metric">${meta.maps} ${escapeHtml(getTypeLabel("map"))}</span>
        <span class="domain-metric">${meta.laws} ${escapeHtml(getTypeLabel("law"))}</span>
      </div>
      <div class="domain-card-footer">${escapeHtml(state.language === "en" ? "Click to focus" : "點擊進入聚焦")}</div>
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
      law: "var(--type-law)",
      concept: "var(--type-concept)",
      quantity: "var(--type-quantity)",
      mathematical_tool: "var(--type-mathematical_tool)",
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
      <p class="detail-kicker">${escapeHtml(t("detailEmptyKicker"))}</p>
      <h2>${escapeHtml(t("detailEmptyTitle"))}</h2>
      <p class="detail-summary">${escapeHtml(t("detailEmptySummary"))}</p>
      <div class="detail-empty-note">${escapeHtml(t("detailEmptyNote"))}</div>
    `;
    return;
  }

  if (node.kind === "domain") {
    const members = state.graph.noteNodes.filter((candidate) => getActiveDomain(candidate) === node.domain);
    const byType = countBy(members, (item) => getTypeLabel(item.type));
    els.detailCard.className = "detail-card";
    els.detailCard.innerHTML = `
      <p class="detail-kicker">${escapeHtml(t("detailDomainKicker"))}</p>
      <h2>${escapeHtml(node.title)}</h2>
      <p class="detail-summary">${escapeHtml(node.summary)}</p>
      <div class="detail-meta">
        ${detailMetaBox(t("detailMembers"), String(node.memberCount))}
        ${detailMetaBox(t("detailCrossLinks"), String(node.degree))}
        ${detailMetaBox(t("detailContainedTypes"), escapeHtml(Object.keys(byType).join(" / ")))}
        ${detailMetaBox(t("detailPerspective"), t("detailPerspectiveValue"))}
      </div>
      <div class="detail-grid">
        <section class="detail-section">
          <h3>${escapeHtml(t("detailTypeDistribution"))}</h3>
          <div class="detail-tags">${renderPills(Object.entries(byType).map(([label, count]) => `${label} ${count}`))}</div>
        </section>
        <section class="detail-section">
          <h3>${escapeHtml(t("detailActions"))}</h3>
          <div class="focus-actions">
            <button id="detailFocusButton" class="ghost-button" type="button">${escapeHtml(t("detailFocusDomain", { title: node.title }))}</button>
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
    t("detailFallbackSummary");
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
      ${detailMetaBox(t("metaDomain"), getDomainLabel(getActiveDomain(node)))}
      ${detailMetaBox(t("metaType"), getTypeLabel(node.type))}
      ${detailMetaBox(t("metaLinks"), String(node.degree))}
      ${detailMetaBox(t("metaPath"), resolvedPath)}
    </div>
    <div class="detail-grid">
      ${renderNotePreview(node, noteDetail)}
      <section class="detail-section">
        <h3>${escapeHtml(t("sectionTags"))}</h3>
        <div class="detail-tags">${renderPills(node.tags)}</div>
      </section>
      <section class="detail-section">
        <h3>${escapeHtml(t("sectionOutgoing"))}</h3>
        ${renderRelationGroups(outgoingGroups)}
      </section>
      <section class="detail-section">
        <h3>${escapeHtml(t("sectionIncoming"))}</h3>
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
        <div class="detail-view-toggle" role="tablist" aria-label="${escapeHtml(state.language === "en" ? "Note view mode" : "筆記檢視模式")}">
          <button class="detail-view-button" type="button" data-note-view-mode="preview">${escapeHtml(t("readerTabPreview"))}</button>
          <button class="detail-view-button active" type="button" data-note-view-mode="full">${escapeHtml(t("readerTabFull"))}</button>
        </div>
        <button class="ghost-button" type="button" data-note-view-mode="preview">${escapeHtml(t("readerBackPreview"))}</button>
      </div>

        <article class="reader-article">
          <div class="reader-layout ${outline ? "has-outline" : ""}">
            ${
              outline
                ? `
            <aside class="reader-outline-panel">
              <div class="reader-outline-header">
                <p class="detail-kicker">${escapeHtml(t("readerOutlineTitle"))}</p>
                <p class="reader-outline-caption">${escapeHtml(t("readerOutlineCaption"))}</p>
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
                  ${detailMetaBox(t("metaDomain"), getDomainLabel(getActiveDomain(node)))}
                  ${detailMetaBox(t("metaType"), getTypeLabel(node.type))}
                  ${detailMetaBox(t("metaLinks"), String(node.degree))}
                  ${detailMetaBox(t("metaPath"), resolvedPath)}
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
                  <p class="detail-kicker">${escapeHtml(t("sectionTags"))}</p>
                  <div class="detail-tags">${renderPills(node.tags)}</div>
                </section>
                <section class="reader-footer-panel">
                  <p class="detail-kicker">${escapeHtml(t("sectionOutgoing"))}</p>
                  ${renderRelationGroups(outgoingGroups)}
                </section>
                <section class="reader-footer-panel">
                  <p class="detail-kicker">${escapeHtml(t("sectionIncoming"))}</p>
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
        <h3>${escapeHtml(t("previewTitle"))}</h3>
        <p class="detail-summary">${escapeHtml(t("readerNoExport"))}</p>
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
          <p class="detail-kicker">${escapeHtml(t("sectionKicker"))}</p>
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
        <h3>${escapeHtml(isFullMode ? t("fullTitle") : t("previewTitle"))}</h3>
        <div class="detail-view-toggle" role="tablist" aria-label="${escapeHtml(state.language === "en" ? "Note view mode" : "筆記檢視模式")}">
          <button class="detail-view-button ${!isFullMode ? "active" : ""}" type="button" data-note-view-mode="preview">${escapeHtml(t("previewShort"))}</button>
          <button class="detail-view-button ${isFullMode ? "active" : ""}" type="button" data-note-view-mode="full">${escapeHtml(t("fullShort"))}</button>
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
        <h3>${escapeHtml(t("outlineSection"))}</h3>
        <p class="detail-section-caption">${escapeHtml(t("outlineCaption"))}</p>
      </div>
      <div class="detail-outline">${outline}</div>
    </section>`
        : ""
    }
    <section class="detail-section preview-sections-panel">
      <h3>${escapeHtml(isFullMode ? t("sectionFull") : t("sectionPreview"))}</h3>
      <div class="preview-sections-grid">
        ${
          sectionCards ||
          `<p class="detail-summary">${escapeHtml(t("noSections"))}</p>`
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
    return `<p class="detail-summary">${escapeHtml(t("noRelations"))}</p>`;
  }
  return groups
    .map(
      (group) => `
        <div class="relation-group">
          <p class="detail-kicker">${escapeHtml(getRelationLabel(group.type))}</p>
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
    const domain = note.domain || t("uncategorized");
    if (!grouped[domain]) grouped[domain] = [];
    grouped[domain].push(note);
  }

  let html = `<p class="detail-kicker">${escapeHtml(t("notesKicker"))}</p>
    <h2>${escapeHtml(t("notesTitle", { count: notes.length }))}</h2>
    <p class="detail-summary">${escapeHtml(t("notesSummary"))}</p>
    <div class="detail-grid">`;

  for (const [domain, domainNotes] of Object.entries(grouped)) {
    html += `<section class="detail-section">
      <h3>${escapeHtml(getDomainLabel(domain))}（${domainNotes.length}）</h3>
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
    <p class="detail-kicker">${escapeHtml(t("settingsKicker"))}</p>
    <h2>${escapeHtml(t("settingsTitle"))}</h2>
    <p class="detail-summary">${escapeHtml(t("settingsSummary"))}</p>
    <div class="detail-meta">
      ${detailMetaBox(t("statsNotes"), String(noteCount))}
      ${detailMetaBox(t("statsEdges"), String(edgeCount))}
      ${detailMetaBox(t("statsDomains"), String(domainCount))}
      ${detailMetaBox(t("settingsVersion"), "prototype")}
    </div>
    <div class="detail-grid">
      <section class="detail-section">
        <h3>${escapeHtml(t("settingsAbout"))}</h3>
        <div class="detail-summary rich-summary">
          <p>${escapeHtml(t("aboutP1"))}</p>
          <p>${escapeHtml(t("aboutP2"))}</p>
        </div>
      </section>
      <section class="detail-section">
        <h3>${escapeHtml(t("settingsLanguage"))}</h3>
        <p class="detail-summary">${escapeHtml(t("settingsLanguageSummary"))}</p>
        <div class="detail-tags settings-language-group">
          <button class="pill note-pill ${state.language === "zh-Hant" ? "active" : ""}" type="button" data-language-option="zh-Hant">${escapeHtml(t("settingsLanguageZh"))}</button>
          <button class="pill note-pill ${state.language === "en" ? "active" : ""}" type="button" data-language-option="en">${escapeHtml(t("settingsLanguageEn"))}</button>
        </div>
      </section>
      <section class="detail-section">
        <h3>${escapeHtml(t("settingsTech"))}</h3>
        <div class="detail-tags">${renderPills(["Obsidian", "Python", "Vanilla JS", "Canvas", "MathJax"])}</div>
      </section>
    </div>
  `;

  for (const button of els.detailCard.querySelectorAll("[data-language-option]")) {
    button.addEventListener("click", () => {
      setLanguage(button.dataset.languageOption);
    });
  }
}

function renderSearchView() {
  els.detailCard.className = "detail-card";
  els.detailCard.innerHTML = `
    <p class="detail-kicker">${escapeHtml(t("searchKicker"))}</p>
    <h2>${escapeHtml(t("searchTitle"))}</h2>
    <p class="detail-summary">${escapeHtml(t("searchSummary"))}</p>
    <label class="search search-view-input">
      <input id="searchViewInput" type="search" placeholder="${escapeAttribute(t("searchPlaceholder"))}" autofocus>
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
      results.innerHTML = `<p class="detail-summary">${escapeHtml(t("searchIdle"))}</p>`;
      return;
    }

    const matches = state.graph.noteNodes.filter((n) => n.searchText.includes(query)).slice(0, 50);

    if (!matches.length) {
      results.innerHTML = `<p class="detail-summary">${escapeHtml(t("searchNoResults", { query: input.value.trim() }))}</p>`;
      return;
    }

    // Group by domain
    const grouped = {};
    for (const note of matches) {
      const domain = note.domain || t("uncategorized");
      if (!grouped[domain]) grouped[domain] = [];
      grouped[domain].push(note);
    }

    let html = `<p class="detail-summary">${escapeHtml(t("searchResults", { count: matches.length, suffix: matches.length === 50 ? t("searchResultsLimitSuffix") : "" }))}</p>`;
    for (const [domain, notes] of Object.entries(grouped)) {
      html += `<section class="detail-section">
        <h3>${escapeHtml(getDomainLabel(domain))}（${notes.length}）</h3>
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
  if (getActiveDomain(node) !== t("uncategorized")) focusDomain(getActiveDomain(node));
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
    mechanics: state.language === "en" ? "Mechanics" : "力學",
    thermodynamics: state.language === "en" ? "Thermodynamics" : "熱學與熱力學",
    electromagnetism: state.language === "en" ? "Electromagnetism" : "電磁學",
    optics: state.language === "en" ? "Optics" : "光學",
    "fluid-mechanics": state.language === "en" ? "Fluid Mechanics" : "流體力學",
    waves: state.language === "en" ? "Waves" : "振動與波動",
    mathematics: state.language === "en" ? "Mathematics" : "數學工具",
  };
  for (const tag of tags) {
    if (domainTagMap[tag]) return domainTagMap[tag];
  }
  return t("uncategorized");
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
  if (!values || values.length === 0) return `<span class="pill">${escapeHtml(state.language === "en" ? "None" : "無")}</span>`;
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
  return String(a).localeCompare(String(b), state.language === "en" ? "en" : "zh-Hant");
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
  const needle = String(title || "").trim();
  return (
    state.graph?.noteNodes?.find(
      (node) =>
        node.title === needle ||
        node.title_zh === needle ||
        node.title_en === needle ||
        node.id === needle.replaceAll(" ", "-")
    ) || null
  );
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
  if (node.focal) return `${state.language === "en" ? "Focused Node" : "焦點節點"} · ${label}`;
  if (node.overviewHub) return `${state.language === "en" ? "High-Link Hub" : "高連結樞紐"} · ${label}`;
  if (node.support) return `${state.language === "en" ? "Support Node" : "支撐節點"} · ${label}`;
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
      ? t("graphHintOverview")
      : isLocalFocus
        ? t("graphHintLocal", { domain: getDomainLabel(state.focusedDomain), title: selectedNode.title })
        : t("graphHintDomain", { domain: getDomainLabel(state.focusedDomain) });
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
      <p class="eyebrow">${escapeHtml(isLocalFocus ? t("focusLocalEyebrow") : t("focusDomainEyebrow"))}</p>
      <p>
        <strong>${escapeHtml(getDomainLabel(state.focusedDomain))}</strong>
        ${
          isLocalFocus
            ? ` ${escapeHtml(t("focusLocalText", { title: selectedNode.title, primary: primaryCount, support: supportCount }))}`
            : ` ${escapeHtml(t("focusDomainText", { primary: primaryCount, support: supportCount }))}`
        }
      </p>
    </div>
    <div class="focus-banner-metrics">
      <span class="focus-banner-metric">${escapeHtml(t("focusPrimaryMetric", { count: primaryCount }))}</span>
      <span class="focus-banner-metric">${escapeHtml(t("focusSupportMetric", { count: supportCount }))}</span>
    </div>
    <div class="focus-actions focus-banner-actions">
      <button id="backToOverviewButton" class="ghost-button" type="button">${escapeHtml(t("backToOverview"))}</button>
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
