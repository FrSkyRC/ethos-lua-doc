# The Lua environment

Ethos embeds **Lua 5.4** (5.4.3 at the time of writing). Most of what you know from desktop Lua works, with three differences: some libraries are missing, the `os` library has radio-specific extras, and file paths can use named prefixes.

## Available libraries

| Library | Available | Notes |
| --- | --- | --- |
| basic (`print`, `pairs`, `pcall`, `loadfile`, ...) | ✔ | `print()` output goes to the simulator console and the radio's debug serial |
| `string` | ✔ | |
| `table` | ✔ | |
| `math` | ✔ | Integers and floats are distinct (Lua 5.4): `7 // 2 == 3`, `7 / 2 == 3.5` |
| `io` | ✔ | `io.open(path, mode)`, read/write/close. Always close what you open |
| `os` | ✔, modified | See below |
| `package` / `require` | Partial | `loadfile()` is the usual way to load modules, see [Code patterns](../best-practice/patterns.md#module-loading) |
| `coroutine`, `utf8`, `debug` | Do not rely on these | |

## `os` extras

| Function | Does |
| --- | --- |
| `os.stat(path)` | Returns a table of file info (for example `size`), or `nil, message, errno` if the path doesn't exist. This is the usual existence check |
| `os.remove(path)` | Remove a file or an **empty** directory |
| `os.rename(from, to)` | Rename a file or directory |
| `os.rmtree(path)` | Remove a directory and everything in it |
| `os.mkdir(path)` | Create **one** directory. Not recursive: the parent must exist. Returns `true`, or `nil, message, errno` |
| `os.copy(from, toDir)` | Copy a file or directory into another directory |
| `os.clock()` | Seconds since boot as a float. Use it for timing and throttling |
| `os.time()` / `os.date()` | Wall-clock time from the radio's RTC |

```lua
-- make sure our log folder exists, then append a line.
-- os.mkdir is not recursive, and on a fresh radio LOGS: itself may not exist yet.
if not os.stat("LOGS:") then os.mkdir("LOGS:") end
if not os.stat("LOGS:/myscript") then os.mkdir("LOGS:/myscript") end
local f = io.open("LOGS:/myscript/events.csv", "a")
if f then
  f:write(os.date("%H:%M:%S"), ",armed\n")
  f:close()
end
```

## Path prefixes

Paths may start with a named prefix, so scripts don't need to know whether the radio stores files on an SD card or in internal flash:

| Prefix | Points to |
| --- | --- |
| `SCRIPTS:` | Lua scripts directory |
| `AUDIO:` | Audio directory (before the language folder) |
| `VOICEx:` | Audio directory for voice *x* (after the language and voice folders) |
| `BITMAPS:` | User bitmaps directory |
| `SCREENSHOTS:` | Screenshots directory |
| `LOGS:` | Logs directory |

### Relative paths only work while your script loads

While Ethos is loading your `main.lua` (its top-level code and `init()`), relative paths resolve against your script's folder. Inside `scripts/mywidget/main.lua`, `lcd.loadMask("icon.png")` loads `scripts/mywidget/icon.png`.

**After loading, that's no longer true.** In callbacks that run later (`create`, `wakeup`, `paint`, `close`, a button's `press`, ...), a relative path resolves against whichever script Ethos loaded *last*, or fails with `Lua::path is not set!` in the console. In a simulator test, a tool that saved `"settings.lua"` from its `close()` callback wrote the file into another script's folder.

```lua
-- ✓ resolve paths once, at load time, or spell them out in full
local BASE = "SCRIPTS:/mywidget/"
local icon = lcd.loadMask("icon.png")               -- fine: top level, runs during load

local function close()
  local f = io.open(BASE .. "settings.lua", "w")    -- ✓ absolute in a callback
  -- io.open("settings.lua", "w")                   -- ✗ lands in some other script's folder
end

local function openPage()
  return assert(loadfile(BASE .. "pages/setup.lua"))()   -- ✓ lazy loading needs absolute paths too
end
```

Rule of thumb: **any file access that can happen after `init()` returns uses an absolute `SCRIPTS:/<folder>/...` path.**

## Limits to design for

| Limit | What happens when you exceed it | How to stay inside it |
| --- | --- | --- |
| **Lua heap** (a few hundred KB to a few MB depending on radio, shared with bitmaps) | *"Lua has used too much RAM, it has been Killed"* | [Saving RAM](../best-practice/memory.md) |
| **Instructions per cycle** | The script is aborted when [`system.getInstructionsUsage()`](../api/system/getInstructionsUsage.md) reaches 100 | Spread long work across wakeups, see [Saving CPU](../best-practice/cpu.md) |
| **C stack** | Deep recursion can reset the radio instead of raising a Lua error | Avoid unbounded recursion, see [Pitfalls](../best-practice/pitfalls.md#unbounded-recursion) |
| **Widget key** | 7 characters max | Keep keys short and unique |

## Compiled scripts (`.luac`)

Ethos 26.1 compiles each script's `main.lua` to `main.luac` when it loads it; the simulator console shows `Lua::compile('main.luac')` right after `Lua::load(...)`. When you copy a new `main.lua` over an old one during development, delete the stale `main.luac` too, so you know which one runs. [`system.compile(path)`](../api/system/compile.md) compiles any `.lua` file to `.luac` on the radio, and a package may ship `main.luac` instead of `main.lua`. Compiled chunks load faster and skip the parser's temporary allocations at boot. Compile on the target firmware: bytecode isn't guaranteed to be portable between Ethos versions.

```lua
-- compile our own modules once, e.g. from a tool's "optimize" button
for _, file in ipairs({ "lib/util.lua", "lib/draw.lua" }) do
  if os.stat(file) then system.compile(file) end
end
```
