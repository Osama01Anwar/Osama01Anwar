"""Minimal 3D projection helpers for the profile's generated SVG assets.

Everything the README renders in "3D" is projected through this module rather
than drawn by eye: isometric solids for data, perspective for the hero grid,
and a real icosahedron for the wireframe. Right-handed coords, +y is up.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

Vec3 = tuple[float, float, float]

COS30 = math.cos(math.radians(30))
SIN30 = math.sin(math.radians(30))


# --- colour ------------------------------------------------------------------

def shade(hex_colour: str, k: float) -> str:
    """Scale a hex colour's brightness by ``k``, clamped to the 0-255 range."""
    h = hex_colour.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(c * k))) for c in (r, g, b))


def mix(a: str, b: str, t: float) -> str:
    """Linear blend between two hex colours, ``t`` in 0..1."""
    ah, bh = a.lstrip("#"), b.lstrip("#")
    out = []
    for i in (0, 2, 4):
        ca, cb = int(ah[i:i + 2], 16), int(bh[i:i + 2], 16)
        out.append(max(0, min(255, round(ca + (cb - ca) * t))))
    return "#%02x%02x%02x" % tuple(out)


# --- rotation ----------------------------------------------------------------

def rotate(p: Vec3, ax: float = 0, ay: float = 0, az: float = 0) -> Vec3:
    """Rotate a point by the given angles in radians, applied X then Y then Z."""
    x, y, z = p
    if ax:
        c, s = math.cos(ax), math.sin(ax)
        y, z = y * c - z * s, y * s + z * c
    if ay:
        c, s = math.cos(ay), math.sin(ay)
        x, z = x * c + z * s, -x * s + z * c
    if az:
        c, s = math.cos(az), math.sin(az)
        x, y = x * c - y * s, x * s + y * c
    return (x, y, z)


# --- projection ---------------------------------------------------------------

def iso(p: Vec3, ox: float = 0, oy: float = 0, scale: float = 1) -> tuple[float, float]:
    """True isometric projection. Larger x+z is nearer the viewer."""
    x, y, z = p
    return (ox + (x - z) * COS30 * scale,
            oy + ((x + z) * SIN30 - y) * scale)


def iso_depth(p: Vec3) -> float:
    """Painter's-algorithm key: draw ascending, so nearer solids land last."""
    return p[0] + p[2]


def perspective(p: Vec3, ox: float, oy: float, focal: float,
                eye: float) -> tuple[float, float, float] | None:
    """Project with a pinhole camera at ``eye`` on -z. None when behind it."""
    x, y, z = p
    d = z + eye
    if d <= 0.01:
        return None
    k = focal / d
    return (ox + x * k, oy - y * k, d)


# --- solids -------------------------------------------------------------------

@dataclass(frozen=True)
class Face:
    """A projected polygon plus the values needed to sort and shade it."""

    points: list[tuple[float, float]]
    fill: str
    depth: float
    stroke: str = ""
    opacity: float = 1.0

    def svg(self) -> str:
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in self.points)
        # non-scaling-stroke keeps edges hairline even when the group is scaled
        # to fit its box, which would otherwise multiply the stroke width too.
        st = (f' stroke="{self.stroke}" stroke-width="1" stroke-linejoin="round"'
              f' vector-effect="non-scaling-stroke"' if self.stroke else "")
        op = f' opacity="{self.opacity:.2f}"' if self.opacity < 1 else ""
        return f'<polygon points="{pts}" fill="{self.fill}"{st}{op}/>'


# Face brightness for an isometric box lit from the upper front-left.
TOP, RIGHT, FRONT = 1.0, 0.62, 0.40


