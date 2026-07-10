#!/usr/bin/env python3
"""Generate the profile banner for github.com/sjelodari.

"Why to how" — scattered points (the problem space) converge through faint
threads into a single bright line (execution) that runs into the typography.
Sector-neutral, calm, editorial. Run:  python3 generate_profile.py
"""
import random
from datetime import date

W, H = 1010, 300
FY = 147                    # focal baseline y (aligns with the rule)
FX = 312                    # convergence point x
TXT_X = 452

# ---------------------------------------------------------------- palette
BG0, BG1 = "#0d1117", "#101722"
GRID = "rgba(148,163,184,0.05)"
ACCENT = "#7aa2ff"          # single professional accent
DOT = "#9aa8bd"
TXT = "#e6edf3"
SUB = "#94a0b0"
MUT = "#5d6875"
LINE = "rgba(148,163,184,0.15)"

SANS = "-apple-system, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
MONO = "'SFMono-Regular', Menlo, Consolas, monospace"

# ---------------------------------------------------------------- the field of "why"
rng = random.Random(11)
pts, dots, threads, links = [], [], [], []
for i in range(40):
    x = rng.uniform(52, 268)
    y = rng.uniform(46, 250)
    r = rng.uniform(1.1, 2.6)
    accent = rng.random() < 0.2
    col = ACCENT if accent else DOT
    cls = rng.choice(["dotA", "dotA", "dotB"])
    dur = rng.uniform(3.5, 7.5)
    glow = ' filter="url(#soft)"' if accent and r > 1.8 else ""
    pts.append((x, y))
    dots.append(
        f'<circle class="{cls}" style="animation-delay:{rng.uniform(0, 5):.1f}s;'
        f'animation-duration:{dur:.1f}s" cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" '
        f'fill="{col}"{glow}/>')
    # roughly half the points send a thread toward the convergence node
    if rng.random() < 0.5:
        cx = (x + FX) / 2 + rng.uniform(10, 40)      # control pulls the curve flat
        op = rng.uniform(0.06, 0.14)
        threads.append(
            f'<path d="M{x:.0f} {y:.0f} Q {cx:.0f} {y:.0f}, {FX} {FY}" fill="none" '
            f'stroke="{DOT}" stroke-width="0.8" opacity="{op:.2f}"/>')

# faint constellation links between close neighbours — texture, not noise
linked = set()
for i, (x1, y1) in enumerate(pts):
    for j, (x2, y2) in enumerate(pts):
        if j <= i or (i, j) in linked or len(links) >= 9:
            continue
        d2 = (x1 - x2) ** 2 + (y1 - y2) ** 2
        if 400 < d2 < 2900 and rng.random() < 0.5:
            linked.add((i, j))
            links.append(
                f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" '
                f'stroke="{DOT}" stroke-width="0.6" opacity="0.09"/>')

DOTS = "\n    ".join(dots)
THREADS = "\n    ".join(threads)
LINKS = "\n    ".join(links)

# ---------------------------------------------------------------- content
NAME = "Saber Jelodari"
TAG = "AI Specialist · Technical Product Management"
FACTS = [
    "DeutschPath v1.0 — self-directed product, zero to launch, solo",
    "PhysioNet Challenge 2025 — Top 10 of 41 teams worldwide",
    "Product Owner — FAU AMOS Project, 11-person Agile team",
]
FOOT = "University of Bayreuth · Bayreuth, Germany · saberjelodari.com"
SYNC = f"updated {date.today().isoformat()}"

