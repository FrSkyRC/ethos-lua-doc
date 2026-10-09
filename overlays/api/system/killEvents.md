```lua
local function event(widget, category, value, x, y)
  if category == EVT_KEY and value == KEY_ENTER_LONG then
    openMenu(widget)
    system.killEvents(KEY_ENTER_BREAK)   -- the release would otherwise also count as a short press
    return true
  end
  return false
end
```

Real projects also kill touch sequences after acting on a touch (`system.killEvents(TOUCH_START)`) so the rest of the gesture doesn't reach other UI.
