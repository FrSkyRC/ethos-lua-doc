# Updating the API docs

The API reference is generated from FrSky's `lua-doc.zip`, which is rebuilt for every Ethos release.

## Where `lua-doc.zip` comes from

Every Ethos release on [FrSkyRC/ETHOS-Feedback-Community → Releases](https://github.com/FrSkyRC/ETHOS-Feedback-Community/releases) has a `lua-doc.zip` asset:

| Release kind | Tag example | Notes |
| --- | --- | --- |
| Nightly series | `nightly26` | Pre-release. The asset is **replaced in place** as nightlies build; a new major gets a new tag (`nightly27`) |
| Stable release | `26.1.2` | One tag per release |
| Maintenance of an older line | `1.6.8` | Can be published *after* newer releases |

**There's no permanent "latest" URL. It changes with each Ethos release**, so the updater asks the GitHub API which release to use:

| Channel | Picks |
| --- | --- |
| `nightly` (default) | Highest `nightlyNN` with a `lua-doc.zip`: the newest API |
| `stable` | Highest **version number** among full releases (not the newest date, which could be an old-line maintenance release) |
| `pinned` | Exactly the `lua_doc_url` in `data/upstream.json` |

The release, sha256 and fetch date of the zip in use are shown at the top of the [API reference](../api/index.md).

## Running an update

```bash
python scripts/update.py                     # channel from data/upstream.json
python scripts/update.py --channel stable
python scripts/update.py --zip ~/Downloads/lua-doc.zip --skip-usage   # offline, from a local file
```

It downloads and parses the zip, refreshes the official examples, rescans real-world usage, and regenerates `docs/api/`. Review with `git diff`, then `mkdocs build --strict`.

## Automatically

The **Update lua-doc** GitHub workflow runs weekly and on demand (choose the channel when running it manually). It opens a pull request with a summary when anything changed. When reviewing:

1. Look at `data/api.json`: new functions, changed parameters, removed functions.
2. A removed function breaks links from guides or overlays, and the strict build fails. Fix the links.
3. New APIs deserve an overlay example and a mention in the relevant guide.
