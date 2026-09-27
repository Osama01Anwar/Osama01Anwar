"""Desktop layouts, 880 px wide. Served to viewports wider than 600 px."""

from __future__ import annotations

from content import (AXES, EXPERIENCE, LANGS, LINKED, PIPE, PY_SHARE, SCALE, SECTIONS,
                     STACK, SYSTEM, TIERS, TOOLS)
from ui import (ACCENT, ACCENT_DEEP, ACCENT_HI, BORDER, DATA, INK, MUTED, NAVY, RED, RULE,
                SLATE, SLATE_DEEP, SURFACE, SURFACE_ACTIVE, TEXT, TEXT_2, Doc, badge, blur,
                frame, items, legend, line, marker, micro, micro_row, pair, prompt, record,
                rect, section_bar, stat_cell, tick_rule)

W = 880


def build_hero() -> Doc:
    d = Doc(470, "Osama Anwar — engineering dossier",
            "A records interface in orange and slate. The active record reads Osama Anwar, "
            "operator, software engineer, Pakistan: 32 public repositories, five languages, "
            "Python 93 percent of code. Adjacent records, out of focus and newest first, list "
            "Database Administrator at The Bank of Punjab from 2026, Camera and Image Evaluation "
            "Engineer at Transsion and Carlcare from 2025, and an IT internship at KP Board of "
            "Investment in 2025.")
    d.defs.append(f'<clipPath id="stack"><rect x="39" y="37" width="{W - 40}" '
                  f'height="{d.h - 38}"/></clipPath>')
    far, near = blur(d, "far", 2.4), blur(d, "near", 1.3)

    H, GAP, ay = 128, 10, 166
    d.add(rect(0, 37, 38, d.h - 37, SLATE_DEEP))
    for i, ch in enumerate("OA"):
        d.add(rect(0, ay + 20 + i * 46, 38, 42, "#1D6272" if i == 0 else "#16505C"))
        d.text(19, ay + 20 + i * 46 + 30, ch, 20, TEXT, "heavy", anchor="middle")
    d.text(19, 60, "00", 9, TEXT_2, "medium", anchor="middle")
    d.text(19, d.h - 18, "REC", 9, TEXT_2, "medium", spacing=0.8, anchor="middle")

    d.add('<g clip-path="url(#stack)">')
    d.add(line(58, 37, 58, d.h, ACCENT, 1, 0.55), line(68, 37, 68, d.h, ACCENT, 1, 0.25))
    ix, iw = 88, W - 112
    d.add(f'<g filter="url(#{near})" opacity="0.5">')
    record(d, ix, ay - H - GAP, iw, H, False, "01", "DB", "role", "database administrator",
           "2026", [("org", "The Bank of Punjab"), ("env", "Oracle prod / staging")],
           (("statistics", "operations"),
            [("scope", "dba", TEXT_2), ("from", "2026", TEXT_2), ("to", "now", TEXT_2)]),
           stub_x=58)
    record(d, ix, ay + H + GAP, iw, H, False, "02", "IQ", "role", "camera / image evaluation",
           "2025", [("org", "Transsion / Carlcare"), ("mode", "validation + regression")],
           (("statistics", "camera"),
            [("scope", "iq", TEXT_2), ("from", "2025", TEXT_2), ("to", "2026", TEXT_2)]),
           stub_x=58)
    d.add("</g>")
    d.add(f'<g filter="url(#{far})" opacity="0.3">')
    record(d, ix, ay + 2 * (H + GAP), iw, H, False, "03", "IT", "intern", "it internship",
           "2025", [("org", "KP Board of Investment")],
           (("statistics", "internship"),
            [("scope", "it", TEXT_2), ("from", "2025", TEXT_2), ("to", "2025", TEXT_2)]),
           stub_x=58)
    d.add("</g>")

    record(d, 62, ay, W - 80, H, True, "00", "OA", "operator", "software engineer",
           "OSAMA ANWAR",
           [("loc", "PAKISTAN"), ("github", "joined 2021-11-03")],
           (("statistics", "profile"),
            [("repos", str(DATA["public_repos"]), TEXT),
             ("langs", str(len(DATA["lang_bytes"])), TEXT),
             ("status", "online", ACCENT)]),
           big_size=50)
    bx, by = W - 18 - 22 - 270, ay + 104
    d.add(rect(bx, by, 10, 10, ACCENT), rect(bx + 16, by + 1, 254, 8, NAVY),
          rect(bx + 16, by + 1, 254 * PY_SHARE, 8, "#2C4B6E"))
    d.text(bx + 270, by - 5, f"PY {PY_SHARE * 100:.0f}% OF CODE", 9, TEXT_2, "medium",
           spacing=0.6, anchor="end")
    d.add("</g>")

    section_bar(d, "FILE PATH", "/osama01anwar/dossier/operator.rec")
    prompt(d, W - 24 - d.glyphs.width("osama@github:~$ whoami  ", 11), 23, "whoami", 11,
           cursor=True)
    frame(d)
    return d


