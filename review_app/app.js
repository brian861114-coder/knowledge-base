const state = {
  session: null,
  decisions: {},
  items: [],
  currentIndex: 0,
  currentItem: null,
  view: "preview",
};

let typesetSequence = Promise.resolve();

function getDecisionStorageKey() {
  return `knowledge-map-review:${state.session?.session_id || "unknown"}`;
}

function loadLocalDecisions() {
  try {
    return JSON.parse(window.localStorage.getItem(getDecisionStorageKey()) || "{}");
  } catch {
    return {};
  }
}

function persistLocalDecisions() {
  window.localStorage.setItem(getDecisionStorageKey(), JSON.stringify(state.decisions));
}

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function renderMarkdown(markdown) {
  let html = escapeHtml(markdown);
  html = html.replace(/^### (.+)$/gm, "<h3>$1</h3>");
  html = html.replace(/^## (.+)$/gm, "<h2>$1</h2>");
  html = html.replace(/^# (.+)$/gm, "<h1>$1</h1>");
  html = html.replace(/^\- (.+)$/gm, "<li>$1</li>");
  html = html.replace(/(<li>.*<\/li>)/gs, "<ul>$1</ul>");
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
  html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/\n\n+/g, "</p><p>");
  html = `<p>${html}</p>`;
  return html.replace(/<p><\/p>/g, "");
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`Request failed: ${url}`);
  }
  return response.json();
}

function updateStatusPill(decision) {
  const pill = document.getElementById("status-pill");
  pill.textContent = decision[0].toUpperCase() + decision.slice(1);
  pill.className = `status ${decision}`;
}

function showSaveState(message, variant = "pending") {
  const pill = document.getElementById("status-pill");
  pill.textContent = message;
  pill.className = `status ${variant}`;
}

function renderChangeSummary(changeSummary) {
  const container = document.getElementById("change-summary");
  container.innerHTML = "";
  const list = document.createElement("ul");
  for (const item of changeSummary) {
    const li = document.createElement("li");
    li.textContent = item;
    list.appendChild(li);
  }
  container.appendChild(list);
}

function renderCurrentItem() {
  const item = state.currentItem;
  const decision = item.review_decision?.decision || "pending";

  document.getElementById("note-title").textContent = item.note_title;
  document.getElementById("note-meta").textContent = `${item.note_path}`;
  document.getElementById("progress").textContent = `${state.currentIndex + 1} / ${state.items.length}`;
  document.getElementById("session-id").textContent = state.session.session_id;
  document.getElementById("source-link").href = item.source_metadata.wikipedia_url || "#";
  document.getElementById("source-link").textContent =
    item.source_metadata.wikipedia_title || "Open source";

  document.getElementById("original-preview").innerHTML = renderMarkdown(item.original_markdown);
  document.getElementById("proposed-preview").innerHTML = renderMarkdown(item.proposed_markdown);
  document.getElementById("original-markdown").textContent = item.original_markdown;
  document.getElementById("proposed-markdown").textContent = item.proposed_markdown;
  renderChangeSummary(item.change_summary || []);
  updateStatusPill(decision);
  updateView();
  scheduleMathTypeset();
}

function updateView() {
  const showPreview = state.view === "preview";
  document.getElementById("original-preview").classList.toggle("hidden", !showPreview);
  document.getElementById("proposed-preview").classList.toggle("hidden", !showPreview);
  document.getElementById("original-markdown").classList.toggle("hidden", showPreview);
  document.getElementById("proposed-markdown").classList.toggle("hidden", showPreview);

  document.querySelectorAll(".view-button").forEach((button) => {
    button.classList.toggle("active", button.dataset.view === state.view);
  });
}

function scheduleMathTypeset() {
  if (state.view !== "preview") {
    return;
  }
  if (!window.MathJax?.typesetPromise) {
    return;
  }

  const targets = [
    document.getElementById("original-preview"),
    document.getElementById("proposed-preview"),
  ];

  typesetSequence = typesetSequence
    .catch(() => {})
    .then(() => window.MathJax.typesetPromise(targets))
    .catch((error) => {
      console.error("MathJax typeset failed", error);
    });
}

async function loadItem(index) {
  state.currentIndex = index;
  const itemMeta = state.items[index];
  state.currentItem = await fetchJson(`/api/item/${encodeURIComponent(itemMeta.item_id)}`);
  renderCurrentItem();
}

async function saveDecision(decision) {
  showSaveState("Saving...", "pending");
  try {
    await fetchJson("/api/decision", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        item_id: state.currentItem.item_id,
        decision,
      }),
    });
    state.currentItem.review_decision = { decision };
    state.decisions[state.currentItem.item_id] = { decision };
    persistLocalDecisions();
    updateStatusPill(decision);
  } catch (error) {
    console.error("Decision save failed", error);
    state.currentItem.review_decision = { decision };
    state.decisions[state.currentItem.item_id] = {
      decision,
      updated_at: new Date().toISOString(),
      persistence: "localStorage",
    };
    persistLocalDecisions();
    showSaveState(`${decision} (local)`, decision);
  }
}

async function init() {
  state.session = await fetchJson("/api/session");
  state.decisions = {
    ...(state.session.decisions || {}),
    ...loadLocalDecisions(),
  };
  state.items = state.session.items || [];
  if (!state.items.length) {
    throw new Error("No review items found.");
  }
  await loadItem(0);
}

document.querySelectorAll(".view-button").forEach((button) => {
  button.addEventListener("click", () => {
    state.view = button.dataset.view;
    updateView();
    scheduleMathTypeset();
  });
});

document.getElementById("prev-button").addEventListener("click", async () => {
  if (state.currentIndex > 0) {
    await loadItem(state.currentIndex - 1);
  }
});

document.getElementById("next-button").addEventListener("click", async () => {
  if (state.currentIndex < state.items.length - 1) {
    await loadItem(state.currentIndex + 1);
  }
});

document.querySelectorAll("[data-decision]").forEach((button) => {
  button.addEventListener("click", async () => {
    await saveDecision(button.dataset.decision);
  });
});

document.getElementById("export-decisions-button").addEventListener("click", () => {
  const payload = {
    session_id: state.session.session_id,
    exported_at: new Date().toISOString(),
    decisions: state.decisions,
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], {
    type: "application/json;charset=utf-8",
  });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `${state.session.session_id}-decisions.json`;
  anchor.click();
  URL.revokeObjectURL(url);
  showSaveState("Decisions exported", "approved");
});

init().catch((error) => {
  document.getElementById("note-title").textContent = "Failed to load review session";
  document.getElementById("note-meta").textContent = error.message;
});
