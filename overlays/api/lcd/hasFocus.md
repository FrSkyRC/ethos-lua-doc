```lua
local function paint(widget)
  local w, h = lcd.getWindowSize()
  if lcd.hasFocus() then
    lcd.color(lcd.themeColor(THEME_FOCUS_COLOR))
    lcd.drawRectangle(0, 0, w, h, 2)          -- show the pilot this widget takes input
  end
end
```

On the home screen a widget only receives key events while it has focus. See [Events](../../guides/events.md).
