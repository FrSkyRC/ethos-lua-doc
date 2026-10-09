---
hide:
  - toc
---

<div class="hero" markdown>

# Ethos Lua Docs

<p class="lead">Lua scripting for FrSky Ethos radios: the complete API reference with examples, practical guides, and the RAM and CPU habits that keep scripts fast on real hardware.</p>

</div>

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **Getting started**

    ---

    Write, install and run your first widget in ten minutes, then learn how widgets, tools, tasks and sources fit together.

    [:octicons-arrow-right-24: First widget](getting-started/first-widget.md)

-   :material-book-open-variant:{ .lg .middle } **API reference**

    ---

    Every function, object and constant, one page each. Each page has its parameters, return values, examples and real code from open-source projects.

    [:octicons-arrow-right-24: Browse the API](api/index.md)

-   :material-memory:{ .lg .middle } **Best practice**

    ---

    Radios have a few hundred KB of Lua heap and a fixed instruction budget per cycle. These patterns come from measurements on real radios.

    [:octicons-arrow-right-24: Saving RAM](best-practice/memory.md)

-   :material-chef-hat:{ .lg .middle } **Cookbook**

    ---

    Complete, commented scripts you can copy: telemetry widgets, alert tasks, system tools, Lua sources. Plus every official FrSky example.

    [:octicons-arrow-right-24: Recipes](cookbook/index.md)

-   :material-monitor-cellphone:{ .lg .middle } **Simulator & Suite**

    ---

    Test without a radio in the browser simulator or FrSky Suite, read the console, and load telemetry.

    [:octicons-arrow-right-24: Web simulator](tools/web-simulator.md)

-   :material-robot:{ .lg .middle } **AI agents**

    ---

    Let Claude Code (or another agent) boot a simulated radio, deploy your script, take screenshots and check its own work with `ethos-tools`.

    [:octicons-arrow-right-24: Agent setup](tools/ai-agents.md)

</div>

## A whole widget in 20 lines

```lua title="scripts/hello/main.lua" linenums="1"
local function create()
  return { source = system.getSource("RSSI"), last = nil }  -- (1)!
end

local function wakeup(widget)
  local v = widget.source and widget.source:value()
  if v ~= widget.last then          -- only redraw when something changed (2)
    widget.last = v
    lcd.invalidate()
  end
end

local function paint(widget)
  local w, h = lcd.getWindowSize()
  lcd.font(FONT_L)
  lcd.drawText(w / 2, h / 2 - 10, widget.last and tostring(widget.last) or "--", CENTERED)
end

local function init()
  system.registerWidget({ key = "hello", name = "Hello RSSI", create = create, wakeup = wakeup, paint = paint })
end

return { init = init }
```

1. `create()` runs once when the widget is placed on a screen. Look up sources here, never in `paint()`.
2. `wakeup()` runs many times a second; `paint()` only runs after `lcd.invalidate()`. Checking for a change before invalidating is the most important performance habit in Ethos Lua. See [Saving CPU](best-practice/cpu.md).

## Where this documentation comes from

| Part | Source | Refreshed |
| --- | --- | --- |
| [API reference](api/index.md) | FrSky's `lua-doc.zip` (Doxygen output from the Ethos firmware), parsed into one page per function | By the scheduled update workflow, see [Updating](contributing/updating.md) |
| [Official examples](examples/official/index.md) | [ETHOS-Feedback-Community/lua/examples](https://github.com/FrSkyRC/ETHOS-Feedback-Community/tree/HEAD/lua/examples) | Same workflow |
| Real-world usage on API pages | Public open-source Ethos Lua projects, see [Real-world usage](contributing/real-world-usage.md) | Same workflow |
| Guides, best practice, cookbook | Written for this site, with RAM figures taken from on-radio measurements | By hand |

!!! tip "Check the version"
    Every API page shows the Ethos version that introduced the call (for example **since 1.5.0**). Calls added in the newest release are highlighted. To support older radios, check before calling: `if lcd.setWindowTitle then ... end`.
