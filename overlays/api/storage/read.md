```lua
local function read(widget)
  widget.source = storage.read("source")            -- a saved Source comes back as a Source
  widget.threshold = storage.read("threshold") or 33 -- default for widgets saved by an older version
end
```

Use it inside `read` callbacks of widgets, tasks and sources. Values live in the model file. See [Saving settings](../../guides/storage.md).
