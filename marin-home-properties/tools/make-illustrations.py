#!/usr/bin/env python3
"""Marin Home Properties — illustration generator.

Every image slot in the "Marin Home Properties" design canvas is a photography
brief, not a photograph. Until the real photography is shot and licensed, the
site ships flat, layered SVG illustrations drawn in the canvas palette so that
no slot renders as an empty hatch swatch.

Run from this directory:

    python3 tools/make-illustrations.py

It rewrites every file in assets/img/. Nothing else in the site depends on it —
the site itself has no build step. To swap in real photography, replace the
file at the same path (any raster format works) and update the one <img> that
points at it.
"""

import math
import os
import random

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "img")

# --- Palette (carried over from the design canvas) --------------------------

INK        = "#171612"
INK_DEEP   = "#0D0C0A"
IVORY      = "#FCFAF6"
IVORY_WARM = "#F7F4EE"
GOLD       = "#CBB28E"
GOLD_LIGHT = "#DED0B8"
GOLD_DEEP  = "#8A6F42"
SAND       = "#E9E2D5"

# Ridge ramps, far to near.
RAMP_GOLDEN = ["#E3CDA8", "#CBB28E", "#A98F6B", "#7C6950", "#4A4134", "#2E2822"]
RAMP_DAY    = ["#DCD2BC", "#C4B99F", "#A29B85", "#777263", "#4C4841"]
RAMP_DUSK   = ["#B7A288", "#8E7C66", "#635648", "#3A332C", "#221E19"]


# --- Primitives -------------------------------------------------------------

def smooth(pts):
    """Quadratic-through-midpoints path across a list of sampled points."""
    d = "M%.1f,%.1f" % pts[0]
    for i in range(1, len(pts)):
        x0, y0 = pts[i - 1]
        x1, y1 = pts[i]
        d += " Q%.1f,%.1f %.1f,%.1f" % (x0, y0, (x0 + x1) / 2.0, (y0 + y1) / 2.0)
    d += " L%.1f,%.1f" % pts[-1]
    return d


def ridge(w, h, ybase, amp, seed, color, n=16, tilt=0.0, opacity=None):
    """One hill layer: a sine-sum ridgeline filled down to the bottom edge."""
    r = random.Random(seed)
    ph = [r.uniform(0, math.tau) for _ in range(3)]
    fr = [r.uniform(0.7, 1.2), r.uniform(2.0, 2.8), r.uniform(4.2, 5.4)]
    wt = [0.62, 0.26, 0.12]
    pts = []
    for i in range(n + 1):
        t = i / float(n)
        y = ybase + tilt * (t - 0.5) * h
        y -= amp * sum(wt[k] * math.sin(math.tau * fr[k] * t + ph[k]) for k in range(3))
        pts.append((t * w, y))
    d = smooth(pts) + " L%.1f,%.1f L0,%.1f Z" % (w, h, h)
    op = "" if opacity is None else ' opacity="%s"' % opacity
    return '<path d="%s" fill="%s"%s/>' % (d, color, op)


def sky(w, h, top, bottom):
    return (
        '<rect width="%d" height="%d" fill="url(#sky)"/>' % (w, h),
        '<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/>'
        "</linearGradient>" % (top, bottom),
    )


def sun(cx, cy, r, core, glow):
    return (
        '<circle cx="%.0f" cy="%.0f" r="%.0f" fill="url(#glow)"/>'
        '<circle cx="%.0f" cy="%.0f" r="%.0f" fill="%s" opacity=".85"/>'
        % (cx, cy, r * 4.6, cx, cy, r, core),
        '<radialGradient id="glow"><stop offset="0" stop-color="%s" stop-opacity=".55"/>'
        '<stop offset="1" stop-color="%s" stop-opacity="0"/></radialGradient>' % (glow, glow),
    )


def water(w, y0, y1, color, seed, highlight="#FCFAF6", bands=7):
    r = random.Random(seed)
    out = ['<rect x="0" y="%.1f" width="%d" height="%.1f" fill="%s"/>' % (y0, w, y1 - y0, color)]
    for _ in range(bands):
        y = r.uniform(y0 + 6, y1 - 4)
        x = r.uniform(-0.05, 0.55) * w
        ln = r.uniform(0.12, 0.42) * w
        out.append(
            '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity="%.2f" rx="1"/>'
            % (x, y, ln, r.uniform(1.4, 3.4), highlight, r.uniform(0.10, 0.30))
        )
    return "".join(out)


def conifer(x, base, hgt, color, tiers=4, spread=0.34):
    parts = ['<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>'
             % (x - hgt * 0.02, base - hgt * 0.12, hgt * 0.04, hgt * 0.12, color)]
    for i in range(tiers):
        t = i / float(tiers)
        top = base - hgt * (1 - t * 0.62)
        bot = base - hgt * (0.60 - t * 0.60) * 0.55 - hgt * 0.08
        half = hgt * spread * (0.42 + t * 0.58)
        parts.append('<path d="M%.1f,%.1f L%.1f,%.1f L%.1f,%.1f Z" fill="%s"/>'
                     % (x, top, x + half, bot, x - half, bot, color))
    return "".join(parts)


