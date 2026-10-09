```lua
-- list .wav files in our sounds folder
for _, name in ipairs(system.listFiles("SCRIPTS:/myscript/sounds") or {}) do
  if name:match("%.wav$") then print(name) end
end
```

Scanning storage is slow. Do it once (on open, or when the pilot asks) and keep the result, never from `wakeup`.
