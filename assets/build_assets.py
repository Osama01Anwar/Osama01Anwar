"""Generate the terminal-style SVG assets used by the profile README.

Every number rendered by this script comes from the GitHub REST API, not from
hand-editing. Run with ``--fetch`` to re-query GitHub and refresh the snapshot
below; run without it to rebuild the SVGs from the recorded snapshot.

    python build_assets.py            # rebuild SVGs from SNAPSHOT
    python build_assets.py --fetch    # re-query GitHub, then rebuild

Requires the GitHub CLI (``gh auth login``) only for ``--fetch``.
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess

import geom3d as g3
from dataclasses import dataclass
from pathlib import Path

USER = "Osama01Anwar"
OUT = Path(__file__).parent

# --- Recorded snapshot -------------------------------------------------------
# Source: GitHub REST API /repos/{owner}/{repo}/languages summed over every
# public repository, plus /users/{user}. Captured 2026-09-27.
SNAPSHOT_DATE = "2026-09-27"
LANG_BYTES: dict[str, int] = {
    "Python": 1_513_981,
    "HTML": 76_776,
    "CSS": 20_960,
    "JavaScript": 13_333,
    "Inno Setup": 2_612,
}
# Number of repositories in which each language is the largest by bytes.
LANG_BREADTH: dict[str, int] = {"Python": 11, "HTML": 9, "JavaScript": 6, "CSS": 2}
PUBLIC_REPOS = 32
TRACKED_FILES = 500

MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"


@dataclass(frozen=True)
class Theme:
    """Colour tokens for one rendering variant."""

    name: str
    bg: str
    panel: str
    border: str
    rule: str
    text: str
    bright: str
    dim: str
    green: str
    cyan: str
    blue: str
    yellow: str
    orange: str
    red: str
    purple: str


DARK = Theme(
    name="dark", bg="#0B0F14", panel="#11171F", border="#1F2A37", rule="#1B2430",
    text="#C9D1D9", bright="#E6EDF3", dim="#6E7681", green="#3FB950", cyan="#2DD4BF",
    blue="#58A6FF", yellow="#E3B341", orange="#FF8C42", red="#F85149", purple="#BC8CFF",
)
# The panel stays dark in light mode on purpose - it is a terminal. Only the
# outer frame changes so the card sits cleanly on a white page instead of
# bleeding into it.
LIGHT = Theme(
    name="light", bg="#0D1117", panel="#161B22", border="#AFB8C1", rule="#21262D",
    text="#C9D1D9", bright="#FFFFFF", dim="#8B949E", green="#3FB950", cyan="#2DD4BF",
    blue="#58A6FF", yellow="#E3B341", orange="#FF8C42", red="#F85149", purple="#BC8CFF",
)


def esc(s: str) -> str:
    """Escape the three characters that are not legal as SVG text content."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x: float, y: float, content: str, fill: str, size: float = 13,
         weight: str = "normal", spacing: float = 0, anchor: str = "start") -> str:
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    an = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return (f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}"{ls}{an} xml:space="preserve">{esc(content)}</text>')


def chrome(t: Theme, w: int, h: int, title: str, card: bool = True) -> str:
    """The window frame: rounded card, title bar, traffic lights, caption.

    ``card=False`` emits only the title bar, for scenes that paint their own
    background and draw the border themselves.
    """
    base = f'''  <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="10"
        fill="{t.bg}" stroke="{t.border}" stroke-width="1"/>
''' if card else ""
    return base + f'''  <path d="M0.5 10.5a10 10 0 0 1 10-10h{w - 21}a10 10 0 0 1 10 10V34H0.5z"
        fill="{t.panel}"/>
  <line x1="0.5" y1="34" x2="{w - 0.5}" y2="34" stroke="{t.border}" stroke-width="1"/>
  <circle cx="20" cy="17.5" r="5" fill="{t.red}"/>
  <circle cx="38" cy="17.5" r="5" fill="{t.yellow}"/>
  <circle cx="56" cy="17.5" r="5" fill="{t.green}"/>
{text(w / 2, 22, title, t.dim, 11.5, anchor='middle')}
'''


def svg(w: int, h: int, body: str, title: str, desc: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d">\n'
            f'  <title id="t">{esc(title)}</title>\n'
            f'  <desc id="d">{esc(desc)}</desc>\n{body}</svg>\n')


