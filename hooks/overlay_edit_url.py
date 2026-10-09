"""Point the "edit this page" button of generated API pages at their overlay.

scripts/gen_api_pages.py writes front matter like:

    overlay: overlays/api/lcd/drawText.md
    overlay_exists: false

Editing the generated page itself would be pointless (it is rebuilt from
data/api.json), so the button opens the overlay instead, or GitHub's
"new file" form pre-filled with the overlay path when none exists yet.
"""

from __future__ import annotations

import posixpath


def on_page_context(context, page, config, nav):
    overlay = page.meta.get("overlay")
    repo = (config.get("repo_url") or "").rstrip("/")
    if not overlay or not repo:
        return context
    if page.meta.get("overlay_exists"):
        page.edit_url = f"{repo}/edit/main/{overlay}"
    else:
        folder, name = posixpath.split(overlay)
        page.edit_url = f"{repo}/new/main/{folder}?filename={name}"
    return context