def broadleaf(x, base, r_, color):
    parts = ['<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>'
             % (x - r_ * 0.07, base - r_ * 0.9, r_ * 0.14, r_ * 0.9, color)]
    for dx, dy, rr in ((0, -1.35, 1.0), (-0.72, -0.95, 0.66), (0.72, -1.0, 0.7), (0, -0.72, 0.78)):
        parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>'
                     % (x + dx * r_, base + dy * r_, rr * r_, color))
    return "".join(parts)


def house(x, base, wd, color, roof=None, pitch=0.42, lit=None, windows=2):
    """A small silhouette house, used on hillsides and in town rows."""
    roof = roof or color
    ht = wd * 0.72
    parts = ['<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>'
             % (x, base - ht, wd, ht, color)]
    parts.append('<path d="M%.1f,%.1f L%.1f,%.1f L%.1f,%.1f Z" fill="%s"/>'
                 % (x - wd * 0.09, base - ht, x + wd / 2.0, base - ht - wd * pitch,
                    x + wd * 1.09, base - ht, roof))
    if lit:
        gap = wd / (windows + 1.0)
        for i in range(windows):
            parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity=".9"/>'
                         % (x + gap * (i + 1) - wd * 0.09, base - ht * 0.66,
                            wd * 0.18, ht * 0.3, lit))
    return "".join(parts)


def townrow(w, base, seed, body, roof, glass, awning=None, x0=0.0, x1=1.0,
            hmin=0.10, hmax=0.19, canvas_h=900):
    """A run of storefront silhouettes — the shared downtown motif."""
    r = random.Random(seed)
    out = []
    x = x0 * w
    end = x1 * w
    while x < end:
        bw = r.uniform(0.055, 0.105) * w
        bh = r.uniform(hmin, hmax) * canvas_h
        top = base - bh
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>'
                   % (x, top, bw, bh, body))
        if r.random() < 0.45:                       # pitched roof
            out.append('<path d="M%.1f,%.1f L%.1f,%.1f L%.1f,%.1f Z" fill="%s"/>'
                       % (x - bw * 0.06, top, x + bw / 2.0, top - bh * 0.34,
                          x + bw * 1.06, top, roof))
        else:                                       # parapet
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>'
                       % (x - bw * 0.05, top - bh * 0.09, bw * 1.10, bh * 0.09, roof))
        cols = r.randint(2, 3)
        gap = bw / (cols + 1.0)
        for i in range(cols):
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity=".85"/>'
                       % (x + gap * (i + 1) - bw * 0.10, top + bh * 0.20, bw * 0.20, bh * 0.26, glass))
        if awning and r.random() < 0.6:
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>'
                       % (x + bw * 0.06, base - bh * 0.40, bw * 0.88, bh * 0.08, awning))
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity=".55"/>'
                   % (x + bw * 0.12, base - bh * 0.26, bw * 0.76, bh * 0.26, glass))
        x += bw + r.uniform(0.006, 0.020) * w
    return "".join(out)


def skyline(w, x0, x1, base, seed, color, opacity=0.5, scale=1.0):
    r = random.Random(seed)
    out = []
    x = x0 * w
    end = x1 * w
    while x < end:
        bw = r.uniform(0.012, 0.030) * w
        bh = r.uniform(0.03, 0.115) * scale * 900
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity="%.2f"/>'
                   % (x, base - bh, bw, bh, color, opacity))
        x += bw + r.uniform(0.002, 0.010) * w
    return "".join(out)


def sailboat(x, base, s, hull, sail):
    return (
        '<path d="M%.1f,%.1f L%.1f,%.1f L%.1f,%.1f Z" fill="%s"/>'
        '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>'
        '<path d="M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f Z" fill="%s" opacity=".9"/>'
        % (x - s * 0.55, base, x + s * 0.55, base, x + s * 0.34, base + s * 0.16, hull,
           x - s * 0.02, base - s * 1.5, s * 0.045, s * 1.5, hull,
           x, base - s * 1.45, x + s * 0.62, base - s * 0.5, x, base, sail)
    )


def bridge(x0, x1, deck, tower_h, color, opacity=0.65):
    span = x1 - x0
    t1 = x0 + span * 0.28
    t2 = x0 + span * 0.72
    top = deck - tower_h
    out = ['<path d="M%.1f,%.1f L%.1f,%.1f" stroke="%s" stroke-width="3" opacity="%.2f" fill="none"/>'
           % (x0, deck, x1, deck, color, opacity)]
    for tx in (t1, t2):
        out.append('<rect x="%.1f" y="%.1f" width="4" height="%.1f" fill="%s" opacity="%.2f"/>'
                   % (tx - 2, top, tower_h, color, opacity))
    out.append('<path d="M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f Q%.1f,%.1f %.1f,%.1f" '
               'stroke="%s" stroke-width="2.2" fill="none" opacity="%.2f"/>'
               % (x0, deck - tower_h * 0.34, (x0 + t1) / 2, deck, t1, top,
                  (t1 + t2) / 2, deck + tower_h * 0.16, t2, top, color, opacity))
    out.append('<path d="M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f" stroke="%s" stroke-width="2.2" '
               'fill="none" opacity="%.2f"/>'
               % (t2, top, (t2 + x1) / 2, deck, x1, deck - tower_h * 0.34, color, opacity))
    return "".join(out)


