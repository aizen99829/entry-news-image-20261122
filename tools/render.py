"""Render The Daily Compass front page for Sunday 22 November 2026.

Revision 5 (art focus): the content of revision 4 is frozen — the
same 64 verified stories, corrected Ukraine and COP31 leads,
orphan-free wrapping, source outlet on every story, key-numbers
strip, computed regions bar and DATE CHECK box. What changes is the
artwork: the three lead scenes are drawn almost twice as tall and
much deeper (layered sky gradients, moon and burst halos, searchlight
beams, a sea with light reflections, a taller two-layer skyline with
glowing missile trails and smoke, a warmer conference hall with
banners, chandeliers and more delegates), and the panel pictograms
sit under the same soft top light. The space comes from a slightly
tighter masthead and stats strip, shorter mini panels, a lower map
strip and a notch tighter index and brief type. Output is
deterministic: the same code always writes byte-identical PNG bytes.
"""

import math
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = 1024
H = 1024
MARGIN = 16

PAPER = (247, 241, 227)
INK = (24, 22, 18)
MUTED = (96, 88, 72)
RULE = (24, 22, 18)
PANEL = (255, 253, 246)
EDGE = (58, 52, 40)
BADGE = (164, 32, 28)
WHITE = (255, 255, 255)
SEA = (196, 216, 228)
LAND = (170, 190, 150)
LAND_EDGE = (120, 140, 105)
GOLD = (176, 128, 24)
BLUE = (38, 84, 140)
GREEN = (38, 110, 72)
RED = (178, 44, 36)
DARK = (28, 32, 44)
SKY = (210, 224, 238)

FONTS = Path("/usr/share/fonts/truetype/dejavu")
SERIF = str(FONTS / "DejaVuSerif-Bold.ttf")
SANS = str(FONTS / "DejaVuSans.ttf")
SANSB = str(FONTS / "DejaVuSans-Bold.ttf")
SERIFB = SERIF

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "poster.png"


def f(path, size):
    return ImageFont.truetype(path, size)


def tw(d, text, font):
    return d.textlength(text, font=font)


def wrap(d, text, font, maxw):
    lines = []
    cur = ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if tw(d, trial, font) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    # Orphan fix: never leave a lone word or number on the last line —
    # pull the previous line's last word down to join it when it fits.
    while len(lines) >= 2:
        last_words = lines[-1].split()
        prev_words = lines[-2].split()
        if len(last_words) > 1 or len(prev_words) < 2:
            break
        joined = prev_words[-1] + " " + lines[-1]
        if tw(d, joined, font) > maxw:
            break
        lines[-2] = " ".join(prev_words[:-1])
        lines[-1] = joined
    return lines


def wrap_tagged(d, text, tag, font, maxw):
    """Wrap an item and append its source tag in the same flow.

    Returns a list of (line, tag_start) where tag_start is -1 for a
    plain ink line, 0 for a line drawn wholly in the muted tag
    colour, or a character index where the muted tag begins.
    """
    lines = wrap(d, text, font, maxw)
    merged = lines[-1] + " " + tag
    if tw(d, merged, font) <= maxw:
        start = len(lines[-1]) + 1
        lines[-1] = merged
        return [(ln, start if i == len(lines) - 1 else -1)
                for i, ln in enumerate(lines)]
    extra = wrap(d, tag, font, maxw)
    return [(ln, -1) for ln in lines] + [(ln, 0) for ln in extra]


def para(d, x, y, text, font, maxw, leading, color=INK, max_lines=None):
    lines = wrap(d, text, font, maxw)
    if max_lines is not None:
        lines = lines[:max_lines]
    for ln in lines:
        d.text((x, y), ln, font=font, fill=color)
        y += leading
    return y


def badge(d, x, y, num, r=13):
    d.ellipse([x - r, y - r, x + r, y + r], fill=BADGE, outline=WHITE, width=2)
    t = str(num)
    fn = f(SANSB, 15 if len(t) == 1 else 12)
    w = tw(d, t, fn)
    d.text((x - w / 2, y - 8 if len(t) == 1 else y - 7), t, font=fn, fill=WHITE)


def frame(d, box):
    x0, y0, x1, y1 = box
    d.rectangle([x0, y0, x1, y1], fill=PANEL, outline=EDGE, width=2)


def rule(d, x0, y, x1, w=2):
    d.line([(x0, y), (x1, y)], fill=RULE, width=w)


def circle(d, cx, cy, r, fill, outline=None, width=1):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=outline, width=width)


def lcg(seed):
    """Deterministic pseudo-random stream (fixed seed, no global state)."""
    s = seed
    while True:
        s = (1103515245 * s + 12345) % (2 ** 31)
        yield s


def vgrad(d, x, y, w, h, top, bot, steps=14):
    for i in range(steps):
        t = i / (steps - 1)
        col = tuple(round(top[c] + (bot[c] - top[c]) * t) for c in range(3))
        y0 = y + h * i // steps
        y1 = y + h * (i + 1) // steps
        d.rectangle([x, y0, x + w, y1], fill=col)


def burst(d, cx, cy, r, col1, col2):
    for rr, col in ((r, col1), (int(r * 0.6), col2)):
        pts = []
        for a in range(16):
            ang = math.pi * a / 8
            rad = rr if a % 2 == 0 else rr * 0.5
            pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
        d.polygon(pts, fill=col)


def halo(d, cx, cy, r, cols):
    """Concentric glow: cols runs from the faintest outer ring inward."""
    n = len(cols)
    for i, col in enumerate(cols):
        rr = r * (n - i) / n
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col)


def glow_line(d, p0, p1, glow, core, wglow=5, wcore=2):
    """A line with a dim wide under-stroke and a bright core."""
    d.line([p0, p1], fill=glow, width=wglow)
    d.line([p0, p1], fill=core, width=wcore)


def refl(d, x, y, w, col, n=3, gap=3, lh=2):
    """Short stacked light streaks, as on water at night."""
    for i in range(n):
        yy = y + i * (lh + gap)
        inset = (i % 2) * 2
        d.line([(x + inset, yy), (x + w - inset, yy)], fill=col, width=lh)


def arc_pts(p0, p1, p2, n=16):
    pts = []
    for i in range(n + 1):
        t = i / n
        px = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
        py = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
        pts.append((px, py))
    return pts


def dot_trail(d, pts, col, r=2, step=2):
    for i, (px, py) in enumerate(pts):
        if i % step == 0:
            d.ellipse([px - r, py - r, px + r, py + r], fill=col)


def starfield(d, x, y, w, h, n, seed, frac=0.6):
    g = lcg(seed)
    for _ in range(n):
        px = x + next(g) % max(w - 4, 1)
        py = y + next(g) % max(int(h * frac), 1)
        d.ellipse([px, py, px + 2, py + 2], fill=(206, 213, 229))

# --- lead scenes: full illustrations drawn at native size --------------------

