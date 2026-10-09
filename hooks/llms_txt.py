"""Write site/llms.txt: a plain-text map of the site for AI agents.

Format follows https://llmstxt.org: an H1, a one-line summary, then one
section per top-level nav entry with `- [title](url): summary` lines. The
per-function API pages are summarised by a pointer to api-index.json rather
than listed one by one, to keep the file small.
"""

from __future__ import annotations

from pathlib import Path

_pages: list = []
_nav = None


def on_nav(nav, config, files):
    global _nav
    _nav = nav
    return nav


def on_page_context(context, page, config, nav):
    _pages.append(page)
    return context


def _first_sentence(page) -> str:
    text = (page.meta or {}).get("description") or ""
    if not text and page.markdown:
        for para in page.markdown.split("\n\n"):
            para = para.strip()
            if para and not para.startswith(("#", "<", "!", "|", "```", "-", "*", "---", "<!--")):
                text = para.replace("\n", " ")
                break
    return text.split(". ")[0].strip()[:200]


def _walk(items, base, out, depth=0):
    for item in items:
        if item.is_page:
            if "/api/" in "/" + (item.file.src_uri if item.file else "") and depth > 0:
                continue  # summarised via api-index.json
            summary = _first_sentence(item)
            line = f"- [{item.title}]({base}{item.url})"
            out.append(line + (f": {summary}" if summary else ""))
        elif item.is_section:
            if depth == 0:
                out.append(f"\n## {item.title}\n")
            _walk(item.children, base, out, depth + 1)


def on_post_build(config):
    if _nav is None:
        return
    base = (config.get("site_url") or "/").rstrip("/") + "/"
    out = [f"# {config['site_name']}", "", f"> {config.get('site_description', '')}", ""]
    out.append("Machine-readable API index (every function, signature, version, URL): "
               f"{base}api/api-index.json")
    _walk(_nav.items, base, out)
    Path(config["site_dir"], "llms.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