def grain(w, h, seed, color=INK, count=140, opacity=0.05):
    """A whisper of tooth so the flat fills do not read as vector clip-art."""
    r = random.Random(seed)
    out = []
    for _ in range(count):
        out.append('<rect x="%.0f" y="%.0f" width="%.0f" height="%.0f" fill="%s" opacity="%.3f"/>'
                   % (r.uniform(0, w), r.uniform(0, h), r.uniform(1, 3), r.uniform(1, 3),
                      color, opacity * r.uniform(0.4, 1.6)))
    return "".join(out)


def write(name, w, h, defs, body, title, crop=None):
    """`crop` is an (x, y, w, h) window on the drawing, for framing a scene
    tighter than the box it was composed in. It must keep the target ratio."""
    vx, vy, vw, vh = crop if crop else (0, 0, w, h)
    doc = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="%d %d %d %d" width="%d" height="%d" '
        'preserveAspectRatio="xMidYMid slice" role="img" aria-label="%s">'
        "<title>%s</title><defs>%s</defs>%s</svg>"
    ) % (vx, vy, vw, vh, vw, vh, title, title, "".join(defs), body)
    path = os.path.join(OUT, name)
    with open(path, "w") as fh:
        fh.write(doc)
    return path


def facade(x, base, wd, body, roof, glass, seed, storeys=2, pitch=0.34,
           wing=None, chimney=True, trim=None, lit="#F3DBAC"):
    """A house elevation: main gable, optional side wing, window grid, door."""
    r = random.Random(seed)
    trim = trim or roof
    ht = wd * (0.40 + 0.20 * storeys)
    top = base - ht
    out = []

    if wing in ("left", "right"):
        ww = wd * 0.42
        wh = ht * 0.62
        wx = x - ww * 0.92 if wing == "left" else x + wd - ww * 0.08
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>'
                   % (wx, base - wh, ww, wh, body))
        out.append('<path d="M%.1f,%.1f L%.1f,%.1f L%.1f,%.1f Z" fill="%s"/>'
                   % (wx - ww * 0.08, base - wh, wx + ww / 2, base - wh - ww * 0.26,
                      wx + ww * 1.08, base - wh, roof))
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity=".92"/>'
                   % (wx + ww * 0.24, base - wh * 0.62, ww * 0.52, wh * 0.34,
                      lit if r.random() < 0.6 else glass))

    out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>'
               % (x, top, wd, ht, body))
    out.append('<path d="M%.1f,%.1f L%.1f,%.1f L%.1f,%.1f Z" fill="%s"/>'
               % (x - wd * 0.07, top, x + wd / 2, top - wd * pitch, x + wd * 1.07, top, roof))
    if chimney:
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>'
                   % (x + wd * 0.70, top - wd * pitch * 0.72, wd * 0.075, wd * pitch * 0.86, roof))

    cols = 3 if wd > 300 else 2
    for s in range(storeys):
        row_y = base - ht * (0.40 + 0.42 * s)
        gap = wd / (cols + 1.0)
        for i in range(cols):
            warm = lit if (r.random() < 0.62) else glass
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity=".94"/>'
                       % (x + gap * (i + 1) - wd * 0.085, row_y, wd * 0.17, ht * 0.19, warm))
            out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity=".55"/>'
                       % (x + gap * (i + 1) - wd * 0.005, row_y, wd * 0.008, ht * 0.19, trim))

    out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>'
               % (x + wd * 0.44, base - ht * 0.30, wd * 0.13, ht * 0.30, trim))
    out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="4" fill="%s" opacity=".8"/>'
               % (x + wd * 0.30, base - ht * 0.31, wd * 0.41, trim))
    return "".join(out)


# --- Scenes -----------------------------------------------------------------

def scene_hero():
    w, h = 1600, 1000
    body, sky_def = sky(w, h, "#F8E8CE", "#E7CCA4")
    s_body, s_def = sun(1210, 286, 56, "#FBEBCB", "#F0CE93")
    p = []
    p.append(body)
    p.append(s_body)
    p.append(ridge(w, h, 452, 46, 11, RAMP_GOLDEN[0], tilt=-0.02))
    p.append(skyline(w, 0.06, 0.40, 520, 21, "#8E7B62", 0.34, 0.62))
    p.append(ridge(w, h, 498, 40, 12, RAMP_GOLDEN[1], tilt=0.03))
    p.append(water(w, 520, 660, "#BCAB90", 13))
    p.append(bridge(120, 470, 546, 92, "#7E6C55", 0.5))
    p.append(ridge(w, h, 668, 58, 14, RAMP_GOLDEN[2], tilt=-0.03))
    # residential context on the near slope
    r = random.Random(15)
    for i in range(11):
        hx = 90 + i * 132 + r.uniform(-26, 26)
        hb = 726 + math.sin(i * 1.1) * 20 + r.uniform(-8, 8)
        p.append(house(hx, hb, r.uniform(46, 74), "#6F5F49", roof="#584B3A",
                       lit="#F0D9AE", windows=2))
    for i in range(9):
        p.append(conifer(150 + i * 176 + r.uniform(-40, 40), 748 + r.uniform(-14, 14),
                         r.uniform(70, 118), "#4E4334"))
    p.append(ridge(w, h, 830, 52, 16, RAMP_GOLDEN[4], tilt=0.02))
    for i in range(7):
        p.append(conifer(60 + i * 250 + r.uniform(-50, 50), 906 + r.uniform(-18, 18),
                         r.uniform(150, 232), "#241F1A"))
    p.append(ridge(w, h, 962, 34, 17, "#1C1815"))
    p.append(grain(w, h, 18))
    return write("hero-marin.svg", w, h, [sky_def, s_def], "".join(p),
                 "Illustration of an elevated Marin viewpoint at golden hour, the Bay and "
                 "hillside homes below")


