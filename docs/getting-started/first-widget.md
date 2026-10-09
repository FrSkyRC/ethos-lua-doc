# Your first widget

We'll build a widget that shows any telemetry value the pilot chooses, in a font that scales with the widget size. Along the way it uses the four callbacks almost every widget needs: `create`, `wakeup`, `paint` and `configure`, plus `read`/`write` to remember the settings.

## 1. Create the folder

Scripts live in the `scripts` folder of the radio's storage, one folder per script:

```text
scripts/
└── bigvalue/
    └── main.lua
```

On a radio connected over USB this is the `scripts` folder on the SD card (or internal storage, depending on the radio). In the simulator it is the `scripts` folder inside the simulator's radio directory (see [Web simulator](../tools/web-simulator.md) and [FrSky Suite](../tools/frsky-suite.md)).

## 2. Write `main.lua`

```lua title="scripts/bigvalue/main.lua" linenums="1"
-- Big Value: shows one source in large text

local function create()
  -- the table returned here is the widget's state; Ethos passes it to every callback
  return { source = nil, value = nil, text = "--" }
end

local function wakeup(widget)
  if not widget.source then return end
  local v = widget.source:value()
  if v ~= widget.value then                    -- redraw only when the value changes
    widget.value = v
    widget.text = widget.source:stringValue()  -- formatted with unit, e.g. "11.8V"
    lcd.invalidate()
  end
end

local function paint(widget)
  local w, h = lcd.getWindowSize()
  -- pick the largest font that fits the widget height
  if h >= 120 then lcd.font(FONT_XXL) elseif h >= 70 then lcd.font(FONT_XL) else lcd.font(FONT_L) end
  local tw, th = lcd.getTextSize(widget.text)
  lcd.color(lcd.themeColor(THEME_DEFAULT_COLOR))
  lcd.drawText((w - tw) / 2, (h - th) / 2, widget.text)
end

local function configure(widget)
  local line = form.addLine("Source")
  form.addSourceField(line, nil,
    function() return widget.source end,
    function(value) widget.source = value; widget.value = nil end)
end

local function read(widget)
  widget.source = storage.read("source")
end

local function write(widget)
  storage.write("source", widget.source)
end

local function init()
  system.registerWidget({
    key = "bigval",          -- unique id, 7 characters max
    name = "Big Value",
    create = create, wakeup = wakeup, paint = paint,
    configure = configure, read = read, write = write,
  })
end

return { init = init }
```

## 3. Run it

1. Copy the `bigvalue` folder into `scripts/` (radio or simulator).
2. Restart the radio or simulator. Scripts are only loaded at boot.
3. Long-press a home screen widget slot (or edit a screen in **Displays**), choose **Big Value**, then open its configuration and pick a source such as **RSSI** or a telemetry sensor.

!!! failure "Nothing shows up?"
    - The folder must contain `main.lua` and that file must `return { init = init }`.
    - `key` must be 7 characters or fewer, and unique across all installed widgets.
    - Open the simulator's **Console** panel: a syntax error in `main.lua` is printed there at boot.

## 4. What just happened

| Callback | Called | What our widget does |
| --- | --- | --- |
| `create()` | Once, when the widget is placed or loaded with the model | Returns the state table |
| `read(widget)` | After create, when settings are restored | Restores the chosen source |
| `wakeup(widget)` | Repeatedly, many times a second, even when nothing changes | Polls the value; calls `lcd.invalidate()` only on change |
| `paint(widget)` | After `lcd.invalidate()`, and when Ethos needs a redraw | Draws the text |
| `configure(widget)` | When the pilot opens the widget's settings | Builds a form |
| `write(widget)` | When settings need saving (after configure) | Stores the source |

The key idea is the split between **wakeup** (cheap, frequent, decides whether anything changed) and **paint** (draws, only when asked). Getting this right keeps scripts smooth. See [Saving CPU](../best-practice/cpu.md).

## Next steps

- [Script types & lifecycle](script-types.md): every callback for every script type.
- [Drawing on screen](../guides/drawing.md): colors, fonts, bitmaps, theme colors.
- [Telemetry value widget](../cookbook/value-widget.md): this widget grown up, with min/max tracking, colors, and alarm thresholds.
