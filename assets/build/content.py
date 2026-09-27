"""Every claim the profile makes, in one place.

Each item is either measured (profile.json, from the GitHub API) or taken from
the owner's career record. Booleans mark evidence: True = present in a public
repository, False = professional or environment record only. Nothing here is a
self-assessed skill level. See CONTENT_INVENTORY.md for the audit trail.
"""

from __future__ import annotations

from ui import DATA

TOTAL_BYTES = sum(DATA["lang_bytes"].values())
PY_SHARE = DATA["lang_bytes"]["Python"] / TOTAL_BYTES

LINKS = [
    ("github", "GH", "github.com/Osama01Anwar", "https://github.com/Osama01Anwar"),
    ("linkedin", "LI", "linkedin.com/in/osama-anwar-4b6a14199",
     "https://linkedin.com/in/osama-anwar-4b6a14199/"),
    ("email", "EM", "theosamaanwar@gmail.com", "mailto:theosamaanwar@gmail.com"),
    ("portfolio", "PF", "theosamaanwar.myportfolio.com", "https://theosamaanwar.myportfolio.com"),
    ("behance", "BE", "behance.net/theosamaanwar", "https://behance.net/theosamaanwar"),
    ("instagram", "IG", "instagram.com/https.osama", "https://instagram.com/https.osama/"),
]

SECTIONS = [
    ("01", "SY", "system profile", "neofetch"),
    ("02", "DO", "dossier", "cat about.txt"),
    ("03", "LG", "languages", "stack --languages"),
    ("04", "SK", "tech stack", "skills --all"),
    ("05", "PR", "projects", "projects --featured"),
    ("06", "XP", "experience", "experience --timeline"),
    ("07", "IQ", "camera / image", "camera --diagnostics"),
    ("08", "TC", "toolchain", "tools --inventory"),
    ("09", "IX", "repository index", "ls -lt ~/repos"),
    ("10", "CT", "contact", "contact --connect"),
]

SYSTEM = [
    ("os", "Windows 11 · WSL2 · Linux", False),
    ("shell", "PowerShell · bash", False),
    ("editor", "VS Code · Git", False),
    ("role", "Database Administrator · The Bank of Punjab", False),
    ("previous", "Camera / Image Evaluation Engineer · Transsion / Carlcare", False),
    ("languages", "Python · HTML · CSS · JavaScript · SQL", True),
    ("focus", "CLI tooling · desktop apps · diagnostics", True),
    ("domains", "SQA · mobile / web · camera IQ · database ops", False),
    ("repos", f"{DATA['public_repos']} public · {DATA['tracked_files']} files measured", True),
    ("uptime", "since 2021-11-03", False),
]

TIERS = {"primary": 3, "working": 2, "familiar": 1}
SCALE = [("primary", "shipped, tested, released in public repos"),
         ("working", "used across repos or daily at work"),
         ("familiar", "training / internship; no public code")]
LANGS = [
    ("PYTHON", "primary", True, "12 repos · CI, packaged releases, 20-module test suite",
     DATA["lang_bytes"]["Python"]),
    ("SQL", "working", False, "Oracle daily as DBA · SQLite schema + migrations in repo", None),
    ("JAVASCRIPT", "working", True, "8 repos · browser apps and exercises",
     DATA["lang_bytes"]["JavaScript"]),
    ("HTML / CSS", "working", True, "17 / 11 repos · pages, dashboards, HUD front-ends",
     DATA["lang_bytes"]["HTML"] + DATA["lang_bytes"]["CSS"]),
    ("DART", "familiar", False, "Flutter internship, 2023 · no public code", None),
]

STACK = [
    ("desktop / cli", [("PySide6 / Qt", True), ("Typer", True), ("Tkinter", True),
                       ("PyQt5", True), ("Flask + Socket.IO", True), ("Streamlit", True)]),
    ("imaging / ml", [("OpenCV", True), ("NumPy", True), ("Pillow", True), ("PyTorch", True),
                      ("timm", True), ("transformers", True), ("scikit-learn", True),
                      ("NLTK", True), ("CuPy", True), ("Numba", True)]),
    ("systems", [("WPD / COM", True), ("PTP / MTP", True), ("libusb", True),
                 ("ExifTool", True), ("Scapy", True), ("psutil", True)]),
    ("data", [("SQLite", True), ("Oracle Database", False)]),
    ("testing / qa", [("pytest", True), ("pytest-qt", True), ("hypothesis", True),
                      ("ruff", True), ("mypy", True), ("regression testing", False),
                      ("mobile / web QA", False), ("Jira", False)]),
    ("build / release", [("GitHub Actions", True), ("uv", True), ("hatchling", True),
                         ("PyInstaller", True), ("Inno Setup", True)]),
    ("mobile", [("Flutter", False), ("Dart", False)]),
    ("security", [("packet classification", True), ("network diagnostics", True),
                  ("Linux / WSL2", False)]),
]