facts_svg = "\n    ".join(
    f'<line x1="{TXT_X + 1}" y1="{184 + i * 27 - 12}" x2="{TXT_X + 1}" y2="{184 + i * 27 + 2}" '
    f'stroke="{ACCENT}" stroke-width="2" opacity="0.7"/>'
    f'<text x="{TXT_X + 16}" y="{184 + i * 27}" font-family="{SANS}" font-size="14.5" '
    f'fill="#bac4d2">{line}</text>'
    for i, line in enumerate(FACTS))

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{BG0}"/><stop offset="1" stop-color="{BG1}"/>
    </linearGradient>
    <linearGradient id="how" x1="{FX}" y1="0" x2="{TXT_X}" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{DOT}" stop-opacity="0.35"/>
      <stop offset="1" stop-color="{ACCENT}"/>
    </linearGradient>
    <linearGradient id="rule" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{ACCENT}" stop-opacity="0.95"/>
      <stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/>
    </linearGradient>
    <filter id="soft" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="1.6" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <pattern id="grid" width="56" height="56" patternUnits="userSpaceOnUse">
      <path d="M56 0H0V56" fill="none" stroke="{GRID}" stroke-width="1"/>
    </pattern>
    <clipPath id="card"><rect width="{W}" height="{H}" rx="14"/></clipPath>
  </defs>
  <style>
    .dotA {{ animation: breatheA 5.5s ease-in-out infinite; }}
    @keyframes breatheA {{ 0%,100% {{ opacity: 0.14; }} 50% {{ opacity: 0.45; }} }}
    .dotB {{ animation: breatheB 5.5s ease-in-out infinite; }}
    @keyframes breatheB {{ 0%,100% {{ opacity: 0.30; }} 50% {{ opacity: 0.70; }} }}
    .node {{ animation: node 2.8s ease-in-out infinite; transform-origin: {FX}px {FY}px; }}
    @keyframes node {{ 0%,100% {{ transform: scale(1); opacity: 0.9; }}
                       50% {{ transform: scale(1.35); opacity: 1; }} }}
    .flow {{ stroke-dasharray: 34 220; animation: flow 3.2s linear infinite; }}
    @keyframes flow {{ from {{ stroke-dashoffset: 254; }} to {{ stroke-dashoffset: 0; }} }}
    .vitals {{ animation: vitals 2.8s ease-in-out infinite; }}
    @keyframes vitals {{ 0%,100% {{ opacity: 0.85; }} 50% {{ opacity: 0.5; }} }}
  </style>

  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="url(#bg)"/>
    <rect width="{W}" height="{H}" fill="url(#grid)"/>

    <!-- why: the problem space -->
    {LINKS}
    {THREADS}
    {DOTS}

    <!-- the insight node -->
    <circle cx="{FX}" cy="{FY}" r="7" fill="{ACCENT}" opacity="0.14"/>
    <circle class="node" cx="{FX}" cy="{FY}" r="3.2" fill="{ACCENT}" filter="url(#soft)"/>

    <!-- how: one line, executed -->
    <line x1="{FX + 4}" y1="{FY}" x2="{TXT_X - 2}" y2="{FY}" stroke="url(#how)" stroke-width="2"/>
    <line class="flow" x1="{FX + 4}" y1="{FY}" x2="{TXT_X - 2}" y2="{FY}"
          stroke="{ACCENT}" stroke-width="2.2" stroke-linecap="round" filter="url(#soft)"/>

    <!-- caption -->
    <text class="vitals" x="160" y="270" text-anchor="middle" font-family="{MONO}"
          font-size="12" fill="{ACCENT}">why &#8594; how</text>

    <!-- identity -->
    <text x="{TXT_X}" y="96" font-family="{SANS}" font-size="40" font-weight="600"
          letter-spacing="0.3" fill="{TXT}">{NAME}</text>
    <text x="{TXT_X}" y="127" font-family="{SANS}" font-size="16" letter-spacing="0.2"
          fill="{SUB}">{TAG}</text>
    <rect x="{TXT_X}" y="146" width="330" height="2" rx="1" fill="url(#rule)"/>

    {facts_svg}

    <text x="{TXT_X}" y="272" font-family="{SANS}" font-size="12.5" fill="{MUT}">{FOOT}</text>
    <text x="{W - 26}" y="272" text-anchor="end" font-family="{MONO}" font-size="11"
          fill="{MUT}">{SYNC}</text>
  </g>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="none" stroke="{LINE}"/>
</svg>'''

with open("profile.svg", "w") as f:
    f.write(svg)
print(f"profile.svg written — {W}x{H}, {len(dots)} dots, {len(threads)} threads")
