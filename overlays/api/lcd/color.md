```lua
lcd.color(lcd.RGB(0, 200, 0))                      -- set: subsequent drawing is green
lcd.drawFilledRectangle(0, 0, 50, 10)

lcd.color(lcd.themeColor(THEME_DEFAULT_COLOR))     -- follow the user's theme for text
lcd.drawText(0, 12, "OK")

local current = lcd.color()                        -- get the current color
```

The current color applies to every following `lcd.draw*` call **and** to masks drawn with `lcd.drawMask`, which take their color from it.