def rich(x: float, y: float, parts: list[tuple[str, str]], size: float = 13,
         weight: str = "normal", spacing: float = 0) -> str:
    """One line of monospace text whose runs carry different colours."""
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    spans = "".join(f'<tspan fill="{fill}">{esc(c)}</tspan>' for c, fill in parts)
    return (f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" '
            f'font-weight="{weight}"{ls} xml:space="preserve">{spans}</text>')



def lang_colour(t: Theme, name: str) -> str:
    """One colour per language, shared by every asset that shows languages."""
    return {"Python": t.blue, "HTML": t.orange, "CSS": t.purple,
            "JavaScript": t.yellow, "Inno Setup": t.green}.get(name, t.text)


# --- 3D scene helpers ---------------------------------------------------------

def anim(attr: str, values: list[str], dur: float) -> str:
    """A seamless SMIL loop. Static viewers keep the element's authored value."""
    return (f'<animate attributeName="{attr}" dur="{dur}s" repeatCount="indefinite" '
            f'calcMode="linear" values="{";".join(values)}"/>')


def wire_frames(verts: list[g3.Vec3], edges: list[tuple[int, int]], cx: float,
                cy: float, r: float, tilt: float, frames: int) -> tuple[list[str], list[str]]:
    """Per-frame path data for a solid's edges and its vertex dots.

    The solid is rotated through a full turn about Y, so the last frame meets
    the first and the SMIL loop has no visible seam.
    """
    edge_d, dot_d = [], []
    for f in range(frames):
        ay = 2 * math.pi * f / frames
        pts = []
        for v in verts:
            x, y, z = g3.rotate(v, ax=tilt, ay=ay)
            # Mild perspective so near vertices spread wider than far ones.
            k = r / (2.6 + z * 0.55)
            pts.append((cx + x * k * 2.6, cy - y * k * 2.6))
        edge_d.append(" ".join(f"M{pts[i][0]:.1f} {pts[i][1]:.1f}L{pts[j][0]:.1f} {pts[j][1]:.1f}"
                               for i, j in edges))
        dot_d.append(" ".join(f"M{x:.1f} {y:.1f}l.01 0" for x, y in pts))
    return edge_d, dot_d


def persp_grid(t: Theme, ox: float, horizon: float, bottom: float, focal: float,
               cam_h: float, eye: float, half: int, depth: float) -> str:
    """A ground plane receding to a vanishing point, drawn as straight lines."""
    def grd(x: float, z: float) -> tuple[float, float]:
        d = z + eye
        k = focal / d
        return (ox + x * k, horizon + cam_h * k)

    near = cam_h * focal / (bottom - horizon) - eye   # depth where the plane meets the bottom edge
    out = []
    for i in range(-half, half + 1):
        a, b = grd(i, near), grd(i, depth)
        w = 1.4 if i == 0 else 0.7
        o = 0.55 if i % 5 == 0 else 0.26
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" '
                   f'stroke="{t.cyan}" stroke-width="{w}" opacity="{o}"/>')
    z, step = near, 0.30
    while z < depth:
        a, b = grd(-half, z), grd(half, z)
        o = max(0.06, 0.5 - (z - near) * 0.05)
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" '
                   f'stroke="{t.green}" stroke-width="0.8" opacity="{o:.2f}"/>')
        z += step
        step *= 1.17
    return "\n".join(out)


def extruded(x: float, y: float, s: str, size: float, face: str, side: str,
             deep: str, steps: int = 11, spacing: float = 5) -> str:
    """Text with a real extrusion.

    The offset copies are the extruded *side*, so they start at ``side`` beside
    the lit face and fall away to ``deep``. Blending toward the face colour
    instead reads as a grey drop shadow rather than as depth.
    """
    out = []
    for i in range(steps, 0, -1):
        out.append(text(x + i * 1.15, y + i * 1.15, s,
                        g3.mix(side, deep, (i / steps) ** 0.8),
                        size, "700", spacing=spacing))
    out.append(text(x, y, s, face, size, "700", spacing=spacing))
    return "\n".join(out)


