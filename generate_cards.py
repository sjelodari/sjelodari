#!/usr/bin/env python3
"""Selected-work cards for github.com/sjelodari — one proof per project.

Each card pairs a headline result with a small chart drawn in the banner's
language (points, threads, one bright node) that shows what the result means:

  01 DeutschPath    a timeline builds feature by feature into v1.0
  02 FAU AMOS       ten teammates' threads converge on one Product Owner
  03 PhysioNet      41 teams; the top 10 light up
  04 Thesis         a marker travels the German grading scale to 1.0

The chart plays once on load, then idles quietly. Reduced motion shows the final frame.
Run:  python3 generate_cards.py   → cards/<slug>-dark.svg, cards/<slug>-light.svg
"""
import math
import random
from pathlib import Path

from generate_v3 import EASE_OUT, SPRING, THEMES, Face

HERE = Path(__file__).parent
W, H, PAD = 496, 250, 26
VX0, VX1 = 262, 462                 # chart area, bottom right

FONTS = HERE / "fonts"
TITLE = Face(FONTS / "Inter.ttf", wght=620, opsz=28)
BODY = Face(FONTS / "Inter.ttf", wght=400, opsz=14)
METRIC = Face(FONTS / "Inter.ttf", wght=640, opsz=32)
SMALL = Face(FONTS / "Inter.ttf", wght=450, opsz=14)
MONO = Face(FONTS / "JetBrainsMono.ttf", wght=450)

CARDS = [
    dict(slug="deutschpath", no="01", kind="product", stack="Next.js · Gemini Vision",
         title="DeutschPath",
         desc=["AI-powered language-learning platform — book reader,",
               "spaced-repetition vocab, grammar roadmap. Runs locally."],
         metric="v1.0", caption="shipped solo · zero to launch", chart="timeline"),
    dict(slug="amos", no="02", kind="leadership", stack="Scrum",
         title="FAU AMOS Project",
         desc=["Agile Methods & Open Source project at FAU Erlangen-Nürnberg.",
               "Product Owner — turning stakeholder needs into a team backlog."],
         metric="11-person", caption="Agile team · Product Owner", chart="team"),
    dict(slug="physionet", no="03", kind="research", stack="PyTorch",
         title="PhysioNet Challenge 2025",
         desc=["15 MB CNN–BiLSTM–Attention model for signal classification",
               "in a global research competition."],
         metric="Top 10", caption="of 41 teams worldwide", chart="ranking"),
    dict(slug="thesis", no="04", kind="thesis", stack="Transformers · BERT",
         title="Clinical Trials NLP",
         desc=["Domain-specific BERT models classifying trial records at scale.",
               "Master's thesis, presented at MIE 2024 in Athens."],
         metric="1.0", caption="thesis grade · best possible", chart="grade"),
]

T0 = 0.35                           # charts start shortly after load


def text(face, s, x, y, size, fill, anchor="start", tracking=0.0, cls="", delay=None):
    adv = face.shape(s, size, tracking)[1]
    x = x - adv if anchor == "end" else x - adv / 2 if anchor == "middle" else x
    d = face.path(s, x, y, size, tracking)[0]
    style = f' style="animation-delay:{delay:.2f}s"' if delay is not None else ""
    c = f' class="{cls}"' if cls else ""
    return f'<path{c}{style} d="{d}" fill="{fill}"/>'


