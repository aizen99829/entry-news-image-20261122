"""Render The Daily Compass front page for Sunday 22 November 2026.

A dense newspaper poster drawn with Pillow primitives: masthead, three lead
panels with small pictograms, ten smaller illustrated panels, a schematic
world map with numbered pins, and a two-column index of the day's remaining
stories. Output is deterministic: the same code always writes byte-identical
PNG bytes.
"""

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
    return lines


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

# --- pictograms: small flat icons drawn with primitives ----------------------

def art_blast(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 32, 46))
    for i in range(14):
        px = x + 8 + (i * 37) % (w - 16)
        py = y + 8 + (i * 23) % 26
        d.ellipse([px, py, px + 2, py + 2], fill=(220, 220, 230))
    cx, cy = x + w // 2, y + h // 2 + 6
    import math
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
    d.rectangle([x, y + h - 22, x + w, y + h], fill=(90, 130, 180))
    d.polygon([(x + 14, y + h - 22), (x + w - 14, y + h - 22),
               (x + w - 26, y + h - 44), (x + 26, y + h - 44)], fill=(60, 60, 70))
    d.rectangle([x + 26, y + h - 62, x + 52, y + h - 44], fill=RED)
    d.rectangle([x + 56, y + h - 62, x + 82, y + h - 44], fill=GOLD)
    d.rectangle([x + 86, y + h - 62, x + w - 6, y + h - 44], fill=BLUE)
    d.line([(x + 8, y + 14), (x + w - 8, y + 14)], fill=GREEN, width=3)
    d.polygon([(x + w - 8, y + 10), (x + w - 8, y + 18), (x + w - 16, y + 14)],
              fill=GREEN)


def art_arrest(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 224, 208))
    cx, cy = x + w // 2, y + h // 2
    for ox in (-26, 26):
        d.ellipse([cx + ox - 15, cy - 15, cx + ox + 15, cy + 15],
                  outline=INK, width=5)
    d.line([(cx - 12, cy), (cx + 12, cy)], fill=INK, width=5)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=INK)


def art_database(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 228, 240))
    cx, cy = x + w // 2, y + h // 2 - 4
    d.ellipse([cx - 26, cy - 26, cx + 26, cy - 12], fill=(90, 110, 150))
    d.rectangle([cx - 26, cy - 19, cx + 26, cy + 22], fill=(120, 140, 180))
    d.ellipse([cx - 26, cy + 8, cx + 26, cy + 22], fill=(90, 110, 150))
    d.line([(cx - 26, cy - 4), (cx + 26, cy - 4)], fill=WHITE, width=2)
    d.line([(cx - 26, cy + 8), (cx + 26, cy + 8)], fill=WHITE, width=2)
    d.rectangle([cx + 8, cy + 14, cx + 30, cy + 34], fill=GOLD, outline=INK, width=2)
    d.ellipse([cx + 15, cy + 19, cx + 23, cy + 27], outline=INK, width=2)


def art_rugby(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 238, 222))
    cx, cy = x + w // 2, y + h // 2
    d.ellipse([cx - 34, cy - 16, cx + 34, cy + 16], fill=(150, 60, 40))
    d.line([(cx - 34, cy), (cx + 34, cy)], fill=WHITE, width=3)
    d.line([(cx - 12, cy - 14), (cx - 12, cy + 14)], fill=WHITE, width=2)
    d.line([(cx + 12, cy - 14), (cx + 12, cy + 14)], fill=WHITE, width=2)
    for ox in (-40, 40):
        d.line([(cx + ox, y + 12), (cx + ox, y + h - 12)], fill=GOLD, width=4)


def art_football(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(220, 232, 220))
    cx, cy, r = x + w // 2, y + h // 2, 28
    circle(d, cx, cy, r, WHITE, outline=INK, width=2)
    d.polygon([(cx, cy - 10), (cx + 10, cy - 3), (cx + 6, cy + 9),
               (cx - 6, cy + 9), (cx - 10, cy - 3)], fill=INK)
    for ang in (0, 72, 144, 216, 288):
        import math
        ax = cx + 22 * math.cos(math.radians(ang - 90))
        ay = cy + 22 * math.sin(math.radians(ang - 90))
        d.ellipse([ax - 4, ay - 4, ax + 4, ay + 4], fill=INK)


