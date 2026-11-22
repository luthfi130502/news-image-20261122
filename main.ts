// Entry point for news-image-20261122.
// Renders the poster by running the Python generator next to this file,
// which writes the single image to /output/entry.png.
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const gen = join(here, "generate.py");
const out = "/output/entry.png";

const run = spawnSync("python3", [gen], { stdio: "inherit" });
if (run.status !== 0) {
  console.error("generate.py failed with status", run.status);
  process.exit(run.status ?? 1);
}
if (!existsSync(out)) {
  console.error("expected output missing:", out);
  process.exit(1);
}
console.log("entry image ready:", out);
