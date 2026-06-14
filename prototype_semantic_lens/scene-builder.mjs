export function buildOverviewSceneData(input, helpers) {
  const {
    graph,
    nodeMap,
    taxonomyOrder,
    centerX,
    centerY,
  } = input;
  const {
    selectOverviewNodesForTaxonomy,
    weakLink,
    weakUse,
    relaxLayout,
    clampNodesToViewport,
    dedupeEdges,
    smoothClosedPath,
  } = helpers;

  const sceneNodes = [];
  const sceneEdges = [];
  const chosenIds = new Set();
  const hubByTaxonomy = new Map();
  const overviewRoot = {
    ...graph.overviewRoot,
    x: centerX,
    y: centerY,
    r: 76,
    focal: true,
  };
  sceneNodes.push(overviewRoot);

  graph.domainHubs.forEach((hub, index) => {
    const angle = (-Math.PI / 2) + (index / graph.domainHubs.length) * Math.PI * 2;
    hubByTaxonomy.set(hub.taxonomy, {
      ...hub,
      x: centerX + Math.cos(angle) * 350,
      y: centerY + Math.sin(angle) * 276,
      r: 56,
      sectorAngle: angle,
    });
  });

  for (const taxonomy of taxonomyOrder) {
    const hub = hubByTaxonomy.get(taxonomy);
    if (!hub) continue;
    const pool = graph.nodes.filter((node) => node.taxonomy === taxonomy);
    const selected = selectOverviewNodesForTaxonomy(pool);
    const bandWidth = 0.84;

    selected.forEach((node, index) => {
      const ratio = selected.length <= 1 ? 0.5 : index / (selected.length - 1);
      const angle = hub.sectorAngle - bandWidth / 2 + ratio * bandWidth;
      const localRadiusX = node.tier === 0 ? 50 : node.tier === 1 ? 90 : 130;
      const localRadiusY = node.tier === 0 ? 38 : node.tier === 1 ? 68 : 100;
      const placed = {
        ...node,
        x: hub.x + Math.cos(angle) * localRadiusX,
        y: hub.y + Math.sin(angle) * localRadiusY,
        r: node.type === "map" ? 36 : node.tier === 0 ? 28 : node.tier === 1 ? 20 : 14,
      };
      chosenIds.add(node.id);
      sceneNodes.push(placed);
    });
  }

  const candidateEdges = [];
  for (const edge of graph.edges) {
    if (!chosenIds.has(edge.source) || !chosenIds.has(edge.target)) continue;
    if (edge.type === "organized_by") continue;
    if (edge.type === "related_to" && weakLink(edge)) continue;
    if ((edge.type === "uses" || edge.type === "explains") && weakUse(edge)) continue;
    const src = nodeMap.get(edge.source);
    const tgt = nodeMap.get(edge.target);
    const score = (src?.degree || 0) + (tgt?.degree || 0);
    candidateEdges.push({ ...edge, family: edge.type, score });
  }

  const edgeCountPerNode = new Map();
  candidateEdges.sort((a, b) => b.score - a.score);
  for (const edge of candidateEdges) {
    const srcCount = edgeCountPerNode.get(edge.source) || 0;
    const tgtCount = edgeCountPerNode.get(edge.target) || 0;
    if (srcCount >= 3 && tgtCount >= 3) continue;
    sceneEdges.push(edge);
    edgeCountPerNode.set(edge.source, srcCount + 1);
    edgeCountPerNode.set(edge.target, tgtCount + 1);
  }

  relaxLayout(sceneNodes, { iterations: 220, padding: 2, lockDomains: false, lockFocal: true, enforceBounds: true });
  clampNodesToViewport(sceneNodes, { padding: 36, preserveFocus: false });

  const domainRegions = new Map();
  for (const taxonomy of taxonomyOrder) {
    const children = sceneNodes.filter((node) => node.taxonomy === taxonomy && node.type !== "domain" && node.type !== "root");
    if (!children.length) continue;
    const points = children.map((n) => ({ x: n.x, y: n.y }));
    const cx = points.reduce((sum, point) => sum + point.x, 0) / points.length;
    const cy = points.reduce((sum, point) => sum + point.y, 0) / points.length;

    const bins = 72;
    const radii = [];
    for (let i = 0; i < bins; i += 1) {
      const angle = (i / bins) * Math.PI * 2;
      const cos = Math.cos(angle);
      const sin = Math.sin(angle);
      let maxR = 0;
      for (const point of points) {
        const proj = (point.x - cx) * cos + (point.y - cy) * sin;
        const perp = Math.abs(-(point.x - cx) * sin + (point.y - cy) * cos);
        const r = proj + Math.max(0, 50 - perp * 0.5);
        if (r > maxR) maxR = r;
      }
      radii.push(maxR + 50);
    }

    const smoothed = radii.slice();
    for (let pass = 0; pass < 3; pass += 1) {
      const snapshot = smoothed.slice();
      for (let i = 0; i < bins; i += 1) {
        const prev = snapshot[(i - 1 + bins) % bins];
        const curr = snapshot[i];
        const next = snapshot[(i + 1) % bins];
        smoothed[i] = curr * 0.5 + prev * 0.25 + next * 0.25;
      }
    }

    const contourPoints = smoothed.map((r, i) => {
      const angle = (i / bins) * Math.PI * 2;
      return { x: cx + Math.cos(angle) * r, y: cy + Math.sin(angle) * r };
    });
    const d = smoothClosedPath(contourPoints);
    const minX = Math.min(...contourPoints.map((point) => point.x));
    const minY = Math.min(...contourPoints.map((point) => point.y));
    domainRegions.set(taxonomy, { d, cx, cy, minX, minY, taxonomy });
  }

  return {
    overviewNodes: sceneNodes,
    overviewEdges: dedupeEdges(sceneEdges),
    domainRegions,
  };
}

