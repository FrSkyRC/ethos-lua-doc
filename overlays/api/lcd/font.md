```lua
lcd.font(FONT_XL)
lcd.drawText(0, 0, "Big")
lcd.font(FONT_S)
lcd.drawText(0, 40, "small print")
```

Pick a font from the widget's height so it scales across screen layouts:

```lua
local function fontFor(h)
  if h >= 120 then return FONT_XXL elseif h >= 70 then return FONT_XL
  elseif h >= 40 then return FONT_L else return FONT_S end
end

local function paint(widget)
  local w, h = lcd.getWindowSize()
  lcd.font(fontFor(h))
  -- ...
end
```

All font constants are under [Fonts](../constants.md#fonts).
