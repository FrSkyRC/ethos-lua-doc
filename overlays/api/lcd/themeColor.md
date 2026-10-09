```lua
local function paint(widget)
  local w, h = lcd.getWindowSize()
  lcd.color(lcd.themeColor(THEME_DEFAULT_BGCOLOR))
  lcd.drawFilledRectangle(0, 0, w, h)
  lcd.color(lcd.themeColor(THEME_DEFAULT_COLOR))
  lcd.drawText(4, 4, widget.label)
  lcd.color(lcd.themeColor(THEME_WARNING_COLOR))
  lcd.drawText(4, 30, "Low battery")
end
```

Using theme colors keeps a script readable on light and dark themes. All indexes are listed under [Theme colors](../constants.md#theme-colors).
