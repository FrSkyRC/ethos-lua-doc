```lua
system.playNumber(11.8, UNIT_VOLT, 1)       -- "eleven point eight volts"
system.playNumber(75, UNIT_PERCENT, 0)      -- "seventy five percent"

-- speak a source with its own unit and precision
local src = system.getSource({ category = CATEGORY_SYSTEM, member = MAIN_VOLTAGE })
if src then system.playNumber(src:value(), src:unit(), src:decimals()) end
```