def scene_sold_hero():
    w, h = 1600, 900
    body, sky_def = sky(w, h, "#8E7C67", "#D8BE9B")
    p = [body]
    p.append('<circle cx="1240" cy="620" r="300" fill="url(#dusk)"/>')
    dusk_def = ('<radialGradient id="dusk"><stop offset="0" stop-color="#F2D6A6" stop-opacity=".55"/>'
                '<stop offset="1" stop-color="#F2D6A6" stop-opacity="0"/></radialGradient>')
    p.append(ridge(w, h, 560, 54, 31, RAMP_DUSK[1], tilt=-0.02))
    p.append(ridge(w, h, 640, 40, 32, RAMP_DUSK[2], tilt=0.02))
    r = random.Random(33)
    for i in range(8):
        p.append(conifer(70 + i * 210 + r.uniform(-40, 40), 706 + r.uniform(-12, 12),
                         r.uniform(120, 200), "#2C261F"))
    p.append('<rect x="0" y="690" width="%d" height="%d" fill="#2A241D"/>' % (w, h - 690))
    p.append(facade(560, 742, 470, "#3D3529", "#251F1A", "#5C5142", 34,
                    storeys=2, pitch=0.30, wing="left", trim="#4A4033"))
    p.append(broadleaf(1300, 760, 96, "#241F19"))
    p.append(broadleaf(200, 780, 78, "#221D18"))
    p.append('<path d="M600,900 Q760,800 1010,762 L1160,762 Q880,812 760,900 Z" '
             'fill="#3A332A" opacity=".85"/>')
    p.append(grain(w, h, 35))
    return write("hero-recently-sold.svg", w, h, [sky_def, dusk_def], "".join(p),
                 "Illustration of a Marin residential exterior at dusk")


def scene_interior():
    w, h = 1200, 900
    p = []
    # The view beyond the glass
    p.append('<rect width="%d" height="%d" fill="url(#isky)"/>' % (w, h))
    isky = ('<linearGradient id="isky" x1="0" y1="0" x2="0" y2="1">'
            '<stop offset="0" stop-color="#F4E4CB"/><stop offset="1" stop-color="#E2CDAC"/>'
            "</linearGradient>")
    p.append(ridge(w, h, 330, 34, 41, "#D3BE9E"))
    p.append(skyline(w, 0.10, 0.62, 392, 42, "#9B8869", 0.42, 0.55))
    p.append(ridge(w, h, 376, 26, 43, "#C0A987"))
    p.append(water(w, 392, 520, "#AF9E85", 44))
    p.append(bridge(690, 1120, 424, 66, "#7C6A54", 0.45))
    p.append(ridge(w, h, 545, 32, 45, "#8C7A61"))
    r = random.Random(46)
    for i in range(6):
        p.append(conifer(70 + i * 210 + r.uniform(-30, 30), 596 + r.uniform(-10, 10),
                         r.uniform(60, 96), "#6B5B46"))
    p.append('<rect x="0" y="600" width="%d" height="30" fill="#7A6A53"/>' % w)
    # Room: ceiling, floor, glass wall mullions
    p.append('<rect x="0" y="0" width="%d" height="96" fill="#1D1A15"/>' % w)
    p.append('<rect x="0" y="630" width="%d" height="%d" fill="#C9B79C"/>' % (w, h - 630))
    p.append('<rect x="0" y="630" width="%d" height="10" fill="#8E7B62"/>' % w)
    for x in (0, 236, 472, 708, 944, 1186):
        p.append('<rect x="%.1f" y="96" width="14" height="534" fill="#1D1A15"/>' % x)
    p.append('<rect x="0" y="96" width="%d" height="12" fill="#1D1A15"/>' % w)
    p.append('<rect x="0" y="618" width="%d" height="14" fill="#1D1A15"/>' % w)
    p.append('<rect x="0" y="96" width="%d" height="534" fill="#FCFAF6" opacity=".07"/>' % w)
    # Furniture silhouettes
    p.append('<rect x="150" y="694" width="520" height="86" rx="10" fill="#6E6152"/>')
    p.append('<rect x="176" y="654" width="112" height="52" rx="10" fill="#7C6E5D"/>')
    p.append('<rect x="300" y="654" width="112" height="52" rx="10" fill="#7C6E5D"/>')
    p.append('<rect x="150" y="776" width="24" height="42" fill="#4B4237"/>')
    p.append('<rect x="646" y="776" width="24" height="42" fill="#4B4237"/>')
    p.append('<rect x="760" y="742" width="270" height="14" rx="7" fill="#5B5044"/>')
    p.append('<rect x="784" y="756" width="14" height="66" fill="#5B5044"/>')
    p.append('<rect x="992" y="756" width="14" height="66" fill="#5B5044"/>')
    p.append('<rect x="836" y="700" width="46" height="44" rx="4" fill="#8A6F42"/>')
    p.append('<path d="M100,900 L1100,900 L1100,868 L100,868 Z" fill="#B3A288" opacity=".55"/>')
    p.append(grain(w, h, 47))
    return write("interior-bay-view.svg", w, h, [isky], "".join(p),
                 "Illustration of a Marin living room with a wall of glass onto the Bay and the "
                 "San Francisco skyline")