def scene_radar(d, x, y, w, h):
    """Gulf coast at night: a Patriot-style radar and radome under fire."""
    vgrad(d, x, y, w, h, (10, 14, 30), (58, 72, 108), steps=26)
    starfield(d, x, y, w, h, 48, 11, frac=0.5)
    # moon with a soft halo, top right
    mx0, my0 = x + w - 34, y + 22
    halo(d, mx0, my0, 17, [(50, 60, 86), (64, 76, 102), (82, 94, 120)])
    circle(d, mx0, my0, 8, (233, 237, 245))
    circle(d, mx0 - 3, my0 - 2, 2, (200, 206, 218))
    circle(d, mx0 + 2, my0 + 3, 1, (200, 206, 218))
    gy = y + h - 24
    # searchlight beams fanning up from the radar position
    bx0 = x + int(w * 0.24)
    d.polygon([(bx0, gy - 52), (x + int(w * 0.02), y + 4),
               (x + int(w * 0.13), y + 2)], fill=(50, 60, 86))
    d.polygon([(bx0, gy - 52), (x + int(w * 0.44), y + 2),
               (x + int(w * 0.55), y + 6)], fill=(46, 56, 82))
    # the sea in the foreground
    vgrad(d, x, gy, w, h - (gy - y), (20, 32, 52), (9, 15, 28), steps=8)
    g = lcg(31)
    # shore installations with lit windows, standing on the coast line
    for bx, bw, bh in ((0.03, 0.09, 0.30), (0.115, 0.055, 0.21),
                       (0.80, 0.10, 0.36), (0.915, 0.065, 0.25)):
        bx1 = x + int(w * bx)
        bw1 = int(w * bw)
        bh1 = int(h * bh)
        d.rectangle([bx1, gy - bh1, bx1 + bw1, gy], fill=(8, 10, 14))
        for wy in range(gy - bh1 + 3, gy - 3, 5):
            for wx in range(bx1 + 3, bx1 + bw1 - 2, 6):
                if next(g) % 2 == 0:
                    d.rectangle([wx, wy, wx + 2, wy + 2], fill=(244, 200, 92))
    # radome on its plinth, with panel seams
    dx0 = x + int(w * 0.60)
    d.rectangle([dx0, gy - 9, dx0 + 46, gy], fill=(52, 56, 64))
    d.pieslice([dx0 - 3, gy - 54, dx0 + 49, gy + 8], 180, 360,
               fill=(208, 212, 216))
    d.arc([dx0 + 6, gy - 44, dx0 + 40, gy + 2], 180, 360, fill=(168, 174, 180))
    d.line([(dx0 + 23, gy - 50), (dx0 + 23, gy)], fill=(168, 174, 180), width=1)
    # phased-array radar panel on a trailer, elements in a 6x4 grid
    rx = x + int(w * 0.13)
    d.rectangle([rx, gy - 10, rx + 58, gy - 3], fill=(74, 79, 88))
    circle(d, rx + 12, gy - 3, 3, (30, 32, 38))
    circle(d, rx + 46, gy - 3, 3, (30, 32, 38))
    d.polygon([(rx + 6, gy - 12), (rx + 16, gy - 64), (rx + 66, gy - 55),
               (rx + 56, gy - 6)], fill=(150, 158, 168), outline=(30, 32, 38))
    for i in range(6):
        for j in range(4):
            px = rx + 20 + i * 7 - j * 2
            py = gy - 57 + j * 11 + i // 3
            col = (255, 190, 90) if (i + j) % 5 == 0 else (96, 104, 114)
            d.ellipse([px, py, px + 3, py + 3], fill=col)
    # surveillance dish on a mast, right of the radar
    mx = rx + 96
    d.line([(mx, gy), (mx, gy - 54)], fill=(120, 126, 134), width=2)
    d.line([(mx - 7, gy - 18), (mx, gy - 30), (mx + 7, gy - 18)],
           fill=(120, 126, 134), width=1)
    d.pieslice([mx - 18, gy - 84, mx + 18, gy - 48], 300, 130,
               fill=(198, 204, 210), outline=(30, 32, 38))
    d.line([(mx, gy - 66), (mx + 13, gy - 76)], fill=(150, 156, 164), width=2)
    circle(d, mx + 14, gy - 77, 3, (210, 216, 222))
    # coast line
    d.line([(x, gy), (x + w, gy)], fill=(110, 120, 132), width=1)
    # two incoming missiles on arcs from the top-right
    pts = arc_pts((x + w - 6, y + 3), (x + int(w * 0.66), y + 1),
                  (x + int(w * 0.55), y + int(h * 0.33)))
    dot_trail(d, pts, (255, 150, 54), 2, 2)
    hx, hy = pts[-1]
    halo(d, hx, hy, 7, [(120, 70, 30), (200, 110, 40)])
    d.polygon([(hx, hy), (hx - 10, hy - 5), (hx - 2, hy + 6)],
              fill=(255, 214, 120))
    pts3 = arc_pts((x + w - 44, y + 2), (x + int(w * 0.82), y + int(h * 0.10)),
                   (x + int(w * 0.74), y + int(h * 0.30)))
    dot_trail(d, pts3, (255, 170, 80), 2, 2)
    hx3, hy3 = pts3[-1]
    d.polygon([(hx3, hy3), (hx3 - 8, hy3 - 4), (hx3 - 1, hy3 + 5)],
              fill=(255, 200, 110))
    # interceptor rising from the radar to a haloed burst
    bx, by = x + int(w * 0.42), y + int(h * 0.28)
    pts2 = arc_pts((rx + 36, gy - 58), (x + int(w * 0.28), y + int(h * 0.20)),
                   (bx, by), 18)
    dot_trail(d, pts2, (240, 226, 170), 2, 2)
    halo(d, bx, by, 24, [(110, 60, 26), (160, 84, 30)])
    burst(d, bx, by, 15, (238, 128, 34), (252, 224, 130))
    # light reflections on the water
    refl(d, bx - 15, gy + 5, 30, (150, 96, 44), n=3)
    refl(d, mx0 - 13, gy + 4, 26, (118, 128, 148), n=4)
    refl(d, x + int(w * 0.82), gy + 6, 22, (96, 82, 48), n=2)