def art_cricket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(228, 238, 210))
    cx, cy = x + w // 2, y + h // 2
    d.polygon([(cx - 34, cy + 30), (cx - 8, cy + 30), (cx + 22, cy - 34),
               (cx + 30, cy - 40), (cx + 34, cy - 26), (cx + 6, cy + 30)],
              fill=(210, 180, 120), outline=INK)
    d.rectangle([cx + 24, cy - 44, cx + 34, cy - 24], fill=(120, 80, 40))
    circle(d, cx - 30, cy - 26, 9, RED, outline=WHITE, width=2)
    d.line([(x + 8, y + h - 10), (x + w - 8, y + h - 10)], fill=GREEN, width=4)


def art_planet(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 26, 44))
    for i in range(10):
        px = x + 6 + (i * 29) % (w - 12)
        py = y + 6 + (i * 17) % (h - 12)
        d.ellipse([px, py, px + 2, py + 2], fill=WHITE)
    cx, cy = x + w // 2, y + h // 2
    d.ellipse([cx - 44, cy - 12, cx + 44, cy + 12], outline=GOLD, width=3)
    circle(d, cx, cy, 24, (200, 120, 60))
    circle(d, cx - 8, cy - 6, 5, (170, 90, 40))
    circle(d, cx + 10, cy + 8, 4, (170, 90, 40))


def art_ballot(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 228, 220))
    cx, cy = x + w // 2, y + h // 2
    d.polygon([(cx - 30, cy - 6), (cx + 30, cy - 6), (cx + 24, cy + 28),
               (cx - 24, cy + 28)], fill=(90, 110, 150))
    d.rectangle([cx - 34, cy - 12, cx + 34, cy - 4], fill=(70, 90, 130))
    d.polygon([(cx - 8, cy - 44), (cx + 14, cy - 44), (cx + 10, cy - 14),
               (cx - 12, cy - 14)], fill=WHITE, outline=INK, width=2)
    d.line([(cx - 4, cy - 30), (cx + 2, cy - 24), (cx + 10, cy - 38)],
           fill=RED, width=3)


def art_hospital(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 236, 232))
    cx, cy = x + w // 2, y + h // 2
    d.rectangle([cx - 30, cy - 20, cx + 30, cy + 28], fill=WHITE, outline=INK, width=2)
    d.rectangle([cx - 6, cy - 34, cx + 6, cy - 8], fill=RED)
    d.rectangle([cx - 13, cy - 27, cx + 13, cy - 15], fill=RED)
    d.rectangle([cx - 30, cy + 12, cx + 30, cy + 28], fill=(120, 160, 200))


def art_film(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 226, 214))
    cx, cy = x + w // 2, y + h // 2
    d.rectangle([cx - 32, cy - 18, cx + 32, cy + 20], fill=(60, 60, 70))
    circle(d, cx, cy, 13, (140, 180, 220), outline=WHITE, width=3)
    circle(d, cx, cy, 5, INK)
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
    """Draw a pictogram at any size: render on a 100x100 tile, then scale."""
    tile = Image.new("RGB", (100, 100), PAPER)
    td = ImageDraw.Draw(tile)
    ART[kind](td, 0, 0, 100, 100)
    tile = tile.resize((w, h), Image.LANCZOS)
    img.paste(tile, (x, y))

# --- panels -----------------------------------------------------------------

def lead_panel(img, d, box, num, art, headline, deck):
    x0, y0, x1, y1 = box
    frame(d, box)
    ax0, ay0, ax1, ay1 = x0 + 2, y0 + 2, x1 - 2, y0 + 96
    draw_art(img, art, ax0, ay0, ax1 - ax0, ay1 - ay0)
    d.line([(x0 + 2, y0 + 96), (x1 - 2, y0 + 96)], fill=EDGE, width=2)
    badge(d, x0 + 16, y0 + 16, num)
    fn = f(SANSB, 20)
    y = para(d, x0 + 10, y0 + 106, headline, fn, x1 - x0 - 20, 24)
    para(d, x0 + 10, y + 2, deck, f(SANS, 13), x1 - x0 - 20, 16, max_lines=3)


