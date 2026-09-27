"""Design tokens, the SVG document model and the shared primitives.

    python build.py            # render from the committed snapshot
    python fetch.py            # refresh the snapshot from the GitHub API first

All text is JetBrains Mono, drawn as glyph outlines (see glyphs.py) because
GitHub's CSP blocks fonts inside repository SVGs.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from glyphs import Glyphs

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / "profile.json").read_text(encoding="utf-8"))
OUT = HERE.parent          # assets/desktop and assets/mobile

# --- tokens (DESIGN_SYSTEM.md) ------------------------------------------------
BG = "#06070B"
SURFACE = "#0C0E14"
SURFACE_ACTIVE = "#1F0C0E"
BORDER = "#2A2C33"
RULE = "#1C1F27"
TEXT = "#ECE7DD"
TEXT_2 = "#A8A397"
MUTED = "#89847B"
ACCENT = "#E8742A"
ACCENT_HI = "#F6A864"
ACCENT_DEEP = "#9A410B"
SLATE = "#6E9A9A"
SLATE_DEEP = "#0E3944"
NAVY = "#16263A"
AMBER = "#E3B341"
RED = "#D8473A"
INK = "#140804"          # text on the bright badge square

W = 880


@dataclass
class Doc:
    """One SVG: a glyph bank, extra defs and body markup."""

    h: int
    title: str
    desc: str
    w: int = 880
    glyphs: Glyphs = field(default_factory=Glyphs)
    defs: list[str] = field(default_factory=list)
    body: list[str] = field(default_factory=list)

    def add(self, *parts: str) -> None:
        self.body.extend(parts)

    def t(self, x: float, y: float, s: str, size: float, fill: str, weight: str = "regular",
          spacing: float = 0, anchor: str = "start", opacity: float = 1.0) -> str:
        return self.glyphs.text(x, y, s, size, fill, weight, spacing, anchor, opacity)

    def text(self, *a, **k) -> None:
        self.add(self.t(*a, **k))

    def render(self) -> str:
        esc = lambda s: s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}" role="img" aria-labelledby="t d">'
                f'<title id="t">{esc(self.title)}</title><desc id="d">{esc(self.desc)}</desc>'
                f'<defs>{self.glyphs.defs()}{"".join(self.defs)}</defs>'
                f'{"".join(self.body)}</svg>\n')


# --- primitives ---------------------------------------------------------------

def rect(x: float, y: float, w: float, h: float, fill: str, stroke: str = "",
         opacity: float = 1.0, rx: float = 0) -> str:
    st = f' stroke="{stroke}" stroke-width="1"' if stroke else ""
    op = f' opacity="{opacity}"' if opacity < 1 else ""
    r = f' rx="{rx}"' if rx else ""
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"{r} fill="{fill}"{st}{op}/>'


def line(x1: float, y1: float, x2: float, y2: float, colour: str, width: float = 1,
         opacity: float = 1.0) -> str:
    op = f' opacity="{opacity}"' if opacity < 1 else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{colour}" stroke-width="{width}"{op}/>')


def frame(d: Doc) -> None:
    """Card base and edge. The edge colour reads on both GitHub themes."""
    d.body.insert(0, rect(0, 0, d.w, d.h, BG))
    d.add(rect(0.5, 0.5, d.w - 1, d.h - 1, "none", BORDER))


def badge(d: Doc, x: float, y: float, index: str, code: str, s: float = 44,
          active: bool = True) -> None:
    """IndexBadge: rust square with the index over a lit square with the code."""
    top, low = (ACCENT_DEEP, ACCENT) if active else ("#3A1A0E", "#5A2A12")
    d.add(rect(x, y, s, s, top), rect(x, y + s, s, s, low))
    d.text(x + s / 2, y + s * 0.66, index, s * 0.42, TEXT, "heavy", anchor="middle")
    d.text(x + s / 2, y + s * 1.66, code, s * 0.42, INK if active else TEXT_2, "heavy",
           anchor="middle")


def pair(d: Doc, x: float, y: float, dim: str, bright: str, size: float = 15,
         bright_fill: str = TEXT) -> float:
    """LabelPair. Returns the x where the pair ends."""
    d.text(x, y, dim.upper(), size, MUTED, "bold", spacing=0.5)
    bx = x + d.glyphs.width(dim, size, 0.5) + size * 0.8
    d.text(bx, y, bright.upper(), size, bright_fill, "bold", spacing=0.5)
    return bx + d.glyphs.width(bright, size, 0.5)


def tick_rule(d: Doc, x: float, y: float, length: float, lit: bool = True) -> None:
    """TickRule: long hairline led by a short, heavier orange tick."""
    d.add(rect(x, y + 5, 20, 3, ACCENT if lit else ACCENT_DEEP),
          rect(x + 26, y, length - 26, 2.5, TEXT_2, opacity=0.55 if lit else 0.25))


def micro(d: Doc, x: float, y: float, label: str, value: str = "", anchor: str = "start",
          value_fill: str = TEXT_2) -> None:
    """MicroLabel: muted key, optional value beside it."""
    if not value:
        d.text(x, y, label.upper(), 9, MUTED, "medium", spacing=0.8, anchor=anchor)
        return
    d.text(x, y, label.upper(), 9, MUTED, "medium", spacing=0.8)
    d.text(x + d.glyphs.width(label, 9, 0.8) + 8, y, value, 9, value_fill, "medium",
           spacing=0.4)


def stat_cell(d: Doc, x: float, y: float, w: float, head: tuple[str, str],
              cells: list[tuple[str, str, str]], h: float = 52) -> None:
    """StatCell: header pair over a divided row of label/value cells."""
    d.text(x, y, head[0].upper(), 11, MUTED, "bold", spacing=1)
    d.text(x + d.glyphs.width(head[0], 11, 1) + 9, y, head[1].upper(), 11, TEXT, "bold",
           spacing=1)
    top = y + 10
    d.add(rect(x, top, w, h, "#0A0C12", RULE))
    cw = w / len(cells)
    for i, (label, value, colour) in enumerate(cells):
        cx = x + i * cw
        if i:
            d.add(line(cx, top + 8, cx, top + h - 8, RULE))
        d.text(cx + 12, top + 18, label.upper(), 9, MUTED, "medium", spacing=0.8)
        d.text(cx + 12, top + 40, value.upper(), 17, colour, "heavy")


def prompt(d: Doc, x: float, y: float, command: str, size: float = 12,
           cursor: bool = False) -> None:
    """Terminal prompt in the house grammar: user@host slate, $ orange."""
    host = "osama@github:~"
    d.text(x, y, host, size, SLATE, "medium")
    px = x + d.glyphs.width(host, size)
    d.text(px, y, "$", size, ACCENT, "bold")
    cx = px + d.glyphs.width("$ ", size)
    d.text(cx, y, command, size, TEXT, "medium")
    if cursor:
        ex = cx + d.glyphs.width(command + " ", size)
        d.add(f'<rect x="{ex:.1f}" y="{y - size * 0.8:.1f}" width="{size * 0.55:.1f}" '
              f'height="{size * 0.95:.1f}" fill="{ACCENT}">'
              f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" '
              f'dur="1.1s" repeatCount="indefinite"/></rect>')


def chevrons(d: Doc, x: float, y: float, n: int = 3, size: float = 7,
             colour: str = ACCENT_HI) -> float:
    for i in range(n):
        cx = x + i * (size + 3)
        d.add(f'<path d="M{cx:.1f} {y - size:.1f} l{size * 0.8:.1f} {size * 0.5:.1f} '
              f'l{-size * 0.8:.1f} {size * 0.5:.1f}" fill="none" stroke="{colour}" '
              f'stroke-width="2" stroke-linejoin="miter"/>')
    return x + n * (size + 3)


def blur(d: Doc, ident: str, sd: float) -> str:
    d.defs.append(f'<filter id="{ident}" x="-5%" y="-20%" width="110%" height="140%">'
                  f'<feGaussianBlur stdDeviation="{sd}"/></filter>')
    return ident


# --- hero ---------------------------------------------------------------------

def record(d: Doc, x: float, y: float, w: float, h: float, active: bool, idx: str, code: str,
           dim: str, bright: str, big: str, micros: list[tuple[str, str]],
           stat: tuple[tuple[str, str], list[tuple[str, str, str]]] | None,
           big_size: float = 44, side: list[tuple[str, str]] | None = None,
           stub_x: float | None = None) -> None:
    """RecordCard on a fixed grid: pair 28, rule 38, code 52+size, micros h-10."""
    if stub_x is not None:
        d.add(line(stub_x, y + h / 2, x, y + h / 2, ACCENT, 1, 0.55),
              rect(stub_x - 2, y + h / 2 - 2, 4, 4, ACCENT))
    d.add(rect(x, y, w, h, SURFACE_ACTIVE if active else SURFACE,
               ACCENT if active else BORDER))
    if active:
        d.add(rect(x, y, 3, h, ACCENT))
    s = 44
    badge(d, x + 20, y + (h - 2 * s) / 2, idx, code, s, active)
    lx = x + 20 + s + 24
    pair(d, lx, y + 28, dim, bright)
    tick_rule(d, lx, y + 38, min(380, w * 0.46), active)
    d.text(lx, y + 52 + big_size, big, big_size, TEXT if active else TEXT_2, "heavy",
           spacing=-1)
    mx = lx
    for k, v in micros:
        micro(d, mx, y + h - 10, k, v)
        mx += d.glyphs.width(k, 9, 0.8) + d.glyphs.width(v, 9, 0.4) + 30
    sw = 270
    sx = x + w - sw - 22
    if side:
        cx = lx + d.glyphs.width(big, big_size, -1) + 36
        for i, (k, v) in enumerate(side):
            micro(d, cx, y + 76 + i * 16, k, v)
    if stat:
        stat_cell(d, sx, y + 28, sw, stat[0], stat[1])


def items(d: Doc, x: float, y: float, entries: list[tuple[str, bool]], max_x: float,
          size: float = 12, pitch: float = 22, boxed: bool = True) -> float:
    """Evidence-marked items flowing left to right, wrapping at ``max_x``.

    ``True`` = present in a public repository (orange), ``False`` = professional
    or environment record (slate). Returns the baseline of the last row.
    """
    cx = x
    for name, repo in entries:
        w = d.glyphs.width(name, size) + (30 if boxed else 22)
        if cx + w > max_x and cx > x:
            cx, y = x, y + pitch
        colour = ACCENT if repo else SLATE
        if boxed:
            d.add(rect(cx, y - size - 3, w - 8, size + 10, "#0A0C12", RULE))
        mx = cx + (9 if boxed else 0)
        d.add(rect(mx, y - size * 0.62, 6, 6, colour) if repo
              else f'<rect x="{mx + 0.5:.1f}" y="{y - size * 0.62 + 0.5:.1f}" width="5" '
                   f'height="5" fill="none" stroke="{colour}" stroke-width="1.2"/>')
        d.text(mx + 13, y, name, size, TEXT if repo else TEXT_2, "regular")
        cx += w
    return y


def wrap(s: str, size: float, width: float) -> list[str]:
    """Greedy word wrap. The face is monospaced, so the fit is exact."""
    cap = max(1, int(width // (size * 0.6)))
    lines: list[str] = []
    cur = ""
    for word in s.split(" "):
        cand = f"{cur} {word}" if cur else word
        if len(cand) <= cap:
            cur = cand
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def hollow(x: float, y: float, colour: str = SLATE) -> str:
    """The professional-record marker: an outlined square."""
    return (f'<rect x="{x + 0.5:.1f}" y="{y + 0.5:.1f}" width="5" height="5" fill="none" '
            f'stroke="{colour}" stroke-width="1.2"/>')


def marker(x: float, y: float, repo: bool) -> str:
    """Evidence marker: filled orange = public repository, hollow slate = record."""
    return rect(x, y, 6, 6, ACCENT) if repo else hollow(x, y)


def legend(d: Doc, x: float, y: float, stacked: bool = False) -> None:
    """The evidence legend, identical wherever it appears."""
    a, b = "IN A PUBLIC REPOSITORY", "PROFESSIONAL / ENVIRONMENT RECORD"
    d.add(marker(x, y - 7, True))
    d.text(x + 13, y, a, 9, TEXT_2, "medium", spacing=0.8)
    ox, oy = (x, y + 16) if stacked else (x + 13 + d.glyphs.width(a, 9, 0.8) + 24, y)
    d.add(marker(ox, oy - 7, False))
    d.text(ox + 13, oy, b, 9, TEXT_2, "medium", spacing=0.8)


def micro_row(d: Doc, right: float, y: float, parts: list[tuple[str, str]]) -> None:
    """Right-aligned run of key/value micro-labels, laid out right to left."""
    mx = right
    for k, v in parts:
        w = d.glyphs.width(k, 9, 0.8) + 8 + d.glyphs.width(v, 9, 0.4)
        micro(d, mx - w, y, k, v)
        mx -= w + 26


def section_bar(d: Doc, left: str, path: str, y: float = 0, h: float = 36,
                size: float = 11) -> float:
    """The slate breadcrumb bar: LABEL >>> /path. Returns where the path ends."""
    d.add(rect(0, y, d.w, h, "#0A1C22"), line(0, y + h + 0.5, d.w, y + h + 0.5, SLATE_DEEP))
    base = y + h / 2 + size * 0.36
    x = 22 if d.w < 600 else 52
    d.text(x, base, left, size, TEXT, "bold", spacing=1.2)
    cx = chevrons(d, x + d.glyphs.width(left, size, 1.2) + 10, base - 1,
                  size=size * 0.64)
    if path:
        d.text(cx + 8, base, path, size, SLATE, "medium")
        return cx + 8 + d.glyphs.width(path, size)
    return cx
