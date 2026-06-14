export function buildBreadcrumbHtml(items, { escapeHtml }) {
  return items
    .map((item, index) => {
      const part = item.action
        ? `<button class="breadcrumb-button" type="button" data-index="${index}">${escapeHtml(item.label)}</button>`
        : `<span>${escapeHtml(item.label)}</span>`;
      const separator = index < items.length - 1 ? `<span class="breadcrumb-separator">/</span>` : "";
      return `${part}${separator}`;
    })
    .join("");
}

export function createModeUiState(state, node, taxonomyLabel) {
  if (state.mode === "focus" && node) {
    return {
      isFocus: true,
      showBackButton: true,
      showBrowseNav: true,
      showFocusAction: true,
      collapseDomainOverview: true,
      breadcrumbItems: [
        { label: "蝮質汗", action: "overview" },
        { label: taxonomyLabel, action: "taxonomy" },
        { label: node.title },
      ],
    };
  }

  return {
    isFocus: false,
    showBackButton: false,
    showBrowseNav: false,
    showFocusAction: Boolean(state.selectedNodeId),
    collapseDomainOverview: false,
    breadcrumbItems: [
      { label: "蝮質汗", action: "overview" },
      { label: "taxonomy domains" },
    ],
  };
}
