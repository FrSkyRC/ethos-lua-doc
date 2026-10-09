```lua
-- a horizontal bar: track + fill
local TRACK, FILL = lcd.GREY(60), lcd.RGB(40, 190, 80)

local function drawBar(x, y, w, h, percent)
  lcd.color(TRACK)
  lcd.drawFilledRectangle(x, y, w, h)
  lcd.color(FILL)
  lcd.drawFilledRectangle(x, y, math.floor(w * percent / 100), h)
end
```

See the [battery gauge recipe](../../cookbook/battery-gauge.md) for a complete widget.
