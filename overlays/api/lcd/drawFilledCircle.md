```lua
-- status LED: green when telemetry is live, red otherwise
local ON, OFF = lcd.RGB(40, 200, 60), lcd.RGB(200, 40, 40)

local function drawLed(x, y, r, on)
  lcd.color(on and ON or OFF)
  lcd.drawFilledCircle(x, y, r)
end
```
