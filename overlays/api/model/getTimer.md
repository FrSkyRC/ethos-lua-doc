```lua
local t = model.getTimer(0)                        -- first timer (or by name: model.getTimer("Flight"))
if t then
  print(t:name(), t:stringValue(), t:running())
  if not t:running() then t:reset() end
end
```

Returns `nil` when the timer doesn't exist. See the [timer recipe](../../cookbook/timer-control.md).