export function buildFocusSceneData(input, helpers) {
  const { nodeId, graph, nodeMap, graphIndex, overviewNodes, taxonomyLabels } = input;
  const {
    collectDirectionalRelations,
    rankFocusNodes,
    dedupeNodes,
    dedupeEdges,
    positionRing,
    relaxLayout,
    clampNodesToViewport,
  } = helpers;

  const focalSource = nodeMap.get(nodeId);
  if (!focalSource) return null;

  if (focalSource.type === "root") {
    const focal = { ...focalSource, x: 670, y: 470, r: 68, focal: true };
    const domainNodes = [];
    const edges = [];
    for (const hub of graph.domainHubs) {
      const hubCopy = {
        ...hub,
        x: 0,
        y: 0,
        r: 44,
        shortTitle: taxonomyLabels[hub.taxonomy] || hub.taxonomy,
        searchText: hub.title,
      };
      domainNodes.push(hubCopy);
      edges.push({ source: focal.id, target: hub.id, type: "organized_by", family: "organized_by" });
    }
    positionRing(domainNodes, focal, 340, 280, 44, 0);
    const sceneNodes = [focal, ...dedupeNodes(domainNodes)];
    relaxLayout(sceneNodes, { iterations: 100, padding: 16, lockDomains: false, lockFocal: true, enforceBounds: true });
    clampNodesToViewport(sceneNodes, { padding: 84, preserveFocus: true });
    return {
      focusSceneNodeId: nodeId,
      focusNodes: sceneNodes,
      focusEdges: dedupeEdges(edges),
    };
  }

  const focal = { ...focalSource, x: 670, y: 470, r: 68, focal: true };
  const edges = [];
  const inner = [];
  const outer = [];
  const related = [];

  const relationEntries = collectDirectionalRelations(nodeId, graphIndex, nodeMap, {
    includeNode: (node) => Boolean(node) && node.type !== "domain",
  });
  for (const entry of relationEntries) {
    const copy = { ...entry.node };
    if (entry.bucket === "requires") inner.push(copy);
    else if (entry.bucket === "extension") outer.push(copy);
    else related.push(copy);
    edges.push({ ...entry.edge, family: entry.edge.type });
  }

  const innerNodes = rankFocusNodes(inner).slice(0, 6);
  const outerNodes = rankFocusNodes(outer).slice(0, 8);
  const relatedNodes = rankFocusNodes(related).slice(0, 6);
  const sceneNodes = [focal];

  positionRing(innerNodes, focal, 254, 194, 34, 0);
  positionRing(outerNodes, focal, 430, 336, 30, 0);
  positionRing(relatedNodes, focal, 334, 262, 24, Math.PI / 7);

  sceneNodes.push(...dedupeNodes([...innerNodes, ...outerNodes, ...relatedNodes]));
  relaxLayout(sceneNodes, { iterations: 100, padding: 16, lockDomains: false, lockFocal: true, enforceBounds: true });
  clampNodesToViewport(sceneNodes, { padding: 84, preserveFocus: true });
  return {
    focusSceneNodeId: nodeId,
    focusNodes: sceneNodes,
    focusEdges: dedupeEdges(
      edges.filter((edge) => sceneNodes.some((node) => node.id === edge.source) && sceneNodes.some((node) => node.id === edge.target))
    ),
  };
}
