"""Mobile layouts, 400 px wide. Served to viewports up to 600 px via <picture> media.

At a 400 px canvas a phone renders the SVG at ~0.9x, so 12-13 px type stays
legible — where the 880 px desktop art would fall to ~0.4x.
"""

from __future__ import annotations

from content import (AXES, EXPERIENCE, LANGS, LINKED, PIPE, PY_SHARE, SCALE, SECTIONS,
                     STACK, SYSTEM, TIERS, TOOLS)
from ui import (ACCENT, ACCENT_DEEP, ACCENT_HI, BORDER, DATA, INK, MUTED, NAVY, RED, RULE,
                SLATE, SLATE_DEEP, SURFACE, SURFACE_ACTIVE, TEXT, TEXT_2, Doc, blur, frame,
                items, legend, line, marker, micro, pair, prompt, rect, section_bar,
                stat_cell, tick_rule, wrap)

W = 400
PAD = 18


def mbadge(d: Doc, x: float, y: float, top: str, bottom: str, s: float,
           active: bool = True) -> None:
    hi, lo = (ACCENT_DEEP, ACCENT) if active else ("#3A1A0E", "#5A2A12")
    d.add(rect(x, y, s, s, hi), rect(x, y + s, s, s, lo))
    d.text(x + s / 2, y + s * 0.7, top, s * 0.44, TEXT, "heavy", anchor="middle")
    d.text(x + s / 2, y + s * 1.7, bottom, s * 0.44, INK if active else TEXT_2, "heavy",
           anchor="middle")


def lines(d: Doc, x: float, y: float, text: str, size: float, width: float, fill: str,
          weight: str = "regular", pitch: float | None = None) -> float:
    """Wrapped paragraph; returns the baseline of the last line."""
    pitch = pitch or size * 1.5
    for i, ln in enumerate(wrap(text, size, width)):
        d.text(x, y + i * pitch, ln, size, fill, weight)
    return y + (len(wrap(text, size, width)) - 1) * pitch


def ghost(d: Doc, x: float, y: float, w: float, idx: str, code: str, title: str,
          year: str) -> None:
    """An out-of-focus neighbouring record in the hero."""
    d.add(rect(x, y, w, 84, SURFACE, BORDER))
    mbadge(d, x + 14, y + 16, idx, code, 26, False)
    d.text(x + 56, y + 30, title.upper(), 12, TEXT_2, "bold", spacing=0.4)
    d.text(x + 56, y + 66, year, 28, TEXT_2, "heavy", spacing=-1)


def build_hero() -> Doc:
    d = Doc(482, "Osama Anwar — engineering dossier",
            "Mobile layout. The active record reads Osama Anwar, operator, software engineer, "
            "Pakistan: 32 public repositories, five languages, Python 93 percent of code. "
            "Neighbouring records, newest first: Database Administrator from 2026, Camera and "
            "Image Evaluation Engineer from 2025, IT internship 2025.",
            w=W)
    d.defs.append(f'<clipPath id="stack"><rect x="25" y="31" width="{W - 26}" '
                  f'height="{d.h - 32}"/></clipPath>')
    near, far = blur(d, "near", 1.2), blur(d, "far", 2.2)
    ay, ah = 128, 222
    d.add(rect(0, 31, 24, d.h - 31, SLATE_DEEP))
    for i, ch in enumerate("OA"):
        d.add(rect(0, ay + 18 + i * 34, 24, 30, "#1D6272" if i == 0 else "#16505C"))
        d.text(12, ay + 18 + i * 34 + 21, ch, 14, TEXT, "heavy", anchor="middle")

    d.add('<g clip-path="url(#stack)">')
    d.add(line(34, 31, 34, d.h, ACCENT, 1, 0.5))
    d.add(f'<g filter="url(#{near})" opacity="0.5">')
    ghost(d, 44, ay - 94, W - 60, "01", "DB", "database administrator", "2026")
    ghost(d, 44, ay + ah + 10, W - 60, "02", "IQ", "camera / image eval", "2025")
    d.add("</g>")
    d.add(f'<g filter="url(#{far})" opacity="0.28">')
    ghost(d, 44, ay + ah + 104, W - 60, "03", "IT", "it internship", "2025")
    d.add("</g>")

    x, w = 30, W - 40
    d.add(rect(x, ay, w, ah, SURFACE_ACTIVE, ACCENT), rect(x, ay, 3, ah, ACCENT))
    mbadge(d, x + 14, ay + 16, "00", "OA", 30)
    lx = x + 14 + 30 + 14
    d.text(lx, ay + 30, "OPERATOR", 11, MUTED, "bold", spacing=0.6)
    d.text(lx, ay + 46, "SOFTWARE ENGINEER", 12, TEXT, "bold", spacing=0.5)
    tick_rule(d, lx, ay + 56, w - (lx - x) - 14)
    d.text(lx, ay + 100, "OSAMA ANWAR", 34, TEXT, "heavy", spacing=-1)
    micro(d, lx, ay + 118, "loc", "PAKISTAN")
    micro(d, lx + 96, ay + 118, "github", "joined 2021-11-03")
    stat_cell(d, x + 14, ay + 146, w - 28, ("statistics", "profile"),
              [("repos", str(DATA["public_repos"]), TEXT),
               ("langs", str(len(DATA["lang_bytes"])), TEXT), ("status", "online", ACCENT)])
    by = ay + 214
    d.add(rect(x + 14, by - 9, 8, 8, ACCENT), rect(x + 28, by - 8, w - 42, 6, NAVY),
          rect(x + 28, by - 8, (w - 42) * PY_SHARE, 6, "#2C4B6E"))
    d.add("</g>")

    section_bar(d, "FILE PATH", "", h=30, size=10)
    prompt(d, W - 16 - d.glyphs.width("osama@github:~$ whoami  ", 10), 20, "whoami", 10,
           cursor=True)
    frame(d)
    return d


