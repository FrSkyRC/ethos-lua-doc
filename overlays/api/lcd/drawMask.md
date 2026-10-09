```lua
local ARROW = lcd.loadMask("gfx/arrow.png")   -- file level

local function paint(widget)
  lcd.color(lcd.RGB(255, 200, 0))   -- the mask is painted in the current color
  lcd.drawMask(10, 10, ARROW)
end
```

Masks are single-channel images, cheaper than full-color bitmaps and recolorable, so they suit icons that should follow the theme or signal state with color.
