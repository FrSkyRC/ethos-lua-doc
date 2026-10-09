-- Memory monitor: a background task that prints Lua heap, bitmap RAM and the
-- lowest main-stack headroom seen, every few seconds, with deltas.
-- Enable it under Model > Lua while developing; watch the simulator console.
-- https://frskyrc.github.io/ethos-lua-doc/cookbook/memory-monitor/

local INTERVAL = 5   -- seconds
local nextAt = 0
local prevLua, prevBmp, prevHeap
local minStack

local function kb(bytes) return string.format("%.1fkB", (bytes or 0) / 1024) end

local function delta(now, prev)
  if not prev or not now then return "" end
  local d = (now - prev) / 1024
  return string.format(" (%+.1f)", d)
end

local function wakeup()
  local now = os.clock()
  if now < nextAt then return end
  nextAt = now + INTERVAL

  local mem = system.getMemoryUsage and system.getMemoryUsage() or {}
  local heap = collectgarbage("count") * 1024  -- live + not-yet-collected garbage
  local stack = tonumber(mem.mainStackAvailable)
  if stack and (not minStack or stack < minStack) then minStack = stack end

  print(string.format("[mem] luaFree=%s%s bmpFree=%s%s heapUsed=%s%s minStack=%s",
    kb(mem.luaRamAvailable), delta(mem.luaRamAvailable, prevLua),
    kb(mem.luaBitmapsRamAvailable), delta(mem.luaBitmapsRamAvailable, prevBmp),
    kb(heap), delta(heap, prevHeap),
    minStack and kb(minStack) or "-"))

  prevLua, prevBmp, prevHeap = mem.luaRamAvailable, mem.luaBitmapsRamAvailable, heap
end

local function init()
  system.registerTask({ key = "memmon", name = "Memory monitor", wakeup = wakeup })
end

return { init = init }
