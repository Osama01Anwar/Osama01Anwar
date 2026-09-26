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
import subprocess
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


def chrome(t: Theme, w: int, h: int, title: str) -> str:
    """The window frame: rounded card, title bar, traffic lights, caption."""
    return f"""  <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="10"
        fill="{t.bg}" stroke="{t.border}" stroke-width="1"/>
  <path d="M0.5 10.5a10 10 0 0 1 10-10h{w - 21}a10 10 0 0 1 10 10V34H0.5z"
        fill="{t.panel}"/>
  <line x1="0.5" y1="34" x2="{w - 0.5}" y2="34" stroke="{t.border}" stroke-width="1"/>
  <circle cx="20" cy="17.5" r="5" fill="{t.red}"/>
  <circle cx="38" cy="17.5" r="5" fill="{t.yellow}"/>
  <circle cx="56" cy="17.5" r="5" fill="{t.green}"/>
{text(w / 2, 22, title, t.dim, 11.5, anchor='middle')}
"""


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


def build_header(t: Theme) -> str:
    w, h = 880, 372
    langs = len(LANG_BYTES)
    boot = [
        ("identity", "done", t.green),
        ("engineering stack", "done", t.green),
        ("repository scan", f"{PUBLIC_REPOS} repos", t.cyan),
        ("language detect", f"{langs} langs", t.cyan),
    ]
    b = [chrome(t, w, h, "osama@github: ~/profile")]

    b.append(rich(24, 62, [
        ("\u250c\u2500\u2500(", t.dim), ("osama", t.green), ("@", t.dim),
        ("github", t.cyan), (")\u2500[", t.dim), ("~/profile", t.blue), ("]", t.dim),
    ]))
    b.append(rich(24, 82, [
        ("\u2514\u2500", t.dim), ("$", t.green), (" ./boot.sh ", t.bright),
        ("--identity --verbose", t.orange),
    ]))

    y = 114
    for label, result, colour in boot:
        b.append(rich(24, y, [
            ("[", t.dim), (" OK ", t.green), ("]", t.dim),
            (f"  {label + ' ':.<76} ", t.text), (result, colour),
        ]))
        y += 20

    b.append(f'<line x1="24" y1="212" x2="{w - 24}" y2="212" '
             f'stroke="{t.rule}" stroke-width="1"/>')

    b.append(text(24, 262, "OSAMA ANWAR", t.bright, 42, "700", spacing=6))
    b.append(rich(26, 292, [
        ("Software Engineer", t.cyan), (" \u00b7 ", t.dim),
        ("Quality Engineering", t.green), (" \u00b7 ", t.dim),
        ("Camera / Image Evaluation", t.yellow), (" \u00b7 ", t.dim),
        ("Database Operations", t.purple),
    ], 13))

    b.append(f'<rect x="16" y="312" width="{w - 32}" height="42" rx="7" '
             f'fill="{t.panel}" stroke="{t.rule}" stroke-width="1"/>')
    chips = [
        (32, "STATUS", "ONLINE", t.green),
        (196, "BASE", "PAKISTAN", t.text),
        (360, "MODE", "BUILD \u00b7 TEST \u00b7 ANALYZE", t.cyan),
        (624, "REPOS", f"{PUBLIC_REPOS} PUBLIC", t.text),
    ]
    for x, key, val, colour in chips:
        b.append(f'<rect x="{x}" y="320" width="2.5" height="26" rx="1.25" fill="{colour}"/>')
        b.append(text(x + 10, 331, key, t.dim, 9))
        b.append(text(x + 10, 345, val, colour, 12, "600"))
    b.append(text(w - 32, 345, f"data {SNAPSHOT_DATE}", t.dim, 9, anchor="end"))

    return svg(w, h, "\n".join(b) + "\n",
               "Osama Anwar - terminal profile header",
               "A terminal window showing a boot sequence, the name Osama Anwar, and the "
               "roles Software Engineer, Quality Engineering, Camera and Image Evaluation, "
               f"and Database Operations. Status online, based in Pakistan, {PUBLIC_REPOS} "
               "public repositories.")


def lang_colour(t: Theme, name: str) -> str:
    """One colour per language, shared by the fastfetch panel and the chart."""
    return {"Python": t.blue, "HTML": t.orange, "CSS": t.purple,
            "JavaScript": t.yellow, "Inno Setup": t.green}.get(name, t.text)


APERTURE = [
    "    \u2584\u2584\u2584\u2584\u2584\u2584\u2584\u2584\u2584",
    "  \u2584\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2584",
    " \u2588\u2588\u2588\u2588\u2580     \u2580\u2588\u2588\u2588\u2588",
    "\u2588\u2588\u2588\u2588\u2580   \u2584   \u2580\u2588\u2588\u2588\u2588",
    "\u2588\u2588\u2588    \u2588\u2588\u2588    \u2588\u2588\u2588",
    "\u2588\u2588\u2588\u2588\u2584   \u2580   \u2584\u2588\u2588\u2588\u2588",
    " \u2588\u2588\u2588\u2588\u2584     \u2584\u2588\u2588\u2588\u2588",
    "  \u2580\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2580",
    "    \u2580\u2580\u2580\u2580\u2580\u2580\u2580\u2580\u2580",
]