def build_header(t: Theme) -> str:
    w, h, horizon = 880, 470, 252
    void = "#04070C" if t.name == "dark" else "#05090F"
    b = [f'<rect width="{w}" height="{h}" rx="10" fill="{void}"/>']

    b.append(f'''<defs>
    <radialGradient id="halo" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="{t.cyan}" stop-opacity="0.30"/>
      <stop offset="0.55" stop-color="{t.blue}" stop-opacity="0.07"/>
      <stop offset="1" stop-color="{t.cyan}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{void}" stop-opacity="1"/>
      <stop offset="0.42" stop-color="{void}" stop-opacity="0.35"/>
      <stop offset="1" stop-color="{void}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="hz" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{t.cyan}" stop-opacity="0"/>
      <stop offset="0.5" stop-color="{t.cyan}" stop-opacity="0.85"/>
      <stop offset="1" stop-color="{t.cyan}" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="floor"><rect x="1" y="{horizon}" width="{w - 2}" height="{h - horizon - 1}"/></clipPath>
    <clipPath id="card"><rect x="0" y="0" width="{w}" height="{h}" rx="10"/></clipPath>
  </defs>''')

    b.append(f'<g clip-path="url(#card)">')
    b.append(f'<ellipse cx="690" cy="150" rx="250" ry="185" fill="url(#halo)"/>')

    # Static starfield - deterministic, so rebuilds produce an identical file.
    seed = 1337
    stars = []
    for _ in range(58):
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        sx = seed % w
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        sy = seed % (horizon - 40) + 20
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        op = 0.10 + (seed % 40) / 130
        stars.append(f'<circle cx="{sx}" cy="{sy}" r="{0.8 if op > 0.28 else 0.6}" '
                     f'fill="{t.text}" opacity="{op:.2f}"/>')
    b.append("".join(stars))

    b.append(f'<g clip-path="url(#floor)">{persp_grid(t, 440, horizon, h, 300, 0.95, 0.62, 13, 34)}</g>')
    b.append(f'<rect x="0" y="{horizon}" width="{w}" height="120" fill="url(#fade)"/>')
    b.append(f'<rect x="0" y="{horizon - 0.8}" width="{w}" height="1.6" fill="url(#hz)"/>')

    # Wireframe icosahedron, rotated in 3D across the keyframes.
    verts, edges = g3.icosahedron()
    edge_d, dot_d = wire_frames(verts, edges, 700, 146, 96, math.radians(-16), 26)
    loop = lambda seq: [*seq, seq[0]]
    b.append(f'<circle cx="700" cy="146" r="104" fill="none" stroke="{t.cyan}" '
             f'stroke-width="0.7" opacity="0.22"/>')
    b.append(f'<circle cx="700" cy="146" r="128" fill="none" stroke="{t.blue}" '
             f'stroke-width="0.6" opacity="0.10"/>')
    b.append(f'<path d="{edge_d[0]}" fill="none" stroke="{t.cyan}" stroke-width="1.15" '
             f'opacity="0.80" stroke-linecap="round">{anim("d", loop(edge_d), 22)}</path>')
    b.append(f'<path d="{dot_d[0]}" fill="none" stroke="{t.green}" stroke-width="4.6" '
             f'stroke-linecap="round">{anim("d", loop(dot_d), 22)}</path>')

    # Identity
    b.append(rich(30, 62, [
        ("\u250c\u2500\u2500(", t.dim), ("osama", t.green), ("@", t.dim), ("github", t.cyan),
        (")\u2500[", t.dim), ("~", t.blue), ("]", t.dim),
    ], 12.5))
    b.append(rich(30, 82, [
        ("\u2514\u2500", t.dim), ("$", t.green), (" ./profile.sh ", t.bright), ("--render 3d", t.orange),
    ], 12.5))

    b.append(extruded(30, 170, "OSAMA ANWAR", 50, t.bright, "#1E8091", void,
                      steps=13, spacing=4))
    b.append(f'<rect x="31" y="194" width="430" height="1" fill="{t.cyan}" opacity="0.45"/>')
    b.append(rich(31, 216, [
        ("Software Engineer", t.cyan), ("  \u2571\u2571  ", t.dim),
        ("Quality Engineering", t.green), ("  \u2571\u2571  ", t.dim),
        ("Camera / Image IQ", t.yellow),
    ], 12.5))
    b.append(rich(31, 234, [
        ("Database Operations", t.purple), ("  ╱╱  ", t.dim),
        ("Linux / Systems", t.text), ("  ╱╱  ", t.dim),
        ("Automation / CLI", t.text),
    ], 11.5))

    # HUD strip floating over the grid
    b.append(f'<rect x="18" y="404" width="{w - 36}" height="48" rx="8" fill="{void}" '
             f'fill-opacity="0.80" stroke="{t.cyan}" stroke-opacity="0.32" stroke-width="1"/>')
    chips = [(36, "STATUS", "ONLINE", t.green), (200, "BASE", "PAKISTAN", t.text),
             (360, "MODE", "BUILD \u00b7 TEST \u00b7 ANALYZE", t.cyan),
             (632, "REPOS", f"{PUBLIC_REPOS} PUBLIC", t.text)]
    for x, key, val, colour in chips:
        b.append(f'<rect x="{x}" y="414" width="2.5" height="28" rx="1.25" fill="{colour}"/>')
        b.append(text(x + 11, 426, key, t.dim, 9))
        b.append(text(x + 11, 441, val, colour, 12.5, "600"))
    b.append(text(w - 34, 441, f"data {SNAPSHOT_DATE}", t.dim, 9, anchor="end"))
    b.append("</g>")
    b.append(f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="10" fill="none" '
             f'stroke="{t.border}" stroke-width="1"/>')

    return svg(w, h, "\n".join(b) + "\n",
               "Osama Anwar - three dimensional terminal profile header",
               "A dark 3D scene: a perspective grid receding to the horizon, a rotating "
               "wireframe icosahedron, and the name Osama Anwar in extruded type above the "
               "roles Software Engineer, Quality Engineering, and Camera and Image Quality. "
               f"Status online, based in Pakistan, {PUBLIC_REPOS} public repositories.")


