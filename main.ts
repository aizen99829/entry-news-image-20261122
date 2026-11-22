// Entrypoint for the news-image-20261122 poster.
//
// Copies the pre-rendered poster (assets/poster.png) to entry.png in the
// output directory. Standard library only, no network access. The output
// directory comes from MAKEFUN_OUTPUT_DIR, defaulting to /output.

import { copyFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const poster = fileURLToPath(new URL("./assets/poster.png", import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

mkdirSync(outDir, { recursive: true });
const target = join(outDir, "entry.png");
copyFileSync(poster, target);
console.log(target);