def build_section(idx: str, code: str, title: str, command: str) -> Doc:
    """SectionHeader: a compact record — the single heading grammar for the page."""
    d = Doc(80, f"{idx} {title}", f"Section {idx}: {title}. Command {command}.")
    d.add(rect(0, 0, 4, d.h, ACCENT))
    s = 30
    d.add(rect(22, 10, s, s, ACCENT_DEEP), rect(22, 10 + s, s, s, ACCENT))
    d.text(22 + s / 2, 10 + s * 0.68, idx, 13, TEXT, "heavy", anchor="middle")
    d.text(22 + s / 2, 10 + s * 1.68, code, 13, INK, "heavy", anchor="middle")
    lx = 22 + s + 24
    d.text(lx, 38, "SECTION", 20, MUTED, "heavy", spacing=0.5)
    d.text(lx + d.glyphs.width("SECTION", 20, 0.5) + 14, 38, title.upper(), 20, TEXT,
           "heavy", spacing=0.5)
    tick_rule(d, lx, 50, 420)
    rx = W - 318
    d.add(line(rx - 20, 16, rx - 20, d.h - 16, RULE))
    micro(d, rx, 30, "command")
    micro(d, W - 22, 30, f"sec {idx} / {len(SECTIONS):02d}", anchor="end")
    prompt(d, rx, 54, command, 12)
    frame(d)
    return d


SWATCHES = [ACCENT_DEEP, ACCENT, ACCENT_HI, SLATE_DEEP, SLATE, NAVY, TEXT_2, TEXT]


def build_system() -> Doc:
    h = 40 + len(SYSTEM) * 24 + 64
    d = Doc(h, "System profile", "A neofetch-style panel. " + ". ".join(
        f"{k}: {v}" for k, v, _ in SYSTEM) + ".")
    d.add(rect(0, 0, 196, h, "#090B10"), line(196, 0, 196, h, RULE))
    bs, bx, by = 72, 62, 44
    d.add(rect(bx, by, bs, bs, ACCENT_DEEP), rect(bx, by + bs, bs, bs, ACCENT))
    d.text(bx + bs / 2, by + bs * 0.66, "SYS", 26, TEXT, "heavy", anchor="middle")
    d.text(bx + bs / 2, by + bs * 1.66, "OA", 30, INK, "heavy", anchor="middle")
    for i in range(4):
        d.add(rect(bx - 22, by + 8 + i * 34, 10, 2, SLATE, opacity=0.6))
    micro(d, 98, by + 2 * bs + 30, "host", anchor="middle")
    d.text(98, by + 2 * bs + 46, "osama@github", 11, SLATE, "medium", anchor="middle")
    micro(d, 98, by + 2 * bs + 72, "kernel", anchor="middle")
    d.text(98, by + 2 * bs + 88, "software eng.", 11, TEXT_2, "medium", anchor="middle")

    x0 = 226
    d.text(x0, 30, "osama", 14, ACCENT, "bold")
    d.text(x0 + d.glyphs.width("osama", 14), 30, "@", 14, MUTED, "bold")
    d.text(x0 + d.glyphs.width("osama@", 14), 30, "github", 14, SLATE, "bold")
    d.add(line(x0, 40, W - 26, 40, RULE))
    y = 40
    for i, (k, v, repo) in enumerate(SYSTEM):
        y += 24
        d.add(marker(x0, y - 8, repo))
        d.text(x0 + 16, y, f"{i + 1:02d}", 9, MUTED, "medium")
        d.text(x0 + 44, y, k.upper(), 11, MUTED, "bold", spacing=1)
        d.text(x0 + 150, y, v, 13, TEXT, "regular")
        if i < len(SYSTEM) - 1:
            d.add(line(x0 + 44, y + 8, W - 26, y + 8, RULE, 1, 0.6))
    sy = y + 24
    sw = (W - 26 - x0) / len(SWATCHES)
    for i, c in enumerate(SWATCHES):
        d.add(rect(x0 + i * sw, sy, sw - 3, 14, c))
    legend(d, x0, sy + 32)
    frame(d)
    return d