# Per-repository size and leading language, snapshot 2026-09-27. This repository
# is excluded from its own statistics so the profile cannot inflate its numbers.
REPO_BLOCKS: list[tuple[str, int, str]] = [
    ("Network-Analyzer", 920091, "Python"), ("camera-count-tool", 452139, "Python"),
    ("ascii-Art", 45269, "Python"), ("ascii_art", 36898, "Python"),
    ("HackingMonitor", 21794, "HTML"), ("flight-weather-tracker", 17439, "HTML"),
    ("3D_AppImage", 16412, "Python"), ("FbClone", 12130, "CSS"),
    ("SpecTest", 12099, "Python"), ("Architecturee", 11716, "HTML"),
    ("10Assignments", 9224, "HTML"), ("CodeCheck---python", 8701, "Python"),
    ("The-Media-Enhancer", 8006, "Python"), ("QUIZZZZ", 7060, "JavaScript"),
    ("Timetable", 6992, "HTML"), ("spam_detetction", 6341, "Python"),
    ("Internet-Speed-Test", 5348, "Python"), ("Calculator", 4946, "JavaScript"),
    ("WebPage", 4674, "HTML"), ("DiceGame", 4268, "CSS"),
    ("SpamTextClassifier", 3045, "Python"), ("MY_CV", 2884, "HTML"),
    ("BMI-Calculator", 2375, "JavaScript"), ("Clock", 1908, "JavaScript"),
    ("SimpleToDo", 1846, "HTML"), ("DUI", 1826, "JavaScript"),
    ("SimpleDrivingLicenseCheck", 1247, "JavaScript"), ("OnClickEvent", 984, "HTML"),
    ("instamonitor", 0, ""), ("Architecture", 0, ""), ("CalcultorApp", 0, ""),
]

COLS, ROWS = 8, 4
FLOOR = 0.09          # height given to a repository with no classified code


def block_height(size: int) -> float:
    """Log10 height, so a 984-byte repo and a 920 KB repo are both legible."""
    if size <= 0:
        return FLOOR
    return max(FLOOR, (math.log10(size + 1) - 2.55) * 0.63)


def fit(faces: list[g3.Face], box: tuple[float, float, float, float]) -> str:
    """Depth-sort, then translate and scale the solid to sit inside ``box``."""
    xs = [x for f in faces for x, _ in f.points]
    ys = [y for f in faces for _, y in f.points]
    bx, by, bw, bh = box
    k = min(bw / (max(xs) - min(xs)), bh / (max(ys) - min(ys)))
    dx = bx - min(xs) * k + (bw - (max(xs) - min(xs)) * k) / 2
    dy = by - min(ys) * k + (bh - (max(ys) - min(ys)) * k) / 2
    body = "".join(f.svg() for f in sorted(faces, key=lambda f: f.depth))
    return f'<g transform="translate({dx:.1f},{dy:.1f}) scale({k:.4f})">{body}</g>'


