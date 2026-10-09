# Debugging

## Where output goes

| Environment | `print()` output and Lua errors |
| --- | --- |
| Web simulator | **Console** panel |
| Ethos Suite simulator | **Console** panel |
| `ethos-tools` (`run_wasm.js`) | `node run_wasm.js log [n]` |
| Real radio | Serial debug over USB (see [below](#on-a-radio)) |

When a widget is blank or a tool doesn't open, **check the console first**. On screen a broken script usually just looks empty.

## Reading the boot log

Each script logs two lines when it loads:

```text
Lua::load('SCRIPTS:/mywidget/main.lua')
Lua::compile('main.luac', strip=0)
```

Errors in your file's top-level code or `init()` appear right after these. Other messages worth knowing:

| Message | Meaning |
| --- | --- |
| `Lua::registerSystemTool(): missing icon` | `registerSystemTool` was called without `icon` |
| `Lua::path is not set!` | A relative path was used from a callback; use `SCRIPTS:/<folder>/...` ([details](../getting-started/lua-environment.md#relative-paths-only-work-while-your-script-loads)) |
| `Bitmap SCRIPTS:/x/icon.png loaded, RAM used: 4096 bytes` | An image was decoded (on first draw). A free per-asset memory report |
| `Lua has used too much RAM, it has been Killed` | Heap limit hit. See [Saving RAM](../best-practice/memory.md) |

## Print well

```lua
local DEBUG = true
local function log(fmt, ...)
  if DEBUG then print(string.format("[mywidget] " .. fmt, ...)) end
end

log("source=%s value=%s", widget.source and widget.source:name() or "nil", tostring(v))
```

- Prefix lines with your script name. The console is shared by every script.
- **Never print every tick in `wakeup`.** It floods the console and costs CPU. Print on change, or throttle with `os.clock()`.
- Turn debug output off for releases (`DEBUG = false`), or strip it.

## Catching errors in callbacks

An error inside a callback stops that call, and Ethos may stop calling your script. While developing, wrap risky work with `pcall` and log the message:

```lua
local function wakeup(widget)
  local ok, err = pcall(update, widget)
  if not ok then print("[mywidget] wakeup error: " .. tostring(err)) end
end
```

Remove blanket `pcall`s from hot paths in release builds, or keep them narrow. They hide bugs and cost a little time on every call.

## On a radio

To see `print` output from scripts running on a real radio, put it in serial debug mode and read the USB serial port:

- **Ethos Suite:** `--serial start` (and `--serial stop`). See [Ethos Suite](ethos-suite.md#command-line).
- Then open the radio's USB serial port in any terminal (115200 baud is what open-source deploy tools use).

## Memory and performance problems

- Run the [memory monitor](../cookbook/memory-monitor.md) task next to your script.
- Check `system.getInstructionsUsage()` inside long loops ([Saving CPU](../best-practice/cpu.md#3-spread-long-jobs-across-cycles)).
- Read [Measuring](../best-practice/measuring.md) before trusting a single number.