def community(key, seed, motif, label, cfg):
    """One 4:3 community card. `cfg` carries the per-town variations."""
    w, h = 1200, 900
    body, sky_def = sky(w, h, cfg.get("skytop", "#F1E7D5"), cfg.get("skybot", "#E0D2B8"))
    defs = [sky_def]
    p = [body]
    r = random.Random(seed)
    band = cfg.get("water")

    if cfg.get("mountain"):
        p.append(ridge(w, h, cfg.get("mountain_y", 300), 118, seed + 1, "#CBBCA0", tilt=0.06))
    p.append(ridge(w, h, cfg.get("far_y", 396), 52, seed + 2, RAMP_DAY[0], tilt=-0.02))
    p.append(ridge(w, h, cfg.get("mid_y", 462), 44, seed + 3, RAMP_DAY[1], tilt=0.03))

    if band:
        p.append(water(w, band[0], band[1], "#A99A82", seed + 4))
        if cfg.get("skyline"):
            p.append(skyline(w, 0.04, 0.44, band[0], seed + 5, "#877457", 0.36, 0.5))

    if motif == "harbor":
        p.append(ridge(w, h, 700, 58, seed + 6, "#7E6E58", tilt=-0.04))
        for i in range(14):
            p.append(house(120 + i * 82 + r.uniform(-20, 20), 700 + r.uniform(-34, 26),
                           r.uniform(40, 62), "#63553F", roof="#4B4032", lit="#EFDAB2"))
        for i in range(7):
            p.append(sailboat(150 + i * 158 + r.uniform(-30, 30), band[1] - r.uniform(4, 40),
                              r.uniform(30, 52), "#3B332A", "#F6EFE1"))
        p.append('<rect x="0" y="812" width="%d" height="88" fill="#3B332A"/>' % w)
        for i in range(10):
            p.append('<rect x="%.0f" y="792" width="9" height="42" fill="#2B251E"/>'
                     % (60 + i * 124))

    elif motif == "island":
        p.append('<path d="M150,742 Q430,556 720,612 Q980,662 1200,712 L1200,900 L0,900 Z" '
                 'fill="#7B6B55"/>')
        for i in range(11):
            p.append(house(210 + i * 88 + r.uniform(-16, 16), 672 + r.uniform(-40, 38),
                           r.uniform(44, 70), "#5B4E3C", roof="#443A2D", lit="#F1DDB6"))
        for i in range(7):
            p.append(broadleaf(180 + i * 152 + r.uniform(-36, 36), 712 + r.uniform(-26, 26),
                               r.uniform(26, 46), "#4A4032"))
        p.append(water(w, 726, 900, "#93846C", seed + 8, bands=6))
        p.append(sailboat(300, 862, 46, "#332C24", "#F6EFE1"))
        p.append(sailboat(900, 826, 34, "#332C24", "#F6EFE1"))
        p.append(sailboat(620, 884, 40, "#332C24", "#F6EFE1"))

    elif motif == "redwoods":
        p.append(ridge(w, h, 618, 48, seed + 6, "#6E6250", tilt=0.02))
        p.append(townrow(w, 792, seed + 7, "#584C3C", "#413729", "#F2E0BC", awning="#8A6F42",
                         x0=0.04, x1=0.96, hmin=0.10, hmax=0.16))
        for i in range(10):
            p.append(conifer(24 + i * 134 + r.uniform(-26, 26), 816 + r.uniform(-10, 10),
                             r.uniform(200, 330), "#241F19", tiers=5, spread=0.22))
        p.append('<rect x="0" y="792" width="%d" height="108" fill="#2B251E"/>' % w)

    elif motif == "estate":
        p.append(ridge(w, h, 596, 54, seed + 6, "#6B5F4D", tilt=-0.02))
        for i in range(6):
            p.append(broadleaf(70 + i * 214 + r.uniform(-34, 34), 700 + r.uniform(-22, 22),
                               r.uniform(56, 92), "#3E362B"))
        p.append(house(486, 690, 168, "#584B3A", roof="#413729", lit="#F1DDB6", windows=3))
        p.append('<rect x="0" y="748" width="%d" height="152" fill="#332D24"/>' % w)
        for x in (352, 848):
            p.append('<rect x="%d" y="656" width="15" height="102" fill="#1E1A15"/>' % x)
            p.append('<rect x="%d" y="646" width="33" height="13" fill="#8A6F42"/>' % (x - 9))
        p.append('<path d="M367,700 L848,700" stroke="#8A6F42" stroke-width="3" opacity=".45"/>')
        p.append('<path d="M430,900 Q560,806 606,758 L700,758 Q650,816 780,900 Z" '
                 'fill="#4E4438" opacity=".9"/>')
        for i in range(5):
            p.append(broadleaf(120 + i * 262 + r.uniform(-30, 30), 880 + r.uniform(-14, 14),
                               r.uniform(32, 52), "#231E19"))

    elif motif == "hillside":
        p.append(ridge(w, h, 596, 56, seed + 6, "#7A6C57", tilt=0.03))
        for i in range(16):
            p.append(house(70 + i * 74 + r.uniform(-18, 18), 664 + r.uniform(-42, 34),
                           r.uniform(38, 58), "#5B4E3C", roof="#443A2D", lit="#F0DAB0"))
        for i in range(8):
            p.append(conifer(90 + i * 152 + r.uniform(-30, 30), 720 + r.uniform(-14, 14),
                             r.uniform(90, 150), "#332C23"))
        p.append(ridge(w, h, 790, 34, seed + 9, "#241F19"))
        for i in range(6):
            p.append(broadleaf(60 + i * 226 + r.uniform(-40, 40), 860 + r.uniform(-16, 16),
                               r.uniform(38, 62), "#1D1915"))

    else:  # every downtown variant
        t = cfg.get("town", {})
        base = t.get("base", 786)
        p.append(ridge(w, h, t.get("hill_y", 596), 52, seed + 6, "#7E7159", tilt=0.02))
        p.append(townrow(w, base, seed + 7, t.get("body", "#5B4E3C"), t.get("roof", "#443A2D"),
                         "#F2E0BC", awning=t.get("awning", "#8A6F42"),
                         x0=t.get("x0", 0.02), x1=t.get("x1", 0.98),
                         hmin=t.get("hmin", 0.12), hmax=t.get("hmax", 0.20)))
        if cfg.get("steeple"):
            sx = cfg["steeple"]
            p.append('<rect x="%d" y="%d" width="46" height="150" fill="#4A3F31"/>'
                     % (sx, base - 150))
            p.append('<path d="M%d,%d L%d,%d L%d,%d Z" fill="#2E2820"/>'
                     % (sx - 8, base - 150, sx + 23, base - 232, sx + 54, base - 150))
            p.append('<rect x="%d" y="%d" width="16" height="30" fill="#F2E0BC" opacity=".85"/>'
                     % (sx + 15, base - 132))
        if cfg.get("tower"):
            tx = cfg["tower"]
            p.append('<rect x="%d" y="%d" width="10" height="120" fill="#3D3428"/>' % (tx, base - 120))
            p.append('<rect x="%d" y="%d" width="10" height="120" fill="#3D3428"/>' % (tx + 54, base - 120))
            p.append('<rect x="%d" y="%d" width="76" height="46" rx="6" fill="#4A3F31"/>'
                     % (tx - 6, base - 176))
        n, rad, col = cfg.get("trees", (6, 60, "#2E281F"))
        for i in range(n):
            p.append(broadleaf(60 + i * (w - 120) / max(n - 1, 1) + r.uniform(-30, 30),
                               base + 8 + r.uniform(-6, 6), rad * r.uniform(0.82, 1.18), col))
        if motif == "waterfront":
            p.append('<rect x="0" y="%d" width="%d" height="%d" fill="#3B332A"/>'
                     % (base, w, 44))
            p.append(water(w, base + 44, 900, "#8E7F68", seed + 11, bands=6))
            for i in range(9):
                p.append('<rect x="%.0f" y="%d" width="9" height="46" fill="#2B251E"/>'
                         % (50 + i * 136, base + 28))
            p.append(sailboat(280, 878, 40, "#2B251E", "#F6EFE1"))
            p.append(sailboat(880, 856, 32, "#2B251E", "#F6EFE1"))
        elif cfg.get("creek"):
            p.append('<rect x="0" y="%d" width="%d" height="%d" fill="#332C24"/>'
                     % (base, w, 62))
            p.append(water(w, base + 62, 900, "#8E8069", seed + 12, bands=5))
            p.append('<path d="M0,%d L%d,%d" stroke="#241F19" stroke-width="10" opacity=".8"/>'
                     % (base + 62, w, base + 62))
        else:
            p.append('<rect x="0" y="%d" width="%d" height="%d" fill="#332C24"/>'
                     % (base, w, 900 - base))
            p.append('<path d="M0,%d L%d,%d" stroke="#8A6F42" stroke-width="3" '
                     'stroke-dasharray="34 26" opacity=".5"/>' % (base + 58, w, base + 58))

    p.append(grain(w, h, seed + 20))
    return write("community-%s.svg" % key, w, h, defs, "".join(p), label,
                 crop=cfg.get("crop", (200, 300, 800, 600)))


