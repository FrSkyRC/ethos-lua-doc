```lua
local function paint(widget)
  local w, h = lcd.getWindowSize()   -- size of this widget / tool page / dialog
  lcd.drawRectangle(0, 0, w, h)      -- outline the whole window
  lcd.drawText(w / 2, h / 2, "middle", CENTERED)
end
```

The same widget can be placed in slots of very different sizes (and radios range from 480×320 to 800×480). Always lay out relative to this size.
