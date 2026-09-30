#!/usr/bin/env python3
"""Profile banner v3 for github.com/sjelodari — the field of "why" becomes the name.

  0.0 s   a cloud of points (the problem space) fades in on the left
  0.4 s   threads draw toward one node
  0.7 s   ~500 points leave the cloud on arcs and assemble, left to right,
          into the letterforms of the name
  2.5 s   the points resolve into solid type; the line runs from the node
          into the underline; the positioning line and meta settle in
  idle    every ~3.5 s one point travels a thread into the node, the node
          answers, and a pulse runs along the underline. Nothing else moves.

All type is converted to outlines (Inter, JetBrains Mono — SIL OFL, see fonts/),
so it renders identically on every OS. Respects prefers-reduced-motion.

Needs:  pip install fonttools uharfbuzz
Run:    python3 generate_v3.py      → v3-dark.svg, v3-light.svg (daily via Actions, for the date)
"""
import math
import random
from datetime import date
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.pointInsidePen import PointInsidePen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).parent
W, H = 1010, 270
FX, FY = 342, 160           # convergence node; FY is the underline's y
TXT_X = 376
FIELD = (40, 36, 300, 240)  # x0, y0, x1, y1 of the problem space

THEMES = {
    "dark": dict(
        BG0="#0d1117", BG1="#101722", GRID="rgba(148,163,184,0.05)",
        ACCENT="#7aa2ff", DOT="#9aa8bd", TXT="#e6edf3", BODY="#c3cdd9",
        MUT="#7d8896", LINE="rgba(148,163,184,0.15)", GLOW=1.6, PULSE="#dbe5ff"),
    "light": dict(
        BG0="#ffffff", BG1="#f6f8fa", GRID="rgba(31,35,40,0.035)",
        ACCENT="#3b63d9", DOT="#7b8594", TXT="#1f2328", BODY="#3d444d",
        MUT="#59636e", LINE="rgba(31,35,40,0.12)", GLOW=0.9, PULSE="#1d3a9e"),
}

# ---------------------------------------------------------------- copy
EYEBROW = "why → how"
NAME = "Saber Jelodari"
LINE1 = "I turn research into products people can use — and buy."
META = "AI Specialist · Technical Product Management · Bayreuth, Germany"
SYNC = f"updated {date.today().isoformat()}"

# ---------------------------------------------------------------- motion tokens
EASE_OUT = "cubic-bezier(.22,1,.36,1)"
EASE_IN_OUT = "cubic-bezier(.65,0,.35,1)"
SPRING = "cubic-bezier(.34,1.56,.64,1)"
T_THREADS, T_NODE = 0.4, 0.75
T_FLY, FLY = 0.7, 1.2               # swarm departs / flight time
SETTLE = 0.9                        # after landing: hold, then dissolve into type
T_SOLID = 2.6                       # copy below the name follows the last letter
T_LINE = 2.3
IDLE_START = 4.2
TRAVEL, BEAT, N_PARTICLES = 1.6, 3.5, 3
CYCLE = BEAT * N_PARTICLES
DOT_PITCH = 3.9                     # spacing of points inside the letters (px)