def mini_panel(img, d, box, num, art, headline, deck):
    x0, y0, x1, y1 = box
    frame(d, box)
    ix, iy = x0 + 8, y0 + 8
    draw_art(img, art, ix, iy, 62, 62)
    d.rectangle([ix, iy, ix + 62, iy + 62], outline=EDGE, width=1)
    badge(d, x0 + 14, y0 + 14, num, r=10)
    tx = x0 + 78
    fn = f(SANSB, 13)
    y = para(d, tx, y0 + 6, headline, fn, x1 - tx - 6, 16, max_lines=4)
    para(d, x0 + 8, y0 + 76, deck, f(SANS, 11), x1 - x0 - 16, 14, max_lines=4)


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
    d.text((x0 + 8, y0 + 4), "WHERE THE NEWS HAPPENED — PINS 1–13",
           font=f(SANSB, 12), fill=INK)
    mx0, my0 = x0 + 8, y0 + 24
    mw, mh = x1 - x0 - 16, y1 - y0 - 30
    for poly in CONTINENTS:
        pts = [project(lon, lat, mx0, my0, mw, mh) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_EDGE)
    for i, (lat, lon) in enumerate(PINS, start=1):
        px, py = project(lon, lat, mx0, my0, mw, mh)
        dx, dy = NUDGES[i - 1]
        badge(d, px + dx, py + dy, i, r=9)

# --- story data ---------------------------------------------------------------

LEADS = [
    ("blast",
     "Gulf widens: Iran claims new strikes on US Patriot radars",
     "Tehran says missiles and drones hit the radars at al-Riffa and Awali "
     "bases. Bahrain probes a Patriot interceptor crash."),
    ("bridge",
     "Zelensky: Crimea bridge strikes a 'fair response'",
     "Kyiv acted after 109 Russian aerial attacks on bridges, he says. "
     "Russia hits Lviv: 2 killed, 10 hurt."),
    ("climate",
     "COP31 deadlocked as fossil-fuel fight drags on",
     "Climate talks in Turkey run into overtime with no deal in sight, as "
     "countries split over the future of fossil fuels and finance."),
]

MINIS = [
    ("trade", "EU and Indonesia sign trade deal",
     "After ten years of talks, a pact to scrap 98.5% of tariffs."),
    ("arrest", "Mexico captures 'El Chapo Isidro'",
     "FBI Ten Most Wanted drug lord held after a shoot-out in Sinaloa; a $5m reward."),
    ("database", "FBI probes hack of crime database",
     "Apparent breach of the national criminal records system is investigated."),
    ("rugby", "England crush All Blacks 37-12",
     "Record Twickenham win, five tries; New Zealand lose twice in a row."),
    ("football", "Leeds stun Chelsea 4-1",
     "First win at Stamford Bridge since 1999; Okafor scores twice."),
    ("cricket", "India lead New Zealand by 118",
     "Day 3 stumps in Wellington: NZ 368, India 486/4. Nicholls 175, Rahul 136."),
    ("planet", "BepiColombo reaches Mercury",
     "Europe-Japan probe enters orbit after an eight-year voyage."),
    ("ballot", "Hong Kong votes for Election Committee",
     "About 5,700 voters choose members of the powerful body."),
    ("hospital", "Bolsonaro in ICU",
     "Brazil's jailed ex-president admitted with acute bowel obstruction."),
    ("film", "Spitting Image co-creator dies at 85",
     "Peter Fluck, satire puppet pioneer, dies at home in Cornwall."),
]