def build_section(idx: str, code: str, title: str, command: str) -> Doc:
    d = Doc(88, f"{idx} {title}", f"Section {idx}: {title}. Command {command}.", w=W)
    d.add(rect(0, 0, 4, d.h, ACCENT))
    mbadge(d, PAD, 14, idx, code, 26)
    lx = PAD + 26 + 16
    micro(d, lx, 24, f"section {idx} / {len(SECTIONS):02d}")
    d.text(lx, 48, title.upper(), 19, TEXT, "heavy", spacing=0.3)
    tick_rule(d, lx, 56, W - lx - PAD)
    prompt(d, lx, 80, command, 10)
    frame(d)
    return d


def build_system() -> Doc:
    def body(d: Doc) -> float:
        mbadge(d, PAD, 18, "SY", "OA", 28)
        lx = PAD + 28 + 14
        d.text(lx, 36, "osama", 14, ACCENT, "bold")
        d.text(lx + d.glyphs.width("osama", 14), 36, "@", 14, MUTED, "bold")
        d.text(lx + d.glyphs.width("osama@", 14), 36, "github", 14, SLATE, "bold")
        micro(d, lx, 56, "kernel", "software engineering")
        y = 92
        d.add(line(PAD, y - 12, W - PAD, y - 12, RULE))
        for i, (k, v, repo) in enumerate(SYSTEM):
            d.add(marker(PAD, y - 7, repo))
            d.text(PAD + 14, y, f"{i + 1:02d}", 9, MUTED, "medium")
            d.text(PAD + 38, y, k.upper(), 10, MUTED, "bold", spacing=1)
            end = lines(d, PAD + 38, y + 19, v, 12, W - PAD * 2 - 38, TEXT, pitch=17)
            y = end + 30
        sw = (W - PAD * 2) / 8
        for i, c in enumerate([ACCENT_DEEP, ACCENT, ACCENT_HI, SLATE_DEEP, SLATE, NAVY,
                               TEXT_2, TEXT]):
            d.add(rect(PAD + i * sw, y - 8, sw - 3, 12, c))
        legend(d, PAD, y + 26, stacked=True)
        return y + 50
    h = int(body(Doc(4000, "", "", w=W)))
    d = Doc(h, "System profile", "Mobile neofetch panel. " + ". ".join(
        f"{k}: {v}" for k, v, _ in SYSTEM) + ".", w=W)
    body(d)
    frame(d)
    return d


