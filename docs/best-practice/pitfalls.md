# Pitfalls

Bugs that cost real projects real time. Each one is cheap to avoid once you know about it.

## `collectgarbage("setpause")` without a value

```lua
collectgarbage("setpause")        -- ✗ sets the pause to 0: the GC runs continuously
collectgarbage("setpause", 120)   -- ✓ returns the PREVIOUS pause, not the new one
```

The setter returns the old value, so reading it back to "check" what you set gives the wrong number. Keep the value you passed and log that.

## Unbounded recursion

Every Lua-to-Lua call uses C stack. On a radio, running out of C stack does **not** raise a catchable Lua error: the stack pointer walks into neighbouring memory and the watchdog resets the radio into emergency mode. (Ethos then restores the model from its RAM backup.)

The usual cause is an event system where handler A publishes an event whose handler publishes back to A. Guard any re-entrant dispatch with a depth limit:

```lua
local depth, MAX_DEPTH = 0, 8

local function publish(topic, ...)
  if depth >= MAX_DEPTH then error("publish depth exceeded: " .. topic) end
  depth = depth + 1
  for _, h in ipairs(handlers[topic] or {}) do
    local ok, err = pcall(h, ...)
    if not ok then print("handler error: " .. tostring(err)) end
  end
  depth = depth - 1
end
```

`system.getMemoryUsage().mainStackAvailable` reports free main-stack bytes. Track its **minimum** over a session, not single readings: the moment that matters is the worst one.

## Relative paths in callbacks

Relative paths resolve against your script's folder only while `main.lua` loads. From a callback, `io.open("settings.lua", "w")` writes into **whichever script Ethos loaded last**, or fails with `Lua::path is not set!` in the console. This was reproduced in the simulator: a tool's `close()` saved its settings into another widget's folder. Use `SCRIPTS:/<folder>/...` for anything that runs after `init()`. Details in [The Lua environment](../getting-started/lua-environment.md#relative-paths-only-work-while-your-script-loads).

## `os.mkdir` is not recursive

`os.mkdir("LOGS:/myscript")` fails with *No such file or directory* if `LOGS:` itself doesn't exist yet, which is the case on a fresh radio or simulator. Create each level:

```lua
if not os.stat("LOGS:") then os.mkdir("LOGS:") end
if not os.stat("LOGS:/myscript") then os.mkdir("LOGS:/myscript") end
```

## Nil handles

These can all return `nil`, and calling a method on `nil` stops your script:

| Call | Returns `nil` when |
| --- | --- |
| `system.getSource(...)` | No such source yet (telemetry not discovered, renamed sensor) |
| `model.createSensor(...)` | Creation failed (retry later, throttled) |
| `lcd.loadBitmap(path)` / `lcd.loadMask(path)` | File missing or can't be decoded |
| `form.openWaitDialog(...)` | Observed during page reloads |
| `io.open(path)` | File missing or no permission |
| `model.getTimer(name)` | No such timer |

## Using drawing calls outside `paint`

`lcd.draw*` only works inside `paint`. Calling it from `wakeup` draws nothing (or errors). Compute in `wakeup`, then `lcd.invalidate()`.

## Stale module state after redeploy

Modules cached in `package.loaded` stay cached until the script restarts. In the simulator, after copying new files, **restart the simulator**, or you'll keep testing the old code.

## Saved settings from older versions

A widget saved by version 1 of your script doesn't have version 2's new settings: `storage.read("newKey")` returns `nil`. Always default (`storage.read("k") or default`). See [Saving settings](../guides/storage.md#widgets-read-and-write).

## Duplicate telemetry sensors

Creating a DIY sensor without first checking for an existing one (by `appId`) adds a duplicate every boot. Look up first, create only if missing, and keep the object.

## Widget keys over 7 characters

`registerWidget`, `registerTask` and `registerSource` keys are limited to 7 characters. Keep them short, unique, and never change them after release: saved models refer to widgets by key.

## Comparing floats for change

`if v ~= last` on a noisy float fires every tick. Compare what you display (rounded or quantized), as in [Saving CPU](cpu.md#1-redraw-only-on-change).

## Shadowed globals

Assigning without `local` creates a global shared by **every script on the radio**:

```lua
line = form.addLine("Source")   -- ✗ global `line`
local line = form.addLine("Source")   -- ✓
```

Globals are also slower to access than locals. In hot code, cache library functions in locals: `local floor = math.floor`.