INDEX = [
    "Estonia to close border with Russia; Moscow decries 'new Iron Curtain'",
    "Trump and Xi meet in Shenzhen; Japan challenges ahead",
    "Judge approves $7.25bn Roundup weedkiller settlement",
    "Lock of George Washington's hair sells for $4,000",
    "US airlines warned of possible al-Qaeda-linked attacks before Thanksgiving",
    "House races still uncalled; Democratic majority in flux",
    "CMS proposes Medicare Advantage overhaul",
    "Trump signs Common Cents Act",
    "Quebecor's $31bn Telus bid would reshape Canadian telecom",
    "Mets' $400m Tarik Skubal offer headlines MLB hot stove",
    "Arsenal six points clear after 2-2 draw at Newcastle",
    "Man City held by Fulham; Anderson volley earns point",
    "Real Madrid beat Celta Vigo 2-1",
    "MI Emirates beat Desert Vipers by 52 runs in ILT20 opener",
    "French police sentenced over beating of producer Michel Zecler",
    "Miliband: EU deal not dependent on tuition fees",
    "Trafalgar Square Christmas tree felled in Norway",
    "Russia-bound ship attacked in Gulf of Finland; Ukraine likely behind it",
    "Teen gamer and mother helped rescue missing girl",
    "ANC fights to keep control of South Africa's key cities",
    "Nigerian youth and the election question",
    "FEMA office found infested with bed bugs; 1,000 staff sent home",
    "LA train heists net thieves $22m in goods, feds say",
    "Court pauses Iowa Army lead-azide blast; eyes Monday",
    "Thanksgiving storms may bring record coastal flooding to N. California",
]


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # masthead
    title = "The Daily Compass"
    tf = f(SERIFB, 58)
    d.text(((W - tw(d, title, tf)) / 2, 6), title, font=tf, fill=INK)
    rule(d, MARGIN, 78, W - MARGIN, 3)
    d.text((MARGIN, 84), "Sunday 22 November 2026",
           font=f(SANSB, 15), fill=INK)
    right = "38 verified stories — reported Sunday 22 Nov 2026"
    d.text((W - MARGIN - tw(d, right, f(SANS, 14)), 85), right,
           font=f(SANS, 14), fill=MUTED)
    rule(d, MARGIN, 106, W - MARGIN, 2)

    # lead row: 3 panels
    top = 114
    lw = (W - 2 * MARGIN - 2 * 10) // 3
    lh = 232
    for i, (art, head, deck) in enumerate(LEADS):
        x0 = MARGIN + i * (lw + 10)
        lead_panel(img, d, (x0, top, x0 + lw, top + lh), i + 1, art, head, deck)

    # mini rows: 2 x 5
    my = top + lh + 10
    mw = (W - 2 * MARGIN - 4 * 8) // 5
    mh = 148
    for r in range(2):
        for c in range(5):
            i = r * 5 + c
            art, head, deck = MINIS[i]
            x0 = MARGIN + c * (mw + 8)
            y0 = my + r * (mh + 8)
            mini_panel(img, d, (x0, y0, x0 + mw, y0 + mh), i + 4, art, head, deck)

    # map strip
    mapy = my + 2 * mh + 8 + 10
    draw_map(d, (MARGIN, mapy, W - MARGIN, mapy + 112))

    # index
    iy = mapy + 112 + 8
    d.text((MARGIN, iy), "ALSO TODAY — INDEX 14–38",
           font=f(SANSB, 14), fill=INK)
    rule(d, MARGIN, iy + 22, W - MARGIN, 2)
    fn = f(SANS, 12)
    colw = (W - 2 * MARGIN - 30) // 2
    y = iy + 28
    for j, item in enumerate(INDEX):
        col = 0 if j < 13 else 1
        row = j if j < 13 else j - 13
        x = MARGIN + col * (colw + 30)
        yy = y + row * 13.5
        d.text((x, yy), f"{14 + j}. {item}", font=fn, fill=INK)
    foot = y + 13 * 13.5 + 4
    rule(d, MARGIN, foot, W - MARGIN, 1)
    d.text((MARGIN, foot + 6),
           "Sources on file for every story. Claims are labelled as claims; "
           "market figures are Friday's closes, reported Sunday 22 November 2026.",
           font=f(SANS, 11), fill=MUTED)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, format="PNG", optimize=True)
    print(OUT)


if __name__ == "__main__":
    build()
