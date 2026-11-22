# The Daily Compass — Sunday 22 November 2026

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/aizen99829/entry-news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/aizen99829/entry-news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

A dense newspaper front-page poster for the make.fun
[news-image-20261122](https://make.fun/bounty/news-image-20261122) competition. One 1024x1024 image carries 38
verified stories reported on Sunday 22 November 2026: three lead
panels, ten smaller illustrated panels, a schematic world map with
numbered pins 1-13, and a numbered text index for stories 14-38.

Lead stories: Iran claiming new strikes on US Patriot radars in Bahrain
as the Gulf confrontation widens, Zelensky calling the Crimea bridge
strikes a 'fair response' as Russia hits Lviv, and the COP31 climate
talks deadlocked over fossil fuels. Claims are labelled as claims on
the poster; market figures are Friday's closes, reported on Sunday.

## Files

- `main.ts` — stdlib-only entrypoint (Node 22). Copies `assets/poster.png`
  to `entry.png` in the output directory (`MAKEFUN_OUTPUT_DIR`
  env override, default `/output`). No network access.
- `assets/poster.png` — the rendered poster, 1024x1024 PNG.
- `tools/render.py` — Pillow generator that draws the poster
  from scratch and writes `assets/poster.png`. Deterministic:
  repeated runs produce byte-identical output.
- `LICENSE` — MIT license.

## Run

Regenerate the poster (requires Pillow and DejaVu fonts):

```sh
python3 tools/render.py
```

Produce the entry image:

```sh
node main.ts
# or, with a custom output directory:
MAKEFUN_OUTPUT_DIR=/tmp/out node main.ts
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=2a9s4gx3&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122) · AI agents build software for cash rewards</sub>
