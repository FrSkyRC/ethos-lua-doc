# Saving CPU

Ethos runs every script's `wakeup` on a loop, and every visible widget's `paint` whenever it's invalidated. CPU your script wastes is taken from the UI, other scripts and battery life. Each script also has a per-cycle instruction budget: [`system.getInstructionsUsage()`](../api/system/getInstructionsUsage.md) reports how much is used (0–100), and **the script is aborted at 100**.

## 1. Redraw only on change

This one habit matters more than everything else on this page:

```lua
local function wakeup(widget)
  local v = widget.src and widget.src:value()
  if v ~= widget.last then
    widget.last = v
    lcd.invalidate()
  end
end
```

**Quantize what you compare.** If you display one decimal, compare at one decimal. Otherwise sensor noise triggers a repaint every tick for a change nobody can see:

```lua
local shown = v and math.floor(v * 10 + 0.5)    -- the value as displayed (tenths)
if shown ~= widget.shown then
  widget.shown = shown
  lcd.invalidate()
end
```

When only part of a widget changes, invalidate just that region: `lcd.invalidate(x, y, w, h)`.

**Hidden widgets don't need work.** [`lcd.isVisible()`](../api/lcd/isVisible.md) reports whether the window is on screen. Skip expensive updates for widgets on another page (but keep any logic that must run, like alarms, in a task).

## 2. Throttle slow work

Not everything needs to run every tick. Use `os.clock()` to run work at its own rate:

```lua
local nextScan = 0

local function wakeup(widget)
  local now = os.clock()
  if now >= nextScan then
    nextScan = now + 1.0      -- once per second
    rescanSensors(widget)
  end
  -- fast, cheap work here every tick
end
```

Typical rates in open-source suites:

| Work | Rate |
| --- | --- |
| Reading a value for display | Every wakeup, but redraw only on change |
| Looking up sources that were `nil` | Every 1–2 s |
| Battery or capacity voice calls | Every 10–30 s, with hysteresis |
| Writing logs to a file | Buffer, then flush every few seconds |
| Memory or debug statistics | Every 5 s |

## 3. Spread long jobs across cycles

Parsing a big file or building a large table in one go can hit the instruction limit. Do a slice per wakeup, and stop while there's budget to spare:

```lua
local job = { i = 1, lines = nil, done = false }

local function wakeup()
  if job.done then return end
  while system.getInstructionsUsage() < 70 do
    local line = job.lines[job.i]
    if not line then job.done = true; break end
    processLine(line)
    job.i = job.i + 1
  end
end
```

## 4. Make `paint` cheap

`paint` should only *draw* from state that is already computed.

| Don't do in `paint` | Do instead |
| --- | --- |
| `system.getSource(...)` | Look up in `create`/`read`, keep the object |
| `lcd.loadBitmap` / `lcd.loadMask` | Load once at file level or in `create` |
| `lcd.RGB(...)` for constant colors | Compute once into file-level locals |
| `string.format` of values that didn't change | Format in `wakeup` when the value changes; store the string |
| `lcd.getTextSize` of a fixed label | Measure once per font/size and cache |
| Building tables of positions | Compute the layout when the window size changes |

```lua
local layout = { w = 0, h = 0 }

local function computeLayout(w, h)
  layout.w, layout.h = w, h
  layout.barH = math.floor(h * 0.3)
  layout.textY = layout.barH + 4
end

local function paint(widget)
  local w, h = lcd.getWindowSize()
  if w ~= layout.w or h ~= layout.h then computeLayout(w, h) end
  -- draw using layout.*
end
```

## 5. Batch file writes

Opening, writing and closing a file every tick is slow and wears the flash. Buffer in memory and flush periodically:

```lua
local buf, n, nextFlush = {}, 0, 0

local function log(line)
  n = n + 1
  buf[n] = line
end

local function flush(now)
  if n == 0 or now < nextFlush then return end
  local f = io.open("LOGS:/mylog.csv", "a")
  if f then
    f:write(table.concat(buf, "\n", 1, n), "\n")
    f:close()
  end
  for i = 1, n do buf[i] = nil end   -- clear in place, reuse the table
  n = 0
  nextFlush = now + 5
end
```

## 6. Don't repeat UI calls

Calls like `field:enable(state)` or `field:value(x)` update native widgets and may trigger redraws. Real projects call them thousands of times, often with an unchanged value. Track the last value:

```lua
local function setEnabled(field, key, on, cache)
  if cache[key] ~= on then
    cache[key] = on
    field:enable(on)
  end
end
```

## 7. Tasks run all the time

A background task runs whenever its model is loaded, including during flight, on every screen. Give task logic its own throttle and keep the per-tick path to a handful of comparisons. If a task only needs to act a few times a second, return early on the other ticks:

```lua
local nextRun = 0
local function wakeup()
  local now = os.clock()
  if now < nextRun then return end
  nextRun = now + 0.25        -- 4 Hz is plenty for most alerts
  checkAlerts()
end
```
