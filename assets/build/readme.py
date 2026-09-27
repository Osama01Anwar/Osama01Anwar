"""Write README.md. Alt text is taken from each SVG's own <desc>, never retyped."""

from __future__ import annotations

from html import escape

import desktop
from build import registry
from content import LINKS, PROJECTS, SECTIONS
from ui import HERE

ASSETS = "assets"
DOCS = {name: fn() for name, fn in registry(desktop).items()}

ABOUT = """\
I build tools that talk to real hardware, measure something precisely, and refuse to guess
when they cannot. `camera-count-tool` is the clearest example: it reports a camera's shutter
count only when it can read it from a documented source, and returns `EXACT COUNT UNAVAILABLE`
rather than estimating one.

That habit comes from quality work. I validated camera image quality on physical devices —
exposure, colour, dynamic range, noise — and drove defects to closure with R&D, QA and vendor
teams. Today I administer Oracle production and staging databases.

Most of what I publish is Python: desktop and CLI tools, network diagnostics, and imaging
utilities. Photography is where the interest started."""


def pic(name: str, alt: str | None = None) -> str:
    """Responsive image: the 400 px layout below 600 px, the 880 px layout above."""
    doc = DOCS[name]
    alt = alt or f"{doc.title}. {doc.desc}"
    return (f'<picture><source media="(max-width: 600px)" srcset="{ASSETS}/mobile/{name}">'
            f'<img src="{ASSETS}/desktop/{name}" width="100%" alt="{escape(alt)}"></picture>')


def heading(idx: str) -> str:
    _, _, title, command = next(s for s in SECTIONS if s[0] == idx)
    return f"## {pic(f'sec-{idx}.svg', f'Section {idx} — {title}. $ {command}')}"


def main() -> None:
    links = "&nbsp;·&nbsp;\n".join(
        f'<a href="{url}"><code>{channel.upper()}</code></a>' for channel, _, _, url in LINKS)
    parts = [
        pic("hero.svg"),
        f'<p align="center">\n{links}\n</p>',
        heading("01"), pic("system.svg"),
        heading("02"), ABOUT,
        heading("03"), pic("languages.svg"),
        heading("04"), pic("stack.svg"),
        heading("05"),
        "\n".join(f'<a href="https://github.com/Osama01Anwar/{name}">'
                  f'{pic(f"project-{name.lower()}.svg")}</a>' for name, *_ in PROJECTS),
        heading("06"), pic("experience.svg"),
        heading("07"), pic("camera.svg"),
        heading("08"), pic("toolchain.svg"),
        heading("09"), pic("index.svg"),
        heading("10"),
        "\n".join(f'<a href="{url}">{pic(f"contact-{channel}.svg", f"{channel}: {address}")}</a>'
                  for channel, _, address, url in LINKS),
        pic("footer.svg"),
    ]
    out = HERE.parent.parent / "README.md"
    out.write_text("\n\n".join(parts) + "\n", encoding="utf-8")
    print(f"  README.md  {out.stat().st_size / 1024:.1f} KB, {len(parts)} blocks")


if __name__ == "__main__":
    main()
