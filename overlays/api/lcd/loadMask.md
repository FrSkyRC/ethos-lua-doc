```lua
-- load once, at file level (relative paths only resolve while main.lua loads)
local ICON = lcd.loadMask("gfx/warning.png")

local function paint(widget)
  if ICON then
    lcd.color(widget.alarm and lcd.RGB(230, 50, 50) or lcd.themeColor(THEME_DEFAULT_COLOR))
    lcd.drawMask(4, 4, ICON)
  end
end
```

!!! warning "Mask images: black on white"
    In a mask, **dark pixels are drawn** (in the current color) and **white is transparent**. Verified in the Ethos 26.1 simulator. Draw icons as black shapes on a white background.

Loading is lazy by default (`lazy = true`): the image is decoded on first draw. The simulator console then logs `Bitmap ... loaded, RAM used: N bytes`.
