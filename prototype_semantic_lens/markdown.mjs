export function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
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

function renderWikiLink(rawLink, helpers) {
  const match = rawLink.match(/^\[\[([^|\]#]+)(?:#[^\]|]+)?(?:\|([^\]]+))?\]\]$/);
  if (!match) return escapeHtml(rawLink);
  const targetTitle = String(match[1] || "").trim();
  const label = String(match[2] || match[1] || "").trim();
  const targetNode = helpers.findNodeByTitle?.(targetTitle);
  if (!targetNode) {
    return `<span class="inline-note-link unresolved">${escapeHtml(label)}</span>`;
  }
  return `<button class="inline-note-link" type="button" data-node-id="${escapeHtml(targetNode.id)}">${escapeHtml(label)}</button>`;
}

function renderInlineMarkup(text, tokens, helpers) {
  const parts = String(text || "").split(/(@@MATH\d+@@|\[\[[^\]]+\]\]|`[^`]+`)/g);
  return parts
    .filter((part) => part !== "")
    .map((part) => {
      if (tokens.has(part)) return tokens.get(part).raw;
      if (part.startsWith("[[")) return renderWikiLink(part, helpers);
      const codeMatch = part.match(/^`([^`]+)`$/);
      if (codeMatch) return `<code>${escapeHtml(codeMatch[1])}</code>`;
      return escapeHtml(part);
    })
    .join("");
}

export function renderMarkdown(value, options = {}, helpers = {}) {
  const { compact = false, stripLeadingTitle = false, title = "" } = options;
  const normalized = String(value || "").replaceAll("\r\n", "\n").trim();
  if (!normalized) return "";

  let prepared = normalized;
  if (stripLeadingTitle) {
    const lines = prepared.split("\n");
    let idx = 0;
    while (idx < lines.length && !lines[idx].trim()) idx++;
    if (idx < lines.length && lines[idx].trim().startsWith("#")) {
      const headingTitle = lines[idx].trim().replace(/^#+\s*/, "").trim();
      if (!title || headingTitle === title.trim()) {
        lines.splice(idx, 1);
        while (idx < lines.length && !lines[idx].trim()) lines.splice(idx, 1);
        prepared = lines.join("\n");
      }
    }
  }

  const protectedText = protectMathSegments(prepared);
  const lines = protectedText.text.split("\n");
  const blocks = [];

  for (let index = 0; index < lines.length; ) {
    const line = lines[index].trim();
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
      blocks.push(`<h${level}>${renderInlineMarkup(headingMatch[2], protectedText.tokens, helpers)}</h${level}>`);
      index += 1;
      continue;
    }

    if (/^- /.test(line)) {
      const items = [];
      while (index < lines.length && /^- /.test(lines[index].trim())) {
        items.push(`<li>${renderInlineMarkup(lines[index].trim().slice(2), protectedText.tokens, helpers)}</li>`);
        index += 1;
      }
      blocks.push(`<ul>${items.join("")}</ul>`);
      continue;
    }

    if (/^\d+\.\s/.test(line)) {
      const items = [];
      while (index < lines.length && /^\d+\.\s/.test(lines[index].trim())) {
        items.push(`<li>${renderInlineMarkup(lines[index].trim().replace(/^\d+\.\s/, ""), protectedText.tokens, helpers)}</li>`);
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
    const paragraphHtml = renderInlineMarkup(paragraphLines.join(compact ? " " : "\n"), protectedText.tokens, helpers).replaceAll("\n", "<br>");
    blocks.push(`<p>${paragraphHtml}</p>`);
  }

  return blocks.join("");
}
