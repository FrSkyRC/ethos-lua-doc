# Saving RAM

## Know the budget

[`system.getMemoryUsage()`](../api/system/getMemoryUsage.md) returns:

| Field | Meaning |
| --- | --- |
| `luaRamAvailable` | Bytes left for Lua scripts (the heap your tables, strings and code live in) |
| `luaBitmapsRamAvailable` | Bytes left for decoded bitmaps and masks |
| `ramAvailable` | Free system RAM |
| `mainStackAvailable` | Free bytes on the main task's C stack (a separate budget, see [Pitfalls](pitfalls.md#unbounded-recursion)) |

!!! info "One region, two views"
    On current radios (an X18RS memory map is shown below), the Lua heap and the Lua bitmap arena are carved from the **same SDRAM region**. A script that grows the heap eats bitmap headroom, and the failure may surface as a *bitmap* error. Treat them as one budget.

    | Region | Size | Holds |
    | --- | --- | --- |
    | DTCMRAM | 128 KB | All firmware variables and all task stacks |
    | RAM_D1 | 512 KB | Model allocator (mixer) |
    | RAM_D2 | 288 KB | Model backup, loaded on emergency mode |
    | SDRAM | 8 MB | **Lua heap and bitmap arena**, plus everything else |

    *Source: the Ethos linker script and firmware author.*

When the heap passes its limit Ethos kills the script with *"Lua has used too much RAM, it has been Killed"*.

## What costs memory

Roughly in order of how often it bites:

1. **Decoded images.** A PNG file of a few KB can decode to hundreds of KB.
2. **Loaded code.** Every module you `loadfile()` keeps its functions, constants and strings resident. Large suites measure tens of KB per subsystem.
3. **Form widgets.** Ethos retains some form allocations even after `form.clear()`, outside Lua's reach (see [below](#forms-retain-memory)).
4. **Caches that never shrink.** A table keyed by file path, sensor name or screen that only grows.
5. **Churn.** Not retained memory, but garbage created per call on hot paths. It raises the heap's peak, and the peak is what gets you killed.

## Bitmaps

```lua
-- ✗ loads and decodes on every paint
local function paint(w)
  lcd.drawBitmap(0, 0, lcd.loadBitmap("bg.png"))
end

-- ✓ load once, reuse the handle
local bg = lcd.loadBitmap("bg.png")
local function paint(w)
  if bg then lcd.drawBitmap(0, 0, bg) end
end
```

- **Size assets to how they're displayed.** Don't ship a 800×480 background for a 200×100 widget and let Ethos scale it.
- **Use masks for icons.** A mask is single-channel and takes its color from `lcd.color()`, so it's smaller and follows the theme.
- **Transparency costs more.** The API notes that bitmaps with transparency use more resources.
- **Lazy load is the default.** `lcd.loadBitmap(path)` / `lcd.loadMask(path)` defer decoding until first draw (`lazy` defaults to `true`).
- **Bound open-ended caches.** If image paths come from user configuration (model photos, theme packs), each new path adds an entry. Cap the cache (a small LRU) *and* clear it on lifecycle events such as theme change, model change and tool close.
- **Cache misses too.** Remember paths that didn't exist (`cache[path] = false`) so you don't probe storage every frame.

## Load code when it's needed, not at boot

