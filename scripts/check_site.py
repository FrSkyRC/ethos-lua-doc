"""Scan the built site for content that failed to render.

Looks at each page's visible text (code blocks removed) for Markdown or
markup that should have been converted: raw links `[x](y.md)`, `**bold**`,
code fences, admonition (`!!!`) and tab (`=== "`) markers, snippet markers,
escaped HTML tags, and empty table cells in API parameter tables.

Usage:
    mkdocs build && python scripts/check_site.py [site]
Exits 1 when problems are found (used in CI).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

PATTERNS = {
    "raw markdown link": re.compile(r"\]\([^)\s]+\)"),
    "raw bold": re.compile(r"\*\*[^*\n]+\*\*"),
    "raw code fence": re.compile(r"```"),
    "raw admonition": re.compile(r"(^|\n)\s*!!! "),
    "raw tab marker": re.compile(r'=== "'),
    "raw snippet marker": re.compile(r"--8<--"),
    "escaped html tag": re.compile(r"</?(div|span|small|br)\b[^>]*>"),
}


def check(site: Path) -> list[str]:
    problems = []
    for html in sorted(site.rglob("*.html")):
        if html.name == "404.html":
            continue
        soup = BeautifulSoup(html.read_text(encoding="utf-8"), "html.parser")
        main = soup.select_one("article.md-content__inner") or soup.body
        if main is None:
            continue
        for tag in main.select("pre, code, script, style, .highlight"):
            tag.decompose()
        text = main.get_text("\n")
        rel = html.relative_to(site).as_posix()
        for name, rx in PATTERNS.items():
            m = rx.search(text)
            if m:
                ctx = text[max(0, m.start() - 40): m.end() + 40].replace("\n", " ")
                problems.append(f"{rel}: {name}: ...{ctx}...")
        # API parameter tables: every row should have a type
        if rel.startswith("api/"):
            for table in main.select("table"):
                head = [th.get_text(strip=True) for th in table.select("thead th")]
                if head[:2] != ["Name", "Type"]:
                    continue
                for tr in table.select("tbody tr"):
                    cells = [td.get_text(strip=True) for td in tr.select("td")]
                    if len(cells) > 1 and not cells[1]:
                        problems.append(f"{rel}: parameter '{cells[0]}' has no type")
    return problems


def main() -> int:
    site = Path(sys.argv[1] if len(sys.argv) > 1 else "site")
    problems = check(site)
    for p in problems:
        print(p)
    print(f"{len(problems)} problem(s) in {site}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
