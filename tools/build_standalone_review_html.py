#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kb_paths import repo_root


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-Hant">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Knowledge Map Offline Review</title>
    <style>
__STYLE__
    </style>
    <script>
      window.MathJax = {
        tex: {
          inlineMath: { "[+]": [["$", "$"]] },
          displayMath: [["$$", "$$"], ["\\\\[", "\\\\]"]],
          processEscapes: true,
        },
      };
    </script>
    <script defer src="https://cdn.jsdelivr.net/npm/mathjax@4/tex-chtml.js"></script>
  </head>
  <body>
    <header class="topbar">
      <div>
        <div class="eyebrow">Wikipedia Pilot Review</div>
        <h1 id="note-title">Loading...</h1>
        <p id="note-meta" class="meta"></p>
      </div>
      <div class="session-stats">
        <div id="session-id" class="badge"></div>
        <div id="progress" class="badge"></div>
      </div>
    </header>

    <section class="toolbar">
      <div class="toolbar-group">
        <button data-view="preview" class="view-button active">Preview</button>
        <button data-view="markdown" class="view-button">Markdown</button>
      </div>
      <div id="status-pill" class="status pending">Pending</div>
    </section>

    <section class="source-panel">
      <div>
        <strong>Wikipedia</strong>
        <a id="source-link" href="#" target="_blank" rel="noreferrer">Open source</a>
      </div>
      <div id="change-summary"></div>
    </section>

    <main class="compare-grid">
      <section class="pane">
        <div class="pane-header">Original</div>
        <div id="original-preview" class="pane-content preview"></div>
        <pre id="original-markdown" class="pane-content markdown hidden"></pre>
      </section>
      <section class="pane">
        <div class="pane-header">Proposed</div>
        <div id="proposed-preview" class="pane-content preview"></div>
        <pre id="proposed-markdown" class="pane-content markdown hidden"></pre>
      </section>
    </main>

    <footer class="actions">
      <div class="nav-buttons">
        <button id="prev-button">Previous</button>
        <button id="next-button">Next</button>
      </div>
      <div class="decision-buttons">
        <button data-decision="rejected" class="danger">Reject</button>
        <button data-decision="skipped">Skip</button>
        <button data-decision="approved" class="primary">Approve overwrite</button>
        <button id="export-decisions-button">Export decisions</button>
      </div>
    </footer>

    <script id="session-data" type="application/json">__SESSION_JSON__</script>
    <script id="items-data" type="application/json">__ITEMS_JSON__</script>
    <script>
__SCRIPT__
    </script>
  </body>
</html>
"""


OFFLINE_SCRIPT = r"""
const embeddedSession = JSON.parse(document.getElementById("session-data").textContent);
const embeddedItems = JSON.parse(document.getElementById("items-data").textContent);

