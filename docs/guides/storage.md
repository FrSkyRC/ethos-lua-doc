# Saving settings

## Widgets: `read` and `write`

A widget's settings are saved **inside the model file**, alongside the screen layout. You don't pick a file: implement `read` and `write`, and use [`storage.read`](../api/storage/read.md) / [`storage.write`](../api/storage/write.md) inside them.

```lua
local function read(widget)
  widget.source = storage.read("source")
  widget.warn   = storage.read("warn") or 33     -- default for widgets saved by an older version
  widget.color  = storage.read("color") or lcd.RGB(0, 200, 0)
end

local function write(widget)
  storage.write("source", widget.source)
  storage.write("warn", widget.warn)
  storage.write("color", widget.color)
end
```

- Values can be numbers, strings, booleans, colors, and **Source objects**. A saved source is restored as a live `Source`.
- Keep `read` and `write` in step: same keys, same order. It makes them easy to compare when you add a setting.
- When you add a setting in a new version, give it a default (`or 33`). Widgets saved by the old version won't have it.

Ethos calls `write` after the pilot leaves the widget's configuration, and `read` when the model loads.

!!! tip "Version your settings"
    Write a version number first. A later release can then migrate old layouts:

    ```lua
    local SETTINGS_VERSION = 2

    local function write(widget)
      storage.write("v", SETTINGS_VERSION)
      storage.write("source", widget.source)
      storage.write("warn", widget.warn)
    end

    local function read(widget)
      local v = storage.read("v")
      widget.source = storage.read("source")
      widget.warn = storage.read("warn")
      if v == nil then              -- saved by version 1: warn was stored in tenths
        widget.warn = widget.warn and widget.warn / 10
      end
    end
    ```

Tasks and sources support the same `read`/`write` pair.

## Tools and global settings: files

System tools aren't tied to a model, so they keep their settings in files. Store them under your script's folder or a `LOGS:` subfolder for data. Use **absolute** paths, because these functions run from callbacks (see [why](../getting-started/lua-environment.md#relative-paths-only-work-while-your-script-loads)):

```lua
local FILE = "SCRIPTS:/mytool/settings.lua"   -- absolute, never relative in callbacks

local function save(t)
  local f = io.open(FILE, "w")
  if not f then return false end
  f:write("return {\n")
  for k, v in pairs(t) do
    if type(v) == "string" then
      f:write(string.format("  %s = %q,\n", k, v))
    else
      f:write(string.format("  %s = %s,\n", k, tostring(v)))
    end
  end
  f:write("}\n")
  f:close()
  return true
end

local function load()
  local chunk = loadfile(FILE)
  local ok, t = pcall(chunk or function() return {} end)
  return (ok and type(t) == "table") and t or {}
end
```

Saving as a Lua table and reading it back with `loadfile` needs no parser code. For larger or user-editable data, INI or CSV files are common in open-source suites.

!!! warning "Write rarely"
    Flash storage is slow and wears out. Never write files from `wakeup` on every tick. Save when the pilot confirms a change, or when a tool closes. For logging, buffer lines in a table and flush every few seconds (see [Saving CPU](../best-practice/cpu.md#batch-file-writes)).

## Per-model data from a tool

To keep tool data per model, include the model in the file name:

```lua
local function modelFile()
  local name = model.name():gsub("[^%w_-]", "_")   -- safe file name
  return "LOGS:/mytool/" .. name .. ".lua"
end
```
