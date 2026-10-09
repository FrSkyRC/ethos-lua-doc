# Files, folders & packaging

## Layout on the radio

Each script is one folder under `SCRIPTS:` (the `scripts` directory on the radio's storage):

```text
scripts/
├── bigvalue/
│   └── main.lua              ← required: entry point, returns { init = init }
└── mysuite/
    ├── main.lua
    ├── ethos_lua_manifest.json   ← written by the installer (see below)
    ├── lib/
    │   └── util.lua          ← loaded with loadfile("lib/util.lua")
    ├── i18n/
    │   └── en.lua
    └── gfx/
        └── icon.png          ← loaded with lcd.loadMask("gfx/icon.png")
```

- Ethos scans `scripts/*/main.lua` (or `main.luac`) at boot. Nothing else is loaded automatically.
- Relative paths resolve against the script folder only while `main.lua` loads. Code that runs later uses absolute `SCRIPTS:/<folder>/...` paths, so pick the folder name once and keep it stable (see [The Lua environment](lua-environment.md#relative-paths-only-work-while-your-script-loads)).
- Keep folder names short, without spaces, and stable across releases. Model files refer to widgets by `key`, but your code refers to the folder in its absolute paths.

## Installable zip packages

Ethos Suite's **Lua Library → Install from local `.zip`** (and the web simulator's **Upload a Lua plugin**) install a zip containing an `ethos_lua_manifest.json` at its root. The manifest says which files to copy and where.

```json title="ethos_lua_manifest.json"
{
  "manifestVersion": 1,
  "name": "Big Value",
  "key": "com.example.bigvalue",
  "version": "1.2.0",
  "introduction": "Shows any source in large text.",
  "releaseNotes": { "format": "markdown", "content": "## 1.2.0\n- Font scales with widget size" },
  "folder": "bigvalue",
  "files": ["main.lua", "lib/*", "gfx/**"]
}
```

| Field | Required | Rules |
| --- | --- | --- |
| `manifestVersion` | yes | Must be `1` |
| `name` | yes | Display name, ≤ 128 chars |
| `key` | yes | Globally unique and **stable forever**; reverse-domain style recommended. Used to match upgrades |
| `version` | yes | Three numeric parts, e.g. `1.0.0`. Increase it every release |
| `folder` | yes | Install directory under `SCRIPTS:`; letters, digits, `.`, `_`, `-` |
| `files` | yes | Paths relative to the zip root. `dir/*` matches one level, `dir/**` recurses. Must resolve to at least `main.lua` or `main.luac` |
| `introduction` | no | One sentence, ≤ 1024 chars |
| `releaseNotes` | no | String (Markdown), or `{ "format": "markdown" | "text", "content": "..." }` |

!!! warning "Things that make an install fail"
    - A manifest that exists but is invalid fails the whole install.
    - `..`, absolute paths, and drive letters are rejected in `files`.
    - If a path's first segment equals `folder`, that segment is stripped on install, so `folder: "C"` with `files: ["C/**"]` installs to `scripts/C/...`, not `scripts/C/C/...`.

On upgrade, files listed in the *previously installed* manifest are removed before the new ones are copied, so files you drop from a release don't linger. The older `scriptinfo.json` format is no longer read.

The full specification is in FrSky's [ethos_lua_manifest.md](https://github.com/FrSkyRC/ETHOS-Feedback-Community/blob/HEAD/lua/frsky/ethos_lua_manifest.md).

## Release checklist

1. `key` unchanged since the last release; `version` increased.
2. Every runtime file is covered by `files` (test by installing the zip into a clean simulator).
3. No development leftovers: test data, `print` spam in `wakeup`, debug overlays.
4. Tested on the smallest screen you support. The X18 family is 480×320; X20 family is 800×480.
5. Consider shipping `.luac` for large modules (see [The Lua environment](lua-environment.md#compiled-scripts-luac)).