def build_languages() -> Doc:
    h = 118 + len(LANGS) * 56 + 40
    d = Doc(h, "Languages by qualitative tier",
            "A defined three-tier scale, not measured proficiency. Primary: Python. Working: "
            "SQL, JavaScript, HTML and CSS. Familiar: Dart. Each row names its evidence.")
    x0 = 26
    d.text(x0, 34, "SCALE", 11, MUTED, "bold", spacing=1)
    for i, (tier, what) in enumerate(SCALE):
        cx = x0 + 70 + i * 262
        for s in range(3):
            d.add(rect(cx + s * 12, 25, 9, 11, ACCENT if s < TIERS[tier] else RULE))
        d.text(cx + 44, 34, tier.upper(), 11, TEXT, "bold", spacing=0.8)
        d.text(cx + 44, 50, what, 9, TEXT_2, "medium")
    d.add(line(x0, 66, W - 26, 66, RULE))
    for cx, label, anchor in ((x0, "language", "start"), (x0 + 196, "tier", "start"),
                              (x0 + 318, "evidence", "start"), (W - 44, "bytes", "end")):
        micro(d, cx, 88, label, anchor=anchor)
    y = 110
    for name, tier, repo, evidence, size in LANGS:
        live = TIERS[tier] == 3
        d.add(rect(x0, y - 4, W - 52, 46, SURFACE_ACTIVE if live else SURFACE,
                   ACCENT if live else BORDER))
        if live:
            d.add(rect(x0, y - 4, 3, 46, ACCENT))
        colour = ACCENT if repo else SLATE
        d.text(x0 + 18, y + 26, name, 17, TEXT, "heavy")
        for s in range(3):
            d.add(rect(x0 + 196 + s * 14, y + 13, 10, 13, colour if s < TIERS[tier] else RULE))
        d.text(x0 + 246, y + 25, tier.upper(), 10, colour, "bold", spacing=0.8)
        d.text(x0 + 318, y + 25, evidence, 12, TEXT_2, "regular")
        d.text(W - 44, y + 25, f"{size:,}" if size else "—", 12,
               TEXT if size else MUTED, "medium", anchor="end")
        y += 56
    legend(d, x0, y + 8)
    micro(d, W - 26, y + 8, f"linguist · {DATA['measured_repos']} repos · this repo excluded",
          anchor="end")
    frame(d)
    return d


def _stack_rows(d: Doc) -> float:
    y = 44
    for i, (cat, entries) in enumerate(STACK):
        d.text(26, y, f"{i + 1:02d}", 9, MUTED, "medium")
        d.text(52, y, cat.upper(), 11, TEXT, "bold", spacing=1)
        d.add(rect(26, y + 8, 20, 2, ACCENT))
        end = items(d, 206, y, entries, W - 26, pitch=28)
        y = end + 42
        if i < len(STACK) - 1:
            d.add(line(26, y - 24, W - 26, y - 24, RULE))
    return y


def build_stack() -> Doc:
    h = int(_stack_rows(Doc(2000, "", "")) + 6)
    d = Doc(h, "Tech stack by category",
            "Categorised technologies with evidence markers. " + ". ".join(
                f"{c}: " + ", ".join(n for n, _ in e) for c, e in STACK) + ".")
    _stack_rows(d)
    legend(d, 26, h - 14)
    frame(d)
    return d


