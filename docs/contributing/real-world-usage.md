# Real-world usage

API pages show a **Real-world usage** section: short excerpts from open-source Ethos Lua projects, each linked to the exact file and line on GitHub. Reference docs say what a function does; production code shows how people actually use it, including the guards, caching and edge cases.

## Projects scanned

A curated set of public, open-source Ethos Lua projects, from large multi-page suites and dashboards to small single-purpose widgets and FrSky's own scripts. The list is in `usage_repos` in [`data/upstream.json`](https://github.com/FrSkyRC/ethos-lua-doc/blob/main/data/upstream.json). Each excerpt links to its exact source file and line.

## How snippets are chosen

`scripts/scan_usage.py` shallow-clones each repository's default branch and finds every call to every namespace function. For each function it keeps up to three excerpts:

- one per project first, for variety;
- preferring calls inside a short enclosing function (shown whole), then a few lines of context;
- skipping calls whose parentheses don't close within reach, so excerpts are never truncated mid-call;
- dropping duplicates.

Call counts also feed the **Most used** table on the [API index](../api/index.md).

Excerpts are shown as-is, under each project's own license. They illustrate usage; they aren't endorsed as best practice. When they conflict with [Best practice](../best-practice/index.md), follow best practice.

## Adding a project

Add it to `usage_repos` in `data/upstream.json`:

```json
{"repo": "owner/name", "label": "Display name"}
```

Optional keys: `branch` (default: the repo's default branch) and `path` (scan only a subfolder; uses a sparse clone). Then run `python scripts/scan_usage.py && python scripts/gen_api_pages.py`.
