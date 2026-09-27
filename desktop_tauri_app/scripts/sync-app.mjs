// 將 ../standalone_html_app 同步到 app/（與 Electron 版 build-desktop.ps1 -SyncOnly 相同來源），
// 並把 MathJax 從 node_modules 複製到 app/vendor/mathjax，改寫 index.html 使公式可離線渲染。
import { cpSync, existsSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const source = join(root, "..", "standalone_html_app");
const appDir = join(root, "app");
if (!existsSync(source)) throw new Error(`Missing source app folder: ${source}`);
cpSync(source, appDir, { recursive: true, force: true });
console.log("Synced standalone_html_app -> desktop_tauri_app/app");

// tex-chtml 元件本體 + 延遲載入的 TeX 擴充、CHTML 字型、選單與無障礙元件（不含 sre 語音，約 4 MB）
const mathjaxSrc = join(root, "node_modules", "mathjax", "es5");
if (!existsSync(mathjaxSrc)) throw new Error("Missing node_modules/mathjax; run npm install first");
const mathjaxDest = join(appDir, "vendor", "mathjax");
rmSync(mathjaxDest, { recursive: true, force: true });
for (const part of ["tex-chtml.js", "input", "output/chtml", "ui", "a11y"]) {
  cpSync(join(mathjaxSrc, part), join(mathjaxDest, part), { recursive: true });
}

const cdnSrc = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js";
const indexPath = join(appDir, "index.html");
const html = readFileSync(indexPath, "utf8");
if (!html.includes(cdnSrc)) throw new Error(`index.html no longer references ${cdnSrc}; update sync-app.mjs`);
writeFileSync(indexPath, html.replace(cdnSrc, "./vendor/mathjax/tex-chtml.js"));
console.log("Bundled MathJax -> app/vendor/mathjax");