def build_project(i: int, name: str, code: str, key: str, desc: str,
                  micros: list[tuple[str, str]], stage: str) -> Doc:
    p = DATA["featured"][name]
    active = i == 1
    d = Doc(150, f"Project {name}",
            f"Project {i:02d}, {name}: {desc} {p['files']} files, "
            f"{p['tests'] or 'no'} test modules, last updated {p['pushed']}.")
    d.add(rect(0, 0, W, d.h, SURFACE_ACTIVE if active else "#0A0C11"))
    if active:
        d.add(rect(0, 0, 4, d.h, ACCENT))
    s = 44
    badge(d, 22, (d.h - 2 * s) / 2, f"{i:02d}", code, s, True)
    lx = 22 + s + 24
    pair(d, lx, 30, "project", name)
    tick_rule(d, lx, 40, 380, True)
    d.text(lx, 88, key, 34, TEXT if active else TEXT_2, "heavy", spacing=-1)
    d.text(lx, 116, desc, 13, TEXT, "regular")
    mx = lx
    for k, v in micros:
        micro(d, mx, d.h - 12, k, v, value_fill=SLATE if k == "live" else TEXT_2)
        mx += d.glyphs.width(k, 9, 0.8) + d.glyphs.width(v, 9, 0.4) + 30
    sx = W - 22 - 262
    stat_cell(d, sx, 30, 262, ("statistics", "build"),
              [("files", str(p["files"]), TEXT),
               ("tests", str(p["tests"] or "—"), TEXT if p["tests"] else MUTED),
               ("updated", p["pushed"][:7], TEXT_2)])
    lic = p["license"].upper() if p["license"] and p["license"] != "other" else "—"
    micro(d, sx, 116, "lic", lic)
    if stage:
        micro(d, sx + 150, 116, "stage", stage.upper(), value_fill=ACCENT)
    frame(d)
    if active:
        d.add(rect(0.5, 0.5, W - 1, d.h - 1, "none", ACCENT))
    return d


def _xp_height(org: str, lines: list[str]) -> int:
    return 44 + 20 * (1 + len(lines)) if (org or lines) else 60


def build_experience() -> Doc:
    heights = [_xp_height(org, lines) for _, _, _, _, org, _, lines, _ in EXPERIENCE]
    h = 20 + sum(hh + 10 for hh in heights) + 10
    d = Doc(h, "Experience timeline", "Career timeline, newest first. " + " ".join(
        f"{period}: {title} — {org}." for _, _, _, title, org, period, _, _ in EXPERIENCE))
    d.add(line(34, 12, 34, h - 12, ACCENT, 1, 0.6), line(44, 12, 44, h - 12, ACCENT, 1, 0.25))
    y = 20
    for (yy, code, dim, title, org, period, lines, current), hh in zip(EXPERIENCE, heights):
        x = 64
        d.add(line(34, y + hh / 2, x, y + hh / 2, ACCENT, 1, 0.6),
              rect(32, y + hh / 2 - 2, 4, 4, ACCENT))
        d.add(rect(x, y, W - x - 22, hh, SURFACE_ACTIVE if current else SURFACE,
                   ACCENT if current else BORDER))
        if current:
            d.add(rect(x, y, 3, hh, ACCENT))
        s = 22
        by = y + (hh - 2 * s) / 2
        d.add(rect(x + 18, by, s, s, ACCENT_DEEP if current else "#3A1A0E"),
              rect(x + 18, by + s, s, s, ACCENT if current else "#5A2A12"))
        d.text(x + 18 + s / 2, by + s * 0.7, yy, 11, TEXT, "heavy", anchor="middle")
        d.text(x + 18 + s / 2, by + s * 1.7, code, 11, INK if current else TEXT_2, "heavy",
               anchor="middle")
        lx = x + 18 + s + 20
        ty = y + 26 if (org or lines) else y + hh / 2 + 5
        pair(d, lx, ty, dim, title, 14)
        ly = ty
        if org:
            ly += 20
            d.text(lx, ly, org, 12, SLATE, "medium")
        for ln in lines:
            ly += 20
            d.text(lx, ly, "→", 12, ACCENT, "bold")
            d.text(lx + 20, ly, ln, 12, TEXT_2, "regular")
        micro(d, W - 44, y + 22, "period" if "—" in period else "year", anchor="end")
        d.text(W - 44, y + 42, period, 13, TEXT if current else TEXT_2, "bold", anchor="end")
        y += hh + 10
    frame(d)
    return d