# ---------------------------------------------------------------- charts
def timeline(t):
    A, y = t["ACCENT"], 204
    feats = ["reader", "vocab", "grammar", "speak", "write"]
    xs = [VX0 + i * 40 for i in range(len(feats))]
    end = VX1
    draw = 1.1
    at = lambda x: T0 + (x - VX0) / (end - VX0) * draw
    parts = [f'<line class="grow" style="animation-delay:{T0}s;animation-duration:{draw}s" '
             f'x1="{VX0}" y1="{y}" x2="{end}" y2="{y}" stroke="url(#track)" stroke-width="1.6"/>']
    for x, f in zip(xs, feats):
        parts.append(f'<g class="pop" style="animation-delay:{at(x):.2f}s">'
                     f'<circle cx="{x}" cy="{y}" r="2.6" fill="{t["DOT"]}"/>'
                     f'{text(MONO, f, x, y - 12, 9, t["MUT"], "middle")}</g>')
    land = at(end)
    parts.append(f'<g class="ignite" style="animation-delay:{land:.2f}s;transform-origin:{end}px {y}px">'
                 f'<circle cx="{end}" cy="{y}" r="9" fill="{A}" opacity=".14"/>'
                 f'<circle cx="{end}" cy="{y}" r="3.8" fill="{A}" filter="url(#soft)"/>'
                 f'{text(MONO, "v1.0", end, y - 14, 10, A, "middle")}</g>')
    L = end - VX0
    parts.append(f'''<g class="idle"><line x1="{VX0}" y1="{y}" x2="{end}" y2="{y}" stroke="{t["PULSE"]}"
        stroke-width="2" filter="url(#softline)" opacity=".8" stroke-dasharray="30 {L + 60}" stroke-dashoffset="30">
      <animate attributeName="stroke-dashoffset" begin="{land + 1.2:.2f}s" dur="4.5s" repeatCount="indefinite"
        values="30;{-L};{-L}" keyTimes="0;.3;1" calcMode="spline" keySplines=".4 0 .6 1;0 0 1 1"/></line></g>''')
    return "\n    ".join(parts)


def team(t):
    A, cx, cy = t["ACCENT"], 366, 196
    rng = random.Random(4)
    parts, paths = [], []
    for i in range(10):
        a = -math.pi / 2 + i * 2 * math.pi / 10 + rng.uniform(-0.18, 0.18)
        x, y = cx + 88 * math.cos(a) * rng.uniform(0.85, 1), cy + 30 * math.sin(a) * rng.uniform(0.8, 1)
        mx, my = (x + cx) / 2 + rng.uniform(-10, 10), (y + cy) / 2 + rng.uniform(-6, 6)
        d = T0 + i * 0.07
        paths.append(f"M{x:.1f} {y:.1f} Q {mx:.1f} {my:.1f}, {cx} {cy}")
        parts.append(f'<path id="m{i}" class="draw" pathLength="1" style="animation-delay:{d + .25:.2f}s" '
                     f'd="{paths[-1]}" fill="none" stroke="{t["DOT"]}" stroke-width=".8" opacity=".3"/>')
        parts.append(f'<circle class="pop" style="animation-delay:{d:.2f}s" cx="{x:.1f}" cy="{y:.1f}" '
                     f'r="{rng.uniform(2.1, 2.8):.1f}" fill="{t["DOT"]}" opacity=".75"/>')
    land = T0 + 0.07 * 9 + 0.25 + 0.5
    parts.append(f'<g class="ignite" style="animation-delay:{land:.2f}s;transform-origin:{cx}px {cy}px">'
                 f'<circle cx="{cx}" cy="{cy}" r="10" fill="{A}" opacity=".14"/>'
                 f'<circle cx="{cx}" cy="{cy}" r="4" fill="{A}" filter="url(#soft)"/></g>')
    # idle: a teammate's input travels to the PO; the node answers
    beat, n = 2.6, 3
    cyc = beat * n
    k = 1.3 / cyc
    idle = []
    for j, m in enumerate((1, 5, 8)):
        b = land + 1 + j * beat
        idle.append(f'''<circle r="1.8" fill="{A}" filter="url(#soft)" opacity="0">
        <animateMotion begin="{b:.2f}s" dur="{cyc}s" repeatCount="indefinite" calcMode="spline"
          keyPoints="0;1;1" keyTimes="0;{k:.4f};1" keySplines=".45 0 .55 1;0 0 1 1"><mpath xlink:href="#m{m}"/></animateMotion>
        <animate attributeName="opacity" begin="{b:.2f}s" dur="{cyc}s" repeatCount="indefinite"
          values="0;.95;.95;0;0" keyTimes="0;.02;{k - .01:.4f};{k:.4f};1"/></circle>''')
    idle.append(f'''<circle cx="{cx}" cy="{cy}" r="4" fill="{A}" opacity="0" filter="url(#soft)">
        <animate attributeName="r" begin="{land + 2.3:.2f}s" dur="{beat}s" repeatCount="indefinite" values="4;7.5;4;4" keyTimes="0;.07;.25;1"/>
        <animate attributeName="opacity" begin="{land + 2.3:.2f}s" dur="{beat}s" repeatCount="indefinite" values="0;.5;0;0" keyTimes="0;.05;.25;1"/></circle>''')
    parts.append('<g class="idle">' + "\n      ".join(idle) + "</g>")
    return "\n    ".join(parts)


