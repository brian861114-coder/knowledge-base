let mathJaxReadyPromise = null;

function getMathJaxReady(timeoutMs = 4000) {
  if (mathJaxReadyPromise) return mathJaxReadyPromise;
  mathJaxReadyPromise = new Promise((resolve) => {
    const startedAt = Date.now();
    const poll = () => {
      if (window.MathJax?.typesetPromise) {
        resolve(window.MathJax);
        return;
      }
      if (Date.now() - startedAt >= timeoutMs) {
        console.warn("MathJax not ready within timeout; skip typesetting.");
        resolve(null);
        return;
      }
      window.setTimeout(poll, 120);
    };
    poll();
  });
  return mathJaxReadyPromise;
}

export function scheduleMathTypeset(container) {
  if (!container) return;
  getMathJaxReady().then((mathJax) => {
    if (!mathJax?.typesetPromise) return;
    if (typeof mathJax.typesetClear === "function") {
      mathJax.typesetClear([container]);
    }
    mathJax.typesetPromise([container]).catch((error) => {
      console.error("Math typeset failed", error);
    });
  }).catch((error) => {
    console.error("MathJax readiness failed", error);
  });
}