def pipeline(d: Doc, px: float, top: float) -> None:
    """The defect loop: seven steps, with retest feeding back to evaluate."""
    for i, step in enumerate(PIPE):
        sy = top + i * 27
        fill = ACCENT if i == 0 else (ACCENT_HI if i == len(PIPE) - 1 else "#5A2A12")
        d.add(rect(px, sy, 22, 20, fill))
        d.text(px + 11, sy + 14, str(i + 1), 11, INK if fill != "#5A2A12" else TEXT, "heavy",
               anchor="middle")
        d.text(px + 36, sy + 15, step.upper(), 12, TEXT, "bold", spacing=0.8)
        if i < len(PIPE) - 1:
            d.add(line(px + 11, sy + 20, px + 11, sy + 27, ACCENT, 1, 0.6))
    d.add(f'<path d="M{px + 150} {top + 5 * 27 + 10} H{px + 190} V{top + 27 + 10} '
          f'H{px + 150}" fill="none" stroke="{RED}" stroke-width="1.2" stroke-dasharray="3 3"/>')
    d.text(px + 198, top + 3 * 27 + 12, "REGRESSION", 9, RED, "bold", spacing=0.8)


def header_pair(d: Doc, x: float, y: float, dim: str, bright: str) -> None:
    d.text(x, y, dim, 11, MUTED, "bold", spacing=1)
    d.text(x + d.glyphs.width(dim, 11, 1) + 9, y, bright, 11, TEXT, "bold", spacing=1)


