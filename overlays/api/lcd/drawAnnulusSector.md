Angles are degrees, 0–360, with **0 at the top, increasing clockwise**. Open-source dashboards split arcs wider than 180° into two calls:

```lua
local function drawArc(cx, cy, inner, outer, a1, a2)
  local sweep = (a2 - a1) % 360
  if sweep <= 180 then
    lcd.drawAnnulusSector(cx, cy, inner, outer, a1, a2)
  else
    local mid = (a1 + sweep / 2) % 360
    lcd.drawAnnulusSector(cx, cy, inner, outer, a1, mid)
    lcd.drawAnnulusSector(cx, cy, inner, outer, mid, a2)
  end
end

-- a 270° gauge from bottom-left (225) to bottom-right (135)
drawArc(cx, cy, r * 0.75, r, 225, (225 + 270 * percent / 100) % 360)
```

Full example in [Drawing on screen](../../guides/drawing.md#shapes).