def scene_sale(n, seed, cfg):
    w, h = 1600, 1000
    body, sky_def = sky(w, h, cfg["skytop"], cfg["skybot"])
    p = [body]
    r = random.Random(seed)
    p.append(ridge(w, h, 452, 60, seed + 1, cfg["far"], tilt=-0.02))
    p.append(ridge(w, h, 552, 46, seed + 2, cfg["mid"], tilt=0.03))
    for i in range(7):
        p.append(conifer(70 + i * 246 + r.uniform(-50, 50), 660 + r.uniform(-14, 14),
                         r.uniform(120, 210), cfg["tree"]))
    p.append('<rect x="0" y="646" width="%d" height="%d" fill="%s"/>' % (w, h - 646, cfg["ground"]))
    p.append(facade(cfg["x"], 812, cfg["w"], cfg["body"], cfg["roof"], cfg["glass"], seed + 3,
                    storeys=cfg["storeys"], pitch=cfg["pitch"], wing=cfg["wing"],
                    chimney=cfg["chimney"], trim=cfg["trim"]))
    p.append(broadleaf(cfg["treex"], 846, cfg["treer"], cfg["tree2"]))
    p.append('<rect x="0" y="836" width="%d" height="10" fill="%s" opacity=".5"/>'
             % (w, cfg["trim"]))
    p.append('<path d="M%d,1000 Q%d,900 %d,842 L%d,842 Q%d,908 %d,1000 Z" fill="%s" opacity=".85"/>'
             % (cfg["x"] + 40, cfg["x"] + 130, cfg["x"] + 170, cfg["x"] + 300,
                cfg["x"] + 300, cfg["x"] + 430, cfg["path"]))
    for i in range(9):
        p.append('<rect x="%.0f" y="%.0f" width="26" height="16" rx="6" fill="%s" opacity=".7"/>'
                 % (r.uniform(0, w), r.uniform(858, 986), cfg["hedge"]))
    p.append(grain(w, h, seed + 9))
    return write("sale-%02d.svg" % n, w, h, [sky_def], "".join(p),
                 "Illustration of a Marin home, placeholder for sold property %02d" % n)


