export function createOverviewState() {
  return {
    mode: "overview",
    selectedNodeId: null,
    browseHistory: [],
    browseIndex: -1,
    noteViewMode: "preview",
    focusSceneNodeId: null,
    panX: 0,
    panY: 0,
    zoom: 1,
  };
}

export function createFocusState(currentState, nodeId, options = {}) {
  const { pushHistory = true } = options;
  const nextState = {
    selectedNodeId: nodeId,
    mode: "focus",
    panX: 0,
    panY: 0,
    zoom: 0.98,
  };

  if (!pushHistory) {
    return nextState;
  }

  const browseHistory = currentState.browseHistory.slice(0, currentState.browseIndex + 1);
  browseHistory.push(nodeId);
  return {
    ...nextState,
    browseHistory,
    browseIndex: browseHistory.length - 1,
  };
}

export function stepBrowseHistory(currentState, direction) {
  const delta = direction === "back" ? -1 : direction === "forward" ? 1 : 0;
  if (!delta) return null;
  const nextIndex = currentState.browseIndex + delta;
  if (nextIndex < 0 || nextIndex >= currentState.browseHistory.length) {
    return null;
  }
  return {
    nodeId: currentState.browseHistory[nextIndex],
    browseIndex: nextIndex,
  };
}