def build_fastfetch(t: Theme) -> str:
    w, h = 880, 336
    b = [chrome(t, w, h, "osama@github: ~ \u2014 fastfetch")]

    # A single vertical gradient reads as one lens ring; per-row colours banded.
    b.append(f'''<defs><linearGradient id="lens" x1="0" y1="0" x2="0.35" y2="1">
    <stop offset="0" stop-color="{t.cyan}"/><stop offset="1" stop-color="{t.green}"/>
  </linearGradient></defs>''')
    for i, line in enumerate(APERTURE):
        b.append(text(38, 130 + i * 16, line, "url(#lens)", 16))

    kx, vx = 236, 352
    b.append(rich(kx, 74, [("osama", t.green), ("@", t.dim), ("github", t.cyan)], 13, "700"))
    b.append(f'<line x1="{kx}" y1="86" x2="{w - 28}" y2="86" stroke="{t.rule}" stroke-width="1"/>')

    lang_parts: list[tuple[str, str]] = []
    for i, name in enumerate(LANG_BYTES):
        if i:
            lang_parts.append(("  ·  ", t.dim))
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

    y = 108
    for key, parts in rows:
        b.append(text(kx, y, key, t.dim, 12.5))
        b.append(rich(vx, y, parts, 12.5))
        y += 20

    return svg(w, h, "\n".join(b) + "\n",
               "System information panel for Osama Anwar",
               "A fastfetch-style panel beside a camera aperture drawn in block characters. "
               "Host Windows 11, WSL2 and Linux. Shell PowerShell and bash. Current role "
               "Database Administrator at The Bank of Punjab. Previous role Camera and Image "
               f"Evaluation Engineer. {PUBLIC_REPOS} public repositories containing "
               f"{TRACKED_FILES} tracked files. Languages Python, HTML, CSS, JavaScript and "
               "Inno Setup.")


def build_languages(t: Theme) -> str:
    w, h = 880, 396
    b = [chrome(t, w, h, "osama@github: ~ \u2014 languages --scan")]
    b.append(rich(24, 60, [
        ("\u2514\u2500", t.dim), ("$", t.green), (" languages ", t.bright),
        ("--scan --source=github-linguist", t.orange),
    ]))

    bx, bw = 150, 500          # bar origin and maximum bar length
    total = sum(LANG_BYTES.values())

    b.append(rich(24, 92, [
        ("BY VOLUME", t.cyan),
        (f"   bytes of code across {PUBLIC_REPOS} public repositories", t.dim),
    ], 12, "700"))
    y = 118
    for name, size in sorted(LANG_BYTES.items(), key=lambda kv: -kv[1]):
        pct = size / total * 100
        colour = lang_colour(t, name)
        b.append(text(24, y + 4, name, t.text, 12))
        b.append(f'<rect x="{bx}" y="{y - 8}" width="{bw}" height="13" rx="2.5" fill="{t.rule}"/>')
        b.append(f'<rect x="{bx}" y="{y - 8}" width="{max(3, bw * size / total):.1f}" '
                 f'height="13" rx="2.5" fill="{colour}"/>')
        b.append(text(bx + bw + 14, y + 4, f"{pct:5.2f}%", colour, 11.5))
        b.append(text(w - 24, y + 4, f"{size:,} B", t.dim, 11, anchor="end"))
        y += 22

    b.append(f'<line x1="24" y1="232" x2="{w - 24}" y2="232" stroke="{t.rule}" stroke-width="1"/>')

    b.append(rich(24, 258, [
        ("BY BREADTH", t.green),
        ("   repositories in which the language is the largest", t.dim),
    ], 12, "700"))
    peak = max(LANG_BREADTH.values())
    y = 284
    for name, count in sorted(LANG_BREADTH.items(), key=lambda kv: -kv[1]):
        colour = lang_colour(t, name)
        b.append(text(24, y + 4, name, t.text, 12))
        b.append(f'<rect x="{bx}" y="{y - 8}" width="{bw}" height="13" rx="2.5" fill="{t.rule}"/>')
        b.append(f'<rect x="{bx}" y="{y - 8}" width="{bw * count / peak:.1f}" '
                 f'height="13" rx="2.5" fill="{colour}"/>')
        b.append(text(bx + bw + 14, y + 4, f"{count:>2} repos", colour, 11.5))
        y += 22

    b.append(rich(24, 378, [
        ("note", t.yellow),
        ("  volume is dominated by two large repositories, so breadth is shown "
         "alongside it. No skill percentages are implied.", t.dim),
    ], 10.5))

    return svg(w, h, "\n".join(b) + "\n",
               "Language distribution across Osama Anwar's public repositories",
               "Two bar charts from GitHub Linguist data. By volume: Python 93.02 percent, "
               "HTML 4.72 percent, CSS 1.29 percent, JavaScript 0.82 percent, Inno Setup 0.16 "
               "percent. By breadth, counting repositories where the language leads: Python 11, "
               "HTML 9, JavaScript 6, CSS 2. Volume is skewed by two large repositories and no "
               "skill level is implied.")


