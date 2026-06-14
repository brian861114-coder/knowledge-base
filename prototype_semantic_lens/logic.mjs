export const SEMANTIC_EDGE_TYPES = new Set([
  "requires",
  "derives_to",
  "formalized_by",
  "related_to",
  "organized_by",
  "verified_by",
  "measures",
  "uses",
  "explains",
]);

const RELATION_BUCKET_RULES = {
  requires: { source: "requires", target: "extension" },
  derives_to: { source: "extension", target: "requires" },
  formalized_by: { source: "requires", target: "extension" },
  related_to: { source: "related", target: "related" },
  organized_by: { source: "related", target: "related" },
  verified_by: { source: "extension", target: "extension" },
  measures: { source: "extension", target: "extension" },
  uses: { source: "extension", target: "extension" },
  explains: { source: "extension", target: "extension" },
};

function isObject(value) {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

export function validateGraphPayload(rawGraph) {
  assert(isObject(rawGraph), "圖譜資料格式錯誤：預期為物件。");
  assert(Array.isArray(rawGraph.nodes), "圖譜資料格式錯誤：缺少 nodes 陣列。");
  assert(Array.isArray(rawGraph.edges), "圖譜資料格式錯誤：缺少 edges 陣列。");

  const nodeIds = new Set();
  rawGraph.nodes.forEach((node, index) => {
    assert(isObject(node), `圖譜節點格式錯誤：nodes[${index}] 不是物件。`);
    assert(typeof node.id === "string" && node.id.trim(), `圖譜節點格式錯誤：nodes[${index}] 缺少有效 id。`);
    assert(!nodeIds.has(node.id), `圖譜節點格式錯誤：重複的 node id ${node.id}。`);
    assert(typeof node.title === "string" && node.title.trim(), `圖譜節點格式錯誤：${node.id} 缺少 title。`);
    assert(typeof node.type === "string" && node.type.trim(), `圖譜節點格式錯誤：${node.id} 缺少 type。`);
    nodeIds.add(node.id);
  });

  rawGraph.edges.forEach((edge, index) => {
    assert(isObject(edge), `圖譜關係格式錯誤：edges[${index}] 不是物件。`);
    assert(typeof edge.source === "string" && edge.source.trim(), `圖譜關係格式錯誤：edges[${index}] 缺少 source。`);
    assert(typeof edge.target === "string" && edge.target.trim(), `圖譜關係格式錯誤：edges[${index}] 缺少 target。`);
    assert(typeof edge.type === "string" && edge.type.trim(), `圖譜關係格式錯誤：edges[${index}] 缺少 type。`);
  });
}

export function validateDetailPayload(rawDetails, nodeIds = []) {
  assert(isObject(rawDetails), "筆記詳情格式錯誤：預期為以 node id 為 key 的物件。");

  for (const [nodeId, detail] of Object.entries(rawDetails)) {
    assert(isObject(detail), `筆記詳情格式錯誤：${nodeId} 的內容不是物件。`);
    if (detail.sections !== undefined) {
      assert(Array.isArray(detail.sections), `筆記詳情格式錯誤：${nodeId}.sections 應為陣列。`);
    }
  }

  const unknownIds = Object.keys(rawDetails).filter((nodeId) => !nodeIds.includes(nodeId));
  assert(unknownIds.length === 0, `筆記詳情格式錯誤：存在未知節點 ${unknownIds.slice(0, 3).join(", ")}。`);
}

export function buildGraphIndex(nodes, edges) {
  const nodeById = new Map(nodes.map((node) => [node.id, node]));
  const incomingByNode = new Map();
  const outgoingByNode = new Map();

  for (const node of nodes) {
    incomingByNode.set(node.id, []);
    outgoingByNode.set(node.id, []);
  }

  for (const edge of edges) {
    assert(nodeById.has(edge.source), `圖譜關係格式錯誤：找不到 source 節點 ${edge.source}。`);
    assert(nodeById.has(edge.target), `圖譜關係格式錯誤：找不到 target 節點 ${edge.target}。`);
    outgoingByNode.get(edge.source).push(edge);
    incomingByNode.get(edge.target).push(edge);
  }

  return { nodeById, incomingByNode, outgoingByNode };
}

export function relationBucketForEdge(edgeType, role) {
  const rules = RELATION_BUCKET_RULES[edgeType];
  if (!rules) return "related";
  return rules[role] || "related";
}

export function detailFileNameForNodeId(nodeId) {
  const text = String(nodeId);
  let hash = 2166136261;
  for (const char of text) {
    hash ^= char.codePointAt(0);
    hash = Math.imul(hash, 16777619);
  }
  return `detail-${(hash >>> 0).toString(16).padStart(8, "0")}.json`;
}

export function collectDirectionalRelations(nodeId, graphIndex, nodeMap, options = {}) {
  const includeNode = options.includeNode || ((node) => Boolean(node));
  const entries = [];
  const outgoingEdges = graphIndex.outgoingByNode.get(nodeId) || [];
  const incomingEdges = graphIndex.incomingByNode.get(nodeId) || [];

  for (const edge of outgoingEdges) {
    const otherNode = nodeMap.get(edge.target);
    if (!includeNode(otherNode, edge, "source")) continue;
    entries.push({
      edge,
      node: otherNode,
      role: "source",
      bucket: relationBucketForEdge(edge.type, "source"),
    });
  }

  for (const edge of incomingEdges) {
    const otherNode = nodeMap.get(edge.source);
    if (!includeNode(otherNode, edge, "target")) continue;
    entries.push({
      edge,
      node: otherNode,
      role: "target",
      bucket: relationBucketForEdge(edge.type, "target"),
    });
  }

  return entries;
}
