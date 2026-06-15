export function createDetailStore({ detailIndexUrl, detailBaseUrl, detailFileNameForNodeId, validateDetailPayload }) {
  let detailIndex = {};
  const detailCache = {};
  const detailErrors = new Map();
  const detailRequests = new Map();

  async function fetchJson(url) {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`${url} 載入失敗：HTTP ${response.status}`);
    }
    return response.json();
  }

  return {
    async loadIndex(expectedNodeIds) {
      const rawDetailIndex = await fetchJson(detailIndexUrl);
      validateDetailPayload(rawDetailIndex, expectedNodeIds);
      detailIndex = rawDetailIndex;
      return detailIndex;
    },
    getIndex(nodeId) {
      return detailIndex[nodeId] || {};
    },
    getCached(nodeId) {
      return detailCache[nodeId] || null;
    },
    hasCached(nodeId) {
      return Boolean(detailCache[nodeId]);
    },
    getError(nodeId) {
      return detailErrors.get(nodeId) || null;
    },
    clearError(nodeId) {
      detailErrors.delete(nodeId);
    },
    async loadDetail(nodeId, options = {}) {
      if (detailCache[nodeId]) return detailCache[nodeId];
      if (detailRequests.has(nodeId)) return detailRequests.get(nodeId);

      const request = fetchJson(`${detailBaseUrl}/${detailFileNameForNodeId(nodeId)}`)
        .then((detail) => {
          detailCache[nodeId] = detail;
          detailErrors.delete(nodeId);
          return detail;
        })
        .catch((error) => {
          detailErrors.set(nodeId, String(error.message || error));
          throw error;
        })
        .finally(() => {
          detailRequests.delete(nodeId);
          options.onSettled?.(nodeId);
        });

      detailRequests.set(nodeId, request);
      return request;
    },
  };
}
