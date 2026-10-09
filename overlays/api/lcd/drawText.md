```lua
local function paint(widget)
  local w, h = lcd.getWindowSize()
  lcd.font(FONT_L)
  lcd.color(lcd.themeColor(THEME_DEFAULT_COLOR))

  lcd.drawText(4, 4, "Left")                       -- default: x is the left edge
  lcd.drawText(w / 2, 4, "Centre", CENTERED)        -- x is the centre
  lcd.drawText(w - 4, 4, "Right", RIGHT)            -- x is the right edge

  -- vertically centre a line of text
  local _, th = lcd.getTextSize("Ag")
  lcd.drawText(w / 2, (h - th) / 2, widget.text, CENTERED)
end
```

- `y` is the **top** of the text, not the baseline.
- Use `lcd.drawNumber` for values with units: it formats decimals and the unit for you.
- Only works inside `paint`.