# ---------------------------------------------------------------- type → outlines
class Face:
    def __init__(self, path, **axes):
        self.tt = TTFont(path)
        self.gs = self.tt.getGlyphSet(location=axes)
        self.order = self.tt.getGlyphOrder()
        self.upem = self.tt["head"].unitsPerEm
        blob = hb.Blob.from_file_path(str(path))
        self.hb = hb.Font(hb.Face(blob))
        self.hb.set_variations(axes)

    def shape(self, text, size, tracking=0.0):
        """[(glyphName, x_font, y_font)], advance_px, scale"""
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hb, buf, {"kern": True, "liga": True})
        s = size / self.upem
        out, pen = [], 0
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            out.append((self.order[info.codepoint], pen + pos.x_offset, pos.y_offset))
            pen += pos.x_advance + tracking / s
        return out, pen * s, s

    def path(self, text, x, y, size, tracking=0.0):
        glyphs, adv, s = self.shape(text, size, tracking)
        svg = SVGPathPen(self.gs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
        for name, gx, gy in glyphs:
            self.gs[name].draw(TransformPen(svg, (s, 0, 0, -s, x + gx * s, y - gy * s)))
        return svg.getCommands(), adv

    def glyph_paths(self, text, x, y, size, tracking=0.0):
        """One outline per glyph (empty for spaces), so letters can resolve one by one."""
        glyphs, _, s = self.shape(text, size, tracking)
        out = []
        for name, gx, gy in glyphs:
            svg = SVGPathPen(self.gs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
            self.gs[name].draw(TransformPen(svg, (s, 0, 0, -s, x + gx * s, y - gy * s)))
            out.append(svg.getCommands())
        return out

    def points(self, text, x, y, size, pitch, tracking=0.0):
        """Hex-grid points inside the filled letterforms: (x, y, glyph index) in SVG px."""
        glyphs, _, s = self.shape(text, size, tracking)
        pts = []
        for gi, (name, gx, gy) in enumerate(glyphs):
            g = self.gs[name]
            bp = _bounds(self.gs, g)
            if not bp:
                continue
            x0, y0, x1, y1 = bp
            step = pitch / s
            row = 0
            yy = y0 + step * 0.5
            while yy < y1:
                xx = x0 + step * (0.25 + 0.5 * (row % 2))
                while xx < x1:
                    pen = PointInsidePen(self.gs, (xx, yy))
                    g.draw(pen)
                    if pen.getResult():
                        pts.append((x + (gx + xx) * s, y - (gy + yy) * s, gi))
                    xx += step
                yy += step * math.sqrt(3) / 2
                row += 1
        return pts


def _bounds(gs, glyph):
    from fontTools.pens.boundsPen import BoundsPen
    bp = BoundsPen(gs)
    glyph.draw(bp)
    return bp.bounds


# ---------------------------------------------------------------- the field
def field(rng):
    fx0, fy0, fx1, fy1 = FIELD
    dots, threads, links, pts = [], [], [], []
    for _ in range(44):
        x, y = rng.uniform(fx0, fx1), rng.uniform(fy0, fy1)
        pts.append((x, y))
        d_in = 0.05 + (x - fx0) / (fx1 - fx0) * 0.35 + rng.uniform(0, 0.12)
        dots.append(dict(x=x, y=y, r=rng.uniform(1.1, 2.6), accent=rng.random() < 0.2,
                         cls=rng.choice(["dotA", "dotA", "dotB"]), d_in=d_in,
                         d_br=rng.uniform(0, 5), dur=rng.uniform(4.5, 8)))
        if rng.random() < 0.5:
            threads.append(dict(x=x, y=y, cx=(x + FX) / 2 + rng.uniform(10, 40),
                                op=rng.uniform(0.07, 0.15), d_in=T_THREADS + d_in * 0.8))
    linked = set()
    for i, (x1, y1) in enumerate(pts):
        for j, (x2, y2) in enumerate(pts):
            if j <= i or (i, j) in linked or len(links) >= 10:
                continue
            d2 = (x1 - x2) ** 2 + (y1 - y2) ** 2
            if 400 < d2 < 2900 and rng.random() < 0.5:
                linked.add((i, j))
                links.append((x1, y1, x2, y2))
    return dots, threads, links


def swarm(rng, targets, name_x0, name_x1):
    """Each target point gets a start in the cloud and a flight delay."""
    fx0, fy0, fx1, fy1 = FIELD
    out = []
    for tx, ty, gi in targets:
        # gaussian cloud centred in the field, so the start reads as one mass
        sx = min(fx1, max(fx0, rng.gauss((fx0 + fx1) / 2, (fx1 - fx0) / 4.2)))
        sy = min(fy1, max(fy0, rng.gauss((fy0 + fy1) / 2, (fy1 - fy0) / 4.2)))
        k = (tx - name_x0) / (name_x1 - name_x0)          # letters fill left → right
        out.append(dict(tx=tx, ty=ty, gi=gi, dx=sx - tx, dy=sy - ty,
                        d=T_FLY + k * 0.7 + rng.uniform(0, 0.22),
                        accent=rng.random() < 0.12))
    return out


def carriers(threads):
    by_y = sorted(range(len(threads)), key=lambda k: threads[k]["y"])
    n = len(by_y)
    return [by_y[int(n * f)] for f in (0.08, 0.5, 0.92)][:N_PARTICLES]


# ---------------------------------------------------------------- svg
def build(t, L, dots, threads, links, flock):
    A = t["ACCENT"]
    k_arrive = TRAVEL / CYCLE
    first_arrival = IDLE_START + TRAVEL
    how_len = TXT_X - (FX + 4)
    rule_w = L["rule_w"]
    kb = lambda s: f"{s / BEAT:.4f}"

    dot_svg = "\n      ".join(
        f'<g class="in" style="animation-delay:{d["d_in"]:.2f}s">'
        f'<circle class="{d["cls"]}" style="animation-delay:{d["d_br"]:.1f}s;'
        f'animation-duration:{d["dur"]:.1f}s" cx="{d["x"]:.0f}" cy="{d["y"]:.0f}" '
        f'r="{d["r"]:.1f}" fill="{A if d["accent"] else t["DOT"]}"/></g>'
        for d in dots)

    thread_svg = "\n      ".join(
        f'<path id="t{i}" class="draw" pathLength="1" style="animation-delay:{th["d_in"]:.2f}s" '
        f'd="M{th["x"]:.0f} {th["y"]:.0f} Q {th["cx"]:.0f} {th["y"]:.0f}, {FX} {FY}" '
        f'fill="none" stroke="{t["DOT"]}" stroke-width="0.8" opacity="{th["op"]:.2f}"/>'
        for i, th in enumerate(threads))

    link_svg = "\n      ".join(
        f'<line x1="{a:.0f}" y1="{b:.0f}" x2="{c:.0f}" y2="{d:.0f}" '
        f'stroke="{t["DOT"]}" stroke-width="0.6" opacity="0.09"/>' for a, b, c, d in links)

    # nested x / y groups with different easings → every point flies an arc
    flock_svg = "\n      ".join(
        f'<g class="sx" style="--x:{p["dx"]:.1f}px;--y:{p["dy"]:.1f}px;--d:{p["d"]:.2f}s">'
        f'<g class="sy"><circle class="sd" cx="{p["tx"]:.1f}" cy="{p["ty"]:.1f}" r="1.25"'
        f'{f" fill=\"{A}\"" if p["accent"] else ""}/></g></g>'
        for p in flock)

    particle_svg = "\n      ".join(
        f'''<circle r="1.9" fill="{A}" filter="url(#soft)" opacity="0">
        <animateMotion begin="{IDLE_START + n * BEAT:.2f}s" dur="{CYCLE}s" repeatCount="indefinite"
          calcMode="spline" keyPoints="0;1;1" keyTimes="0;{k_arrive:.4f};1"
          keySplines="0.45 0 0.55 1;0 0 1 1"><mpath xlink:href="#t{k}"/></animateMotion>
        <animate attributeName="opacity" begin="{IDLE_START + n * BEAT:.2f}s" dur="{CYCLE}s"
          repeatCount="indefinite" values="0;0.95;0.95;0;0"
          keyTimes="0;0.02;{k_arrive - 0.01:.4f};{k_arrive:.4f};1"/>
      </circle>''' for n, k in enumerate(carriers(threads)))

    idle_response = f'''<circle cx="{FX}" cy="{FY}" r="3.2" fill="{A}" opacity="0" filter="url(#soft)">
        <animate attributeName="r" begin="{first_arrival:.2f}s" dur="{BEAT}s" repeatCount="indefinite"
          values="3.2;6;3.2;3.2" keyTimes="0;{kb(0.18)};{kb(0.6)};1"/>
        <animate attributeName="opacity" begin="{first_arrival:.2f}s" dur="{BEAT}s" repeatCount="indefinite"
          values="0;0.55;0;0" keyTimes="0;{kb(0.12)};{kb(0.6)};1"/>
      </circle>
      <line x1="{FX + 4}" y1="{FY}" x2="{TXT_X + rule_w}" y2="{FY}" stroke="{t["PULSE"]}" stroke-width="2"
            filter="url(#softline)" opacity="0.75" stroke-dasharray="44 {how_len + rule_w + 100}" stroke-dashoffset="44">
        <animate attributeName="stroke-dashoffset" begin="{first_arrival + 0.05:.2f}s" dur="{BEAT}s"
          repeatCount="indefinite" values="44;{-(how_len + rule_w)};{-(how_len + rule_w)}" keyTimes="0;{kb(1.3)};1"
          calcMode="spline" keySplines="0.35 0 0.45 1;0 0 1 1"/>
      </line>'''

    landed = {}
    for p in flock:
        landed[p["gi"]] = max(landed.get(p["gi"], 0), p["d"] + FLY)
    letters_svg = "\n    ".join(
        f'<path class="solid" style="animation-delay:{landed[i] - 0.15:.2f}s" d="{d}"/>'
        for i, d in enumerate(L["letters"]) if d and i in landed)

    rise = lambda d, body: f'<g class="rise" style="animation-delay:{d:.2f}s">{body}</g>'

    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="ttl">
  <title id="ttl">{NAME} — {LINE1}</title>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{t["BG0"]}"/><stop offset="1" stop-color="{t["BG1"]}"/>
    </linearGradient>
    <linearGradient id="how" x1="{FX}" y1="0" x2="{TXT_X}" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{t["DOT"]}" stop-opacity="0.35"/><stop offset="1" stop-color="{A}"/>
    </linearGradient>
    <linearGradient id="rule" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{A}" stop-opacity="0.95"/><stop offset="1" stop-color="{A}" stop-opacity="0"/>
    </linearGradient>
    <filter id="soft" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="{t["GLOW"]}" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="softline" filterUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">
      <feGaussianBlur stdDeviation="{t["GLOW"]}" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <pattern id="grid" width="56" height="56" patternUnits="userSpaceOnUse">
      <path d="M56 0H0V56" fill="none" stroke="{t["GRID"]}" stroke-width="1"/>
    </pattern>
    <clipPath id="card"><rect width="{W}" height="{H}" rx="14"/></clipPath>
  </defs>
  <style>
    /* intro — plays once; base styles are the final frame */
    .in    {{ animation: fadeIn .6s {EASE_OUT} backwards; }}
    .draw  {{ stroke-dasharray: 1; animation: draw .9s {EASE_OUT} backwards; }}
    .node  {{ transform-origin: {FX}px {FY}px; animation: ignite .6s {SPRING} {T_NODE}s backwards; }}
    .how   {{ transform-origin: {FX}px {FY}px; animation: grow .4s {EASE_OUT} {T_LINE}s backwards; }}
    .rule  {{ transform-origin: {TXT_X}px {FY}px; animation: grow .9s {EASE_OUT} {T_LINE + .3:.2f}s backwards; }}
    .rise  {{ animation: rise .7s {EASE_OUT} backwards; }}
    .solid {{ fill: {t["TXT"]}; animation: fadeIn .55s ease-out backwards; }}

    /* the swarm: x eases in-out, y eases out — together, an arc; each point
       lands, holds, then dissolves as its letter turns solid */
    .sx    {{ animation: fx {FLY}s {EASE_IN_OUT} var(--d) backwards; }}
    .sy    {{ animation: fy {FLY}s cubic-bezier(.3,.9,.3,1) var(--d) backwards; }}
    .sd    {{ fill: {t["TXT"]}; opacity: 0; animation: land {FLY + SETTLE:.2f}s linear var(--d) backwards; }}

    @keyframes fadeIn   {{ from {{ opacity: 0; }} }}
    @keyframes draw     {{ from {{ stroke-dashoffset: 1; }} to {{ stroke-dashoffset: 0; }} }}
    @keyframes ignite   {{ from {{ transform: scale(0); opacity: 0; }} }}
    @keyframes grow     {{ from {{ transform: scaleX(0); }} }}
    @keyframes rise     {{ from {{ opacity: 0; transform: translateY(6px); }} }}
    @keyframes fx       {{ from {{ transform: translateX(var(--x)); }} to {{ transform: none; }} }}
    @keyframes fy       {{ from {{ transform: translateY(var(--y)); }} to {{ transform: none; }} }}
    @keyframes land     {{ 0% {{ opacity: 0; }} 8% {{ opacity: .5; }} {100 * FLY / (FLY + SETTLE):.0f}% {{ opacity: 1; }} {100 * (FLY + .45 * SETTLE) / (FLY + SETTLE):.0f}% {{ opacity: .9; }} 100% {{ opacity: 0; }} }}

    .dotA {{ animation: breatheA 6s ease-in-out infinite; }}
    .dotB {{ animation: breatheB 6s ease-in-out infinite; }}
    @keyframes breatheA {{ 0%,100% {{ opacity: .22; }} 50% {{ opacity: .45; }} }}
    @keyframes breatheB {{ 0%,100% {{ opacity: .40; }} 50% {{ opacity: .70; }} }}

    @media (prefers-reduced-motion: reduce) {{
      * {{ animation: none !important; }}
      .idle, .flock {{ display: none; }}
    }}
  </style>

  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>
    <rect width="{W}" height="{H}" fill="url(#grid)"/>

    <!-- why: the problem space -->
    <g class="in" style="animation-delay:.5s">
      {link_svg}
    </g>
    <g>
      {thread_svg}
    </g>
    <g>
      {dot_svg}
    </g>

    <!-- the insight node -->
    <g class="node">
      <circle cx="{FX}" cy="{FY}" r="7" fill="{A}" opacity="0.14"/>
      <circle cx="{FX}" cy="{FY}" r="3.2" fill="{A}" filter="url(#soft)"/>
    </g>

    <!-- how: one line, executed, becoming the underline -->
    <line class="how" x1="{FX + 4}" y1="{FY}" x2="{TXT_X}" y2="{FY}" stroke="url(#how)" stroke-width="2"/>
    <rect class="rule" x="{TXT_X}" y="{FY - 1}" width="{rule_w}" height="2" fill="url(#rule)"/>

    <!-- identity: the name, assembled from the field -->
    {rise(T_SOLID - .5, f'<path d="{L["eyebrow"]}" fill="{A}"/>')}
    {letters_svg}
    <g class="flock">
      {flock_svg}
    </g>
    {rise(T_SOLID + .45, f'<path d="{L["line1"]}" fill="{t["BODY"]}"/>')}
    {rise(T_SOLID + .6, f'<path d="{L["meta"]}" fill="{t["MUT"]}"/>')}
    {rise(T_SOLID + .6, f'<path d="{L["sync"]}" fill="{t["MUT"]}"/>')}

    <!-- idle loop: cause → effect -->
    <g class="idle">
      {particle_svg}
      {idle_response}
    </g>
  </g>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="none" stroke="{t["LINE"]}"/>
</svg>
'''


if __name__ == "__main__":
    fonts = HERE / "fonts"
    display = Face(fonts / "Inter.ttf", wght=620, opsz=32)
    text = Face(fonts / "Inter.ttf", wght=400, opsz=20)
    small = Face(fonts / "Inter.ttf", wght=450, opsz=14)
    mono = Face(fonts / "JetBrainsMono.ttf", wght=450)

    NAME_SIZE, NAME_Y = 74, 138
    _, name_w = display.path(NAME, TXT_X - 4, NAME_Y, NAME_SIZE, tracking=-1.0)
    letters = display.glyph_paths(NAME, TXT_X - 4, NAME_Y, NAME_SIZE, tracking=-1.0)
    targets = display.points(NAME, TXT_X - 4, NAME_Y, NAME_SIZE, DOT_PITCH, tracking=-1.0)

    L = dict(
        letters=letters,
        eyebrow=mono.path(EYEBROW, TXT_X, 64, 13, tracking=1.2)[0],
        line1=text.path(LINE1, TXT_X, 203, 21, tracking=-0.1)[0],
        meta=small.path(META, TXT_X, 237, 14)[0],
        sync=mono.path(SYNC, W - 28 - mono.shape(SYNC, 11.5)[1], 64, 11.5)[0],
        rule_w=min(520, round(name_w + 30)),
    )

    rng = random.Random(11)
    dots, threads, links = field(rng)
    flock = swarm(random.Random(7), targets, TXT_X, TXT_X + name_w)
    for theme, t in THEMES.items():
        (HERE / f"v3-{theme}.svg").write_text(build(t, L, dots, threads, links, flock))
    print(f"v3-dark.svg + v3-light.svg — {W}x{H}, {len(flock)} swarm points, "
          f"name {name_w:.0f}px wide, {len(threads)} threads")