def scene_barrage(d, x, y, w, h):
    """Night barrage over a city skyline, a river and its bridge."""
    vgrad(d, x, y, w, h, (6, 8, 20), (50, 50, 78), steps=26)
    starfield(d, x, y, w, h, 26, 23, frac=0.35)
    g = lcg(47)
    base = y + h - 18
    # far skyline, taller now the scene has room to breathe
    fx = x + 4
    while fx < x + w - 12:
        bw = 14 + next(g) % 16
        bh = int(h * 0.22) + next(g) % int(h * 0.20)
        d.rectangle([fx, base - bh, fx + bw, base], fill=(30, 32, 46))
        fx += bw + 3
    # near skyline with many lit windows
    nx = x + 2
    while nx < x + w - 14:
        bw = 18 + next(g) % 20
        bh = int(h * 0.34) + next(g) % int(h * 0.28)
        d.rectangle([nx, base - bh, nx + bw, base], fill=(13, 14, 21))
        for _ in range(6):
            wx = nx + 3 + next(g) % max(bw - 6, 1)
            wy = base - bh + 3 + next(g) % max(bh - 6, 1)
            d.rectangle([wx, wy, wx + 2, wy + 2], fill=(246, 202, 94))
        nx += bw + 4
    # explosions above the rooftops, haloed
    for fx_, fy_, r in ((0.28, 0.36, 13), (0.66, 0.27, 10), (0.86, 0.47, 8)):
        ex, ey = x + int(w * fx_), y + int(h * fy_)
        halo(d, ex, ey, int(r * 1.9), [(104, 56, 24), (150, 80, 28)])
        burst(d, ex, ey, r, (240, 140, 40), (252, 226, 140))
    # smoke plumes drifting off three rooftops
    for sx_, sy_, sw in ((0.52, 0.60, 30), (0.16, 0.55, 22), (0.74, 0.66, 26)):
        sx0, sy0 = x + int(w * sx_), base - int(h * sy_)
        for k in range(3):
            d.ellipse([sx0 + k * 9, sy0 - k * 6, sx0 + k * 9 + sw - k * 5,
                       sy0 - k * 6 + 11], fill=(70 + k * 8, 70 + k * 8, 80 + k * 8))
    # descending missile streaks with glow trails
    for sx, ex, ey_ in ((0.14, 0.27, 0.55), (0.40, 0.50, 0.62),
                        (0.58, 0.68, 0.50), (0.82, 0.92, 0.58)):
        p0 = (x + int(w * sx), y + 3)
        p1 = (x + int(w * ex), y + int(h * ey_))
        glow_line(d, p0, p1, (122, 70, 28), (255, 190, 84), 5, 2)
        halo(d, p1[0], p1[1], 6, [(140, 82, 30), (210, 130, 44)])
        circle(d, p1[0], p1[1], 2, (255, 232, 160))
    # drones at varied sizes and depths: an X body with a red eye
    for fx_, fy_, s in ((0.20, 0.20, 8), (0.34, 0.13, 6), (0.47, 0.22, 9),
                        (0.60, 0.10, 5), (0.72, 0.19, 7), (0.86, 0.12, 6),
                        (0.93, 0.30, 5)):
        cx, cy = x + int(w * fx_), y + int(h * fy_)
        d.line([(cx - s, cy - s * 2 // 3), (cx + s, cy + s * 2 // 3)],
               fill=(126, 130, 142), width=2)
        d.line([(cx - s, cy + s * 2 // 3), (cx + s, cy - s * 2 // 3)],
               fill=(126, 130, 142), width=2)
        circle(d, cx, cy, 2, (216, 66, 52))
    # river and bridge silhouette, with reflections under the lamps
    vgrad(d, x, base, w, h - (base - y), (16, 30, 52), (8, 14, 28), steps=6)
    deck = base + 4
    for tx_ in (x + int(w * 0.33), x + int(w * 0.66)):
        d.line([(tx_, deck - 20), (tx_, deck + 3)], fill=(4, 5, 8), width=3)
        d.line([(tx_, deck - 20), (tx_ - 22, deck)], fill=(4, 5, 8), width=1)
        d.line([(tx_, deck - 20), (tx_ + 22, deck)], fill=(4, 5, 8), width=1)
        d.line([(tx_, deck - 20), (tx_ - 10, deck)], fill=(4, 5, 8), width=1)
        d.line([(tx_, deck - 20), (tx_ + 10, deck)], fill=(4, 5, 8), width=1)
    d.line([(x + 2, deck), (x + w - 2, deck)], fill=(4, 5, 8), width=3)
    for i in range(7):
        lx = x + 12 + i * (w - 24) // 6
        d.ellipse([lx, deck - 2, lx + 2, deck], fill=(255, 220, 140))
        refl(d, lx - 2, deck + 4, 6, (96, 84, 44), n=2, gap=2)
    refl(d, x + int(w * 0.28) - 12, base + 3, 24, (110, 70, 30), n=2)
    refl(d, x + int(w * 0.66) - 10, base + 6, 20, (100, 64, 28), n=2)


def scene_conference(d, x, y, w, h):
    """A climate-conference hall: globe, clock at 03:00, long table, delegates."""
    vgrad(d, x, y, w, h, (242, 232, 206), (216, 198, 166), steps=18)
    # chandeliers: a stem, a warm halo and a lit disc
    for fx_ in (0.14, 0.50, 0.86):
        cx = x + int(w * fx_)
        d.line([(cx, y), (cx, y + 8)], fill=(120, 100, 64), width=2)
        halo(d, cx, y + 13, 10, [(226, 208, 164), (236, 220, 182)])
        circle(d, cx, y + 13, 4, (252, 240, 200), outline=(150, 124, 78))
    # banners on the back wall, left and right
    for bx, col, emb in ((x + 8, (52, 84, 128), WHITE),
                         (x + w - 32, (44, 104, 74), (240, 220, 150))):
        d.rectangle([bx, y + 6, bx + 24, y + 62], fill=col)
        d.polygon([(bx, y + 62), (bx + 24, y + 62), (bx + 12, y + 54)],
                  fill=col)
        circle(d, bx + 12, y + 24, 7, None, outline=emb, width=2)
        d.ellipse([bx + 8, y + 20, bx + 13, y + 26], fill=emb)
    # globe on the back wall, with graticule arcs
    gx, gy = x + int(w * 0.26), y + 38
    d.ellipse([gx - 30, gy - 30, gx + 30, gy + 30], fill=(246, 238, 214))
    circle(d, gx, gy, 24, (74, 142, 192), outline=(52, 96, 140), width=2)
    d.ellipse([gx - 17, gy - 12, gx - 3, gy + 1], fill=GREEN)
    d.ellipse([gx + 2, gy + 5, gx + 18, gy + 16], fill=GREEN)
    d.ellipse([gx + 6, gy - 18, gx + 18, gy - 8], fill=GREEN)
    d.ellipse([gx - 8, gy - 24, gx + 8, gy + 24], outline=(52, 96, 140))
    d.ellipse([gx - 24, gy - 9, gx + 24, gy + 9], outline=(52, 96, 140))
    d.line([(gx - 24, gy), (gx + 24, gy)], fill=(52, 96, 140), width=1)
    # wall clock reading 03:00 — the objections deadline
    kx, ky = x + int(w * 0.74), y + 38
    d.ellipse([kx - 27, ky - 27, kx + 27, ky + 27], fill=(246, 238, 214))
    circle(d, kx, ky, 21, WHITE, outline=INK, width=2)
    for a in range(12):
        ang = math.pi * a / 6
        r0, r1 = (15, 19) if a % 3 == 0 else (17, 19)
        d.line([(kx + r0 * math.cos(ang), ky + r0 * math.sin(ang)),
                (kx + r1 * math.cos(ang), ky + r1 * math.sin(ang))],
               fill=INK, width=1)
    d.line([(kx, ky), (kx, ky - 13)], fill=INK, width=2)
    d.line([(kx, ky), (kx + 11, ky)], fill=INK, width=2)
    d.line([(kx, ky), (kx - 8, ky + 9)], fill=RED, width=1)
    # floor, then the long table in perspective with shaded bands
    ty = y + h - 46
    d.rectangle([x, ty + 18, x + w, y + h], fill=(158, 124, 80))
    d.polygon([(x + 18, y + h - 2), (x + w - 18, y + h - 2),
               (x + int(w * 0.66), ty), (x + int(w * 0.34), ty)],
              fill=(146, 106, 66))
    d.polygon([(x + 34, y + h - 8), (x + w - 34, y + h - 8),
               (x + int(w * 0.64), ty + 4), (x + int(w * 0.36), ty + 4)],
              fill=(160, 120, 76))
    d.line([(x + int(w * 0.34), ty), (x + int(w * 0.66), ty)],
           fill=(110, 78, 44), width=2)
    # delegates along the far side: shoulders, heads, name plates,
    # microphones, and for some a paper and a glass of water
    skins = [(233, 192, 152), (196, 142, 102), (122, 84, 58), (240, 205, 168)]
    suits = [(38, 44, 66), (74, 60, 54), (52, 66, 52), (86, 44, 48),
             (44, 52, 74), (64, 64, 64), (70, 52, 70), (54, 62, 78)]
    n = 8
    for i in range(n):
        cx = x + int(w * (0.10 + 0.80 * i / (n - 1)))
        cy = ty - 6
        d.pieslice([cx - 12, cy - 3, cx + 12, cy + 17], 180, 360,
                   fill=suits[i % len(suits)])
        circle(d, cx, cy - 6, 6, skins[i % len(skins)])
        d.rectangle([cx - 6, ty + 6, cx + 6, ty + 11], fill=(245, 243, 236))
        d.line([(cx + 8, ty + 3), (cx + 12, cy + 3)], fill=(60, 56, 50),
               width=1)
        if i % 3 == 0:
            d.rectangle([cx - 13, ty + 15, cx - 3, ty + 20],
                        fill=(248, 246, 238))
        if i % 3 == 1:
            d.rectangle([cx + 9, ty + 13, cx + 13, ty + 19],
                        fill=(168, 196, 216))
    # near-side delegates seen from behind, larger in the tall frame
    for cx, col, suit in ((x + int(w * 0.07), (42, 34, 30), (36, 38, 46)),
                          (x + int(w * 0.31), (24, 24, 26), (48, 42, 52)),
                          (x + int(w * 0.93), (96, 74, 52), (40, 46, 40))):
        d.pieslice([cx - 23, y + h - 15, cx + 23, y + h + 21], 180, 360,
                   fill=suit)
        circle(d, cx, y + h - 5, 10, col)


SCENES = {
    "radar": scene_radar, "barrage": scene_barrage,
    "conference": scene_conference,
}

# --- pictograms: small scenes drawn with primitives (enriched, revision 4) ---

def art_blast(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 32, 46))
    for i in range(14):
        px = x + 8 + (i * 37) % (w - 16)
        py = y + 8 + (i * 23) % 26
        d.ellipse([px, py, px + 2, py + 2], fill=(220, 220, 230))
    cx, cy = x + w // 2, y + h // 2 + 6
    for k, r in enumerate((36, 26, 16)):
        col = ((232, 122, 30), (240, 180, 40), (250, 230, 120))[k]
        pts = []
        for a in range(16):
            ang = math.pi * a / 8
            rr = r if a % 2 == 0 else r * 0.55
            pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
        d.polygon(pts, fill=col)
    d.line([(x + 12, y + h - 12), (cx, cy)], fill=(240, 180, 40), width=3)


def art_bridge(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.rectangle([x, y + h - 16, x + w, y + h], fill=(120, 150, 190))
    deck_y = y + h - 26
    for tx in (x + w // 4, x + 3 * w // 4):
        d.rectangle([tx - 3, y + 16, tx + 3, deck_y], fill=INK)
    d.arc([x + w // 4 - 3, y + 2, x + 3 * w // 4 + 3, y + 62],
          180, 360, fill=INK, width=3)
    d.line([(x + 6, deck_y), (x + w - 6, deck_y)], fill=INK, width=4)
    for fx in range(x + 14, x + w - 10, 14):
        d.line([(fx, deck_y - 14), (fx, deck_y)], fill=INK, width=1)
    d.line([(x + 6, y + h - 22), (x + w - 6, y + h - 22)], fill=WHITE, width=3)


def art_climate(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 232, 214))
    cx, cy, r = x + w // 2, y + h // 2, 30
    circle(d, cx, cy, r, (70, 140, 190))
    d.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=WHITE, width=4)
    d.arc([cx - r, cy - r, cx + r, cy + r], 20, 160, fill=WHITE, width=4)
    d.ellipse([cx - 22, cy - 14, cx - 2, cy + 2], fill=GREEN)
    d.ellipse([cx + 2, cy + 4, cx + 20, cy + 18], fill=GREEN)


def art_trade(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 236, 248))
    circle(d, x + 16, y + 14, 7, (246, 200, 84))
    d.rectangle([x, y + h - 22, x + w, y + h], fill=(90, 130, 180))
    for wx in (10, 38, 66):
        d.arc([x + wx, y + h - 16, x + wx + 16, y + h - 6], 0, 180,
              fill=WHITE, width=2)
    d.polygon([(x + 14, y + h - 22), (x + w - 14, y + h - 22),
               (x + w - 26, y + h - 44), (x + 26, y + h - 44)], fill=(60, 60, 70))
    d.rectangle([x + 26, y + h - 62, x + 52, y + h - 44], fill=RED)
    d.rectangle([x + 56, y + h - 62, x + 82, y + h - 44], fill=GOLD)
    d.rectangle([x + 86, y + h - 62, x + w - 6, y + h - 44], fill=BLUE)
    # dockside crane over the ship
    d.line([(x + w - 12, y + 8), (x + w - 12, y + h - 44)], fill=(70, 74, 84), width=4)
    d.line([(x + w - 12, y + 8), (x + 40, y + 8)], fill=(70, 74, 84), width=3)
    d.line([(x + 52, y + 8), (x + 52, y + 22)], fill=(70, 74, 84), width=2)
    d.rectangle([x + 46, y + 22, x + 58, y + 30], fill=GOLD)


def art_arrest(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 224, 208))
    cx, cy = x + w // 2, y + h // 2 - 4
    for ox in (-26, 26):
        d.ellipse([cx + ox - 15, cy - 15, cx + ox + 15, cy + 15],
                  outline=INK, width=5)
    d.line([(cx - 12, cy), (cx + 12, cy)], fill=INK, width=5)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=INK)
    # a sheriff's star in the corner
    sx, sy = x + w - 16, y + 14
    pts = []
    for a in range(10):
        ang = math.pi * a / 5 - math.pi / 2
        rr = 9 if a % 2 == 0 else 4
        pts.append((sx + rr * math.cos(ang), sy + rr * math.sin(ang)))
    d.polygon(pts, fill=GOLD, outline=INK)
    # red-and-blue light bar along the bottom
    d.rectangle([x + 18, y + h - 14, x + w // 2, y + h - 6], fill=RED)
    d.rectangle([x + w // 2, y + h - 14, x + w - 18, y + h - 6], fill=BLUE)


def art_database(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 228, 240))
    # a second rack behind the main cylinder
    d.rectangle([x + 8, y + 26, x + 26, y + h - 14], fill=(104, 122, 158))
    for ry in range(y + 34, y + h - 20, 10):
        d.line([(x + 11, ry), (x + 23, ry)], fill=WHITE, width=2)
    cx, cy = x + w // 2 + 8, y + h // 2 - 4
    d.ellipse([cx - 26, cy - 26, cx + 26, cy - 12], fill=(90, 110, 150))
    d.rectangle([cx - 26, cy - 19, cx + 26, cy + 22], fill=(120, 140, 180))
    d.ellipse([cx - 26, cy + 8, cx + 26, cy + 22], fill=(90, 110, 150))
    d.line([(cx - 26, cy - 4), (cx + 26, cy - 4)], fill=WHITE, width=2)
    d.line([(cx - 26, cy + 8), (cx + 26, cy + 8)], fill=WHITE, width=2)
    d.rectangle([cx + 8, cy + 14, cx + 30, cy + 34], fill=GOLD, outline=INK, width=2)
    d.ellipse([cx + 15, cy + 19, cx + 23, cy + 27], outline=INK, width=2)
    # warning triangle
    tx, ty = x + w - 18, y + 12
    d.polygon([(tx, ty - 8), (tx + 8, ty + 6), (tx - 8, ty + 6)],
              fill=(240, 180, 40), outline=INK)
    d.line([(tx, ty - 3), (tx, ty + 2)], fill=INK, width=2)
    d.ellipse([tx - 1, ty + 3, tx + 1, ty + 5], fill=INK)


def art_rugby(d, x, y, w, h):
    for i in range(5):
        col = (206, 232, 206) if i % 2 == 0 else (222, 238, 222)
        d.rectangle([x, y + h * i // 5, x + w, y + h * (i + 1) // 5], fill=col)
    d.line([(x, y + h // 2), (x + w, y + h // 2)], fill=WHITE, width=2)
    cx, cy = x + w // 2, y + h // 2
    d.ellipse([cx - 34, cy - 16, cx + 34, cy + 16], fill=(150, 60, 40))
    d.line([(cx - 34, cy), (cx + 34, cy)], fill=WHITE, width=3)
    d.line([(cx - 12, cy - 14), (cx - 12, cy + 14)], fill=WHITE, width=2)
    d.line([(cx + 12, cy - 14), (cx + 12, cy + 14)], fill=WHITE, width=2)
    for ox in (-40, 40):
        d.line([(cx + ox, y + 12), (cx + ox, y + h - 12)], fill=GOLD, width=4)


def art_football(d, x, y, w, h):
    for i in range(5):
        col = (204, 228, 204) if i % 2 == 0 else (220, 232, 220)
        d.rectangle([x, y + h * i // 5, x + w, y + h * (i + 1) // 5], fill=col)
    cx, cy = x + w // 2, y + h // 2
    circle(d, cx, cy, 40, None, outline=WHITE, width=2)
    d.line([(x, cy), (x + w, cy)], fill=WHITE, width=2)
    r = 28
    circle(d, cx, cy, r, WHITE, outline=INK, width=2)
    d.polygon([(cx, cy - 10), (cx + 10, cy - 3), (cx + 6, cy + 9),
               (cx - 6, cy + 9), (cx - 10, cy - 3)], fill=INK)
    for ang in (0, 72, 144, 216, 288):
        ax = cx + 22 * math.cos(math.radians(ang - 90))
        ay = cy + 22 * math.sin(math.radians(ang - 90))
        d.ellipse([ax - 4, ay - 4, ax + 4, ay + 4], fill=INK)


def art_cricket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(228, 238, 210))
    d.polygon([(x + 30, y + h), (x + 52, y + h), (x + 48, y + 20),
               (x + 36, y + 20)], fill=(232, 220, 182))
    cx, cy = x + w // 2 - 8, y + h // 2
    d.polygon([(cx - 34, cy + 30), (cx - 8, cy + 30), (cx + 22, cy - 34),
               (cx + 30, cy - 40), (cx + 34, cy - 26), (cx + 6, cy + 30)],
              fill=(210, 180, 120), outline=INK)
    d.rectangle([cx + 24, cy - 44, cx + 34, cy - 24], fill=(120, 80, 40))
    circle(d, cx - 30, cy - 26, 9, RED, outline=WHITE, width=2)
    # stumps at the far end of the pitch
    for sx in (x + w - 22, x + w - 17, x + w - 12):
        d.line([(sx, y + 22), (sx, y + 38)], fill=GOLD, width=2)
    d.line([(x + w - 23, y + 21), (x + w - 11, y + 21)], fill=GOLD, width=2)
    d.line([(x + 8, y + h - 10), (x + w - 8, y + h - 10)], fill=GREEN, width=4)


def art_planet(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 26, 44))
    for i in range(12):
        px = x + 6 + (i * 29) % (w - 12)
        py = y + 6 + (i * 17) % (h - 12)
        d.ellipse([px, py, px + 2, py + 2], fill=WHITE)
    cx, cy = x + w // 2, y + h // 2
    d.ellipse([cx - 44, cy - 12, cx + 44, cy + 12], outline=GOLD, width=3)
    circle(d, cx, cy, 24, (200, 120, 60))
    circle(d, cx - 8, cy - 6, 5, (170, 90, 40))
    circle(d, cx + 10, cy + 8, 4, (170, 90, 40))
    circle(d, x + w - 18, y + 16, 5, (190, 196, 204))
    d.line([(x + 10, y + h - 16), (x + 26, y + h - 26)], fill=WHITE, width=2)


def art_ballot(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 228, 220))
    cx, cy = x + w // 2, y + h // 2 - 4
    d.polygon([(cx - 30, cy - 6), (cx + 30, cy - 6), (cx + 24, cy + 28),
               (cx - 24, cy + 28)], fill=(90, 110, 150))
    d.rectangle([cx - 34, cy - 12, cx + 34, cy - 4], fill=(70, 90, 130))
    d.polygon([(cx - 8, cy - 44), (cx + 14, cy - 44), (cx + 10, cy - 14),
               (cx - 12, cy - 14)], fill=WHITE, outline=INK, width=2)
    d.line([(cx - 4, cy - 30), (cx + 2, cy - 24), (cx + 10, cy - 38)],
           fill=RED, width=3)
    # a queue of voters along the bottom
    for i, vx in enumerate(range(x + 18, x + w - 12, 16)):
        circle(d, vx, y + h - 12, 4, (70, 80, 100) if i % 2 else (120, 90, 70))


def art_hospital(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 236, 232))
    cx, cy = x + w // 2, y + h // 2
    d.rectangle([cx - 30, cy - 20, cx + 30, cy + 28], fill=WHITE, outline=INK, width=2)
    d.rectangle([cx - 6, cy - 34, cx + 6, cy - 8], fill=RED)
    d.rectangle([cx - 13, cy - 27, cx + 13, cy - 15], fill=RED)
    for wy in (cy - 2, cy + 8):
        for wx in (cx - 24, cx + 16):
            d.rectangle([wx, wy, wx + 8, wy + 6], fill=(150, 180, 205))
    d.rectangle([cx - 5, cy + 16, cx + 5, cy + 28], fill=(90, 100, 110))
    d.rectangle([cx - 30, cy + 24, cx + 30, cy + 28], fill=(120, 160, 200))


def art_film(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 226, 214))
    cx, cy = x + w // 2, y + h // 2
    # film-strip bands with perforations
    for by in (cy - 30, cy + 22):
        d.rectangle([cx - 40, by, cx + 40, by + 8], fill=(40, 40, 48))
        for px in range(cx - 36, cx + 34, 10):
            d.rectangle([px, by + 2, px + 5, by + 6], fill=(238, 226, 214))
    d.rectangle([cx - 32, cy - 18, cx + 32, cy + 20], fill=(60, 60, 70))
    circle(d, cx, cy, 13, (140, 180, 220), outline=WHITE, width=3)
    d.polygon([(cx - 3, cy - 6), (cx - 3, cy + 6), (cx + 6, cy)], fill=WHITE)
    d.polygon([(cx + 32, cy - 10), (cx + 44, cy - 4), (cx + 32, cy + 2)],
              fill=(60, 60, 70))
    d.rectangle([cx - 40, cy - 30, cx - 20, cy - 18], fill=(120, 120, 130))


ART = {
    "blast": art_blast, "bridge": art_bridge, "climate": art_climate,
    "trade": art_trade, "arrest": art_arrest, "database": art_database,
    "rugby": art_rugby, "football": art_football, "cricket": art_cricket,
    "planet": art_planet, "ballot": art_ballot, "hospital": art_hospital,
    "film": art_film,
}


def draw_art(img, kind, x, y, w, h):
    """Draw a pictogram at any size: render on a 100x100 tile, then scale.

    A soft top light and a gentle foot shade are laid over the tile so
    the flat pictograms sit under the same light as the lead scenes.
    """
    tile = Image.new("RGB", (100, 100), PAPER)
    td = ImageDraw.Draw(tile)
    ART[kind](td, 0, 0, 100, 100)
    tile = tile.resize((w, h), Image.LANCZOS)
    img.paste(tile, (x, y))
    light = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ld = ImageDraw.Draw(light)
    for j in range(h):
        t = j / max(h - 1, 1)
        ld.line([(0, j), (w, j)], fill=(255, 255, 255, int(30 * (1 - t))))
    img.paste(light, (x, y), light)
    shade = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for j in range(h):
        t = j / max(h - 1, 1)
        sd.line([(0, j), (w, j)], fill=(20, 16, 8, int(22 * t)))
    img.paste(shade, (x, y), shade)

# --- panels, strips and boxes -------------------------------------------------

LEAD_ART_H = 168


def lead_panel(img, d, box, num, art, headline, deck, src):
    x0, y0, x1, y1 = box
    frame(d, box)
    ax0, ay0, ax1 = x0 + 2, y0 + 2, x1 - 2
    SCENES[art](d, ax0, ay0, ax1 - ax0, LEAD_ART_H)
    d.line([(x0 + 2, y0 + LEAD_ART_H + 2), (x1 - 2, y0 + LEAD_ART_H + 2)],
           fill=EDGE, width=2)
    badge(d, x0 + 15, y0 + 15, num, r=12)
    y = para(d, x0 + 9, y0 + LEAD_ART_H + 9, headline, f(SANSB, 16),
             x1 - x0 - 18, 19, max_lines=3)
    para(d, x0 + 9, y + 1, deck, f(SANS, 11), x1 - x0 - 18, 13.5, max_lines=3)
    d.text((x0 + 9, y1 - 14), src, font=f(SANSB, 8), fill=MUTED)


def mini_panel(img, d, box, num, art, headline, deck, src):
    x0, y0, x1, y1 = box
    frame(d, box)
    ix, iy = x0 + 6, y0 + 5
    draw_art(img, art, ix, iy, 40, 40)
    d.rectangle([ix, iy, ix + 40, iy + 40], outline=EDGE, width=1)
    badge(d, x0 + 11, y0 + 11, num, r=9)
    tx = x0 + 52
    para(d, tx, y0 + 5, headline, f(SANSB, 11), x1 - tx - 5, 13, max_lines=3)
    para(d, x0 + 6, y0 + 49, deck, f(SANS, 10), x1 - x0 - 12, 11, max_lines=3)
    d.text((x0 + 6, y1 - 11), src, font=f(SANSB, 8), fill=MUTED)


def stats_strip(d, box, stats):
    """Key-numbers strip: big verified figures, small labels, divided cells."""
    x0, y0, x1, y1 = box
    d.rectangle([x0, y0, x1, y1], fill=PANEL, outline=EDGE, width=1)
    n = len(stats)
    cw = (x1 - x0) / n
    nf = f(SANSB, 16)
    lf = f(SANS, 8)
    for i, (num, label) in enumerate(stats):
        cx = x0 + i * cw
        if i:
            d.line([(cx, y0 + 4), (cx, y1 - 4)], fill=EDGE, width=1)
        d.text((cx + (cw - tw(d, num, nf)) / 2, y0 + 1), num, font=nf, fill=RED)
        d.text((cx + (cw - tw(d, label, lf)) / 2, y0 + 20), label,
               font=lf, fill=MUTED)


def date_check(d, box, text):
    """Red-bordered DATE CHECK box: label in bold red, body wrapped after it."""
    x0, y0, x1, y1 = box
    d.rectangle([x0, y0, x1, y1], outline=RED, width=2)
    lab = "DATE CHECK — "
    lfn = f(SANSB, 9)
    bfn = f(SANS, 9)
    labw = tw(d, lab, lfn)
    maxw = x1 - x0 - 16
    # wrap the body with a narrower first line to make room for the label
    words = text.split()
    lines = []
    cur = ""
    limit = maxw - labw
    for word in words:
        trial = word if not cur else cur + " " + word
        if tw(d, trial, bfn) <= limit:
            cur = trial
        else:
            lines.append(cur)
            cur = word
            limit = maxw
    if cur:
        lines.append(cur)
    d.text((x0 + 8, y0 + 5), lab, font=lfn, fill=RED)
    yy = y0 + 5
    for i, ln in enumerate(lines):
        xx = x0 + 8 + labw if i == 0 else x0 + 8
        d.text((xx, yy), ln, font=bfn, fill=INK)
        yy += 12
    return yy

# --- schematic world map --------------------------------------------------------

# (lon, lat) outlines, drawn schematically
CONTINENTS = [
    # North America
    [(-168, 66), (-150, 70), (-130, 71), (-110, 68), (-95, 69), (-85, 66),
     (-75, 62), (-60, 55), (-55, 47), (-65, 44), (-70, 42), (-76, 36),
     (-80, 30), (-84, 30), (-90, 21), (-97, 26), (-105, 20), (-110, 23),
     (-117, 33), (-124, 42), (-125, 49), (-135, 58), (-155, 58), (-165, 60)],
    # Greenland
    [(-55, 60), (-43, 60), (-40, 64), (-30, 68), (-22, 70), (-28, 76),
     (-45, 76), (-58, 72), (-60, 66)],
    # South America
    [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18),
     (-70, -23), (-70, -33), (-73, -44), (-71, -54), (-66, -55), (-64, -47),
     (-62, -41), (-57, -38), (-50, -30), (-41, -23), (-39, -15), (-35, -8),
     (-38, -4), (-44, -2), (-50, 0), (-53, 5), (-59, 8), (-66, 10),
     (-72, 12), (-77, 8)],
    # Eurasia
    [(-10, 37), (-9, 43), (-2, 48), (2, 51), (8, 57), (12, 58), (20, 56),
     (24, 59), (30, 62), (38, 67), (45, 68), (55, 69), (65, 69), (72, 72),
     (80, 73), (95, 76), (110, 74), (125, 72), (140, 72), (155, 70),
     (170, 66), (178, 65), (178, 62), (170, 60), (162, 58), (158, 52),
     (156, 51), (150, 59), (142, 58), (140, 54), (138, 46), (135, 43),
     (130, 42), (127, 39), (126, 37), (122, 38), (120, 32), (115, 25),
     (110, 20), (108, 12), (105, 9), (103, 2), (100, 6), (97, 10),
     (94, 16), (91, 22), (88, 22), (85, 20), (80, 14), (77, 8), (74, 14),
     (72, 20), (68, 23), (64, 25), (60, 25), (56, 26), (52, 26), (49, 30),
     (47, 29), (44, 29), (40, 31), (36, 36), (34, 36), (30, 36), (28, 38),
     (26, 40), (23, 40), (22, 37), (19, 40), (15, 44), (12, 45), (8, 44),
     (3, 43), (0, 40), (-2, 37), (-6, 36), (-9, 37)],
    # Africa
    [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 11),
     (-12, 8), (-8, 5), (-4, 5), (0, 6), (6, 4), (9, 4), (12, -1),
     (13, -5), (12, -10), (13, -17), (12, -22), (15, -27), (18, -32),
     (20, -35), (26, -34), (28, -32), (32, -28), (35, -24), (40, -16),
     (40, -11), (42, -5), (46, -1), (51, 2), (51, 11), (48, 11), (44, 11),
     (42, 13), (39, 15), (38, 18), (37, 22), (35, 28), (32, 31), (30, 32),
     (25, 32), (20, 32), (15, 32), (11, 34), (10, 37), (6, 37), (0, 36)],
    # Australia
    [(113, -22), (114, -30), (115, -34), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -22), (146, -19), (142, -15), (142, -11),
     (137, -12), (135, -12), (132, -12), (130, -13), (126, -14), (122, -17),
     (118, -20), (114, -21)],
    # SE Asia islands
    [(95, 5), (100, 6), (104, 2), (100, -2), (95, 0)],
    [(110, -6), (115, -7), (118, -9), (113, -10), (108, -8)],
    [(120, -2), (125, -1), (128, -3), (123, -5), (119, -4)],
]

# (lat, lon) pins for stories 1-13
PINS = [
    (26.2, 50.6), (45.0, 34.0), (39.0, 35.0), (50.8, 4.4), (24.8, -107.4),
    (38.9, -77.0), (51.5, -0.1), (53.8, -1.5), (-41.3, 174.8), (49.9, 8.7),
    (22.3, 114.2), (-15.8, -47.9), (50.3, -5.0),
]

# pixel nudges so crowded European pins do not overlap
NUDGES = [
    (0, 0), (0, -9), (8, 10), (12, 6), (0, 0), (0, 0), (-14, -8),
    (14, -10), (0, 0), (16, 10), (0, 0), (0, 0), (-14, 10),
]


def project(lon, lat, x0, y0, w, h):
    px = x0 + (lon + 180.0) / 360.0 * w
    py = y0 + (75.0 - lat) / 130.0 * h
    return px, py


def draw_map(d, box):
    x0, y0, x1, y1 = box
    d.rectangle([x0, y0, x1, y1], fill=SEA, outline=EDGE, width=2)
    d.text((x0 + 8, y0 + 2), "WHERE THE NEWS HAPPENED — PINS 1–13",
           font=f(SANSB, 11), fill=INK)
    mx0, my0 = x0 + 8, y0 + 17
    mw, mh = x1 - x0 - 16, y1 - y0 - 20
    for poly in CONTINENTS:
        pts = [project(lon, lat, mx0, my0, mw, mh) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_EDGE)
    for i, (lat, lon) in enumerate(PINS, start=1):
        px, py = project(lon, lat, mx0, my0, mw, mh)
        dx, dy = NUDGES[i - 1]
        badge(d, px + dx, py + dy, i, r=8)

# --- story data -----------------------------------------------------------------
# Every story carries its source tag (from SOURCES.md) and a region code so
# the regions bar can be computed from the list itself.
# Regions: EU Europe, ME Middle East, AP Asia-Pacific, AM Americas,
#          AF Africa, GL Global.

LEADS = [
    ("radar",
     "Gulf widens: Iran claims new strikes on US Patriot radars",
     "Tehran says missiles and drones hit the radars at al-Riffa and Awali "
     "bases. Bahrain probes a Patriot interceptor crash.",
     "(Al Jazeera · Times of India)", "ME"),
    ("barrage",
     "Zelensky: Crimea bridge strikes a 'fair response'",
     "Russia replied with 400+ drones and 110 missiles in one night: "
     "nine killed, three Kyiv bridges hit, Lviv station struck.",
     "(BBC · Reuters)", "EU"),
    ("conference",
     "COP31 final text omits fossil fuels; vote due Sunday",
     "After double overtime in Antalya, the presidency's 10-page package "
     "drops phase-out language; EU and island states object.",
     "(AP · DPA · LaPresse)", "GL"),
]

MINIS = [
    ("trade", "EU and Indonesia sign trade deal",
     "After ten years of talks, a pact to scrap 98.5% of tariffs.",
     "(Global Digest)", "GL"),
    ("arrest", "Mexico captures 'El Chapo Isidro'",
     "FBI Ten Most Wanted drug lord held after a shoot-out in Sinaloa; a $5m reward.",
     "(AP · NYT)", "AM"),
    ("database", "FBI probes hack of crime database",
     "Apparent breach of the national criminal records system is investigated.",
     "(BBC)", "AM"),
    ("rugby", "England crush All Blacks 37-12",
     "Record Twickenham win, five tries; New Zealand lose twice in a row.",
     "(Flashscore)", "EU"),
    ("football", "Leeds stun Chelsea 4-1",
     "First win at Stamford Bridge since 1999; Okafor scores twice.",
     "(BBC)", "EU"),
    ("cricket", "India lead New Zealand by 118",
     "Day 3 stumps in Wellington: NZ 368, India 486/4. Nicholls 175, Rahul 136.",
     "(UNP)", "AP"),
    ("planet", "BepiColombo reaches Mercury",
     "Europe-Japan probe enters orbit after an eight-year voyage.",
     "(Axo News)", "GL"),
    ("ballot", "Hong Kong votes for Election Committee",
     "About 5,700 voters choose members of the powerful body.",
     "(Global Digest)", "AP"),
    ("hospital", "Bolsonaro in ICU",
     "Brazil's jailed ex-president admitted with acute bowel obstruction.",
     "(Times of India)", "AM"),
    ("film", "Spitting Image co-creator dies at 85",
     "Peter Fluck, satire puppet pioneer, dies at home in Cornwall.",
     "(BBC)", "EU"),
]

# stories 14-54: (text, source tag, region)
INDEX = [
    ("Estonia to close border with Russia; Moscow decries 'new Iron Curtain'", "(Jagran)", "EU"),
    ("Trump and Xi meet in Shenzhen; Japan challenges ahead", "(Global Digest)", "AP"),
    ("Judge approves $7.25bn Roundup weedkiller settlement", "(BBC)", "AM"),
    ("Lock of George Washington's hair sells for $4,000", "(BBC)", "AM"),
    ("US airlines warned of al-Qaeda-linked attack risk before Thanksgiving", "(TOI)", "AM"),
    ("House races still uncalled; Democratic majority in flux", "(Axo News)", "AM"),
    ("CMS proposes Medicare Advantage overhaul", "(Axo News)", "AM"),
    ("Trump signs Common Cents Act", "(Media Alert)", "AM"),
    ("Quebecor's $31bn Telus bid would reshape Canadian telecom", "(Axo News)", "AM"),
    ("Mets' $400m Tarik Skubal offer headlines MLB hot stove", "(Axo News)", "AM"),
    ("Arsenal six points clear after 2-2 draw at Newcastle", "(NYT · BBC)", "EU"),
    ("Man City held by Fulham; Anderson volley earns point", "(BBC)", "EU"),
    ("Real Madrid beat Celta Vigo 2-1", "(ScoreZaap)", "EU"),
    ("MI Emirates beat Desert Vipers by 52 runs in ILT20 opener", "(Sportradar)", "ME"),
    ("French police sentenced over beating of producer Michel Zecler", "(BBC)", "EU"),
    ("Miliband: EU deal not dependent on tuition fees", "(BBC)", "EU"),
    ("Trafalgar Square Christmas tree felled in Norway", "(BBC)", "EU"),
    ("Russia-bound ship attacked in Gulf of Finland; Ukraine likely behind it", "(Reuters)", "EU"),
    ("Teen gamer and mother helped rescue missing girl", "(BBC)", "GL"),
    ("ANC fights to keep control of South Africa's key cities", "(BBC)", "AF"),
    ("Nigerian youth and the election question", "(BBC)", "AF"),
    ("FEMA office found infested with bed bugs; 1,000 staff sent home", "(Life Science)", "AM"),
    ("LA train heists net thieves $22m in goods, feds say", "(Media Alert)", "AM"),
    ("Court pauses Iowa Army lead-azide blast; eyes Monday", "(Edit USA)", "AM"),
    ("Thanksgiving storms may bring record coastal flooding to N. California", "(Edit USA)", "AM"),
    ("Saudi-led coalition intercepts three Houthi missiles at Riyadh", "(90 Seconds)", "ME"),
    ("Fire at Iraq's Hartha power station kills at least four, injures 35", "(90 Seconds)", "ME"),
    ("Toxic liquor kills at least 11 in India's Manipur; 180 in hospital", "(90 Seconds)", "AP"),
    ("At least 24 dead as boat capsizes on funeral trip in Nigeria", "(News Media)", "AF"),
    ("Blasts reported near Russian Baltic Fleet base in Kaliningrad", "(snowurb)", "EU"),
    ("Finland probes suspected Russian helicopter incursion", "(AppiSToS)", "EU"),
    ("UN talks agree first international pact on autonomous weapons", "(snowurb)", "GL"),
    ("Four Palestinians killed in Gaza amid ceasefire breaches, medics say", "(WAFA)", "ME"),
    ("Denmark seeks EU-wide curbs on Russian tourists after murder-plot claim", "(snowurb)", "EU"),
    ("Zagreb protesters demand answers over hospital patient death", "(AppiSToS)", "EU"),
    ("Asia shares plunge as AI sell-off spreads; Nikkei -5.1%, Kospi -5.5%", "(Weekend Buzz)", "AP"),
    ("Trump warns US firms building AI data centres abroad of 'tremendous tax'", "(Weekend Buzz)", "AM"),
    ("Chinese banks issue rare joint warning on precious-metals risk", "(Weekend Buzz)", "AP"),
    ("Nvidia finances face SEC inquiry, sources say", "(snowurb)", "AM"),
    ("Voyager 1 now one light-day from Earth, a first for any spacecraft", "(CASRAI)", "GL"),
    ("Webb study reconstructs stellar merger in Andromeda galaxy", "(CASRAI)", "GL"),
]

# stories 55-64: rapid-fire one-liners (text, source tag, region)
BRIEFS = [
    ("Zverev and Alcaraz reach ATP Finals title match in Turin", "(kendanafrica)", "EU"),
    ("Ireland beat South Africa 20-17 in Dublin", "(kendanafrica)", "EU"),
    ("France rout Argentina 45-17 to reach Nations Championship final", "(Apex Sports)", "EU"),
    ("Russell takes Las Vegas GP pole, 0.098s clear of Sainz", "(kendanafrica)", "AM"),
    ("Pakistan beat Sri Lanka by 8 wickets to seal Test series 1-0", "(Daily Dose)", "AP"),
    ("Harden scores 51 as Cavaliers beat Pacers 128-119 in NBA Cup", "(Flashscore)", "AM"),
    ("Ronaldo nets 986th career goal but misses penalty in Al-Nassr loss", "(Apex Sports)", "ME"),
    ("Ramayana overtakes Godzilla Minus Zero at the box office", "(Standard Topic)", "AP"),
    ("Lattice-crypto method speeds NASA pulsar hunt a million-fold", "(CASRAI)", "GL"),
    ("Leapmotor Q3 profit plunges 73% despite record deliveries", "(Weekend Buzz)", "AP"),
]

# key numbers for the strip under the masthead — each figure is in SOURCES.md
STATS = [
    ("~200", "nations at COP31"),
    ("03:00", "GMT deadline for objections"),
    ("404", "drones in one night"),
    ("110+", "missiles over Ukraine"),
    ("9", "killed in the barrage"),
    ("2", "US bases targeted in Bahrain"),
]

REGION_ORDER = [("EU", "EUROPE"), ("ME", "MIDDLE EAST"), ("AP", "ASIA-PACIFIC"),
                ("AM", "AMERICAS"), ("AF", "AFRICA"), ("GL", "GLOBAL")]

DATE_CHECK_TEXT = (
    "Every story here was reported or still developing on Sunday 22 Nov "
    "2026 — wires read through Sunday morning (WIB), Saturday's sport "
    "carried as Saturday results, as a Sunday paper does. Left out as "
    "other days' news: the Peru earthquake (20 Nov) and the Poland "
    "missile falls (21 Nov)."
)


def regions_bar():
    counts = {}
    for story in LEADS + MINIS + INDEX + BRIEFS:
        counts[story[-1]] = counts.get(story[-1], 0) + 1
    return "  ·  ".join(f"{name} {counts.get(code, 0)}"
                         for code, name in REGION_ORDER)


def flow_columns(d, items, first_num, font, colw, ncols):
    """Wrap numbered, source-tagged items into balanced columns.

    Returns a list of ncols columns, each a list of per-item line lists,
    items kept in reading order down column 1, then column 2, and so on.
    """
    entries = [wrap_tagged(d, f"{first_num + j}. {text}", tag, font, colw)
               for j, (text, tag, _region) in enumerate(items)]
    total = sum(len(e) for e in entries)
    cols = [[] for _ in range(ncols)]
    counts = [0] * ncols
    ci = 0
    for e in entries:
        if ci < ncols - 1 and counts[ci] > 0 and counts[ci] >= total / ncols:
            ci += 1
        cols[ci].append(e)
        counts[ci] += len(e)
    return cols


def draw_flow(d, cols, x0, y, colw, gap, font, leading, item_gap=1.0):
    bottom = y
    for ci, col in enumerate(cols):
        x = x0 + ci * (colw + gap)
        yy = y
        for lines in col:
            for ln, tag_start in lines:
                if tag_start < 0:
                    d.text((x, yy), ln, font=font, fill=INK)
                elif tag_start == 0:
                    d.text((x, yy), ln, font=font, fill=MUTED)
                else:
                    d.text((x, yy), ln[:tag_start], font=font, fill=INK)
                    d.text((x + tw(d, ln[:tag_start], font), yy),
                           ln[tag_start:], font=font, fill=MUTED)
                yy += leading
            yy += item_gap
        bottom = max(bottom, yy - item_gap)
    return bottom


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # masthead
    title = "The Daily Compass"
    tf = f(SERIFB, 44)
    d.text(((W - tw(d, title, tf)) / 2, 2), title, font=tf, fill=INK)
    rule(d, MARGIN, 57, W - MARGIN, 3)
    d.text((MARGIN, 62), "Sunday 22 November 2026",
           font=f(SANSB, 13), fill=INK)
    right = "64 verified stories — reported Sunday 22 Nov 2026"
    d.text((W - MARGIN - tw(d, right, f(SANS, 12)), 63), right,
           font=f(SANS, 12), fill=MUTED)
    rule(d, MARGIN, 79, W - MARGIN, 2)

    # key-numbers strip
    stats_strip(d, (MARGIN, 85, W - MARGIN, 114), STATS)

    # lead row: 3 panels with full scene art, almost twice as tall
    top = 120
    lw = (W - 2 * MARGIN - 2 * 10) // 3
    lh = 274
    for i, (art, head, deck, src, _region) in enumerate(LEADS):
        x0 = MARGIN + i * (lw + 10)
        lead_panel(img, d, (x0, top, x0 + lw, top + lh), i + 1, art, head,
                   deck, src)

    # mini rows: 2 x 5, a notch shorter than revision 4
    my = top + lh + 5
    mw = (W - 2 * MARGIN - 4 * 8) // 5
    mh = 96
    for r in range(2):
        for c in range(5):
            i = r * 5 + c
            art, head, deck, src, _region = MINIS[i]
            x0 = MARGIN + c * (mw + 8)
            y0 = my + r * (mh + 5)
            mini_panel(img, d, (x0, y0, x0 + mw, y0 + mh), i + 4, art, head,
                       deck, src)

    # map strip, slightly lower than revision 4
    mapy = my + 2 * mh + 5 + 5
    draw_map(d, (MARGIN, mapy, W - MARGIN, mapy + 48))

    # index: three balanced columns, stories 14-54, each with its source
    iy = mapy + 48 + 7
    d.text((MARGIN, iy), "ALSO TODAY — INDEX 14–54",
           font=f(SANSB, 13), fill=INK)
    bar = regions_bar()
    bfn_bar = f(SANSB, 10)
    d.text((W - MARGIN - tw(d, bar, bfn_bar), iy + 2), bar,
           font=bfn_bar, fill=MUTED)
    rule(d, MARGIN, iy + 18, W - MARGIN, 2)
    ifn = f(SANS, 8.5)
    icolw = (W - 2 * MARGIN - 2 * 14) // 3
    icols = flow_columns(d, INDEX, 14, ifn, icolw, 3)
    ibot = draw_flow(d, icols, MARGIN, iy + 24, icolw, 14, ifn, 9.2,
                     item_gap=0.5)

    # in brief: two columns of one-liners, stories 55-64, each with its source
    by = ibot + 7
    d.text((MARGIN, by), "IN BRIEF — THE REST OF THE DAY IN ONE LINE EACH",
           font=f(SANSB, 12), fill=INK)
    rule(d, MARGIN, by + 17, W - MARGIN, 2)
    bfn = f(SANS, 8.5)
    bcolw = (W - 2 * MARGIN - 24) // 2
    bcols = flow_columns(d, BRIEFS, 55, bfn, bcolw, 2)
    bbot = draw_flow(d, bcols, MARGIN, by + 23, bcolw, 24, bfn, 9.2,
                     item_gap=0.5)

    # date check box
    cby = bbot + 7
    date_check(d, (MARGIN, cby, W - MARGIN, cby + 30), DATE_CHECK_TEXT)

    # footer
    d.text((MARGIN, cby + 34),
           "Every story dated & sourced — checked Sunday 22 Nov 2026. "
           "Full source list on file for all 64 stories; claims are "
           "labelled as claims; market figures are Friday's closes. "
           "All pictures drawn in code.",
           font=f(SANS, 8.5), fill=MUTED)

    if os.environ.get("RENDER_DEBUG"):
        print(f"index_bottom={ibot:.0f} briefs_bottom={bbot:.0f} "
              f"datebox_bottom={cby + 30} footer_y={cby + 34}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, format="PNG", optimize=True)
    print(OUT)


if __name__ == "__main__":
    build()
