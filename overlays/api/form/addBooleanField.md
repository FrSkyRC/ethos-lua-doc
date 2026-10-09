```lua
local line = form.addLine("Voice alerts")
form.addBooleanField(line, nil,
  function() return config.voice end,
  function(v) config.voice = v end)
```