def scene_portrait():
    w, h = 1200, 1500
    p = ['<rect width="%d" height="%d" fill="url(#psky)"/>' % (w, h)]
    psky = ('<linearGradient id="psky" x1="0" y1="0" x2="0.6" y2="1">'
            '<stop offset="0" stop-color="#2A241D"/><stop offset="1" stop-color="#12100D"/>'
            "</linearGradient>")
    p.append(ridge(w, h, 1180, 70, 71, "#241F19", tilt=0.03))
    p.append(ridge(w, h, 1300, 50, 72, "#1A1713"))
    p.append('<rect x="70" y="70" width="%d" height="%d" fill="none" stroke="%s" '
             'stroke-width="2" opacity=".45"/>' % (w - 140, h - 140, GOLD))
    p.append('<rect x="%d" y="%d" width="26" height="26" fill="%s" transform="rotate(45 %d %d)"/>'
             % (w / 2 - 13, 470, GOLD, w / 2, 483))
    p.append('<text x="%d" y="800" text-anchor="middle" font-family="Georgia,serif" '
             'font-size="250" font-weight="500" fill="%s" letter-spacing="14">SC</text>'
             % (w / 2, GOLD_LIGHT))
    p.append('<rect x="%d" y="862" width="240" height="1.5" fill="%s" opacity=".6"/>'
             % (w / 2 - 120, GOLD))
    p.append('<text x="%d" y="936" text-anchor="middle" font-family="Helvetica,Arial,sans-serif" '
             'font-size="30" letter-spacing="9" fill="#9B927F">SUSAN COLEMAN</text>' % (w / 2))
    p.append('<text x="%d" y="990" text-anchor="middle" font-family="Helvetica,Arial,sans-serif" '
             'font-size="21" letter-spacing="7" fill="#6E675A">PORTRAIT TO BE SUPPLIED</text>'
             % (w / 2))
    p.append(grain(w, h, 73, color="#FCFAF6", count=200, opacity=0.035))
    return write("susan-coleman.svg", w, h, [psky], "".join(p),
                 "Placeholder card for the Susan Coleman portrait")


