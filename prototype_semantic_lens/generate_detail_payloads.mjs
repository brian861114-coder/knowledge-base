import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { detailFileNameForNodeId, validateDetailPayload } from "./logic.mjs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..");
const sourcePath = path.join(repoRoot, "physics_note_details.json");
const outputRoot = path.join(__dirname, "data");
const detailIndexPath = path.join(outputRoot, "detail-index.json");
const detailDir = path.join(outputRoot, "details");

async function main() {
  const rawText = await fs.readFile(sourcePath, "utf8");
  const details = JSON.parse(rawText);
  validateDetailPayload(details, Object.keys(details));

  await fs.rm(outputRoot, { recursive: true, force: true });
  await fs.mkdir(detailDir, { recursive: true });

  const detailIndex = {};
  for (const [nodeId, detail] of Object.entries(details)) {
    detailIndex[nodeId] = {
      summary: detail.summary || "",
      path: detail.path || "",
      section_count: Array.isArray(detail.sections) ? detail.sections.length : 0,
      has_content: Boolean(detail.body_preview || detail.body_full || detail.summary),
    };
    await fs.writeFile(
      path.join(detailDir, detailFileNameForNodeId(nodeId)),
      JSON.stringify(detail, null, 2),
      "utf8"
    );
  }

  await fs.writeFile(detailIndexPath, JSON.stringify(detailIndex, null, 2), "utf8");
  console.log(`Generated ${Object.keys(detailIndex).length} detail payloads in ${outputRoot}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