# name, badge code, record key, one-line description, micro-labels, documented stage
PROJECTS = [
    ("camera-count-tool", "CC", "CCT", "Exact shutter count from a documented source, or none.",
     [("stack", "Python 3.12 · PySide6 · Typer · SQLite"), ("os", "Windows 10/11")], "alpha"),
    ("Network-Analyzer", "NA", "NETAN", "Windows network analyzer: Wi-Fi, discovery, diagnostics.",
     [("stack", "Python · argparse CLI · psutil"), ("os", "Windows 10/11")], ""),
    ("HackingMonitor", "HM", "HKMON", "Live packet classifier: SYN flood, port scan, ICMP probe.",
     [("stack", "Python · Scapy · Flask + Socket.IO"), ("live", "hacking-monitor.vercel.app")],
     ""),
    ("ascii-Art", "AA", "ASCII", "Image, video and webcam to ASCII, with a GPU path.",
     [("stack", "Python · OpenCV · CuPy · Numba")], ""),
    ("The-Media-Enhancer", "ME", "MENH", "Desktop 4x image and video upscaler.",
     [("stack", "Python · PyTorch · OpenCV · Tkinter")], ""),
    ("3D_AppImage", "3D", "3DAPP", "Single photo to a 3D view via MiDaS depth estimation.",
     [("stack", "Python · Streamlit · PyTorch · timm")], ""),
]

# Reverse-chronological by end date.
EXPERIENCE = [
    ("26", "DB", "role", "database administrator", "The Bank of Punjab", "2026 — now",
     ["Oracle production and staging: health, performance, capacity, availability",
      "Backup, DR drills, patching, access control, audit and compliance records"], True),
    ("25", "IQ", "role", "camera / image evaluation engineer", "Transsion Holdings / Carlcare",
     "2025 — 2026",
     ["Camera validation and regression on physical devices and in software",
      "Exposure, colour, dynamic range, noise; defects to closure via Jira"], False),
    ("25", "IT", "intern", "it internship", "KP Board of Investment", "2025", [], False),
    ("24", "ED", "edu", "bsc software engineering", "Iqra National University", "2020 — 2024",
     ["CGPA 3.21"], False),
    ("23", "FL", "intern", "flutter development internship", "", "2023", [], False),
    ("23", "MW", "training", "mobile / web development", "SMIT", "2023", [], False),
    ("21", "AW", "award", "huawei next image award", "Pakistan National Winner", "2021", [],
     False),
]

AXES = ["exposure", "colour accuracy", "white balance", "dynamic range", "noise",
        "detail", "optical behaviour", "consistency", "regression"]
PIPE = ["capture", "evaluate", "compare", "isolate", "report", "retest", "release"]
LINKED = [("camera-count-tool: EXIF + MakerNotes", True), ("Next Image Award 2021", False),
          ("Lightroom", False)]

TOOLS = [
    ("os", [("Windows 11", False), ("WSL2", False), ("Linux", False)]),
    ("editor", [("VS Code", False)]),
    ("terminal", [("PowerShell", False), ("bash", False)]),
    ("vcs / ci", [("Git", True), ("GitHub", True), ("GitHub Actions", True)]),
    ("python", [("uv", True), ("ruff", True), ("mypy", True), ("pytest", True)]),
    ("packaging", [("PyInstaller", True), ("Inno Setup", True), ("hatchling", True)]),
    ("database", [("SQLite", True), ("Oracle", False)]),
    ("ai-assisted", [("Claude Code", True), ("Codex", False)]),
    ("mobile", [("Flutter", False), ("Dart", False)]),
    ("photo", [("Lightroom", False)]),
]
