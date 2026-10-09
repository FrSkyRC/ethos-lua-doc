```lua
local mem = system.getMemoryUsage and system.getMemoryUsage() or {}
print(string.format("lua free %.1fkB, bitmaps free %.1fkB, stack free %.1fkB",
  (mem.luaRamAvailable or 0) / 1024,
  (mem.luaBitmapsRamAvailable or 0) / 1024,
  (mem.mainStackAvailable or 0) / 1024))
```

On current radios the Lua heap and bitmap memory come from one shared region, so treat the two numbers as one budget. Track the **minimum** stack seen, not single readings. See the [memory monitor recipe](../../cookbook/memory-monitor.md) and [Saving RAM](../../best-practice/memory.md).