def build_matrix(t: Theme) -> str:
    w, h = 880, 474
    void = "#04070C" if t.name == "dark" else "#05090F"
    b = [f'<rect width="{w}" height="{h}" rx="10" fill="{void}"/>']
    b.append(chrome(t, w, h, "osama@github: ~ — repo --matrix", card=False))
    b.append(rich(24, 62, [
        ("\u2514\u2500", t.dim), ("$", t.green), (" repo ", t.bright),
        ("--matrix --height=log10(bytes)", t.orange),
    ], 12.5))

    faces: list[g3.Face] = []
    # Ground plate, drawn first so every solid sits on top of it.
    plate = [g3.iso(p, 0, 0, 1) for p in
             ((-0.3, 0, -0.3), (COLS + 0.3, 0, -0.3),
              (COLS + 0.3, 0, ROWS + 0.3), (-0.3, 0, ROWS + 0.3))]
    faces.append(g3.Face(plate, g3.mix(void, t.cyan, 0.07), -999, "", 1.0))
    for i in range(COLS + 1):
        a, c = g3.iso((i, 0, -0.3), 0, 0, 1), g3.iso((i, 0, ROWS + 0.3), 0, 0, 1)
        faces.append(g3.Face([a, c, c, a], "none", -998, t.cyan, 0.16))
    for j in range(ROWS + 1):
        a, c = g3.iso((-0.3, 0, j), 0, 0, 1), g3.iso((COLS + 0.3, 0, j), 0, 0, 1)
        faces.append(g3.Face([a, c, c, a], "none", -998, t.cyan, 0.16))

    for i, (name, size, lang) in enumerate(REPO_BLOCKS):
        gx, gz = i % COLS, i // COLS
        colour = lang_colour(t, lang) if lang else t.dim
        faces += g3.iso_box(gx + 0.07, gz + 0.07, 0.86, 0.86, block_height(size),
                            colour, 0, 0, 1, edge=g3.shade(colour, 1.35))

    b.append(fit(faces, (28, 92, 560, 350)))

    # Right-hand readout
    rx = 616
    b.append(f'<line x1="{rx - 18}" y1="96" x2="{rx - 18}" y2="426" stroke="{t.rule}" stroke-width="1"/>')
    b.append(text(rx, 106, "TALLEST", t.cyan, 11, "700"))
    y = 128
    for name, size, lang in REPO_BLOCKS[:4]:
        b.append(f'<rect x="{rx}" y="{y - 9}" width="8" height="8" fill="{lang_colour(t, lang)}"/>')
        b.append(text(rx + 15, y, name[:26], t.text, 11))
        b.append(text(rx + 15, y + 14, f"{size:,} B", t.dim, 10))
        y += 38

    b.append(text(rx, y + 8, "LANGUAGE", t.cyan, 11, "700"))
    y += 30
    for lang in ("Python", "HTML", "CSS", "JavaScript"):
        n = sum(1 for _, _, l in REPO_BLOCKS if l == lang)
        b.append(f'<rect x="{rx}" y="{y - 8}" width="8" height="8" fill="{lang_colour(t, lang)}"/>')
        b.append(text(rx + 15, y, f"{lang:<11}{n:>2}", t.text, 11))
        y += 19
    b.append(f'<rect x="{rx}" y="{y - 8}" width="8" height="8" fill="{t.dim}"/>')
    b.append(text(rx + 15, y, f"{'empty':<11}{sum(1 for _, s, _ in REPO_BLOCKS if s == 0):>2}", t.dim, 11))

    b.append(rich(24, 452, [
        ("note", t.yellow),
        (f"  {len(REPO_BLOCKS)} repositories, one solid each, height = log\u2081\u2080 of bytes. "
         "This repository is excluded from its own statistics.", t.dim),
    ], 10.5))

    b.append(f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="10" fill="none" '
             f'stroke="{t.border}" stroke-width="1"/>')
    return svg(w, h, "\n".join(b) + "\n",
               "Repository matrix rendered as isometric solids",
               f"An isometric field of {len(REPO_BLOCKS)} solids, one per public repository, "
               "each coloured by its leading language and raised to the log of its byte count. "
               "The two tallest are Network-Analyzer at 920,091 bytes and camera-count-tool at "
               "452,139 bytes.")