STAGES = ["SPEC", "BUILD", "TEST", "MEASURE", "DEBUG", "VERIFY", "SHIP"]


def build_pipeline(t: Theme) -> str:
    w, h = 880, 206
    b = [chrome(t, w, h, "osama@github: ~ \u2014 workflow")]
    b.append(rich(24, 60, [
        ("\u2514\u2500", t.dim), ("$", t.green), (" workflow ", t.bright), ("--execute", t.orange),
    ]))

    ramp = [t.cyan, t.blue, t.green, t.yellow, t.orange, t.purple, t.green]
    bw_, bh, gap, x0, y0 = 104, 40, 16, 28, 96
    for i, stage in enumerate(STAGES):
        x = x0 + i * (bw_ + gap)
        colour = ramp[i]
        b.append(f'<rect x="{x}" y="{y0}" width="{bw_}" height="{bh}" rx="5" '
                 f'fill="{t.panel}" stroke="{colour}" stroke-width="1.2"/>')
        b.append(text(x + bw_ / 2, y0 - 8, f"{i + 1:02d}", t.dim, 9, anchor="middle"))
        b.append(text(x + bw_ / 2, y0 + 25, stage, colour, 12.5, "700", anchor="middle"))
        if i < len(STAGES) - 1:
            cx = x + bw_ + gap / 2
            b.append(f'<path d="M{cx - 4} {y0 + 14} l5 6 -5 6" fill="none" '
                     f'stroke="{t.dim}" stroke-width="1.4" stroke-linecap="round" '
                     f'stroke-linejoin="round"/>')

    # Feedback arc: VERIFY (stage 06) returns to BUILD (stage 02) on regression.
    x_verify = x0 + 5 * (bw_ + gap) + bw_ / 2
    x_build = x0 + 1 * (bw_ + gap) + bw_ / 2
    b.append(f'<path d="M{x_verify} {y0 + bh} V162 H{x_build} V{y0 + bh}" fill="none" '
             f'stroke="{t.red}" stroke-width="1.2" stroke-dasharray="4 4"/>')
    b.append(f'<path d="M{x_build - 4.5} {y0 + bh + 7} l4.5 -7 4.5 7" fill="none" '
             f'stroke="{t.red}" stroke-width="1.2" stroke-linecap="round" '
             f'stroke-linejoin="round"/>')
    b.append(f'<rect x="{(x_build + x_verify) / 2 - 78}" y="152" width="156" height="19" '
             f'rx="4" fill="{t.bg}"/>')
    b.append(text((x_build + x_verify) / 2, 166, "regression \u2192 retest", t.red, 10.5,
                  anchor="middle"))

    return svg(w, h, "\n".join(b) + "\n",
               "Engineering workflow pipeline",
               "A seven stage pipeline: spec, build, test, measure, debug, verify, ship. "
               "A dashed feedback path returns from verify to build when a regression is found.")


def _gh(*args: str) -> str:
    return subprocess.run(["gh", *args], capture_output=True, text=True, check=True).stdout


def fetch_snapshot() -> None:
    """Re-query GitHub and replace the in-memory snapshot, then print it.

    The printed block is meant to be pasted back over the constants at the top
    of this file so the committed snapshot and the SVGs never drift apart.
    """
    global PUBLIC_REPOS, TRACKED_FILES
    names = [r["name"] for r in json.loads(_gh("repo", "list", USER, "--limit", "200",
                                              "--json", "name"))]
    byte_totals: dict[str, int] = {}
    leads: dict[str, int] = {}
    files = 0
    for name in names:
        langs = json.loads(_gh("api", f"repos/{USER}/{name}/languages") or "{}")
        for lang, size in langs.items():
            byte_totals[lang] = byte_totals.get(lang, 0) + size
        if langs:
            top = max(langs, key=langs.get)
            leads[top] = leads.get(top, 0) + 1
        tree = _gh("api", f"repos/{USER}/{name}/git/trees/HEAD?recursive=1",
                   "--jq", '[.tree[]|select(.type=="blob")]|length').strip()
        files += int(tree) if tree.isdigit() else 0

    LANG_BYTES.clear()
    LANG_BYTES.update(dict(sorted(byte_totals.items(), key=lambda kv: -kv[1])))
    LANG_BREADTH.clear()
    LANG_BREADTH.update(dict(sorted(leads.items(), key=lambda kv: -kv[1])))
    PUBLIC_REPOS, TRACKED_FILES = len(names), files

    print("# Paste over the snapshot constants:")
    print(f"LANG_BYTES = {json.dumps(LANG_BYTES, indent=4)}")
    print(f"LANG_BREADTH = {json.dumps(LANG_BREADTH, indent=4)}")
    print(f"PUBLIC_REPOS = {PUBLIC_REPOS}")
    print(f"TRACKED_FILES = {TRACKED_FILES}\n")


BUILDERS = {
    "header": build_header,
    "fastfetch": build_fastfetch,
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
