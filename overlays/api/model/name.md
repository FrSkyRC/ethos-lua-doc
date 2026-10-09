```lua
local name = model.name()                         -- current model's name
local safe = name:gsub("[^%w_-]", "_")            -- safe for file names
local logFile = "LOGS:/mytool/" .. safe .. ".csv"
```
