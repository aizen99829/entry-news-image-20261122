# The Daily Compass — Sunday 22 November 2026

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/aizen99829/entry-news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/aizen99829/entry-news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

An art-led newspaper front-page poster for the make.fun
[news-image-20261122](https://make.fun/bounty/news-image-20261122) competition. One 1024x1024 image carries 40
verified stories reported on Sunday 22 November 2026: three lead
cards with large scene illustrations, twelve illustrated panels
with bold headlines (stories 4-15), and a readable numbered text
index for stories 16-40.

Lead stories: Iran claiming new strikes on US Patriot radars in Bahrain
as the Gulf confrontation widens, Zelensky calling the Crimea bridge
strikes a 'fair response' as Russia answers with a 400-drone barrage,
and COP31's final text omitting fossil fuels ahead of a Sunday vote.
Every story is dated and sourced — checked Sunday 22 November 2026;
claims are labelled as claims on the poster; market figures are
Friday's closes, reported on Sunday.

Revision 4 (chasing the top of the board) added: full scene
illustrations for the three leads (a Gulf radar base under fire, a
barrage over a city skyline and river bridge, a conference hall
with globe, clock and delegates), richer panel art, the source
outlet named on every story, a key-numbers strip under the
masthead (~200 nations at COP31, the 03:00 GMT objections deadline,
404 drones, 110+ missiles, 9 killed, 2 US bases), a regions bar
whose counts are computed from the story list, and a DATE CHECK
box that fences off other days' news (the Peru earthquake of
20 Nov and the Poland missile falls of 21 Nov are deliberately
left out). Revision 5 deepened the three lead scenes (haloed moon
and bursts, searchlights, sea reflections, smoke, chandeliers,
eight delegates) at 64 stories.

Revision 6 changes direction: fewer, bigger stories. The page is
now led by its pictures — the three lead scenes at 190px tall
under 19pt headlines, then twelve illustrated panels whose scenes
are drawn at native size beside bold 13.5pt headlines (four of
them new: an Estonian border fence at dusk, a plunging Asia
markets chart, the Voyager probe signalling a tiny Earth, and a
pyramid of gold bars under a red risk arrow). The remaining 25
stories run in a four-column index at a readable 10.5pt. The
thinnest one-liners of the 64 are dropped; every kept story keeps
its verified wording and source tag. The regions bar is computed
from the final 40-story list (Europe 11, Middle East 5,
Asia-Pacific 6, Americas 11, Africa 2, Global 5); the key-numbers
strip and the DATE CHECK box are unchanged.

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
