```lua
local function write(widget)
  storage.write("v", 2)                     -- settings version, for future migrations
  storage.write("source", widget.source)
  storage.write("threshold", widget.threshold)
end
```

Keep the keys and order in step with your `read` callback.