def ranking(t):
    A = t["ACCENT"]
    cols, pitch, row_h, y0 = 14, 14.4, 15, 184
    x0 = VX0 + 6
    parts = []
    for i in range(41):
        r, c = divmod(i, cols)
        x, y = x0 + c * pitch, y0 + r * row_h
        d = T0 + (r * cols + c) * 0.012
        parts.append(f'<circle class="pop" style="animation-delay:{d:.2f}s" cx="{x:.1f}" cy="{y}" r="2.5" '
                     f'fill="{t["DOT"]}" opacity=".4"/>')
    lit = T0 + 0.75
    for i in range(10):
        x = x0 + i * pitch
        parts.append(f'<circle class="top" style="animation-delay:{lit + i * .06:.2f}s, {lit + 2.5 + i * .09:.2f}s" '
                     f'cx="{x:.1f}" cy="{y0}" r="2.9" fill="{A}"/>')
    bx0, bx1, by = x0 - 4, x0 + 9 * pitch + 4, y0 - 11
    parts.append(f'<g class="grow" style="animation-delay:{lit + .3:.2f}s;transform-origin:{bx0}px {by}px">'
                 f'<path d="M{bx0} {by + 4} V{by} H{bx1:.1f} V{by + 4}" fill="none" stroke="{A}" '
                 f'stroke-width="1" opacity=".7"/></g>')
    parts.append(text(MONO, "top 10", bx1 + 8, by + 3, 9, A, cls="rise", delay=lit + .7))
    return "\n    ".join(parts)


def grade(t):
    A, y = t["ACCENT"], 198
    marks = ["4.0", "3.0", "2.0", "1.0"]
    xs = [VX0 + 6 + i * (VX1 - VX0 - 12) / 3 for i in range(4)]
    x0, x1 = xs[0], xs[-1]
    run = 1.5
    parts = [text(MONO, "German grading scale", x0, y - 22, 9, t["MUT"], cls="rise", delay=T0),
             f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{t["DOT"]}" stroke-width="1.4" opacity=".25"/>',
             f'<line class="grow" style="animation-delay:{T0 + .2:.2f}s;animation-duration:{run}s;transform-origin:{x0}px {y}px" '
             f'x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="url(#track)" stroke-width="1.8"/>']
    for x, m in zip(xs, marks):
        best = m == "1.0"
        parts.append(f'<line x1="{x:.1f}" y1="{y - 4}" x2="{x:.1f}" y2="{y + 4}" stroke="{A if best else t["DOT"]}" '
                     f'stroke-width="1" opacity="{1 if best else .5}"/>')
        parts.append(text(MONO, m, x, y + 18, 9, A if best else t["MUT"], "middle"))
    land = T0 + .2 + run
    parts.append(f'<g class="slide" style="animation-delay:{T0 + .2:.2f}s;animation-duration:{run}s;--from:{x0 - x1:.1f}px">'
                 f'<circle cx="{x1:.1f}" cy="{y}" r="4" fill="{A}" filter="url(#soft)"/></g>')
    parts.append(f'<g class="ignite" style="animation-delay:{land - .1:.2f}s;transform-origin:{x1:.1f}px {y}px">'
                 f'<circle cx="{x1:.1f}" cy="{y}" r="10" fill="{A}" opacity=".14"/></g>')
    parts.append(f'''<g class="idle"><circle cx="{x1:.1f}" cy="{y}" r="4" fill="{A}" opacity="0" filter="url(#soft)">
        <animate attributeName="r" begin="{land + 1:.2f}s" dur="4s" repeatCount="indefinite" values="4;8;4;4" keyTimes="0;.12;.4;1"/>
        <animate attributeName="opacity" begin="{land + 1:.2f}s" dur="4s" repeatCount="indefinite" values="0;.45;0;0" keyTimes="0;.08;.4;1"/></circle></g>''')
    return "\n    ".join(parts)


