"""One-shot refresh: fetch the latest upstream sources and regenerate the site content.

Steps:
  1. Download lua-doc.zip (FrSky's Doxygen API dump) into .cache/
  2. Extract it and parse it into data/api.json (with source metadata)
  3. Fetch FrSky's official Lua examples (sparse git clone) into .cache/
  4. Scan public Ethos Lua projects for real-world calls (data/usage.json)
  5. Regenerate docs/examples/official/ and docs/api/

Which lua-doc.zip:
  Every Ethos release on FrSkyRC/ETHOS-Feedback-Community carries a lua-doc.zip
  asset. "nightlyNN" tags are rolling pre-releases whose asset is replaced in
  place as new nightlies build. --channel picks one (default: "channel" in
  data/upstream.json):
    nightly   highest-numbered nightlyNN release that has lua-doc.zip (newest API)
    stable    newest non-prerelease release that has lua-doc.zip
    pinned    exactly data/upstream.json "lua_doc_url"

Usage:
    python scripts/update.py                      # default channel, download everything
    python scripts/update.py --channel stable
    python scripts/update.py --zip path/to/lua-doc.zip --examples C:/Github/ETHOS-Feedback-Community/lua/examples
    python scripts/update.py --url https://github.com/FrSkyRC/ETHOS-Feedback-Community/releases/download/nightly27/lua-doc.zip

See AGENTS.md for where the upstream files come from and how to pick the release tag.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache"
CONFIG = ROOT / "data/upstream.json"


def rmtree(path: Path) -> None:
    """shutil.rmtree that also removes read-only files (git packs on Windows)."""
    def onexc(func, p, _exc):
        os.chmod(p, stat.S_IWRITE)
        func(p)
    shutil.rmtree(path, onexc=onexc)


def run(*args: str) -> None:
    print("+", " ".join(args))
    subprocess.run(args, check=True)


def download(url: str, dst: Path) -> None:
    print(f"downloading {url}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "ethos-lua-doc-updater"})
    with urllib.request.urlopen(req, timeout=120) as r, open(dst, "wb") as f:
        shutil.copyfileobj(r, f)


def safe_extract(zf: zipfile.ZipFile, dst: Path) -> None:
    dst = dst.resolve()
    for info in zf.infolist():
        target = (dst / info.filename).resolve()
        if not str(target).startswith(str(dst)):
            raise SystemExit(f"refusing zip entry outside target: {info.filename}")
    zf.extractall(dst)


def find_doc_root(path: Path) -> Path:
    """The zip may or may not wrap everything in a top-level folder."""
    hit = next(path.rglob("namespacelcd.html"), None)
    if not hit:
        raise SystemExit(f"no namespacelcd.html found under {path}: is this really lua-doc.zip?")
    return hit.parent


def fetch_examples(repo: str) -> Path:
    dst = CACHE / "feedback-community"
    if dst.exists():
        rmtree(dst)
    # default branch on purpose: FrSky names it after the current release (e.g. "26.1")
    run("git", "clone", "--depth", "1", "--filter=blob:none", "--sparse",
        f"https://github.com/{repo}.git", str(dst))
    run("git", "-C", str(dst), "sparse-checkout", "set", "lua/examples")
    return dst / "lua/examples"


def resolve_url(repo: str, channel: str, pinned: str) -> str:
    """Find the lua-doc.zip download URL for a release channel via the GitHub API."""
    if channel == "pinned":
        return pinned
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/releases?per_page=100",
                                 headers={"User-Agent": "ethos-lua-doc-updater",
                                          "Accept": "application/vnd.github+json",
                                          **({"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"}
                                             if os.environ.get("GITHUB_TOKEN") else {})})
    with urllib.request.urlopen(req, timeout=60) as r:
        releases = json.load(r)

    def asset(rel):
        return next((a["browser_download_url"] for a in rel.get("assets", []) if a["name"] == "lua-doc.zip"), None)

    if channel == "nightly":
        nightlies = [(int(m.group(1)), r) for r in releases
                     if (m := re.fullmatch(r"nightly(\d+)", r["tag_name"])) and asset(r)]
        if nightlies:
            return asset(max(nightlies, key=lambda t: t[0])[1])
        print("no nightly release with lua-doc.zip found; falling back to stable")
    # Highest version, not newest date: FrSky also ships maintenance releases of
    # older lines (e.g. 1.6.8 published after 26.1.2), which must not win.
    stable = [(tuple(int(x) for x in r["tag_name"].split(".")), r) for r in releases
              if re.fullmatch(r"\d+(\.\d+)+", r["tag_name"])
              and not r.get("prerelease") and not r.get("draft") and asset(r)]
    if stable:
        return asset(max(stable, key=lambda t: t[0])[1])
    raise SystemExit(f"no release with lua-doc.zip found in {repo}")


def main() -> int:
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--channel", choices=["nightly", "stable", "pinned"], default=cfg.get("channel", "nightly"))
    ap.add_argument("--url", help="explicit lua-doc.zip URL (overrides --channel)")
    ap.add_argument("--zip", type=Path, help="use a local lua-doc.zip instead of downloading")
    ap.add_argument("--examples", type=Path, help="use a local lua/examples folder instead of cloning")
    ap.add_argument("--skip-examples", action="store_true")
    ap.add_argument("--skip-usage", action="store_true", help="keep data/usage.json as is (no repo clones)")
    args = ap.parse_args()

    py = sys.executable
    CACHE.mkdir(exist_ok=True)

    # 1. lua-doc.zip
    zpath = args.zip or CACHE / "lua-doc.zip"
    if not args.zip:
        args.url = args.url or resolve_url(cfg["examples_repo"], args.channel, cfg["lua_doc_url"])
        print(f"channel {args.channel}: {args.url}")
        download(args.url, zpath)
        if args.url != cfg["lua_doc_url"]:  # remember what we used, so the next run / reviewers can see it
            cfg["lua_doc_url"] = args.url
            CONFIG.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    sha = hashlib.sha256(zpath.read_bytes()).hexdigest()
    extract = CACHE / "lua-doc"
    if extract.exists():
        rmtree(extract)
    with zipfile.ZipFile(zpath) as zf:
        safe_extract(zf, extract)
    doc_root = find_doc_root(extract)

    # 2. parse
    release = re.search(r"/download/([^/]+)/", args.url or "")
    meta = {
        "url": None if args.zip else args.url,
        "release": release.group(1) if (release and not args.zip) else "local",
        "sha256": sha,
        "fetched": dt.date.today().isoformat(),
    }
    old = {}
    api_json = ROOT / "data/api.json"
    if api_json.exists():
        old = json.loads(api_json.read_text(encoding="utf-8")).get("source", {})
    if old.get("sha256") == sha:
        meta["fetched"] = old.get("fetched", meta["fetched"])  # keep diffs quiet when nothing changed
    meta_path = CACHE / "meta.json"
    meta_path.write_text(json.dumps(meta), encoding="utf-8")
    run(py, "-I", str(ROOT / "scripts/parse_lua_doc.py"), str(doc_root), "-o", str(api_json), "--meta", str(meta_path))

    # 3/4. examples, then API pages (API pages link to examples, so examples go first)
    if not args.skip_examples:
        ex = args.examples or fetch_examples(cfg["examples_repo"])
        run(py, "-I", str(ROOT / "scripts/sync_examples.py"), str(ex))
    if not args.skip_usage:
        run(py, "-I", str(ROOT / "scripts/scan_usage.py"))
    run(py, "-I", str(ROOT / "scripts/gen_api_pages.py"))

    print(f"\nlua-doc sha256 {sha[:12]} (previous {old.get('sha256', 'none')[:12]})")
    print("review with: git status && git diff --stat")
    return 0


if __name__ == "__main__":
    sys.exit(main())
