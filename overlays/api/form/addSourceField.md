```lua
local function configure(widget)
  local line = form.addLine("Source")
  form.addSourceField(line, nil,
    function() return widget.source end,
    function(value) widget.source = value end)
end

local function write(widget) storage.write("source", widget.source) end
local function read(widget) widget.source = storage.read("source") end
```