const state = {
  session: embeddedSession,
  decisions: {},
  items: embeddedItems,
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

function scheduleMathTypeset() {
  if (state.view !== "preview") return;
  if (!window.MathJax?.typesetPromise) return;
  const targets = [
    document.getElementById("original-preview"),
    document.getElementById("proposed-preview"),
  ];
  typesetSequence = typesetSequence
    .catch(() => {})
    .then(() => window.MathJax.typesetPromise(targets))
    .catch((error) => console.error("MathJax typeset failed", error));
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

function diffLines(as, bs) {
  const m = as.length, n = bs.length;
  const dp = Array.from({ length: m + 1 }, () => new Uint16Array(n + 1));
  for (let i = 1; i <= m; i++)
    for (let j = 1; j <= n; j++)
      dp[i][j] = as[i-1] === bs[j-1] ? dp[i-1][j-1] + 1 : Math.max(dp[i-1][j], dp[i][j-1]);
  const ops = [];
  let i = m, j = n;
  while (i > 0 || j > 0) {
    if (i > 0 && j > 0 && as[i-1] === bs[j-1]) { ops.push({ op: "keep", a: as[--i], b: bs[--j] }); }
    else if (j > 0 && (i === 0 || dp[i][j-1] >= dp[i-1][j])) { ops.push({ op: "add", b: bs[--j] }); }
    else { ops.push({ op: "remove", a: as[--i] }); }
  }
  return ops.reverse();
}

function highlightDiffs(origText, propText) {
  // Normalize line endings
  const origNorm = origText.replace(/\r\n/g, "\n").replace(/\r/g, "\n");
  const propNorm = propText.replace(/\r\n/g, "\n").replace(/\r/g, "\n");

  if (origNorm === propNorm) {
    const html = renderMarkdown(origNorm);
    return { original: html, proposed: html };
  }

  const origLines = origNorm.split("\n");
  const propLines = propNorm.split("\n");
  const ops = diffLines(origLines, propLines);

  // Group into blocks
  const blocks = [];
  for (const op of ops) {
    const last = blocks[blocks.length - 1];
    if (last && last.op === op.op) {
      last.aLines.push(op.a || "");
      last.bLines.push(op.b || "");
    } else {
      blocks.push({ op: op.op, aLines: [op.a || ""], bLines: [op.b || ""] });
    }
  }

  let origOut = "", propOut = "";
  for (const block of blocks) {
    if (block.op === "keep") {
      const h = renderMarkdown(block.aLines.join("\n") + "\n");
      origOut += h;
      propOut += renderMarkdown(block.bLines.join("\n") + "\n");
    } else if (block.op === "remove") {
      origOut += '<div class="diff-removed">' + renderMarkdown(block.aLines.join("\n") + "\n") + '</div>';
    } else if (block.op === "add") {
      propOut += '<div class="diff-added">' + renderMarkdown(block.bLines.join("\n") + "\n") + '</div>';
    } else {
      origOut += '<div class="diff-removed">' + renderMarkdown(block.aLines.join("\n") + "\n") + '</div>';
      propOut += '<div class="diff-added">' + renderMarkdown(block.bLines.join("\n") + "\n") + '</div>';
    }
  }
  return { original: origOut, proposed: propOut };
}

function renderCurrentItem() {
  const item = state.currentItem;
  const decision = item.review_decision?.decision || "pending";
  document.getElementById("note-title").textContent = item.note_title;
  document.getElementById("note-meta").textContent = item.note_path;
  document.getElementById("progress").textContent = `${state.currentIndex + 1} / ${state.items.length}`;
  document.getElementById("session-id").textContent = state.session.session_id;
  document.getElementById("source-link").href = item.source_metadata.wikipedia_url || "#";
  document.getElementById("source-link").textContent = item.source_metadata.wikipedia_title || "Open source";
  const diff = highlightDiffs(item.original_markdown, item.proposed_markdown);
  document.getElementById("original-preview").innerHTML = diff.original;
  document.getElementById("proposed-preview").innerHTML = diff.proposed;
  document.getElementById("original-markdown").textContent = item.original_markdown;
  document.getElementById("proposed-markdown").textContent = item.proposed_markdown;
  renderChangeSummary(item.change_summary || []);
  updateStatusPill(decision);
  updateView();
  // Force MathJax re-typeset after diff content update
  if (window.MathJax && MathJax.typesetPromise) {
    MathJax.typesetClear([document.getElementById("original-preview"), document.getElementById("proposed-preview")]);
    MathJax.typesetPromise([document.getElementById("original-preview"), document.getElementById("proposed-preview")]).catch(() => {});
  }
}

function loadItem(index) {
  state.currentIndex = index;
  const item = { ...state.items[index] };
  item.review_decision = state.decisions[item.item_id] || { decision: "pending", updated_at: null };
  state.currentItem = item;
  renderCurrentItem();
}

function saveDecision(decision) {
  state.currentItem.review_decision = {
    decision,
    updated_at: new Date().toISOString(),
    persistence: "localStorage",
  };
  state.decisions[state.currentItem.item_id] = state.currentItem.review_decision;
  persistLocalDecisions();
  showSaveState(`${decision} (local)`, decision);
}

function init() {
  state.decisions = {
    ...(state.session.decisions || {}),
    ...loadLocalDecisions(),
  };
  if (!state.items.length) {
    throw new Error("No review items found.");
  }
  loadItem(0);
}

document.querySelectorAll(".view-button").forEach((button) => {
  button.addEventListener("click", () => {
    state.view = button.dataset.view;
    updateView();
    scheduleMathTypeset();
  });
});

document.getElementById("prev-button").addEventListener("click", () => {
  if (state.currentIndex > 0) loadItem(state.currentIndex - 1);
});

document.getElementById("next-button").addEventListener("click", () => {
  if (state.currentIndex < state.items.length - 1) loadItem(state.currentIndex + 1);
});

document.querySelectorAll("[data-decision]").forEach((button) => {
  button.addEventListener("click", () => {
    saveDecision(button.dataset.decision);
  });
});

document.getElementById("export-decisions-button").addEventListener("click", () => {
  const payload = {
    session_id: state.session.session_id,
    exported_at: new Date().toISOString(),
    decisions: state.decisions,
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `${state.session.session_id}-decisions.json`;
  anchor.click();
  URL.revokeObjectURL(url);
  showSaveState("Decisions exported", "approved");
});

init();
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a standalone offline review HTML file.")
    parser.add_argument("--session-dir", required=True, help="Path to tmp/review_sessions/<session-id>.")
    parser.add_argument("--out-file", help="Output HTML file path. Defaults to <session-dir>/review.html.")
    args = parser.parse_args()

    session_dir = Path(args.session_dir).resolve()
    manifest = json.loads((session_dir / "manifest.json").read_text(encoding="utf-8"))
    decisions = json.loads((session_dir / "decisions.json").read_text(encoding="utf-8"))
    manifest["decisions"] = decisions

    items = []
    for item_meta in manifest.get("items", []):
        item = json.loads((session_dir / item_meta["item_path"]).read_text(encoding="utf-8"))
        items.append(item)

    index_html = (repo_root() / "review_app" / "index.html").read_text(encoding="utf-8")
    del index_html
    style = (repo_root() / "review_app" / "styles.css").read_text(encoding="utf-8")

    html = HTML_TEMPLATE.replace("__STYLE__", style.rstrip())
    html = html.replace("__SESSION_JSON__", json.dumps(manifest, ensure_ascii=False))
    html = html.replace("__ITEMS_JSON__", json.dumps(items, ensure_ascii=False))
    html = html.replace("__SCRIPT__", OFFLINE_SCRIPT.rstrip())

    out_file = Path(args.out_file).resolve() if args.out_file else (session_dir / "review.html")
    out_file.write_text(html, encoding="utf-8")
    print(str(out_file))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