def build_languages(t: Theme) -> str:
    w, h = 880, 430
    void = "#04070C" if t.name == "dark" else "#05090F"
    b = [f'<rect width="{w}" height="{h}" rx="10" fill="{void}"/>',
         chrome(t, w, h, "osama@github: ~ \u2014 languages --scan", card=False)]
    b.append(rich(24, 62, [
        ("\u2514\u2500", t.dim), ("$", t.green), (" languages ", t.bright),
        ("--scan --projection=iso", t.orange),
    ], 12.5))

    total = sum(LANG_BYTES.values())
    vol = sorted(LANG_BYTES.items(), key=lambda kv: -kv[1])
    brd = sorted(LANG_BREADTH.items(), key=lambda kv: -kv[1])

    def podium(items: list[tuple[str, int]], heights: list[float],
               box: tuple[float, float, float, float], caption: list[tuple[str, str]],
               labeller) -> None:
        faces: list[g3.Face] = []
        n = len(items)
        plate = [g3.iso(pt, 0, 0, 1) for pt in
                 ((-0.25, 0, -0.25), (n + 0.25, 0, -0.25),
                  (n + 0.25, 0, 1.25), (-0.25, 0, 1.25))]
        faces.append(g3.Face(plate, g3.mix(void, t.cyan, 0.08), -999))
        for i, ((name, _), hh) in enumerate(zip(items, heights)):
            c = lang_colour(t, name)
            faces += g3.iso_box(i + 0.13, 0.13, 0.74, 0.74, hh, c, 0, 0, 1,
                                edge=g3.shade(c, 1.4))
        b.append(fit(faces, box))
        bx, by, bw, bh = box
        b.append(rich(bx, by - 18, caption, 11, "700"))
        step = bw / n
        for i, (name, val) in enumerate(items):
            cx = bx + step * (i + 0.5)
            b.append(text(cx, by + bh + 20, name, lang_colour(t, name), 10.5, anchor="middle"))
            for k, line in enumerate(labeller(name, val)):
                b.append(text(cx, by + bh + 34 + k * 12, line, t.dim, 9, anchor="middle"))

    podium(vol, [max(0.18, (math.log10(v + 1) - 2.4) * 0.72) for _, v in vol],
           (36, 112, 410, 182),
           [("BY VOLUME", t.cyan), ("   log\u2081\u2080 bytes", t.dim)],
           lambda n, v: (f"{v / total * 100:.2f}%", f"{v:,} B"))
    podium(brd, [0.28 + v / max(LANG_BREADTH.values()) * 1.5 for _, v in brd],
           (486, 112, 350, 182),
           [("BY BREADTH", t.green), ("   repos led", t.dim)],
           lambda n, v: (f"{v} repos",))

    b.append(rich(24, 410, [
        ("note", t.yellow),
        ("  log-scaled bars; exact bytes and linear percentages printed beneath each. "
         "No skill level is implied.", t.dim),
    ], 10.5))
    b.append(f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="10" fill="none" '
             f'stroke="{t.border}" stroke-width="1"/>')
    return svg(w, h, "\n".join(b) + "\n",
               "Language distribution as isometric solids",
               "Two isometric podiums. By volume, log scaled: Python 93.02 percent at "
               "1,513,981 bytes, HTML 4.72, CSS 1.29, JavaScript 0.82, Inno Setup 0.16. "
               "By breadth, repositories where the language leads: Python 11, HTML 9, "
               "JavaScript 6, CSS 2.")


