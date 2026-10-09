```lua
local v = system.getVersion()
print(v.board, v.version, v.major, v.minor, v.revision, v.lcdWidth, v.lcdHeight, v.simulation)

-- feature gate: 1.6 or newer (26.x counts as newer)
local function atLeast(major, minor)
  return v.major > major or (v.major == major and v.minor >= minor)
end

-- behave differently in the simulator (e.g. fake telemetry)
if v.simulation then
  -- ...
end
```

Prefer feature checks (`if system.getSources then`) over version checks where possible: they also work on builds you didn't anticipate.
