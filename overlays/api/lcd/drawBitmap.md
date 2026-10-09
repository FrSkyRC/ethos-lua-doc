```lua
local LOGO = lcd.loadBitmap("gfx/logo.png")

local function paint(widget)
  local w, h = lcd.getWindowSize()
  if not LOGO then return end
  lcd.drawBitmap(0, 0, LOGO)                 -- natural size
  lcd.drawBitmap(w - 64, 0, LOGO, 64, 64)    -- scaled into a 64x64 box
end
```

Scaling at draw time is convenient, but an image that is always shown small should be stored small: the decoded size is what costs RAM.
