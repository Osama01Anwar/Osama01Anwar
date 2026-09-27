"""JetBrains Mono rendered as SVG geometry.

GitHub serves repository SVGs with ``Content-Security-Policy: default-src
'none'``, so an SVG can neither fetch nor embed a font. Text therefore ships
as glyph outlines: each glyph is defined once in ``<defs>`` and placed with
``<use>``. Because the face is monospaced, every width and anchor is exact.
"""

from __future__ import annotations

import io
import urllib.request
import zipfile
from functools import lru_cache
from pathlib import Path

from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont

RELEASE = "https://github.com/JetBrains/JetBrainsMono/releases/download/v2.304/JetBrainsMono-2.304.zip"
WEIGHTS = {"regular": "Regular", "medium": "Medium", "bold": "Bold", "heavy": "ExtraBold"}
CACHE = Path(__file__).resolve().parent / ".fonts"


def ensure_fonts() -> Path:
    """Download the OFL-licensed release once; the repo never stores the TTFs."""
    CACHE.mkdir(exist_ok=True)
    if all((CACHE / f"JetBrainsMono-{w}.ttf").exists() for w in WEIGHTS.values()):
        return CACHE
    with urllib.request.urlopen(RELEASE, timeout=120) as r:
        z = zipfile.ZipFile(io.BytesIO(r.read()))
    for name in z.namelist():
        base = name.rsplit("/", 1)[-1]
        if "/ttf/" in name and base in {f"JetBrainsMono-{w}.ttf" for w in WEIGHTS.values()}:
            (CACHE / base).write_bytes(z.read(name))
    return CACHE


@lru_cache(maxsize=None)
def _font(weight: str) -> TTFont:
    return TTFont(ensure_fonts() / f"JetBrainsMono-{WEIGHTS[weight]}.ttf")


@lru_cache(maxsize=None)
def _outline(weight: str, ch: str) -> tuple[str, int]:
    """Path data in font units (y flipped to SVG-down) and the advance width."""
    f = _font(weight)
    gname = f.getBestCmap().get(ord(ch)) or ".notdef"
    gs = f.getGlyphSet()
    pen = RelativePen(gs)
    gs[gname].draw(pen)
    return pen.path(), gs[gname].width


class RelativePen(BasePen):
    """Emit compact *relative* SVG path data straight from the glyph's draw calls.

    Absolute coordinates are rounded first and deltas taken between rounded
    points, so rounding never accumulates. BasePen decomposes TrueType
    qCurveTo runs (with implied on-curve points) into single quadratic segments.
    Output is flipped to SVG's y-down space.
    """

    def __init__(self, glyphset) -> None:
        super().__init__(glyphset)
        self.out: list[str] = []
        self.cur = (0, 0)
        self.start = (0, 0)

    @staticmethod
    def _pt(p) -> tuple[int, int]:
        return round(p[0]), -round(p[1])

    def _emit(self, cmd: str, nums: list[int]) -> None:
        body = ""
        for n in nums:
            t = str(n)
            body += t if (not body or t.startswith("-")) else " " + t
        self.out.append(cmd + body)

    def _moveTo(self, p) -> None:
        x, y = self._pt(p)
        self._emit("m", [x - self.cur[0], y - self.cur[1]])
        self.cur = self.start = (x, y)

    def _lineTo(self, p) -> None:
        x, y = self._pt(p)
        dx, dy = x - self.cur[0], y - self.cur[1]
        if dy == 0:
            self._emit("h", [dx])
        elif dx == 0:
            self._emit("v", [dy])
        else:
            self._emit("l", [dx, dy])
        self.cur = (x, y)

    def _qCurveToOne(self, p1, p2) -> None:
        (x1, y1), (x, y) = self._pt(p1), self._pt(p2)
        cx, cy = self.cur
        self._emit("q", [x1 - cx, y1 - cy, x - cx, y - cy])
        self.cur = (x, y)

    def _curveToOne(self, p1, p2, p3) -> None:
        (x1, y1), (x2, y2), (x, y) = self._pt(p1), self._pt(p2), self._pt(p3)
        cx, cy = self.cur
        self._emit("c", [x1 - cx, y1 - cy, x2 - cx, y2 - cy, x - cx, y - cy])
        self.cur = (x, y)

    def _closePath(self) -> None:
        self.out.append("z")
        self.cur = self.start

    _endPath = _closePath

    def path(self) -> str:
        return "".join(self.out)


UPM = 1000
ADVANCE = 600          # JetBrains Mono is strictly monospaced at 600/1000 em


class Glyphs:
    """Collects the glyphs one SVG uses and emits them as a single <defs>."""

    def __init__(self) -> None:
        self._used: dict[str, str] = {}

    # Medium duplicated nearly every regular glyph in every file for a barely
    # visible difference at micro-label sizes, so it renders as regular.
    ALIAS = {"medium": "regular"}

    def _id(self, weight: str, ch: str) -> str | None:
        if ch == " ":
            return None
        weight = self.ALIAS.get(weight, weight)
        gid = f"{weight[0]}{ord(ch):x}"
        if gid not in self._used:
            d, _ = _outline(weight, ch)
            self._used[gid] = d
        return gid

    @staticmethod
    def width(s: str, size: float, spacing: float = 0) -> float:
        return len(s) * ADVANCE * size / UPM + max(0, len(s) - 1) * spacing

    def text(self, x: float, y: float, s: str, size: float, fill: str,
             weight: str = "regular", spacing: float = 0, anchor: str = "start",
             opacity: float = 1.0) -> str:
        """Baseline-anchored monospace text as <use> references."""
        w = self.width(s, size, spacing)
        if anchor == "middle":
            x -= w / 2
        elif anchor == "end":
            x -= w
        k = size / UPM
        step = ADVANCE + spacing / k
        uses = []
        for i, ch in enumerate(s):
            gid = self._id(weight, ch)
            if gid:
                uses.append(f'<use href="#{gid}" x="{i * step:.0f}"/>')
        op = f' opacity="{opacity}"' if opacity < 1 else ""
        return (f'<g fill="{fill}"{op} transform="translate({x:.1f} {y:.1f}) '
                f'scale({k:.5f})">{"".join(uses)}</g>')

    def defs(self) -> str:
        return "".join(f'<path id="{g}" d="{d}"/>' for g, d in self._used.items())