def build_languages() -> Doc:
    def body(d: Doc) -> float:
        y = 30
        d.text(PAD, y, "SCALE", 10, MUTED, "bold", spacing=1)
        for tier, what in SCALE:
            y += 22
            for s in range(3):
                d.add(rect(PAD + s * 11, y - 10, 8, 10, ACCENT if s < TIERS[tier] else RULE))
            d.text(PAD + 42, y, tier.upper(), 10, TEXT, "bold", spacing=0.6)
            d.text(PAD + 124, y, what, 9, TEXT_2, "medium")
        y += 22
        d.add(line(PAD, y, W - PAD, y, RULE))
        y += 16
        for name, tier, repo, evidence, size in LANGS:
            ev = wrap(evidence, 11, W - PAD * 2 - 28)
            ch = 58 + len(ev) * 16
            live = TIERS[tier] == 3
            d.add(rect(PAD, y, W - PAD * 2, ch, SURFACE_ACTIVE if live else SURFACE,
                       ACCENT if live else BORDER))
            if live:
                d.add(rect(PAD, y, 3, ch, ACCENT))
            colour = ACCENT if repo else SLATE
            d.text(PAD + 14, y + 26, name, 15, TEXT, "heavy")
            for s in range(3):
                d.add(rect(W - PAD - 104 + s * 12, y + 15, 9, 12,
                           colour if s < TIERS[tier] else RULE))
            d.text(W - PAD - 14, y + 26, tier.upper(), 9, colour, "bold", spacing=0.6,
                   anchor="end")
            for j, ln in enumerate(ev):
                d.text(PAD + 14, y + 48 + j * 16, ln, 11, TEXT_2)
            micro(d, PAD + 14, y + ch - 10, "bytes", f"{size:,}" if size else "—")
            y += ch + 8
        legend(d, PAD, y + 14, stacked=True)
        micro(d, PAD, y + 50, "linguist", f"{DATA['measured_repos']} repos · this repo excluded")
        return y + 66
    h = int(body(Doc(4000, "", "", w=W)))
    d = Doc(h, "Languages by qualitative tier", "Primary: Python. Working: SQL, JavaScript, "
            "HTML and CSS. Familiar: Dart. A defined scale, not measured proficiency.", w=W)
    body(d)
    frame(d)
    return d


def build_stack() -> Doc:
    def body(d: Doc) -> float:
        y = 34
        for i, (cat, entries) in enumerate(STACK):
            d.text(PAD, y, f"{i + 1:02d}", 9, MUTED, "medium")
            d.text(PAD + 24, y, cat.upper(), 11, TEXT, "bold", spacing=1)
            d.add(rect(PAD, y + 7, 18, 2, ACCENT))
            end = items(d, PAD, y + 34, entries, W - PAD, 11, pitch=27)
            y = end + 44
        legend(d, PAD, y - 10, stacked=True)
        return y + 20
    h = int(body(Doc(4000, "", "", w=W)))
    d = Doc(h, "Tech stack by category", "Mobile layout. " + ". ".join(
        f"{c}: " + ", ".join(n for n, _ in e) for c, e in STACK) + ".", w=W)
    body(d)
    frame(d)
    return d


def build_project(i: int, name: str, code: str, key: str, desc: str,
                  micros: list[tuple[str, str]], stage: str) -> Doc:
    p = DATA["featured"][name]
    active = i == 1

    def body(d: Doc) -> float:
        d.add(rect(0, 0, W, 4000, SURFACE_ACTIVE if active else "#0A0C11"))
        if active:
            d.add(rect(0, 0, 4, 4000, ACCENT))
        mbadge(d, PAD, 16, f"{i:02d}", code, 28)
        lx = PAD + 28 + 14
        d.text(lx, 28, "PROJECT", 10, MUTED, "bold", spacing=0.6)
        d.text(lx, 45, name.upper(), 13, TEXT, "bold", spacing=0.4)
        tick_rule(d, lx, 54, W - lx - PAD)
        d.text(lx, 96, key, 30, TEXT if active else TEXT_2, "heavy", spacing=-1)
        y = lines(d, PAD, 128, desc, 12, W - PAD * 2, TEXT)
        for k, v in micros:
            y += 18
            micro(d, PAD, y, k, v, value_fill=SLATE if k == "live" else TEXT_2)
        stat_cell(d, PAD, y + 32, W - PAD * 2, ("statistics", "build"),
                  [("files", str(p["files"]), TEXT),
                   ("tests", str(p["tests"] or "—"), TEXT if p["tests"] else MUTED),
                   ("updated", p["pushed"][:7], TEXT_2)])
        y += 32 + 62 + 22
        lic = p["license"].upper() if p["license"] and p["license"] != "other" else "—"
        micro(d, PAD, y, "lic", lic)
        if stage:
            micro(d, PAD + 150, y, "stage", stage.upper(), value_fill=ACCENT)
        return y + 18
    h = int(body(Doc(4000, "", "", w=W)))
    d = Doc(h, f"Project {name}", f"Project {i:02d}, {name}: {desc} {p['files']} files, "
            f"{p['tests'] or 'no'} test modules, last updated {p['pushed']}.", w=W)
    body(d)
    frame(d)
    if active:
        d.add(rect(0.5, 0.5, W - 1, h - 1, "none", ACCENT))
    return d


