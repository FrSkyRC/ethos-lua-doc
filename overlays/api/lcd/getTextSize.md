Returns **width and height** in pixels for the current font:

```lua
lcd.font(FONT_L)
local tw, th = lcd.getTextSize("12.6V")
lcd.drawText(w - tw - 4, h - th - 4, "12.6V")      -- bottom-right corner with 4 px margin
```

Find the biggest font that fits a box:

```lua
local FONTS = { FONT_XXL, FONT_XL, FONT_L, FONT_M, FONT_S }

local function fit(text, maxW, maxH)
  for i = 1, #FONTS do
    lcd.font(FONTS[i])
    local tw, th = lcd.getTextSize(text)
    if tw <= maxW and th <= maxH then return FONTS[i] end
  end
  return FONTS[#FONTS]
end
```

!!! tip
    Measuring is not free. If the text only changes occasionally, cache the result and re-measure when the text, font or window size changes, as in the [value widget recipe](../../cookbook/value-widget.md).
