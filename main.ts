// Entrypoint for the news-image-20261122 poster.
//
// Copies the pre-rendered poster (assets/poster.png) to entry.png in the
// output directory. Standard library only, no network access. The output
// directory comes from MAKEFUN_OUTPUT_DIR, defaulting to /output.
// The poster bytes are fixed, so every run writes identical output.
// Revision 2 packs the page denser: 64 verified stories (three leads, ten
// illustrated panels, a 41-item index and a ten-line IN BRIEF strip).
// Revision 3 polishes the layout (no orphan lines), re-verifies the
// Ukraine and COP31 leads, and adds a regions line and a dated-and-sourced
// footer.
// Revision 4 adds full scene illustrations for the three leads, richer
// panel art, the source outlet named on every story, a key-numbers
// strip, a regions bar with counts computed from the story list, and a
// DATE CHECK box fencing off other days' news.

import { copyFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const poster = fileURLToPath(new URL("./assets/poster.png", import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

mkdirSync(outDir, { recursive: true });
const target = join(outDir, "entry.png");
copyFileSync(poster, target);
console.log(target);