CHARTS = dict(timeline=timeline, team=team, ranking=ranking, grade=grade)


# ---------------------------------------------------------------- card
def build(c, t):
    A = t["ACCENT"]
    desc = "\n    ".join(text(BODY, line, PAD, 110 + i * 20, 14, t["BODY"]) for i, line in enumerate(c["desc"]))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="ttl">
  <title id="ttl">{c["title"]} — {c["metric"]} {c["caption"]}</title>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{t["BG0"]}"/><stop offset="1" stop-color="{t["BG1"]}"/>
    </linearGradient>
    <linearGradient id="track" x1="{VX0}" y1="0" x2="{VX1}" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{t["DOT"]}" stop-opacity=".35"/><stop offset="1" stop-color="{A}"/>
    </linearGradient>
    <filter id="soft" x="-60%" y="-60%" width="220%" height="220%">
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
    .pop    {{ animation: fadeIn .45s {EASE_OUT} backwards; }}
    .rise   {{ animation: rise .6s {EASE_OUT} backwards; }}
    .draw   {{ stroke-dasharray: 1; animation: draw .7s {EASE_OUT} backwards; }}
    .grow   {{ transform-origin: {VX0}px 0; animation: grow .9s {EASE_OUT} backwards; }}
    .ignite {{ animation: ignite .6s {SPRING} backwards; }}
    .slide  {{ animation: slide 1.5s {EASE_OUT} backwards; }}
    .top    {{ animation: fadeIn .45s {EASE_OUT} backwards, shimmer 5s ease-in-out infinite; }}
    @keyframes fadeIn  {{ from {{ opacity: 0; }} }}
    @keyframes rise    {{ from {{ opacity: 0; transform: translateY(5px); }} }}
    @keyframes draw    {{ from {{ stroke-dashoffset: 1; }} to {{ stroke-dashoffset: 0; }} }}
    @keyframes grow    {{ from {{ transform: scaleX(0); }} }}
    @keyframes ignite  {{ from {{ transform: scale(0); opacity: 0; }} }}
    @keyframes slide   {{ from {{ transform: translateX(var(--from)); }} }}
    @keyframes shimmer {{ 0%, 70%, 100% {{ opacity: 1; }} 80% {{ opacity: .45; }} }}
    @media (prefers-reduced-motion: reduce) {{
      * {{ animation: none !important; }}
      .idle {{ display: none; }}
    }}
  </style>

  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>
    <rect width="{W}" height="{H}" fill="url(#grid)"/>

    {text(MONO, f'{c["no"]} · {c["kind"]}', PAD, 42, 11.5, A, tracking=0.6)}
    {text(MONO, c["stack"], W - PAD, 42, 11, t["MUT"], "end")}
    {text(TITLE, c["title"], PAD - 1, 78, 25, t["TXT"], tracking=-0.3)}
    {desc}

    {text(METRIC, c["metric"], PAD - 1, 206, 36, t["TXT"], tracking=-0.6)}
    {text(SMALL, c["caption"], PAD, 229, 12.5, t["MUT"])}

    {CHARTS[c["chart"]](t)}
  </g>
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="none" stroke="{t["LINE"]}"/>
</svg>
'''


if __name__ == "__main__":
    out = HERE / "cards"
    out.mkdir(exist_ok=True)
    for c in CARDS:
        for theme, t in THEMES.items():
            (out / f'{c["slug"]}-{theme}.svg').write_text(build(c, t))
    print(f"{len(CARDS) * len(THEMES)} cards written to cards/")
