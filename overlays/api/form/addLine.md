```lua
local line = form.addLine("Max RPM")                      -- labelled line
form.addNumberField(line, nil, 0, 20000, getMax, setMax)

local panel = form.addExpansionPanel("Advanced")
local l2 = form.addLine("Smoothing", panel)               -- inside a panel
form.addNumberField(l2, nil, 0, 10, getS, setS)

form.addLine("Notes", nil, false)                         -- no separator after the line
```

Always keep `line` **local**. A global `line` (as in some older examples) is shared by every script on the radio.
