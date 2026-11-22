// Entrypoint for the news-image-20261122 poster.
//
// Copies the pre-rendered poster (assets/poster.png) to entry.png in the
// output directory. Standard library only, no network access. The output
// directory comes from MAKEFUN_OUTPUT_DIR, defaulting to /output.
// The poster bytes are fixed, so every run writes identical output.
// Revision 2 packed the page denser (64 stories); revision 3 polished
// the layout and re-verified the leads; revision 4 added full scene
// illustrations, per-story sources, a key-numbers strip, a computed
// regions bar and a DATE CHECK box; revision 5 deepened the lead art.
// Revision 6 changes direction: an art-led front page of 40 stories —
// three large lead scenes under 19pt headlines, twelve illustrated
// panels with bold headlines and native-size scenes, and a readable
// 10.5pt index for the rest. Every kept story keeps its verified
// wording and source tag; the regions bar is computed from the final
// 40-story list.

import { copyFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const poster = fileURLToPath(new URL("./assets/poster.png", import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

mkdirSync(outDir, { recursive: true });
const target = join(outDir, "entry.png");
copyFileSync(poster, target);
console.log(target);
