```lua
-- a simple graph of the last N samples
local function drawGraph(samples, n, x, y, w, h, min, max)
  local step = w / (n - 1)
  local prevX, prevY
  for i = 1, n do
    local v = samples[i] or min
    local px = x + (i - 1) * step
    local py = y + h - (v - min) / (max - min) * h
    if prevX then lcd.drawLine(prevX, prevY, px, py) end
    prevX, prevY = px, py
  end
end
```

Use [`lcd.pen(PEN_DOTTED)`](pen.md) before drawing for dotted lines (grid lines, thresholds).