def build_fastfetch(t: Theme) -> str:
    w, h = 880, 344
    void = "#04070C" if t.name == "dark" else "#05090F"
    b = [f'<rect width="{w}" height="{h}" rx="10" fill="{void}"/>',
         chrome(t, w, h, "osama@github: ~ \u2014 fastfetch", card=False)]

    b.append(f'''<defs><radialGradient id="lensglow" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="{t.cyan}" stop-opacity="0.22"/>
      <stop offset="1" stop-color="{t.cyan}" stop-opacity="0"/>
    </radialGradient></defs>''')
    b.append(f'<ellipse cx="118" cy="190" rx="118" ry="112" fill="url(#lensglow)"/>')

    verts, edges = g3.torus(1.0, 0.36, 15, 8)
    tilted = [g3.rotate(v, ax=math.radians(66), az=math.radians(-12)) for v in verts]
    b.append(g3.depth_wire(tilted, edges, 118, 190, 1, 150, 3.4, t.cyan,
                           g3.mix(void, t.blue, 0.45)))

    kx, vx = 264, 380
    b.append(rich(kx, 76, [("osama", t.green), ("@", t.dim), ("github", t.cyan)], 13, "700"))
    b.append(f'<line x1="{kx}" y1="88" x2="{w - 28}" y2="88" stroke="{t.rule}" stroke-width="1"/>')

    lang_parts: list[tuple[str, str]] = []
    for i, name in enumerate(LANG_BYTES):
        if i:
            lang_parts.append(("  \u00b7  ", t.dim))
        lang_parts.append((name, lang_colour(t, name)))

    rows: list[tuple[str, list[tuple[str, str]]]] = [
        ("Host", [("Windows 11", t.text), ("  \u00b7  ", t.dim), ("WSL2", t.text),
                  ("  \u00b7  ", t.dim), ("Linux", t.text)]),
        ("Shell", [("PowerShell", t.text), ("  \u00b7  ", t.dim), ("bash", t.text)]),
        ("Editor", [("VS Code", t.text), ("  \u00b7  ", t.dim), ("Git", t.text)]),
        ("Role", [("Database Administrator", t.purple), ("  \u00b7  ", t.dim),
                  ("The Bank of Punjab", t.dim)]),
        ("Previous", [("Camera / Image Evaluation Engineer", t.yellow)]),
        ("Repos", [(f"{PUBLIC_REPOS} public", t.cyan), ("  \u00b7  ", t.dim),
                   (f"{TRACKED_FILES} tracked files", t.dim)]),
        ("Languages", lang_parts),
        ("Surface", [("CLI", t.green), ("  \u00b7  ", t.dim), ("desktop GUI", t.green),
                     ("  \u00b7  ", t.dim), ("diagnostics", t.green)]),
        ("Domains", [("QA", t.text), ("  \u00b7  ", t.dim), ("camera IQ", t.text),
                     ("  \u00b7  ", t.dim), ("database ops", t.text),
                     ("  \u00b7  ", t.dim), ("networking", t.text)]),
        ("Uptime", [("since 2021-11-03", t.dim)]),
    ]
    y = 112
    for key, parts in rows:
        b.append(text(kx, y, key, t.dim, 12.5))
        b.append(rich(vx, y, parts, 12.5))
        y += 20

    b.append(f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="10" fill="none" '
             f'stroke="{t.border}" stroke-width="1"/>')
    return svg(w, h, "\n".join(b) + "\n",
               "System information panel for Osama Anwar",
               "A fastfetch-style panel beside a wireframe torus rendered in 3D. Host "
               "Windows 11, WSL2 and Linux. Shell PowerShell and bash. Current role Database "
               "Administrator at The Bank of Punjab. Previous role Camera and Image Evaluation "
               f"Engineer. {PUBLIC_REPOS} public repositories containing {TRACKED_FILES} "
               "tracked files. Languages Python, HTML, CSS, JavaScript and Inno Setup.")


STAGES = ["SPEC", "BUILD", "TEST", "MEASURE", "DEBUG", "VERIFY", "SHIP"]


def build_pipeline(t: Theme) -> str:
    w, h = 880, 252
    void = "#04070C" if t.name == "dark" else "#05090F"
    b = [f'<rect width="{w}" height="{h}" rx="10" fill="{void}"/>',
         chrome(t, w, h, "osama@github: ~ \u2014 workflow", card=False)]
    b.append(rich(24, 62, [
        ("\u2514\u2500", t.dim), ("$", t.green), (" workflow ", t.bright),
        ("--execute --projection=iso", t.orange),
    ], 12.5))

    # Stepping +x and -z together moves purely sideways in isometric, so the
    # stages sit in a level row instead of marching down the screen.
    k, ox, oy = 62, 88, 150
    size, lift = 0.8, 0.52
    ramp = [t.cyan, t.blue, t.green, t.yellow, t.orange, t.purple, t.green]

    faces: list[g3.Face] = []
    centres: list[float] = []
    for i, _ in enumerate(STAGES):
        gx, gz = i, -i
        faces += g3.iso_box(gx, gz, size, size, lift, ramp[i], ox, oy, k,
                            edge=g3.shade(ramp[i], 1.45))
        centres.append((gx + size / 2 - (gz + size / 2)) * g3.COS30 * k + ox)
    b.append("".join(f.svg() for f in faces))

    for i, stage in enumerate(STAGES):
        b.append(text(centres[i], 96, f"{i + 1:02d}", t.dim, 9, anchor="middle"))
        b.append(text(centres[i], 112, stage, ramp[i], 12.5, "700", anchor="middle"))
        if i < len(STAGES) - 1:
            mid = (centres[i] + centres[i + 1]) / 2
            b.append(f'<path d="M{mid - 4} 143 l5 6 -5 6" fill="none" stroke="{t.dim}" '
                     f'stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>')

    # Regression path: VERIFY back to BUILD.
    x_v, x_b = centres[5], centres[1]
    b.append(f'<path d="M{x_v} 190 V216 H{x_b} V190" fill="none" stroke="{t.red}" '
             f'stroke-width="1.2" stroke-dasharray="4 4"/>')
    b.append(f'<path d="M{x_b - 4.5} 197 l4.5 -7 4.5 7" fill="none" stroke="{t.red}" '
             f'stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>')
    b.append(f'<rect x="{(x_v + x_b) / 2 - 80}" y="206" width="160" height="19" rx="4" fill="{void}"/>')
    b.append(text((x_v + x_b) / 2, 220, "regression \u2192 retest", t.red, 10.5, anchor="middle"))

    b.append(f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="10" fill="none" '
             f'stroke="{t.border}" stroke-width="1"/>')
    return svg(w, h, "\n".join(b) + "\n",
               "Engineering workflow pipeline in isometric projection",
               "Seven isometric blocks in a row: spec, build, test, measure, debug, verify, "
               "ship. A dashed regression path returns from verify to build.")


