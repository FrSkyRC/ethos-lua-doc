# Code patterns

## Module loading

Large scripts split code across files and load them with `loadfile`. At the top level of `main.lua` a relative path works. Anything loaded later, from a callback, needs an absolute path (see [why](../getting-started/lua-environment.md#relative-paths-only-work-while-your-script-loads)):

```lua
local BASE = "SCRIPTS:/myscript/"
local util = assert(loadfile("lib/util.lua"))()                 -- top level: relative is fine

local function openSetup()
  return assert(loadfile(BASE .. "pages/setup.lua"))()          -- callback: absolute
end
```

`loadfile(path)()` **re-parses and re-runs the file on every call**. Unlike `require`, nothing is cached: each call creates a new, independent copy of the module's tables and closures. For a module loaded once at boot that's fine. For one loaded every time a page opens, it wastes RAM and CPU, and it's a real bug if the module has load-time side effects.

### Self-caching modules

Make modules that may be loaded more than once cache themselves, like `require` does:

```lua title="lib/units.lua"
local KEY = "myscript.lib.units"
if package.loaded[KEY] then return package.loaded[KEY] end

local units = {}
local NAMES = { [UNIT_VOLT] = "V", [UNIT_AMPERE] = "A" }   -- built once

function units.name(u) return NAMES[u] or "" end

package.loaded[KEY] = units
return units
```

Self-cache when a module is **loaded repeatedly** (from a page or menu the pilot opens again and again) **and** it either costs something to rebuild or has load-time side effects. Don't bother for modules loaded once by a long-lived subsystem.

### The subscription leak

If a module registers a handler **at load time** (subscribes to an event bus, registers a callback), loading it ten times registers ten handlers. None are ever removed, and all fire on every event. This is the most important reason to self-cache:

```lua
-- ✗ every loadfile() of this module adds one more handler, forever
bus.subscribe("telemetry", onTelemetry)
```

Either self-cache the module, or subscribe inside an explicit `open()` and unsubscribe in `close()`:

```lua
local handler

function page.open()
  handler = function(data) ... end
  bus.subscribe("telemetry", handler)
end

function page.close()
  if handler then
    bus.unsubscribe("telemetry", handler)
    handler = nil
  end
end
```

### Release what you cached

A self-cached module lives for the whole session. For large modules that only one tool uses, remove them when the tool closes:

```lua
local OWNED = { "myscript.pages.setup", "myscript.lib.parser" }

local function close()
  for _, key in ipairs(OWNED) do package.loaded[key] = nil end
end
```

## Clear in place

```lua
-- ✗ allocates a new table; anything holding the old one now sees stale data
cache = {}

-- ✓ empties the same table
local function clearTable(t)
  for k in pairs(t) do t[k] = nil end
end
clearTable(cache)
```

Replacing a table allocates again on the next use, and breaks every other reference to the old table, a real bug class. For arrays you refill with the same number of items each time, keep a count instead of clearing:

```lua
local items, count = {}, 0
local function reset() for i = 1, count do items[i] = nil end; count = 0 end
local function push(v) count = count + 1; items[count] = v end
```

## Change detection

Do work only when inputs change:

```lua
local last = {}

local function changed(key, value)
  if last[key] ~= value then
    last[key] = value
    return true
  end
  return false
end

-- in wakeup
if changed("volts", math.floor(v * 10)) then
  widget.voltText = string.format("%.1fV", v)
  lcd.invalidate()
end
```

## Per-instance state

Several copies of the same widget can be on screen at once. Ethos gives each one its own table from `create()`, so keep instance state there, not in file-level variables:

```lua
-- ✗ shared by every instance: two widgets fight over `value`
local value
local function wakeup(widget) value = widget.src:value() end

-- ✓ each instance has its own
local function create() return { src = nil, value = nil } end
local function wakeup(widget) widget.value = widget.src and widget.src:value() end
```

File-level variables are right for things that really are shared: constants, loaded images used by every instance, lookup tables.

## Guard optional APIs

Newer calls don't exist on older firmware. Calling a missing function is an error that stops your script:

```lua
if system.getSources then
  sensors = system.getSources(CATEGORY_TELEMETRY_SENSOR)
end

local mem = system.getMemoryUsage and system.getMemoryUsage() or {}
```

## Bounded caches (small LRU)

For caches keyed by something open-ended (file paths, sensor names), cap the size:

```lua
local MAX = 16
local cache, order = {}, {}

local function getImage(path)
  local hit = cache[path]
  if hit ~= nil then return hit or nil end      -- false = known missing
  local img = os.stat(path) and lcd.loadBitmap(path) or false
  cache[path] = img
  order[#order + 1] = path
  if #order > MAX then
    cache[table.remove(order, 1)] = nil         -- evict the oldest
  end
  return img or nil
end
```

An evicted bitmap is freed once nothing else references it. Clear the whole cache on lifecycle events too: model change, theme change, tool close.
