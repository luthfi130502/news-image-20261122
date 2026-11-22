#!/usr/bin/env python3
"""Generate /output/entry.png — 'The World in One Day', Sunday 22 November 2026.

A single-image newspaper poster: 36 dated news stories from seven regions,
a stylised location map, a UTC timeline, and a day-in-numbers strip.
Written from scratch for the news-image-20261122 competition.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- data
# Every story is dated 22 November 2026 (or the weekend's reporting of it)
# and carries the outlet that reported it. Headlines/decks are my own
# summaries of the day's reporting, gathered by web search on 22 Nov 2026.
LEAD = {
    "headline": "Three leaders, one table \u2014 then a night of missiles",
    "deck": ("Trump, Xi and Putin meet in Shenzhen with no breakthrough on Ukraine; "
             "hours later Russia fires 400 drones and 110 missiles, and a missile "
             "lands in Poland."),
    "source": "CNN \u00b7 Reuters \u00b7 The Independent \u2014 19\u201321 Nov",
}

# (region, category, headline, deck, source)
STORIES = [
    # ---- North America (7)
    ("NA", "tech", "Trump warns firms over AI data centres abroad",
     "US companies building centres overseas face a \u2018tremendous tax\u2019, he says.",
     "LinkedIn Weekend Buzz \u2014 21 Nov"),
    ("NA", "markets", "Nasdaq wipes out all its 2026 gains",
     "Tech rout deepens: Nasdaq -5.3% on Friday, S&P 500 into correction as Nvidia slides 14%.",
     "LinkedIn Weekend Buzz \u2014 21 Nov"),
    ("NA", "security", "US airlines warned of Thanksgiving terror threat",
     "Possible al-Qaeda-linked attacks flagged ahead of the holiday travel rush.",
     "Times of India \u2014 22 Nov"),
    ("NA", "politics", "Vance refuses to back Trump\u2019s Iran strikes",
     "Vice-president declines public endorsement despite the president\u2019s demand.",
     "ARY News \u2014 22 Nov"),
    ("NA", "politics", "Trump: an Iran deal \u2018could last 20 years\u2019",
     "President claims the US removed Tehran\u2019s leadership twice and eyes \u2018ultimate regime change\u2019.",
     "Times of India \u2014 22 Nov"),
    ("NA", "crime", "\u2018El Chapo Isidro\u2019 arrested in Mexico raid",
     "Alleged cartel boss captured; ensuing violence in Sinaloa leaves 11 dead.",
     "Times of India \u2014 22 Nov"),
    ("NA", "crime", "19 years for plot to kill Sikh separatist",
     "Indian man sentenced in the US over the Pannun murder conspiracy.",
     "ARY News \u2014 22 Nov"),
    # ---- South America (3)
    ("SA", "quake", "M6.9 earthquake shakes Peru\u2019s Andes",
     "Strong tremor hits the highlands; no damage or casualties immediately reported.",
     "Daily Jagran \u2014 22 Nov"),
    ("SA", "health", "Bolsonaro admitted to ICU",
     "Brazil\u2019s jailed ex-president hospitalised with an acute bowel obstruction.",
     "Times of India \u2014 22 Nov"),
    ("SA", "disaster", "\u2018We lost everything\u2019: Brazil storm town clears rubble",
     "Residents pick through wreckage after a deadly storm.",
     "Arab News \u2014 22 Nov"),
    # ---- Europe (7)
    ("EU", "conflict", "Russian missile lands in Poland",
     "NATO jets scrambled and Patriots activated as debris falls during the barrage on Ukraine.",
     "CNN \u00b7 The Independent \u2014 21 Nov"),
    ("EU", "politics", "Estonia to shut its border with Russia",
     "Road crossings close for at least six months; Moscow decries a \u2018new Iron Curtain\u2019.",
     "The Independent \u2014 22 Nov"),
    ("EU", "conflict", "Drones hit Russian cargo ship in the Baltic",
     "Finland tightens security; Ukraine is seen as likely behind the strike.",
     "Times of India \u2014 22 Nov"),
    ("EU", "climate", "COP31 deadlocked over fossil fuels",
     "Antalya talks go into overtime as fossil-fuel language is stripped from drafts.",
     "BBC \u2014 22 Nov"),
    ("EU", "protest", "French march for a sixth weekend",
     "Protesters rally over living costs and public services.",
     "Arab News \u2014 22 Nov"),
    ("EU", "politics", "Belgium faces air-traffic shutdown",
     "National strike on Monday threatens to ground flights.",
     "Arab News \u2014 22 Nov"),
    ("EU", "crime", "France probes Depardieu over gang-rape claim",
     "Actor and an author under investigation, French prosecutors say.",
     "Times of India \u2014 22 Nov"),
    # ---- Middle East (6)
    ("ME", "conflict", "Iran strikes US air base in Kuwait",
     "Tehran targets Bahrain too as Gulf attacks widen.",
     "Daily Jagran \u2014 22 Nov"),
    ("ME", "conflict", "Two tankers hit off the coast of Oman",
     "Iran says a vessel struck a mine east of Hormuz; one ADNOC crew member missing.",
     "ARY News \u00b7 TOI \u2014 22 Nov"),
    ("ME", "conflict", "Bahrain: Iran hit a civilian industrial site",
     "Strike sparks a fire; a Patriot interceptor crash is also under investigation.",
     "Arab News \u2014 22 Nov"),
    ("ME", "diplomacy", "162 nations back Palestinian self-determination",
     "UN General Assembly committee adopts the resolution 162\u20138.",
     "Middle East Monitor \u2014 20 Nov"),
    ("ME", "politics", "Eisenkot invites Likud into coalition talks",
     "Ex-Israeli PM backs Eisenkot for premier; he says he will not serve under Netanyahu.",
     "India Today \u2014 22 Nov"),
    ("ME", "politics", "Lebanon\u2019s Aoun: end occupation and interference",
     "President demands an end to Israeli occupation and Iranian meddling.",
     "Arab News \u2014 22 Nov"),
    # ---- Africa (3)
    ("AF", "disaster", "24 dead as boat capsizes in Nigeria",
     "Vessel carrying mourners to a funeral overturns.",
     "Arab News \u2014 22 Nov"),
    ("AF", "energy", "Libya loses $30.8m to pipeline blockade",
     "Armed group has blocked an oil pipeline for more than 20 days.",
     "Arab News \u2014 22 Nov"),
    ("AF", "health", "Ebola fight hampered in DR Congo",
     "Geography, violence and distrust slow the response, aid groups warn.",
     "Arab News \u2014 22 Nov"),
    # ---- Asia (7)
    ("AS", "diplomacy", "Japan to train with live fire in India \u2014 a first",
     "Japanese forces will use Indian facilities for live-fire drills.",
     "Daily Jagran \u2014 22 Nov"),
    ("AS", "politics", "Modi opens Nitish Setu bridge in Bihar",
     "New crossing links Patna and Vaishali districts.",
     "Daily Jagran \u2014 22 Nov"),
    ("AS", "disaster", "Cyclone Akvan cancels 14 flights in Ranchi",
     "Storm disrupts air travel in eastern India.",
     "Daily Jagran \u2014 22 Nov"),
    ("AS", "markets", "Crude futures slide more than 3%",
     "Oil falls to Rs 7,842 a barrel as Gulf tensions jolt energy markets.",
     "Daily Jagran \u2014 22 Nov"),
    ("AS", "security", "Pakistan kills 15 militants in Balochistan",
     "Security forces destroy hideouts in a sweep, officials say.",
     "Arab News \u2014 22 Nov"),
    ("AS", "politics", "Chahal joins BJP, gets OBC Morcha role",
     "Cricketer\u2019s political entry lands him a party post the same day.",
     "NDTV \u2014 22 Nov"),
    ("AS", "politics", "Air India extends Jeddah suspension to 24 Nov",
     "Flights to the Saudi city stay grounded amid regional tensions.",
     "Daily Jagran \u2014 22 Nov"),
    # ---- Oceania (2)
    ("OC", "sport", "Cummins keeps Australia\u2019s Test captaincy",
     "Cricket Australia gives him \u2018unanimous support\u2019 to stay on.",
     "Daily Jagran \u2014 22 Nov"),
    ("OC", "sport", "India face a windy Wellington Test",
     "Confident India meet New Zealand in the first Test of the tour.",
     "PW.live \u2014 22 Nov"),
]

REGIONS = [
    ("NA", "NORTH AMERICA", (31, 78, 121)),
    ("SA", "SOUTH AMERICA", (46, 125, 50)),
    ("EU", "EUROPE", (106, 27, 154)),
    ("ME", "MIDDLE EAST", (178, 106, 0)),
    ("AF", "AFRICA", (198, 40, 40)),
    ("AS", "ASIA", (0, 105, 92)),
    ("OC", "OCEANIA", (230, 81, 0)),
]
REGION = {k: (name, color) for k, name, color in REGIONS}

# (lon, lat, region) — where the day's stories happened
DOTS = [
    (114.05, 22.55, "AS"), (30.52, 50.45, "EU"), (33.39, 47.91, "EU"),
    (21.01, 52.23, "EU"), (24.75, 59.44, "EU"), (21.0, 58.0, "EU"),
    (30.71, 36.88, "EU"), (2.35, 48.86, "EU"), (4.35, 50.85, "EU"),
    (47.98, 29.38, "ME"), (50.59, 26.23, "ME"), (56.5, 26.5, "ME"),
    (34.47, 31.5, "ME"), (35.5, 33.89, "ME"), (-75.0, -10.0, "SA"),
    (-47.88, -15.79, "SA"), (-107.4, 24.8, "NA"), (-77.04, 38.9, "NA"),
    (-74.0, 40.7, "NA"), (77.21, 28.61, "AS"), (85.14, 25.6, "AS"),
    (85.31, 23.34, "AS"), (139.69, 35.68, "AS"), (174.78, -41.29, "OC"),
    (151.21, -33.87, "OC"), (3.38, 6.45, "AF"), (13.19, 32.9, "AF"),
    (15.27, -4.32, "AF"), (73.05, 33.68, "AS"), (39.17, 21.49, "AS"),
]

# (hour UTC, label) — as reported through the day
TIMELINE = [
    (0.5, "COP31 into overtime"),
    (2.5, "Tankers hit off Oman"),
    (6.5, "M6.9 quake, Peru"),
    (9.0, "Estonia to shut border"),
    (12.0, "UN backs Palestine 162\u20138"),
    (15.0, "Bolsonaro in ICU"),
    (18.0, "Zelensky: Trump told Europe"),
    (21.0, "Nigeria boat toll: 24"),
]

STATS = [
    ("-5.3%", "Nasdaq on Friday \u2014 all of its 2026 gains wiped out"),
    ("400 + 110", "drones and missiles fired at Ukraine in one night"),
    ("M6.9", "earthquake shakes Peru\u2019s Andes"),
    ("162\u20138", "nations back Palestinian self-determination at the UN"),
]

# ---------------------------------------------------------------- fonts
def font(name, size):
    paths = {
        "serif_b": "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf",
        "serif": "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf",
        "sans_b": "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
        "sans": "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        "sans_i": "/usr/share/fonts/truetype/noto/NotoSans-Italic.ttf",
    }
    try:
        return ImageFont.truetype(paths[name], size)
    except OSError:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)

def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns list of lines."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

# ---------------------------------------------------------------- icons
def draw_icon(d, x, y, s, cat, color):
    """Small pictogram tile, drawn with plain shapes."""
    d.rounded_rectangle([x, y, x + s, y + s], radius=s // 5, fill=color)
    ink = (255, 255, 255)
    cx, cy = x + s / 2, y + s / 2
    w = 2.5
    if cat == "conflict":  # burst
        for a in range(0, 360, 45):
            r = math.radians(a)
            d.line([cx + 5 * math.cos(r), cy + 5 * math.sin(r),
                    cx + 15 * math.cos(r), cy + 15 * math.sin(r)], fill=ink, width=3)
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=ink)
    elif cat == "climate":  # sun
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], outline=ink, width=3)
        for a in range(0, 360, 45):
            r = math.radians(a)
            d.line([cx + 10 * math.cos(r), cy + 10 * math.sin(r),
                    cx + 14 * math.cos(r), cy + 14 * math.sin(r)], fill=ink, width=3)
    elif cat == "quake":  # zigzag crack
        pts = [(x + 8, y + 8), (x + 18, y + 20), (x + 13, y + 24),
               (x + 24, y + 34), (x + 36, y + 40)]
        d.line(pts, fill=ink, width=3, joint="curve")
    elif cat == "markets":  # rising bars
        for i, h in enumerate((8, 13, 18)):
            bx = x + 9 + i * 11
            d.rectangle([bx, y + s - 8 - h, bx + 7, y + s - 8], fill=ink)
    elif cat == "politics":  # columned building
        d.polygon([(x + 7, y + 14), (cx, y + 7), (x + s - 7, y + 14)], fill=ink)
        for i in range(3):
            bx = x + 10 + i * 11
            d.rectangle([bx, y + 17, bx + 5, y + s - 9], fill=ink)
        d.rectangle([x + 8, y + s - 9, x + s - 8, y + s - 6], fill=ink)
    elif cat == "sport":  # ball
        d.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], outline=ink, width=3)
        d.arc([cx - 11, cy - 11, cx + 11, cy + 11], 200, 340, fill=ink, width=3)
    elif cat == "tech":  # chip
        d.rectangle([x + 13, y + 13, x + s - 13, y + s - 13], outline=ink, width=3)
        for i in range(3):
            d.line([x + 13 + i * 8, y + 8, x + 13 + i * 8, y + 13], fill=ink, width=2)
            d.line([x + 13 + i * 8, y + s - 13, x + 13 + i * 8, y + s - 8], fill=ink, width=2)
            d.line([x + 8, y + 13 + i * 8, x + 13, y + 13 + i * 8], fill=ink, width=2)
            d.line([x + s - 13, y + 13 + i * 8, x + s - 8, y + 13 + i * 8], fill=ink, width=2)
    elif cat == "health":  # cross
        d.rectangle([cx - 4, y + 9, cx + 4, y + s - 9], fill=ink)
        d.rectangle([x + 9, cy - 4, x + s - 9, cy + 4], fill=ink)
    elif cat == "energy":  # flame
        d.polygon([(cx, y + 8), (cx + 9, y + 22), (cx + 6, y + 32),
                   (cx - 6, y + 32), (cx - 9, y + 22)], fill=ink)
    elif cat == "diplomacy":  # linked rings
        d.ellipse([x + 8, cy - 8, x + 24, cy + 8], outline=ink, width=3)
        d.ellipse([x + s - 24, cy - 8, x + s - 8, cy + 8], outline=ink, width=3)
    elif cat == "disaster":  # wave
        pts = []
        for i in range(25):
            pts.append((x + 7 + i * 1.3, cy + 6 * math.sin(i * 0.55)))
        d.line(pts, fill=ink, width=3, joint="curve")
        pts2 = [(px, py + 12) for px, py in pts]
        d.line(pts2, fill=ink, width=3, joint="curve")
    elif cat == "crime":  # magnifier
        d.ellipse([x + 9, y + 9, x + 29, y + 29], outline=ink, width=3)
        d.line([x + 26, y + 26, x + 37, y + 37], fill=ink, width=4)
    elif cat == "security":  # shield
        d.polygon([(cx, y + 8), (x + s - 9, y + 13), (x + s - 9, y + 24),
                   (cx, y + s - 8), (x + 9, y + 24), (x + 9, y + 13)], outline=ink, width=3)
    elif cat == "protest":  # megaphone
        d.polygon([(x + 9, y + 18), (x + 26, y + 10), (x + 26, y + 32), (x + 9, y + 26)], fill=ink)
        d.rectangle([x + 26, y + 14, x + 31, y + 28], fill=ink)
        d.line([x + 13, y + 28, x + 13, y + 36], fill=ink, width=3)
    else:  # dot
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=ink)

# ---------------------------------------------------------------- layout
W = 2400
M = 90                      # margin
CW = W - 2 * M              # content width
PAPER = (246, 241, 231)
INK = (22, 21, 19)
MUTED = (107, 101, 92)
RULE = (22, 21, 19)
PANEL = (255, 253, 246)

def main():
    img = Image.new("RGB", (W, 5800), PAPER)
    d = ImageDraw.Draw(img)
    y = 64

    # ---- masthead
    f_kick = font("sans_b", 30)
    kick = "O N E   I M A G E   \u00b7   T H E   W H O L E   D A Y"
    d.text((W / 2, y), kick, font=f_kick, fill=MUTED, anchor="ma")
    y += 52
    f_title = font("serif_b", 148)
    d.text((W / 2, y), "THE WORLD IN ONE DAY", font=f_title, fill=INK, anchor="ma")
    y += 168
    f_sub = font("sans", 42)
    d.text((W / 2, y), "Sunday, 22 November 2026  \u00b7  36 stories  \u00b7  seven regions",
           font=f_sub, fill=INK, anchor="ma")
    y += 70
    d.line([M, y, W - M, y], fill=RULE, width=5)
    y += 8
    d.line([M, y, W - M, y], fill=RULE, width=2)
    y += 34

    # ---- day in numbers
    f_stat_n = font("serif_b", 66)
    f_stat_l = font("sans", 24)
    tile_w = (CW - 3 * 24) // 4
    top = y
    for i, (num, label) in enumerate(STATS):
        x0 = M + i * (tile_w + 24)
        d.rounded_rectangle([x0, top, x0 + tile_w, top + 172], radius=14,
                            fill=PANEL, outline=(205, 196, 178), width=2)
        d.text((x0 + tile_w / 2, top + 14), num, font=f_stat_n, fill=(150, 30, 30), anchor="ma")
        for j, ln in enumerate(wrap(d, label, f_stat_l, tile_w - 36)):
            d.text((x0 + tile_w / 2, top + 92 + j * 28), ln, font=f_stat_l,
                   fill=MUTED, anchor="ma")
    y = top + 172 + 36

    # ---- map panel
    f_sec = font("sans_b", 34)
    f_note = font("sans_i", 24)
    d.text((M, y), "WHERE IT HAPPENED", font=f_sec, fill=INK, anchor="la")
    d.text((W - M, y), "STYLISED MAP \u2014 NOT TO SCALE", font=f_note, fill=MUTED, anchor="ra")
    y += 52
    map_top = y
    map_h = 400
    d.rounded_rectangle([M, map_top, W - M, map_top + map_h], radius=16,
                        fill=(232, 238, 240), outline=(205, 196, 178), width=2)
    mx0, my0 = M + 30, map_top + 24
    mw, mh = 1420, map_h - 48
    # graticule
    for gx in range(0, 361, 30):
        gx_px = mx0 + gx / 360 * mw
        d.line([gx_px, my0, gx_px, my0 + mh], fill=(210, 218, 220), width=1)
    for gy in range(-60, 91, 30):
        gy_px = my0 + (90 - gy) / 180 * mh
        d.line([mx0, gy_px, mx0 + mw, gy_px], fill=(210, 218, 220), width=1)
    # rough continent blobs (stylised land)
    land = (198, 205, 196)
    blobs = [
        [(150, 60), (300, 30), (430, 55), (420, 130), (330, 190), (260, 220), (180, 180), (120, 110)],   # N America
        [(330, 240), (420, 230), (450, 290), (400, 350), (350, 330), (320, 280)],                        # S America
        [(700, 55), (800, 40), (850, 90), (800, 130), (720, 110)],                                       # Europe
        [(700, 140), (800, 135), (860, 190), (830, 280), (760, 300), (710, 220)],                        # Africa
        [(860, 45), (1050, 25), (1250, 45), (1330, 110), (1200, 180), (1000, 190), (900, 130)],          # Asia
        [(1250, 260), (1360, 250), (1390, 290), (1300, 310)],                                            # Oceania
    ]
    for b in blobs:
        pts = [(mx0 + px / 1440 * mw, my0 + py / 380 * mh) for px, py in b]
        d.polygon(pts, fill=land)
    # dots
    for lon, lat, reg in DOTS:
        px = mx0 + (lon + 180) / 360 * mw
        py = my0 + (90 - lat) / 180 * mh
        col = REGION[reg][1]
        d.ellipse([px - 11, py - 11, px + 11, py + 11], fill=col, outline=(255, 255, 255), width=3)
    # legend
    lx = M + 30 + mw + 60
    f_leg = font("sans_b", 30)
    f_leg2 = font("sans", 28)
    d.text((lx, map_top + 30), "STORIES BY REGION", font=f_leg, fill=INK)
    ly = map_top + 86
    for code, name, color in REGIONS:
        n = sum(1 for s in STORIES if s[0] == code)
        d.rounded_rectangle([lx, ly, lx + 34, ly + 34], radius=8, fill=color)
        d.text((lx + 48, ly - 2), f"{name}", font=f_leg2, fill=INK)
        d.text((W - M - 30, ly - 2), str(n), font=f_leg, fill=INK, anchor="ra")
        ly += 44
    y = map_top + map_h + 36

    # ---- timeline strip
    d.text((M, y), "THE DAY UNFOLDS \u2014 AS REPORTED, UTC", font=f_sec, fill=INK, anchor="la")
    d.text((W - M, y), "SUNDAY 22 NOVEMBER 2026", font=f_note, fill=MUTED, anchor="ra")
    y += 52
    tl_top = y
    tl_x0, tl_x1 = M + 40, W - M - 40
    tl_y = tl_top + 66
    d.line([tl_x0, tl_y, tl_x1, tl_y], fill=INK, width=4)
    f_hr = font("sans_b", 24)
    for h in range(0, 25, 3):
        hx = tl_x0 + h / 24 * (tl_x1 - tl_x0)
        d.line([hx, tl_y - 10, hx, tl_y + 10], fill=INK, width=3)
        d.text((hx, tl_y + 18), f"{h:02d}:00", font=f_hr, fill=MUTED, anchor="ma")
    f_tl = font("sans", 23)
    for i, (hour, label) in enumerate(TIMELINE):
        hx = tl_x0 + hour / 24 * (tl_x1 - tl_x0)
        d.ellipse([hx - 8, tl_y - 8, hx + 8, tl_y + 8], fill=(150, 30, 30),
                  outline=(255, 255, 255), width=2)
        if i % 2 == 0:
            d.text((hx, tl_y - 46), label, font=f_tl, fill=INK, anchor="ma")
        else:
            d.text((hx, tl_y + 54), label, font=f_tl, fill=INK, anchor="ma")
    y = tl_top + 66 + 92 + 30

    # ---- lead feature
    d.line([M, y, W - M, y], fill=RULE, width=5)
    y += 26
    f_lead_k = font("sans_b", 28)
    d.text((M, y), "THE LEAD STORY", font=f_lead_k, fill=(150, 30, 30))
    y += 44
    f_lead = font("serif_b", 72)
    lead_lines = wrap(d, LEAD["headline"], f_lead, CW - 560)
    ly3 = y
    for ln in lead_lines:
        d.text((M, ly3), ln, font=f_lead, fill=INK)
        ly3 += 84
    f_deck = font("sans", 32)
    deck_lines = wrap(d, LEAD["deck"], f_deck, CW - 560)
    ly3 += 12
    for ln in deck_lines:
        d.text((M, ly3), ln, font=f_deck, fill=(60, 56, 50))
        ly3 += 42
    ly3 += 10
    f_src = font("sans_i", 26)
    d.text((M, ly3), LEAD["source"], font=f_src, fill=MUTED)
    # pictogram: three leaders at one table
    px0 = W - M - 500
    py0 = y - 6
    d.rounded_rectangle([px0, py0, px0 + 500, py0 + 300], radius=16,
                        fill=PANEL, outline=(205, 196, 178), width=2)
    d.text((px0 + 250, py0 + 18), "SHENZHEN \u00b7 19 NOV", font=font("sans_b", 26),
           fill=MUTED, anchor="ma")
    cols = [((31, 78, 121), "US"), ((198, 40, 40), "CN"), ((106, 27, 154), "RU")]
    for i, (col, tag) in enumerate(cols):
        cxp = px0 + 90 + i * 160
        d.ellipse([cxp - 52, py0 + 70, cxp + 52, py0 + 174], fill=col)
        d.text((cxp, py0 + 106), tag, font=font("sans_b", 34), fill=(255, 255, 255), anchor="mm")
    d.ellipse([px0 + 70, py0 + 205, px0 + 430, py0 + 245], outline=INK, width=4)
    d.text((px0 + 250, py0 + 258), "400 drones \u00b7 110 missiles that night",
           font=font("sans_b", 26), fill=(150, 30, 30), anchor="ma")
    y = max(ly3 + 44, py0 + 300) + 30

    # ---- region bands
    f_band = font("sans_b", 32)
    f_head = font("sans_b", 33)
    f_deck2 = font("sans", 26)
    f_src2 = font("sans_i", 23)
    n_total = 0
    for code, name, color in REGIONS:
        items = [s for s in STORIES if s[0] == code]
        n_total += len(items)
        d.line([M, y, W - M, y], fill=RULE, width=3)
        y += 14
        d.rounded_rectangle([M, y, M + 46, y + 46], radius=9, fill=color)
        d.text((M + 23, y + 6), code, font=font("sans_b", 24), fill=(255, 255, 255), anchor="ma")
        d.text((M + 62, y + 2), name, font=f_band, fill=INK)
        d.text((W - M, y + 2), f"{len(items)} stories", font=f_band, fill=MUTED, anchor="ra")
        y += 62
        col_w = (CW - 50) // 2
        rows = [items[i:i + 2] for i in range(0, len(items), 2)]
        for row in rows:
            row_h = 0
            heights = []
            for it in row:
                _, cat, head, deck, src = it
                hl = wrap(d, head, f_head, col_w - 66)
                dl = wrap(d, deck, f_deck2, col_w - 66)
                h = max(52, len(hl) * 40 + len(dl) * 32 + 30)
                heights.append(h)
                row_h = max(row_h, h)
            for ci, it in enumerate(row):
                _, cat, head, deck, src = it
                x0 = M + ci * (col_w + 50)
                draw_icon(d, x0, y + 4, 46, cat, color)
                tx = x0 + 62
                ly4 = y
                for ln in wrap(d, head, f_head, col_w - 66):
                    d.text((tx, ly4), ln, font=f_head, fill=INK)
                    ly4 += 40
                for ln in wrap(d, deck, f_deck2, col_w - 66):
                    d.text((tx, ly4), ln, font=f_deck2, fill=(60, 56, 50))
                    ly4 += 32
                d.text((tx, ly4 + 2), src, font=f_src2, fill=MUTED)
            y += row_h + 18
        y += 12

    # ---- footer / date check
    d.line([M, y, W - M, y], fill=RULE, width=5)
    y += 22
    f_foot = font("sans", 26)
    f_footb = font("sans_b", 26)
    d.text((M, y), "DATE CHECK", font=f_footb, fill=(150, 30, 30))
    foot = ("Every story above is dated Sunday 22 November 2026 in the reporting "
            "of its source (weekend reporting, 20\u201322 Nov, is marked). "
            f"{n_total + 1} stories in total \u2014 the lead plus {n_total} across seven regions.")
    for j, ln in enumerate(wrap(d, foot, f_foot, CW - 210)):
        d.text((M + 210, y + j * 34), ln, font=f_foot, fill=INK)
    y += max(34, 34 * len(wrap(d, foot, f_foot, CW - 210))) + 26
    d.text((M, y), "Sources: BBC \u00b7 Reuters \u00b7 CNN \u00b7 The Independent \u00b7 Arab News \u00b7 "
                   "Times of India \u00b7 NDTV \u00b7 ARY News \u00b7 Daily Jagran \u00b7 India Today \u00b7 "
                   "Middle East Monitor \u00b7 PW.live",
           font=font("sans_i", 23), fill=MUTED)
    y += 40
    d.text((W / 2, y), "\u2014  THE WORLD IN ONE DAY  \u00b7  22 NOVEMBER 2026  \u2014",
           font=font("sans_b", 26), fill=MUTED, anchor="ma")
    y += 56

    img = img.crop((0, 0, W, y + 20))
    out1 = "/output/entry.png"
    out2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    os.makedirs("/output", exist_ok=True)
    img.save(out1)
    img.save(out2)
    print(f"saved {out1} and {out2}  size={img.size}  stories={n_total + 1}")

if __name__ == "__main__":
    main()