def build_experience() -> Doc:
    def body(d: Doc) -> float:
        y = 16
        d.add(line(14, 8, 14, 4000, ACCENT, 1, 0.55))
        for yy, code, dim, title, org, period, bullets, current in EXPERIENCE:
            x, w = 28, W - 28 - 12
            tl = wrap(title.upper(), 12, w - 60)
            wrapped = [wrap(b, 11, w - 76) for b in bullets]
            ch = 30 + len(tl) * 16 + (18 if org else 0) + 18 + sum(len(b) * 15 + 3 for b in wrapped) + 8
            d.add(line(14, y + 22, x, y + 22, ACCENT, 1, 0.55), rect(12, y + 20, 4, 4, ACCENT))
            d.add(rect(x, y, w, ch, SURFACE_ACTIVE if current else SURFACE,
                       ACCENT if current else BORDER))
            if current:
                d.add(rect(x, y, 3, ch, ACCENT))
            mbadge(d, x + 12, y + 12, yy, code, 18, current)
            lx = x + 12 + 18 + 12
            d.text(lx, y + 22, dim.upper(), 10, MUTED, "bold", spacing=0.6)
            ty = y + 22
            for ln in tl:
                ty += 16
                d.text(lx, ty, ln, 12, TEXT, "bold", spacing=0.3)
            if org:
                ty += 18
                d.text(lx, ty, org, 11, SLATE, "medium")
            ty += 18
            micro(d, lx, ty, "period" if "—" in period else "year", period,
                  value_fill=TEXT if current else TEXT_2)
            for b in wrapped:
                ty += 3
                for j, ln in enumerate(b):
                    ty += 15
                    if j == 0:
                        d.text(lx, ty, "→", 11, ACCENT, "bold")
                    d.text(lx + 16, ty, ln, 11, TEXT_2)
            y += ch + 8
        return y + 6
    h = int(body(Doc(4000, "", "", w=W)))
    d = Doc(h, "Experience timeline", "Mobile layout, newest first. " + " ".join(
        f"{period}: {title} — {org}." for _, _, _, title, org, period, _, _ in EXPERIENCE), w=W)
    d.defs.append(f'<clipPath id="xp"><rect width="{W}" height="{h}"/></clipPath>')
    d.add(f'<g clip-path="url(#xp)">')
    body(d)
    d.add("</g>")
    frame(d)
    return d


