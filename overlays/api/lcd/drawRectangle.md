```lua
lcd.drawRectangle(10, 10, 100, 40)        -- 1 px outline
lcd.drawRectangle(10, 60, 100, 40, 3)     -- 3 px thick outline

-- highlight the focused element
if lcd.hasFocus() then
  lcd.color(lcd.themeColor(THEME_FOCUS_COLOR))
  lcd.drawRectangle(0, 0, w, h, 2)
end
```