def build_camera() -> Doc:
    h = 332
    d = Doc(h, "Camera and image-quality engineering",
            "Evaluation axes: " + ", ".join(AXES) + ". Defect loop: " + " to ".join(PIPE) +
            ", with regressions returning to evaluation. Linked to camera-count-tool, the "
            "Huawei Next Image Award and Lightroom.")
    x0 = 26
    header_pair(d, x0, 34, "EVALUATION", "AXES")
    cw, ch = 136, 56
    for i, ax in enumerate(AXES):
        cx, cy = x0 + (i % 3) * (cw + 8), 48 + (i // 3) * (ch + 8)
        d.add(rect(cx, cy, cw, ch, SURFACE, BORDER), rect(cx, cy, cw, 2, ACCENT_DEEP))
        d.text(cx + 12, cy + 20, f"A{i + 1:02d}", 9, ACCENT, "bold", spacing=0.6)
        d.text(cx + 12, cy + 40, ax.upper(), 11, TEXT, "bold", spacing=0.3)
    px = 484
    d.add(line(px - 18, 24, px - 18, 240, RULE))
    header_pair(d, px, 34, "PIPELINE", "DEFECT LOOP")
    pipeline(d, px, 52)
    d.add(line(x0, 256, W - 26, 256, RULE))
    d.text(x0, 282, "LINKED", 11, MUTED, "bold", spacing=1)
    items(d, 124, 282, LINKED, W - 26)
    legend(d, x0, h - 16)
    frame(d)
    return d


def build_toolchain() -> Doc:
    rows = (len(TOOLS) + 1) // 2
    ch = 58
    h = 20 + rows * (ch + 8) + 30
    d = Doc(h, "Workstation inventory", "Toolchain. " + ". ".join(
        f"{k}: " + ", ".join(n for n, _ in v) for k, v in TOOLS) + ".")
    cw = (W - 52 - 8) / 2
    for i, (key, entries) in enumerate(TOOLS):
        cx = 26 + (i % 2) * (cw + 8)
        cy = 20 + (i // 2) * (ch + 8)
        d.add(rect(cx, cy, cw, ch, SURFACE, BORDER), rect(cx, cy, 3, ch, ACCENT_DEEP))
        d.text(cx + 16, cy + 20, f"{i + 1:02d}", 9, MUTED, "medium")
        d.text(cx + 40, cy + 20, key.upper(), 10, TEXT_2, "bold", spacing=1)
        items(d, cx + 16, cy + 44, entries, cx + cw - 10, 12, boxed=False)
    legend(d, 26, h - 14)
    frame(d)
    return d


def build_index() -> Doc:
    repos = DATA["repos"][:10]
    h = 60 + len(repos) * 26 + 46
    d = Doc(h, "Repository index by last modified",
            "ls -lt of public repositories. " + "; ".join(
                f"{r['name']}, {r['lang'] or 'no code'}, {r['bytes']} bytes, {r['pushed']}"
                for r in repos) + ".")
    x0 = 26
    prompt(d, x0, 30, "ls -lt ~/repos | head -10", 12)
    for cx, label, anchor in ((x0, "modified", "start"), (x0 + 130, "lang", "start"),
                              (x0 + 320, "size", "end"), (x0 + 360, "name", "start")):
        micro(d, cx, 58, label, anchor=anchor)
    d.add(line(x0, 66, W - 26, 66, RULE))
    y = 66
    for i, r in enumerate(repos):
        y += 26
        if i == 0:
            d.add(rect(x0 - 8, y - 18, W - 36, 26, SURFACE_ACTIVE),
                  rect(x0 - 8, y - 18, 3, 26, ACCENT))
        d.text(x0, y, r["pushed"], 12, TEXT_2, "medium")
        d.text(x0 + 130, y, (r["lang"] or "—").lower(), 12, ACCENT if r["lang"] else MUTED,
               "medium")
        kb = f"{r['bytes'] / 1024:,.1f}K" if r["bytes"] else "0"
        d.text(x0 + 320, y, kb, 12, TEXT if r["bytes"] else MUTED, "medium", anchor="end")
        d.text(x0 + 360, y, r["name"], 13, TEXT, "bold" if i == 0 else "regular")
    d.add(line(x0, h - 32, W - 26, h - 32, RULE))
    micro(d, x0, h - 14, "total", f"{DATA['measured_repos']} repos measured · this repo excluded")
    micro(d, W - 26, h - 14, f"snapshot {DATA['snapshot']}", anchor="end")
    frame(d)
    return d


def build_contact(i: int, channel: str, code: str, address: str) -> Doc:
    """One clickable contact strip — a record reduced to its essentials."""
    d = Doc(58, f"Contact: {channel}", f"{channel}: {address}")
    s = 19
    d.add(rect(0, 0, 4, d.h, ACCENT if i == 1 else ACCENT_DEEP))
    d.add(rect(22, 10, s, s, ACCENT_DEEP), rect(22, 10 + s, s, s, ACCENT))
    d.text(22 + s / 2, 10 + s * 0.72, f"{i:02d}", 9, TEXT, "heavy", anchor="middle")
    d.text(22 + s / 2, 10 + s * 1.72, code, 9, INK, "heavy", anchor="middle")
    lx = 22 + s + 22
    pair(d, lx, 26, "channel", channel, 12)
    d.text(lx, 45, address, 13, SLATE, "medium")
    d.text(W - 26, 36, "OPEN", 11, TEXT_2, "bold", spacing=1.2,
           anchor="end")
    d.text(W - 26 - d.glyphs.width("OPEN ", 11, 1.2) - 4, 36, "→", 13, ACCENT, "bold",
           anchor="end")
    frame(d)
    return d


def build_footer() -> Doc:
    d = Doc(96, "Terminal footer", f"Session end. Snapshot {DATA['snapshot']}, source GitHub "
            "API, type JetBrains Mono drawn as outlines.")
    section_bar(d, "END OF FILE", "/osama01anwar/dossier", h=34)
    prompt(d, 26, 68, "logout", 13, cursor=True)
    micro_row(d, W - 26, 68, [("snapshot", DATA["snapshot"]), ("src", "github api"),
                              ("type", "jetbrains mono · outlined")])
    frame(d)
    return d
