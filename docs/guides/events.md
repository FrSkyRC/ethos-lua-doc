# Events, keys & touch

Widgets, system tools and tasks can receive input through an `event` callback:

```lua
local function event(widget, category, value, x, y)
  -- category: EVT_KEY, EVT_TOUCH, ...
  -- value:    which key / which touch phase
  -- x, y:     touch coordinates (window-relative), for touch events
  return false   -- return true to consume the event
end
```

**Return `true` to consume** an event: Ethos then won't pass it to the parent window. Return `false` (or nothing) to let Ethos handle it as usual. Returning `true` for every key traps the pilot in your script, so only consume what you actually use.

## Categories

| Category | Meaning |
| --- | --- |
| `EVT_KEY` | Hardware key or rotary encoder |
| `EVT_TOUCH` | Touch screen |
| `EVT_OPEN` / `EVT_CLOSE` | Expansion panel opened / closed |
| `EVT_SHUTDOWN` | Radio is shutting down |
| `EVT_SENSOR_DISCOVER` | Telemetry sensor discovery |

## Key codes

FrSky's lua-doc doesn't list the key constants, but they are global in every script and used widely. Each key has a **phase** suffix:

| Suffix | Fires |
| --- | --- |
| `_FIRST` | When the key goes down |
| `_BREAK` | When the key is released after a short press |
| `_LONG` | Once, when held for a long press |

| Key | Constants seen in real scripts |
| --- | --- |
| Enter / encoder press | `KEY_ENTER_FIRST`, `KEY_ENTER_BREAK`, `KEY_ENTER_LONG` |
| Return / exit | `KEY_RTN_FIRST`, `KEY_RTN_BREAK`, `KEY_RTN_LONG`, `KEY_EXIT_FIRST`, `KEY_EXIT_BREAK` |
| Page | `KEY_PAGE_FIRST`, `KEY_PAGE_BREAK`, `KEY_PAGE_LONG`, `KEY_PAGE_UP`, `KEY_PAGE_DOWN` |
| System | `KEY_SYS_BREAK`, `KEY_SYS_LONG` |
| Rotary encoder | `KEY_ROTARY_LEFT`, `KEY_ROTARY_RIGHT` |
| Directional (games, custom UIs) | `KEY_UP_FIRST`, `KEY_UP_BREAK`, `KEY_DOWN_FIRST`, `KEY_DOWN_BREAK`, `KEY_LEFT_FIRST`, `KEY_LEFT_BREAK`, `KEY_RIGHT_FIRST`, `KEY_RIGHT_BREAK` |

Not every radio has every key. To find out what a key sends, print it:

```lua
local function event(widget, category, value, x, y)
  print("event", category, value, x, y)
  return false
end
```

Then press keys in the simulator and watch the console.

## Long presses: kill the release

A long press is followed by a release event. If you act on `KEY_ENTER_LONG`, the trailing `KEY_ENTER_BREAK` will *also* arrive and may trigger your short-press action. [`system.killEvents()`](../api/system/killEvents.md) suppresses it:

```lua
if category == EVT_KEY then
  if value == KEY_ENTER_LONG then
    openMenu()
    system.killEvents(KEY_ENTER_BREAK)   -- don't also treat it as a short press
    return true
  elseif value == KEY_ENTER_BREAK then
    toggle()
    return true
  end
end
```

## Touch

Touch events carry a phase in `value` and coordinates in `x, y`:

| `value` | Meaning |
| --- | --- |
| `TOUCH_START` | Finger down |
| `TOUCH_MOVE` | Finger moved |
| `TOUCH_END` | Finger up (a tap ends here) |

Hit-testing a button you drew yourself:

```lua
local BTN = { x = 10, y = 40, w = 120, h = 50 }

local function event(widget, category, value, x, y)
  if category == EVT_TOUCH and value == TOUCH_END and x and y then
    if x >= BTN.x and x < BTN.x + BTN.w and y >= BTN.y and y < BTN.y + BTN.h then
      widget.pressed = not widget.pressed
      lcd.invalidate()
      return true
    end
  end
  return false
end
```

A swipe gesture, measured from start to end:

```lua
local startX

local function event(widget, category, value, x, y)
  if category ~= EVT_TOUCH or not x then return false end
  if value == TOUCH_START then
    startX = x
  elseif value == TOUCH_END and startX then
    local dx = x - startX
    startX = nil
    if dx > 60 then nextPage(widget); return true end
    if dx < -60 then prevPage(widget); return true end
  end
  return false
end
```

!!! note "Home screen widgets and focus"
    On the home screen, a widget only gets keys while it has focus. [`lcd.hasFocus()`](../api/lcd/hasFocus.md) tells you whether it does, and [`lcd.resetFocusTimeout()`](../api/lcd/resetFocusTimeout.md) stops focus from timing out after 10 s while the pilot is interacting. Swiping between home screens also produces touch events: check [`lcd.isSwiping()`](../api/lcd/isSwiping.md) before treating a move as yours.

## Widget context menu

Widgets can add entries to their long-press menu with a `menu` callback:

```lua
local function menu(widget)
  return {
    { "Reset min/max", function() widget.min, widget.max = nil, nil; lcd.invalidate() end },
  }
end

system.registerWidget({ key = "mywdgt", name = "My widget", create = create, paint = paint, menu = menu })
```