COMMUNITIES = [
    ("san-rafael", 100, "town",
     "Illustration of downtown San Rafael storefronts on Fourth Street",
     dict(skytop="#F3EAD9", skybot="#E2D5BC", steeple=760, trees=(5, 38, "#2E281F"),
          town=dict(hmin=0.15, hmax=0.25, base=792))),
    ("mill-valley", 130, "redwoods",
     "Illustration of downtown Mill Valley beneath the redwoods",
     dict(skytop="#EFE8D9", skybot="#DCD3BC", far_y=360, mid_y=440)),
    ("tiburon", 160, "waterfront",
     "Illustration of the Tiburon shoreline with Angel Island and San Francisco beyond",
     dict(skytop="#F4E9D3", skybot="#E4D3B4", water=(452, 640), skyline=True, far_y=372,
          mid_y=430, trees=(4, 32, "#2A241C"),
          town=dict(hmin=0.09, hmax=0.15, base=744, hill_y=560, x0=0.04, x1=0.96))),
    ("san-anselmo", 190, "town",
     "Illustration of downtown San Anselmo along San Anselmo Avenue",
     dict(skytop="#F0E7D6", skybot="#DED0B6", creek=True, trees=(7, 40, "#2A241C"),
          town=dict(hmin=0.11, hmax=0.17, base=768, hill_y=572, awning="#9C7F4C"))),
    ("larkspur", 220, "town",
     "Illustration of historic downtown Larkspur on Magnolia Avenue",
     dict(skytop="#F5ECDA", skybot="#E3D6BB", trees=(5, 50, "#241F18"),
          town=dict(hmin=0.13, hmax=0.19, base=780, x0=0.06, x1=0.94, roof="#3B3227"))),
    ("novato", 250, "town",
     "Illustration of downtown Novato's walkable Grant Avenue district",
     dict(skytop="#F4ECDC", skybot="#E6D9C0", far_y=430, mid_y=498, tower=880,
          trees=(6, 34, "#332C22"),
          town=dict(hmin=0.08, hmax=0.13, base=756, hill_y=628, x0=0.03, x1=0.97))),
    ("sausalito", 280, "harbor",
     "Illustration of the Sausalito harbour, hillside homes and San Francisco across the Bay",
     dict(skytop="#F2E8D5", skybot="#E2D2B6", water=(470, 700), skyline=True)),
    ("belvedere", 310, "island",
     "Illustration of the Belvedere island peninsula and lagoon",
     dict(skytop="#F5EAD6", skybot="#E5D5B8", water=(452, 620), skyline=True, far_y=372,
          mid_y=432)),
    ("ross", 340, "estate",
     "Illustration of a leafy Ross residential lane and estate gates",
     dict(skytop="#EFE7D6", skybot="#DCD0B6")),
    ("kentfield", 370, "hillside",
     "Illustration of Kentfield's tree-lined streets below Mount Tamalpais",
     dict(skytop="#F1E8D6", skybot="#DFD2B8", mountain=True, mountain_y=286,
          crop=(150, 225, 900, 675))),
    ("corte-madera", 400, "town",
     "Illustration of the Corte Madera town centre with Mount Tamalpais behind",
     dict(skytop="#F2E9D8", skybot="#E0D3B9", mountain=True, mountain_y=252, far_y=444,
          crop=(150, 225, 900, 675),
          mid_y=506, trees=(8, 30, "#2C261E"),
          town=dict(hmin=0.07, hmax=0.12, base=764, hill_y=636, x0=0.05, x1=0.95))),
    ("fairfax", 430, "town",
     "Illustration of Fairfax's small-town main street",
     dict(skytop="#EEE6D4", skybot="#DACCB2", far_y=344, mid_y=420, trees=(9, 36, "#231E18"),
          town=dict(hmin=0.09, hmax=0.14, base=774, hill_y=548, x0=0.08, x1=0.92,
                    awning="#7C6440"))),
]

SALES = [
    dict(skytop="#F3E7D2", skybot="#E1D2B6", far="#D2C6AC", mid="#B0A288", tree="#4E4535",
         ground="#6E6350", body="#E7DCC7", roof="#4A4034", glass="#8D8168", trim="#8A6F42",
         tree2="#372F26", treex=1330, treer=104, x=470, w=560, storeys=2, pitch=0.32,
         wing="left", chimney=True, path="#8F8269", hedge="#4E4535"),
    dict(skytop="#EFE3CE", skybot="#DACAAE", far="#CCC0A6", mid="#A89A80", tree="#463D2F",
         ground="#65593F", body="#4C4032", roof="#2E2820", glass="#8A7C63", trim="#B49A72",
         tree2="#312A21", treex=300, treer=118, x=560, w=600, storeys=2, pitch=0.24,
         wing="right", chimney=False, path="#857755", hedge="#463D2F"),
    dict(skytop="#F5EAD6", skybot="#E5D6BA", far="#D6CAB0", mid="#B4A78D", tree="#514736",
         ground="#736750", body="#D9CBB1", roof="#6B5B45", glass="#948567", trim="#8A6F42",
         tree2="#3B3228", treex=1220, treer=96, x=420, w=520, storeys=1, pitch=0.18,
         wing="right", chimney=True, path="#948669", hedge="#514736"),
    dict(skytop="#EEE2CC", skybot="#D8C8AC", far="#C9BCA2", mid="#A2957B", tree="#413929",
         ground="#5F5540", body="#8B7A5E", roof="#3A3128", glass="#C7B694", trim="#DED0B8",
         tree2="#2E271F", treex=1380, treer=88, x=520, w=580, storeys=2, pitch=0.40,
         wing=None, chimney=True, path="#7E7157", hedge="#413929"),
    dict(skytop="#F2E6D1", skybot="#DFD0B4", far="#D0C4AA", mid="#ADA086", tree="#4A4132",
         ground="#6A5F4A", body="#F0E7D4", roof="#57493A", glass="#8E8268", trim="#8A6F42",
         tree2="#352E25", treex=260, treer=110, x=600, w=540, storeys=2, pitch=0.36,
         wing="left", chimney=True, path="#8C7F65", hedge="#4A4132"),
    dict(skytop="#E9DCC6", skybot="#CFBE9F", far="#C2B69C", mid="#9B8E74", tree="#3D3527",
         ground="#584E3B", body="#3F3729", roof="#241F19", glass="#D9C69F", trim="#CBB28E",
         tree2="#2A241C", treex=1300, treer=100, x=480, w=600, storeys=2, pitch=0.20,
         wing="left", chimney=False, path="#756A51", hedge="#3D3527"),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    made = [scene_hero(), scene_sold_hero(), scene_interior(), scene_portrait()]
    for key, seed, motif, label, cfg in COMMUNITIES:
        made.append(community(key, seed, motif, label, cfg))
    for i, cfg in enumerate(SALES, start=1):
        made.append(scene_sale(i, 500 + i * 17, cfg))
    for pth in made:
        print(os.path.relpath(pth, os.path.join(OUT, "..", "..")))


if __name__ == "__main__":
    main()
