# Profile generator

Every image in the profile README is generated here. Nothing is hand-drawn and
no number is hand-typed.

```bash
pip install fonttools
python fetch.py     # optional: refresh profile.json from the GitHub API (needs `gh auth login`)
python build.py     # render ../desktop/*.svg and ../mobile/*.svg
python readme.py    # regenerate ../../README.md
```

| file | role |
|---|---|
| `content.py` | every claim the profile makes, with its evidence marker |
| `profile.json` | measured snapshot from the GitHub API (this repo excluded) |
| `ui.py` | design tokens and shared primitives |
| `desktop.py` / `mobile.py` | 880 px and 400 px layouts |
| `glyphs.py` | JetBrains Mono drawn as outlines |
| `readme.py` | writes the README; alt text comes from each SVG's `<desc>` |

**Why outlines.** GitHub serves repository SVGs with
`Content-Security-Policy: default-src 'none'`, which blocks every font, embedded
ones included. Text therefore ships as glyph geometry. JetBrains Mono (OFL 1.1) is
downloaded on first run into `.fonts/`, which is not committed.

**Why two layouts.** `<picture><source media="(max-width: 600px)">` serves the
400 px layouts to phones, so type stays legible instead of shrinking to ~0.4×.