def iso_box(gx: float, gz: float, w: float, d: float, h: float, colour: str,
            ox: float, oy: float, scale: float, edge: str = "",
            opacity: float = 1.0) -> list[Face]:
    """Three visible faces of an axis-aligned box standing on the y=0 plane."""
    def P(x: float, y: float, z: float) -> tuple[float, float]:
        return iso((x, y, z), ox, oy, scale)

    x0, x1, z0, z1 = gx, gx + w, gz, gz + d
    depth = iso_depth((gx + w / 2, 0, gz + d / 2))
    return [
        Face([P(x0, h, z0), P(x1, h, z0), P(x1, h, z1), P(x0, h, z1)],
             shade(colour, TOP), depth, edge, opacity),
        Face([P(x1, h, z0), P(x1, h, z1), P(x1, 0, z1), P(x1, 0, z0)],
             shade(colour, RIGHT), depth, edge, opacity),
        Face([P(x0, h, z1), P(x1, h, z1), P(x1, 0, z1), P(x0, 0, z1)],
             shade(colour, FRONT), depth, edge, opacity),
    ]


def icosahedron() -> tuple[list[Vec3], list[tuple[int, int]]]:
    """Unit-ish icosahedron as 12 vertices and its 30 unique edges."""
    g = (1 + 5 ** 0.5) / 2
    raw = [(0, 1, g), (0, -1, g), (0, 1, -g), (0, -1, -g),
           (1, g, 0), (-1, g, 0), (1, -g, 0), (-1, -g, 0),
           (g, 0, 1), (-g, 0, 1), (g, 0, -1), (-g, 0, -1)]
    n = math.sqrt(1 + g * g)
    verts = [(x / n, y / n, z / n) for x, y, z in raw]

    # Every vertex pair at the minimum separation forms an edge.
    def d2(a: Vec3, b: Vec3) -> float:
        return sum((p - q) ** 2 for p, q in zip(a, b))

    best = min(d2(verts[i], verts[j])
               for i in range(12) for j in range(i + 1, 12))
    edges = [(i, j) for i in range(12) for j in range(i + 1, 12)
             if abs(d2(verts[i], verts[j]) - best) < 1e-6]
    return verts, edges


def torus(major: float, minor: float, nu: int, nv: int
          ) -> tuple[list[Vec3], list[tuple[int, int]]]:
    """Wireframe torus: ``nu`` rings around the main axis, ``nv`` around the tube."""
    verts: list[Vec3] = []
    for i in range(nu):
        a = 2 * math.pi * i / nu
        for j in range(nv):
            t = 2 * math.pi * j / nv
            rr = major + minor * math.cos(t)
            verts.append((rr * math.cos(a), minor * math.sin(t), rr * math.sin(a)))

    edges: list[tuple[int, int]] = []
    for i in range(nu):
        for j in range(nv):
            here = i * nv + j
            edges.append((here, i * nv + (j + 1) % nv))          # around the tube
            edges.append((here, ((i + 1) % nu) * nv + j))        # along the ring
    return verts, edges


def depth_wire(verts: list[Vec3], edges: list[tuple[int, int]], cx: float, cy: float,
               scale: float, focal: float, eye: float, colour_near: str,
               colour_far: str) -> str:
    """Project a wireframe and fade each edge by depth, painted back to front."""
    pts, zs = [], []
    for v in verts:
        p = perspective(v, cx, cy, focal, eye)
        pts.append(p[:2] if p else (cx, cy))
        zs.append(p[2] if p else 99)
    lo, hi = min(zs), max(zs)
    span = (hi - lo) or 1

    drawn = []
    for i, j in edges:
        z = (zs[i] + zs[j]) / 2
        t = (z - lo) / span                      # 0 = nearest, 1 = farthest
        drawn.append((z, i, j, t))
    out = []
    for z, i, j, t in sorted(drawn, key=lambda e: -e[0]):
        out.append(f'<line x1="{pts[i][0]:.1f}" y1="{pts[i][1]:.1f}" '
                   f'x2="{pts[j][0]:.1f}" y2="{pts[j][1]:.1f}" '
                   f'stroke="{mix(colour_near, colour_far, t)}" '
                   f'stroke-width="{1.25 - 0.6 * t:.2f}" opacity="{0.95 - 0.62 * t:.2f}"/>')
    return "".join(out)
