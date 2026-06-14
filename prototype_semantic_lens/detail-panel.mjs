export function buildMetaItemsHtml(entries, { escapeHtml }) {
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

export function buildStatCardsHtml(entries, { escapeHtml }) {
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

export function buildPillListHtml(items, family, { escapeHtml }) {
  if (!items.length) return "";
  return items
    .map((item) => `<button class="pill" type="button" data-family="${family}" data-node-id="${escapeHtml(item.id)}">${escapeHtml(item.title)}</button>`)
    .join("");
}

export function buildSearchResultsHtml(query, matches, { escapeHtml, messages }) {
  if (!query) return "";
  if (!matches.length) {
    return `<p style="color:var(--muted);font-size:0.88rem;">${messages.emptyPrefix}${escapeHtml(query)}${messages.emptySuffix}</p>`;
  }

  let html = `<div class="section-head"><h3>${messages.resultCountPrefix}${matches.length}${messages.resultCountSuffix}</h3></div><div class="pill-list">`;
  for (const match of matches) {
    html += `<button class="pill" type="button" data-node-id="${escapeHtml(match.id)}" data-family="related">${escapeHtml(match.title)}</button>`;
  }
  html += `</div>`;
  return html;
}
