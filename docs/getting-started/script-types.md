# Script types & lifecycle

A script's `init()` registers one or more **items**. Each item type is a table of callbacks that Ethos calls at specific moments. Pick the type by what the pilot should see.

| Type | Register with | Pilot sees it | Use it for |
| --- | --- | --- | --- |
| **Widget** | [`system.registerWidget`](../api/system/registerWidget.md) | A tile on a home screen | Live displays: telemetry, gauges, timers |
| **System tool** | [`system.registerSystemTool`](../api/system/registerSystemTool.md) | An icon in the System menu, full-screen page | Setup apps, configurators, games |
| **Task** | [`system.registerTask`](../api/system/registerTask.md) | Nothing (enabled per model under *Model → Lua*) | Background work: alerts, logging, telemetry bridges |
| **Source** | [`system.registerSource`](../api/system/registerSource.md) | A new source in every source picker | Computed values usable by mixes, logic switches, other widgets |
| **Sensor** | [`system.registerSensor`](../api/system/registerSensor.md) | Proper name/unit for an S.Port sensor | Teaching Ethos about a custom sensor ID |
| **Layout** | [`system.registerLayout`](../api/system/registerLayout.md) | A new screen layout | Custom arrangements of widget slots |
| **Theme** | [`system.registerTheme`](../api/system/registerTheme.md) | A color theme | Branding |

One `main.lua` may register any combination of these.

## Widgets

```lua
system.registerWidget({
  key = "mywdgt",              -- unique, max 7 chars; used to save/restore the widget
  name = "My widget",          -- string, or function returning a (translated) string
  create = create,             -- () -> widget state table
  build = build,               -- (widget) after create + configure, when the screen is built
  wakeup = wakeup,             -- (widget) called continuously
  paint = paint,               -- (widget) draw; called after lcd.invalidate()
  event = event,               -- (widget, category, value, x, y) -> true to consume
  configure = configure,       -- (widget) build a form with form.* calls
  read = read, write = write,  -- (widget) restore / save settings with storage.*
  menu = menu,                 -- (widget) -> { {"Label", function() ... end}, ... }
  destroy = destroy,           -- (widget) widget removed
  persistent = false,          -- keep running when the screen isn't shown
  title = false,               -- force the widget title bar on/off
})
```

**Order of calls when a screen loads:** `create` → `read` → (`build`) → `wakeup`/`paint` loop. When the pilot edits settings: `configure` → `write`. Each instance of the widget on a screen gets its **own** state table from `create()`, so never keep per-instance state in file-level locals.

!!! note "`wakeup` vs `paint`"
    `wakeup` runs on a loop whether or not anything changed; keep it cheap. `paint` runs only when the widget has been invalidated (`lcd.invalidate()`) or Ethos needs a redraw. Drawing calls (`lcd.draw*`) only work inside `paint`.

## System tools

```lua
system.registerSystemTool({
  name = "My tool",
  icon = lcd.loadMask("icon.png"),  -- required: without it Ethos logs "missing icon"; black-on-white mask
  create = create,   -- () -> state; build your form here with form.* calls
  wakeup = wakeup,   -- (state)
  paint = paint,     -- (state) for custom drawing on top of / instead of a form
  event = event,     -- (state, category, value, x, y)
  close = close,     -- (state) the page was closed: release resources here
})
```

A tool's `create()` usually builds a form (see [Forms](../guides/forms.md)). The page stays alive until the pilot leaves it, then `close` runs. Use `close` to free bitmaps, close files, and drop caches; see [Saving RAM](../best-practice/memory.md#release-on-close). `system.exit()` closes the tool from code.

## Tasks

```lua
system.registerTask({
  key = "mytask",       -- max 7 chars
  name = "My task",
  init = init,          -- task started (model loaded with the task enabled)
  wakeup = wakeup,      -- called continuously
  event = event,
  done = done,          -- task stopped
  configure = configure, read = read, write = write,  -- optional settings form
})
```

Tasks have no screen. They are ideal for alerts and data collection, but because they run **all the time**, they are also where careless code costs the most battery and CPU. Throttle them (see [Background alert task](../cookbook/alert-task.md)).

## Sources

```lua
system.registerSource({
  key = "mysrc", name = "My source",
  init = init,        -- (source) set unit, decimals, range here
  wakeup = wakeup,    -- (source) compute and source:value(newValue)
  configure = configure, read = read, write = write,
})
```

The registered source appears everywhere a source can be picked: mixes, logic switches, telemetry screens, other widgets. See the [Lua source recipe](../cookbook/lua-source.md).

## The event handler

Widgets, tools and tasks share one event signature:

```lua
local function event(widget, category, value, x, y)
  if category == EVT_KEY and value == KEY_ENTER_BREAK then
    -- ...
    return true      -- consumed: Ethos won't also handle this key
  end
  return false
end
```

See [Events, keys & touch](../guides/events.md) for categories and key codes.

## Checking the radio before calling new APIs

Every [API page](../api/index.md) shows the Ethos version that introduced the call. To support older firmware, test for the function before you call it:

```lua
if lcd.setWindowTitle then
  lcd.setWindowTitle("My tool")
end

local v = system.getVersion()   -- { major=26, minor=1, revision=0, board="X20S", simulation=false, ... }
if v.major > 1 or (v.major == 1 and v.minor >= 6) then
  -- 1.6+ only code
end
```
