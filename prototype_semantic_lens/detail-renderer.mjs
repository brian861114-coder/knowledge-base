export function buildEmptyDetailView() {
  return {
    typeText: "概覽",
    titleText: "請選取一個節點",
    summaryHtml: "右側會顯示該頁的摘要、領域、頁型，以及它在知識地圖中的前置關係與延伸方向。<br><br>先從左側選一個領域，或直接點擊中央圖譜中的節點。",
    taxonomyBadge: "overview",
    metaEntries: [
      ["視圖模式", "Semantic Zoom"],
      ["焦點狀態", "未選取"],
      ["關係策略", "語意邊優先"],
      ["節點標籤", "依縮放顯示"],
    ],
    statsEntries: [],
  };
}

export function buildNodeDetailView(node, detail, relations, helpers) {
  const {
    taxonomyLabels,
    typeLabels,
    renderMarkdown,
    findNodeByTitle,
    overviewNodeCount,
    overviewEdgeCount,
  } = helpers;
  if (!node) {
    const emptyView = buildEmptyDetailView();
    emptyView.statsEntries = [
      ["顯示節點", String(overviewNodeCount)],
      ["顯示關係", String(overviewEdgeCount)],
      ["已隱藏", "wikilink"],
      ["總層級", "3"],
    ];
    return emptyView;
  }

  const resolvedSummary = detail.summary || node.summary || "這個節點目前沒有整理好的摘要。";
  return {
    typeText: typeLabels[node.type] || node.type,
    titleText: node.title,
    summaryHtml: renderMarkdown(resolvedSummary, { compact: true }, { findNodeByTitle }),
    taxonomyBadge: taxonomyLabels[node.taxonomy] || node.taxonomy,
    metaEntries: [
      ["領域", taxonomyLabels[node.taxonomy] || node.taxonomy],
      ["類型", typeLabels[node.type] || node.type],
      ["連結數", String(node.degree)],
      ["來源路徑", detail.path || node.path || "—"],
    ],
    statsEntries: [
      ["先備", String(relations.requires.length)],
      ["延伸", String(relations.extension.length)],
      ["相關", String(relations.related.length)],
      ["章節", String(detail.sections?.length || detail.section_count || 0)],
    ],
  };
}

export function buildNoteSectionHtml(node, detail, options) {
  const { escapeHtml, renderMarkdown, findNodeByTitle, loadError, isLoaded } = options;

  if (loadError) {
    return `
      <div class="section-head"><h3>筆記內容</h3></div>
      <p style="color:var(--red);font-size:0.88rem;">筆記載入失敗：${escapeHtml(loadError)}</p>
      <button class="ghost-button" type="button" data-retry-detail="${escapeHtml(node.id)}">重試載入</button>
    `;
  }

  if (!isLoaded) {
    return `
      <div class="section-head"><h3>筆記內容</h3></div>
      <p style="color:var(--muted);font-size:0.88rem;">正在載入筆記內容…</p>
    `;
  }

  if (!detail || (!detail.sections?.length && !detail.body_preview && !detail.body_full)) {
    return `
      <div class="section-head"><h3>筆記內容</h3></div>
      <p style="color:var(--muted);font-size:0.88rem;">這個節點目前沒有對應的筆記內容。</p>
    `;
  }

  const isFullMode = options.noteViewMode === "full";
  const sections = detail.sections || [];
  const hasFullBody = Boolean(detail.body_full);
  const displaySections = isFullMode
    ? (hasFullBody ? [] : sections)
    : sections.slice(0, 6);

  let html = `
    <div class="section-head">
      <h3>${isFullMode ? "筆記全文" : "筆記預覽"}</h3>
    </div>
  `;

  const bodyContent = isFullMode
    ? (detail.body_full || detail.body_preview || detail.summary || "")
    : (detail.body_preview || detail.summary || "");
  if (bodyContent) {
    html += `<div class="note-body rich-summary">${renderMarkdown(bodyContent, { stripLeadingTitle: true, compact: !isFullMode, title: node.title }, { findNodeByTitle })}</div>`;
  }

  if (displaySections.length) {
    html += `<div class="section-head" style="margin-top:18px"><h3>${isFullMode ? "章節全文" : "章節預覽"}</h3></div>`;
    html += `<div class="note-sections-grid">`;
    for (const sec of displaySections) {
      html += `
        <article class="section-card">
          <h4>${escapeHtml(sec.title)}</h4>
          <div class="section-card-content">${renderMarkdown(isFullMode ? sec.content || sec.preview || "" : sec.preview || "", { compact: !isFullMode }, { findNodeByTitle })}</div>
        </article>
      `;
    }
    html += `</div>`;
  }

  return html;
}