def _gh(*args: str) -> str:
    return subprocess.run(["gh", *args], capture_output=True, encoding="utf-8",
                          errors="replace", check=True).stdout


def fetch_snapshot() -> None:
    """Re-query GitHub and replace the in-memory snapshot, then print it.

    This repository is skipped so the profile never counts its own generator
    toward the statistics it publishes.
    """
    global PUBLIC_REPOS, TRACKED_FILES
    names = [r["name"] for r in json.loads(_gh("repo", "list", USER, "--limit", "200",
                                               "--json", "name"))]
    byte_totals: dict[str, int] = {}
    leads: dict[str, int] = {}
    blocks: list[tuple[str, int, str]] = []
    files = 0
    for name in names:
        if name == USER:
            continue
        langs = json.loads(_gh("api", f"repos/{USER}/{name}/languages") or "{}")
        for lang, size in langs.items():
            byte_totals[lang] = byte_totals.get(lang, 0) + size
        if langs:
            leads[max(langs, key=langs.get)] = leads.get(max(langs, key=langs.get), 0) + 1
        tree = _gh("api", f"repos/{USER}/{name}/git/trees/HEAD?recursive=1",
                   "--jq", '[.tree[]|select(.type=="blob")]|length').strip()
        files += int(tree) if tree.isdigit() else 0
        blocks.append((name, sum(langs.values()), max(langs, key=langs.get) if langs else ""))

    LANG_BYTES.clear()
    LANG_BYTES.update(dict(sorted(byte_totals.items(), key=lambda kv: -kv[1])))
    LANG_BREADTH.clear()
    LANG_BREADTH.update(dict(sorted(leads.items(), key=lambda kv: -kv[1])))
    REPO_BLOCKS[:] = sorted(blocks, key=lambda r: -r[1])
    PUBLIC_REPOS, TRACKED_FILES = len(names), files

    print("# Paste over the snapshot constants:")
    print(f"LANG_BYTES = {json.dumps(LANG_BYTES, indent=4)}")
    print(f"LANG_BREADTH = {json.dumps(LANG_BREADTH, indent=4)}")
    print(f"PUBLIC_REPOS = {PUBLIC_REPOS}")
    print(f"TRACKED_FILES = {TRACKED_FILES}")
    print(f"REPO_BLOCKS = {json.dumps(REPO_BLOCKS, indent=4)}\n")


BUILDERS = {
    "header": build_header,
    "fastfetch": build_fastfetch,
    "matrix": build_matrix,
    "languages": build_languages,
    "pipeline": build_pipeline,
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true",
                        help="re-query GitHub before rendering")
    if parser.parse_args().fetch:
        fetch_snapshot()

    for stem, builder in BUILDERS.items():
        for theme in (DARK, LIGHT):
            path = OUT / f"{stem}-{theme.name}.svg"
            path.write_text(builder(theme), encoding="utf-8")
            print(f"  wrote {path.name:<26}{path.stat().st_size / 1024:6.1f} KB")


if __name__ == "__main__":
    main()