Code you load at boot stays in RAM for the whole session. For parts most pilots rarely open (setup pages, diagnostics, a tool's sub-pages), load them at the point of use:

```lua
local diagnostics   -- not loaded until first opened

local function openDiagnostics()
  diagnostics = diagnostics or assert(loadfile("SCRIPTS:/mytool/pages/diagnostics.lua"))()  -- absolute: runs after load
  diagnostics.open()
end
```

Measured on an X18RS: deferring a tool's UI subtree (ten modules, ~53 KB of source) from boot to first use saved **60.4 KB** of resting RAM. The saving is in the resting state only: once the tool is open, the code is loaded either way.

!!! warning "Not for top-level registration"
    Don't wrap a widget's or tool's **registration** in lazy proxy callbacks to save startup RAM. One large suite tried exactly that, measured *more* retained RAM over a session than registering real callbacks eagerly, and reverted. Defer the UI *underneath* an eagerly registered item, not the registration. FrSky's [lazy-loading example](../examples/official/lazy-loading.md) documents the same caveat, and notes that wrapping `read`/`write` rarely defers anything, because Ethos calls `read` when the screen loads.

## Release on close

A system tool's `close()` is your chance to give memory back:

```lua
local state = {}

local function close()
  state.images = nil        -- drop bitmap handles
  state.pages = nil         -- drop page modules
  for _, key in ipairs(state.loadedKeys or {}) do
    package.loaded[key] = nil  -- un-cache modules this tool cached
  end
  state = {}
  collectgarbage("collect") -- one full cycle on close is fine; never on a hot path
end
```

Nil every large reference: bitmap handles, page modules, caches and big tables. Anything still referenced from a module-level variable stays alive.

## Forms retain memory

Testing on radios shows Ethos keeps some `form` widget and callback allocations after `form.clear()`, outside the Lua garbage collector's reachability graph. A forced `collectgarbage("collect")` does **not** recover it. One suite measured roughly 30–44 KB per complex page visit that no Lua-side fix could reclaim. A census of every Lua object reachable from `_G` and `package.loaded` showed nothing retained, so the memory is held by the platform.

What you *can* do:

- **Rebuild forms only when their structure changes.** Use `field:enable()` to show and hide options, and update values through getters, instead of `form.clear()` plus a rebuild.
- **Reuse getter/setter closures** across rebuilds (pool them per page and field). Fresh closures on every rebuild add to what's retained.
- **Don't evict that closure pool** when a page closes. Widgets that are still retained hold the old closures, so eviction just guarantees a new set next visit. Measured: a pool keyed by field shape saturates at its first tour (195 entries), while evict-on-release grew linearly (3,900 after 20 tours).

## Hot paths: stop allocating

`wakeup` runs many times a second, and a widget's `paint` often does too. Every table, closure or concatenated string created there is garbage a moment later. That garbage raises the heap's peak and makes the collector work harder.

```lua
-- ✗ new table + new closure + new string every tick
local function wakeup(widget)
  local cfg = { min = 0, max = 100 }                     -- table per call
  local fmt = function(v) return v .. "%" end            -- closure per call
  widget.text = fmt(widget.src:value())                  -- string per call, even if unchanged
  lcd.invalidate()
end

-- ✓ constants at file level, work only on change
local CFG = { min = 0, max = 100 }
local function wakeup(widget)
  local v = widget.src:value()
  if v ~= widget.last then
    widget.last = v
    widget.text = v .. "%"
    lcd.invalidate()
  end
end
```

Measured in one suite's dashboard: three per-call allocations on wakeup paths cost 184 B, 128 B and 1,392 B **per call**: a lookup table rebuilt for constants the file already had, a throwaway closure, and a copy of a subscriber list. At 20 Hz that's ~34 KB/s of garbage from three lines.

Rules that follow:

1. **Constant lookup tables live at file level, in one place only.** Two copies of the same mapping will eventually disagree.
2. **Reuse result tables per key** instead of returning a fresh table per call.
3. **Clear reusable tables in place** instead of replacing them. See [Code patterns](patterns.md#clear-in-place).

## Tuning the garbage collector

Lua's incremental collector starts a cycle when the heap reaches `pause`% of the live size after the last cycle. The default is **200**: with 400 KB live, the heap may reach ~800 KB before collection starts. On a radio that can be past the kill limit.

Some suites lower the pause at startup so collection starts earlier:

```lua
local function init()
  local ok, prev = pcall(collectgarbage, "setpause", 120)  -- returns the PREVIOUS value
  print("gc pause set to 120 (was " .. tostring(prev) .. ")")
  -- ...
end
```

- This changes **when** collection starts, not **what** can be collected. It lowers the peak; it doesn't reduce allocation, and it can't free retained memory.
- Never call `collectgarbage("setpause")` **without a value**. That sets the pause to **0**: the collector then runs continuously.
- Judge the change by the **peak** Lua memory over a real session, A/B against the default.

## Don't reach for `collectgarbage("collect")`

A forced full collection reclaims only memory that is already unreachable. If RAM keeps growing, something still holds a reference, or the platform holds it (see [forms](#forms-retain-memory)). One suite forced a collect on every menu rebuild and measured growth that was statistically indistinguishable from not forcing it. A full collection on a hot path also costs a lot of CPU.

Fix growth by removing references: cache modules properly, unsubscribe handlers, clear caches, bound open-ended keys. One `collectgarbage("collect")` when a tool closes is reasonable housekeeping.

## Quick reference

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| RAM climbs on every visit to the same page | Module reloaded with `loadfile()` each visit, rebuilding its tables | Cache it in `package.loaded` ([patterns](patterns.md#module-loading)) |
| RAM climbs *and* events fire twice, then three times... | A module subscribes or registers at load time and is loaded repeatedly | Cache the module; never subscribe at load time without caching |
| A page's callbacks keep firing after it closed | Subscribed in `open`, never unsubscribed | Pair every subscribe with an unsubscribe in `close` |
| A cache grows for the whole session | Open-ended keys and no eviction | LRU bound plus clearing on lifecycle events |
| Growth on page or menu rebuilds that a forced collect can't recover | Ethos `form` retention | Rebuild less often; pool closures |
| Heap spikes during busy telemetry | Per-call allocations on wakeup paths | File-level constants, reuse tables, compute on change |
| *"Lua has used too much RAM"* during boot | Everything loaded eagerly at boot | Load rarely-used UI at point of use; consider `.luac` |
| Bitmap load fails while Lua RAM looks fine | Shared SDRAM region exhausted by heap or other images | Smaller images, masks, release on close |