def build_camera() -> Doc:
    h = 560
    d = Doc(h, "Camera and image-quality engineering", "Mobile layout. Evaluation axes: " +
            ", ".join(AXES) + ". Defect loop: " + " to ".join(PIPE) + ".", w=W)
    d.text(PAD, 30, "EVALUATION", 10, MUTED, "bold", spacing=1)
    d.text(PAD + d.glyphs.width("EVALUATION", 10, 1) + 8, 30, "AXES", 10, TEXT, "bold",
           spacing=1)
    cw = (W - PAD * 2 - 12) / 3
    for i, ax in enumerate(AXES):
        cx, cy = PAD + (i % 3) * (cw + 6), 42 + (i // 3) * 58
        d.add(rect(cx, cy, cw, 52, SURFACE, BORDER), rect(cx, cy, cw, 2, ACCENT_DEEP))
        d.text(cx + 9, cy + 18, f"A{i + 1:02d}", 9, ACCENT, "bold")
        for j, ln in enumerate(wrap(ax.upper(), 9, cw - 14)):
            d.text(cx + 9, cy + 32 + j * 12, ln, 9, TEXT, "bold")
    top = 42 + 3 * 58 + 18
    d.add(line(PAD, top, W - PAD, top, RULE))
    d.text(PAD, top + 26, "PIPELINE", 10, MUTED, "bold", spacing=1)
    d.text(PAD + d.glyphs.width("PIPELINE", 10, 1) + 8, top + 26, "DEFECT LOOP", 10, TEXT,
           "bold", spacing=1)
    py = top + 40
    for i, step in enumerate(PIPE):
        sy = py + i * 27
        fill = ACCENT if i == 0 else (ACCENT_HI if i == len(PIPE) - 1 else "#5A2A12")
        d.add(rect(PAD, sy, 22, 20, fill))
        d.text(PAD + 11, sy + 14, str(i + 1), 11, INK if fill != "#5A2A12" else TEXT, "heavy",
               anchor="middle")
        d.text(PAD + 36, sy + 15, step.upper(), 12, TEXT, "bold", spacing=0.8)
        if i < len(PIPE) - 1:
            d.add(line(PAD + 11, sy + 20, PAD + 11, sy + 27, ACCENT, 1, 0.6))
    d.add(f'<path d="M{PAD + 150} {py + 5 * 27 + 10} H{PAD + 190} V{py + 27 + 10} '
          f'H{PAD + 150}" fill="none" stroke="{RED}" stroke-width="1.2" stroke-dasharray="3 3"/>')
    d.text(PAD + 198, py + 3 * 27 + 12, "REGRESSION", 9, RED, "bold", spacing=0.8)
    ly = py + 7 * 27 + 18
    d.add(line(PAD, ly, W - PAD, ly, RULE))
    d.text(PAD, ly + 24, "LINKED", 10, MUTED, "bold", spacing=1)
    end = items(d, PAD, ly + 52, LINKED, W - PAD, 11, pitch=27)
    legend(d, PAD, end + 34, stacked=True)
    d.h = int(end + 62)
    frame(d)
    return d


def build_toolchain() -> Doc:
    ch = 56
    h = 16 + len(TOOLS) * (ch + 6) + 50
    d = Doc(h, "Workstation inventory", "Mobile layout. " + ". ".join(
        f"{k}: " + ", ".join(n for n, _ in v) for k, v in TOOLS) + ".", w=W)
    for i, (key, entries) in enumerate(TOOLS):
        cy = 16 + i * (ch + 6)
        d.add(rect(PAD, cy, W - PAD * 2, ch, SURFACE, BORDER), rect(PAD, cy, 3, ch, ACCENT_DEEP))
        d.text(PAD + 14, cy + 19, f"{i + 1:02d}", 9, MUTED, "medium")
        d.text(PAD + 36, cy + 19, key.upper(), 10, TEXT_2, "bold", spacing=1)
        items(d, PAD + 14, cy + 42, entries, W - PAD - 10, 11, boxed=False)
    legend(d, PAD, h - 30, stacked=True)
    frame(d)
    return d


def build_index() -> Doc:
    repos = DATA["repos"][:10]
    h = 58 + len(repos) * 24 + 52
    d = Doc(h, "Repository index by last modified", "Mobile layout. " + "; ".join(
        f"{r['name']}, {r['pushed']}" for r in repos) + ".", w=W)
    prompt(d, PAD, 28, "ls -lt ~/repos", 11)
    for cx, label, anchor in ((PAD, "modified", "start"), (PAD + 84, "lang", "start"),
                              (W - PAD, "size", "end"), (PAD + 136, "name", "start")):
        micro(d, cx, 52, label, anchor=anchor)
    d.add(line(PAD, 60, W - PAD, 60, RULE))
    y = 60
    for i, r in enumerate(repos):
        y += 24
        if i == 0:
            d.add(rect(PAD - 6, y - 16, W - PAD * 2 + 12, 23, SURFACE_ACTIVE),
                  rect(PAD - 6, y - 16, 3, 23, ACCENT))
        d.text(PAD, y, r["pushed"][2:], 10, TEXT_2, "medium")
        d.text(PAD + 84, y, (r["lang"] or "—").lower()[:6], 10,
               ACCENT if r["lang"] else MUTED, "medium")
        name = r["name"] if len(r["name"]) <= 26 else r["name"][:25] + "…"
        d.text(PAD + 136, y, name, 11, TEXT, "bold" if i == 0 else "regular")
        kb = f"{r['bytes'] / 1024:,.0f}K" if r["bytes"] else "0"
        d.text(W - PAD, y, kb, 10, TEXT if r["bytes"] else MUTED, "medium", anchor="end")
    d.add(line(PAD, h - 38, W - PAD, h - 38, RULE))
    micro(d, PAD, h - 20, "total", f"{DATA['measured_repos']} repos · this repo excluded")
    frame(d)
    return d


def build_contact(i: int, channel: str, code: str, address: str) -> Doc:
    d = Doc(62, f"Contact: {channel}", f"{channel}: {address}", w=W)
    d.add(rect(0, 0, 4, d.h, ACCENT if i == 1 else ACCENT_DEEP))
    mbadge(d, PAD, 12, f"{i:02d}", code, 19)
    lx = PAD + 19 + 14
    d.text(lx, 26, channel.upper(), 11, TEXT, "bold", spacing=0.8)
    d.text(lx, 46, address, 12, SLATE, "medium")
    d.text(W - PAD, 38, "→", 15, ACCENT, "bold", anchor="end")
    frame(d)
    return d


def build_footer() -> Doc:
    d = Doc(110, "Terminal footer", f"Session end. Snapshot {DATA['snapshot']}.", w=W)
    section_bar(d, "END OF FILE", "", h=30, size=10)
    prompt(d, PAD, 62, "logout", 12, cursor=True)
    micro(d, PAD, 86, "snapshot", DATA["snapshot"])
    micro(d, PAD + 150, 86, "src", "github api")
    micro(d, PAD, 100, "type", "jetbrains mono · outlined")
    frame(d)
    return d
