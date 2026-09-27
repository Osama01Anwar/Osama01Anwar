"""Render every README asset, desktop and mobile, from profile.json.

    python fetch.py     # refresh profile.json from the GitHub API (optional)
    python build.py     # render into assets/desktop and assets/mobile

Layout lives in desktop.py / mobile.py, claims in content.py, primitives and
tokens in ui.py, and the JetBrains Mono outline engine in glyphs.py.
"""

from __future__ import annotations

from collections.abc import Callable

import desktop
import mobile
from content import LINKS, PROJECTS, SECTIONS
from ui import OUT, Doc


def registry(mod) -> dict[str, Callable[[], Doc]]:
    reg: dict[str, Callable[[], Doc]] = {
        "hero.svg": mod.build_hero,
        "footer.svg": mod.build_footer,
        "system.svg": mod.build_system,
        "languages.svg": mod.build_languages,
        "stack.svg": mod.build_stack,
        "experience.svg": mod.build_experience,
        "camera.svg": mod.build_camera,
        "toolchain.svg": mod.build_toolchain,
        "index.svg": mod.build_index,
    }
    for idx, code, title, command in SECTIONS:
        reg[f"sec-{idx}.svg"] = lambda a=(idx, code, title, command): mod.build_section(*a)
    for i, (name, code, key, desc, micros, stage) in enumerate(PROJECTS, 1):
        reg[f"project-{name.lower()}.svg"] = (
            lambda a=(i, name, code, key, desc, micros, stage): mod.build_project(*a))
    for i, (channel, code, address, _) in enumerate(LINKS, 1):
        reg[f"contact-{channel}.svg"] = lambda a=(i, channel, code, address): mod.build_contact(*a)
    return reg


def main() -> None:
    grand = 0
    for layer, mod in (("desktop", desktop), ("mobile", mobile)):
        total = 0
        for name, fn in registry(mod).items():
            p = OUT / layer / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(fn().render(), encoding="utf-8")
            total += p.stat().st_size
        grand += total
        print(f"  {layer:<8} {len(registry(mod)):>3} files  {total / 1024:7.1f} KB")
    print(f"  {'total':<8}      {grand / 1024:7.1f} KB")


if __name__ == "__main__":
    main()
