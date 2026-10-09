"""Index real-world calls to every API function across public Ethos Lua projects.

For each namespace function in data/api.json (e.g. `lcd.drawText`) this finds
call sites in the repos listed under "usage_repos" in data/upstream.json,
keeps a few short, varied snippets, and writes data/usage.json. The page
generator renders them as "Real-world usage" with permalinks to the exact
commit and line on GitHub.

Repos are shallow-cloned into .cache/usage/ (default branch), so links always
point at public code, never at a local feature branch.

Usage:
    python scripts/scan_usage.py                # clone/refresh all repos, then scan
    python scripts/scan_usage.py --no-fetch     # scan what is already in .cache/usage/
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import textwrap
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache/usage"
MAX_SNIPPETS = 3
MAX_LINES = 14
SKIP_DIRS = {".git", "node_modules", "simulator", "simulators", "tests", "test", "bin", "demo", ".vscode"}


def rmtree(path: Path) -> None:
    """shutil.rmtree that also removes read-only files (git packs on Windows)."""
    def onexc(func, p, _exc):
        os.chmod(p, stat.S_IWRITE)
        func(p)
    shutil.rmtree(path, onexc=onexc)


def git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def fetch(repo: dict) -> Path:
    dst = CACHE / repo["repo"].replace("/", "__")
    if dst.exists():
        rmtree(dst)
    branch = repo.get("branch")  # omitted = the repo's default branch
    print(f"cloning {repo['repo']}@{branch or 'default'}")
    url = f"https://github.com/{repo['repo']}.git"
    opts = ["--depth", "1"] + (["--branch", branch] if branch else [])
    if repo.get("path"):  # big repos (PDF manuals etc.): only check out the Lua subtree
        git("clone", *opts, "--filter=blob:none", "--sparse", url, str(dst))
        git("-C", str(dst), "sparse-checkout", "set", repo["path"])
    else:
        git("clone", *opts, url, str(dst))
    return dst


FUNC_RE = re.compile(r"^(\s*)(?:local\s+)?function\b|^(\s*).*=\s*function\s*\(")
STRING_RE = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'')


def indent(line: str) -> int:
    return len(line) - len(line.lstrip())


def call_end(lines: list[str], start: int, col: int) -> int | None:
    """Index of the line where the call opened at (start, col) closes, or None."""
    depth = 0
    for i in range(start, min(start + 16, len(lines))):
        seg = lines[i][col:] if i == start else lines[i]
        seg = STRING_RE.sub('""', seg)  # ignore parens inside strings
        seg = seg.split("--", 1)[0]
        for ch in seg:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    return i
    return None


def enclosing_function(lines: list[str], i: int) -> tuple[int, int] | None:
    """(start, end) of the smallest function around line i, if it is short."""
    ind = indent(lines[i])
    for j in range(i - 1, max(-1, i - MAX_LINES - 1), -1):
        if not lines[j].strip():
            continue
        if indent(lines[j]) < ind and FUNC_RE.match(lines[j]):
            fi = indent(lines[j])
            for k in range(i + 1, min(len(lines), j + MAX_LINES + 4)):
                if indent(lines[k]) == fi and re.match(r"\s*end\b", lines[k]):
                    return (j, k) if k - j + 1 <= MAX_LINES + 4 else None
            return None
        if indent(lines[j]) < ind:
            ind = indent(lines[j])  # walked out of an if/for block, keep looking
    return None


def snippet(lines: list[str], i: int, col: int) -> tuple[str, int, int] | None:
    """(text, first line number, score); lower score = better example."""
    end = call_end(lines, i, col)
    if end is None:
        return None  # call not closed within reach: would print a broken fragment
    fn = enclosing_function(lines, i)
    if fn:
        start, end = fn
    else:
        start = i
        for _ in range(3):
            prev = start - 1
            if prev < 0 or not lines[prev].strip() or re.match(r"\s*(end|else|elseif)\b", lines[prev]):
                break
            if FUNC_RE.match(lines[prev]):
                break
            start = prev
    block = lines[start:end + 1]
    text = textwrap.dedent("\n".join(l.rstrip().replace("\t", "    ") for l in block)).strip("\n")
    n = text.count("\n") + 1
    longest = max(len(l) for l in text.splitlines())
    score = abs(n - 6) + (4 if not fn else 0) + (3 if longest > 110 else 0) + (5 if n == 1 else 0)
    return text, start + 1, score


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-fetch", action="store_true", help="reuse clones already in .cache/usage/")
    args = ap.parse_args()

    cfg = json.loads((ROOT / "data/upstream.json").read_text(encoding="utf-8"))
    api = json.loads((ROOT / "data/api.json").read_text(encoding="utf-8"))
    funcs = [f"{p['name']}.{m['name']}" for p in api["pages"]
             if p["kind"] == "namespace" for m in p["members"] if m["kind"] == "function"]
    rx = re.compile(r"(?<![\w.:])(" + "|".join(re.escape(f) for f in sorted(funcs, key=len, reverse=True)) + r")\s*\(")

    CACHE.mkdir(parents=True, exist_ok=True)
    repos_meta = {}
    hits: dict[str, list[dict]] = defaultdict(list)
    for repo in cfg["usage_repos"]:
        path = CACHE / repo["repo"].replace("/", "__") if args.no_fetch else fetch(repo)
        if not path.exists():
            print(f"skip {repo['repo']}: not cloned", file=sys.stderr)
            continue
        sha = git("-C", str(path), "rev-parse", "HEAD")
        repos_meta[repo["repo"]] = {"label": repo.get("label", repo["repo"]), "sha": sha}
        sub = path / repo.get("path", "")
        for lua in sorted(sub.rglob("*.lua")):
            relparts = lua.relative_to(path).parts
            if any(part in SKIP_DIRS for part in relparts[:-1]):
                continue
            try:
                lines = lua.read_text(encoding="utf-8").splitlines()
            except UnicodeDecodeError:
                continue
            for i, line in enumerate(lines):
                code = line.split("--", 1)[0]
                for m in rx.finditer(code):
                    sn = snippet(lines, i, m.start())
                    if not sn:
                        continue
                    text, start, score = sn
                    hits[m.group(1)].append({
                        "repo": repo["repo"], "path": "/".join(relparts), "line": i + 1,
                        "start": start, "snippet": text, "score": score,
                    })

    calls = {}
    for fn in funcs:
        found = hits.get(fn, [])
        if not found:
            continue
        # choose varied, compact snippets: one per repo first, shortest first, no duplicates
        found.sort(key=lambda h: (h["snippet"].count("\n"), len(h["snippet"])))
        chosen, seen_text, seen_repo = [], set(), set()
        for pass_ in (0, 1):
            for h in found:
                key = re.sub(r"\s+", "", h["snippet"])
                if key in seen_text or len(h["snippet"]) < len(fn) + 3:
                    continue
                if pass_ == 0 and h["repo"] in seen_repo:
                    continue
                chosen.append(h)
                seen_text.add(key)
                seen_repo.add(h["repo"])
                if len(chosen) >= MAX_SNIPPETS:
                    break
            if len(chosen) >= MAX_SNIPPETS:
                break
        for h in chosen:
            h.pop("score", None)
        calls[fn] = {
            "count": len(found),
            "projects": sorted({h["repo"] for h in found}),
            "snippets": chosen,
        }

    out = {"repos": repos_meta, "calls": calls}
    (ROOT / "data/usage.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    unused = [f for f in funcs if f not in calls]
    print(f"indexed {sum(c['count'] for c in calls.values())} call sites for {len(calls)}/{len(funcs)} functions "
          f"across {len(repos_meta)} repos; {len(unused)} functions have no real-world usage")
    return 0


if __name__ == "__main__":
    sys.exit(main())
