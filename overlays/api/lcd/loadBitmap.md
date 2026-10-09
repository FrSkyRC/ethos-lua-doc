```lua
local BG = lcd.loadBitmap("gfx/panel.png")   -- file level: loaded once

local function paint(widget)
  if BG then lcd.drawBitmap(0, 0, BG) end
end
```

- Returns `nil` if the file is missing or can't be decoded. Check before drawing.
- Decoded images use the Lua bitmap memory, which shares a region with the Lua heap. Size images to how they are displayed and release handles (`= nil`) when a tool closes. See [Saving RAM](../../best-practice/memory.md#bitmaps).
- Transparency (PNG alpha) is supported but costs more.
