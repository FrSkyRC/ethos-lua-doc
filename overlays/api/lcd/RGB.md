```lua
-- build colors once, at file level, and reuse them in paint()
local ORANGE  = lcd.RGB(255, 128, 0)
local SHADOW  = lcd.RGB(0, 0, 0, 0.4)      -- 40 % opaque black
local WARNING = lcd.RGB(0xE6, 0x32, 0x32)  -- hex components work too

local function paint(widget)
  lcd.color(widget.alarm and WARNING or ORANGE)
  lcd.drawFilledRectangle(0, 0, 20, 20)
end
```

!!! tip
    `lcd.RGB` is one of the most-called functions in real scripts. Calling it with constant arguments inside `paint` repeats work every frame; compute constant colors once.
