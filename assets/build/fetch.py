"""Refresh profile.json from the GitHub API. The profile repo itself is excluded."""

from __future__ import annotations

import json
import subprocess
from datetime import date
from pathlib import Path

USER = "Osama01Anwar"
OUT = Path(__file__).resolve().parent / "profile.json"
FEATURED = ["camera-count-tool", "Network-Analyzer", "HackingMonitor",
            "ascii-Art", "The-Media-Enhancer", "3D_AppImage"]


def gh(*args: str) -> str:
    return subprocess.run(["gh", *args], capture_output=True, encoding="utf-8",
                          errors="replace", check=True).stdout


def tree(repo: str) -> list[str]:
    out = gh("api", f"repos/{USER}/{repo}/git/trees/HEAD?recursive=1",
             "--jq", '.tree[]|select(.type=="blob")|.path')
    return [p for p in out.splitlines() if p]


def main() -> None:
    repos = [r for r in json.loads(gh("repo", "list", USER, "--limit", "200", "--json",
             "name,description,pushedAt,licenseInfo,homepageUrl"))
             if r["name"] != USER]
    lang_bytes: dict[str, int] = {}
    leads: dict[str, int] = {}
    files = 0
    per: dict[str, dict] = {}
    for r in repos:
        langs = json.loads(gh("api", f"repos/{USER}/{r['name']}/languages") or "{}")
        for k, v in langs.items():
            lang_bytes[k] = lang_bytes.get(k, 0) + v
        if langs:
            top = max(langs, key=langs.get)
            leads[top] = leads.get(top, 0) + 1
        paths = tree(r["name"])
        files += len(paths)
        per[r["name"]] = {
            "description": r["description"] or "",
            "pushed": r["pushedAt"][:10],
            "license": (r["licenseInfo"] or {}).get("key", ""),
            "homepage": r["homepageUrl"] or "",
            "files": len(paths),
            "tests": sum(1 for p in paths if "/test_" in p or p.startswith("test_")),
            "bytes": sum(langs.values()),
            "languages": langs,
        }

    commits = []
    for r in sorted(repos, key=lambda r: r["pushedAt"], reverse=True)[:7]:
        c = json.loads(gh("api", f"repos/{USER}/{r['name']}/commits?per_page=1"))
        if c:
            msg = c[0]["commit"]["message"].splitlines()[0]
            commits.append({"date": c[0]["commit"]["author"]["date"][:10],
                            "repo": r["name"], "sha": c[0]["sha"][:7], "message": msg})

    data = {
        "snapshot": date.today().isoformat(),
        "public_repos": len(repos) + 1,
        "measured_repos": len(repos),
        "tracked_files": files,
        "lang_bytes": dict(sorted(lang_bytes.items(), key=lambda kv: -kv[1])),
        "lang_leads": dict(sorted(leads.items(), key=lambda kv: -kv[1])),
        "featured": {n: per[n] for n in FEATURED if n in per},
        "commits": commits,
        "repos": sorted(({"name": n, "pushed": v["pushed"], "bytes": v["bytes"],
                          "lang": max(v["languages"], key=v["languages"].get) if v["languages"] else ""}
                         for n, v in per.items()), key=lambda r: r["pushed"], reverse=True),
    }
    OUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"wrote {OUT.name}: {len(repos)} repos measured, {files} files, "
          f"{len(commits)} commits, {len(data['featured'])} featured")


if __name__ == "__main__":
    main()
