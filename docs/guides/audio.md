# Audio & haptics

| Call | Plays |
| --- | --- |
| [`system.playFile(path)`](../api/system/playFile.md) | A `.wav` file |
| [`system.playNumber(value [, unit, decimals, voice, priority])`](../api/system/playNumber.md) | A number spoken in the current language, with unit: *"eleven point eight volts"* |
| [`system.playTone(freq, duration [, pause])`](../api/system/playTone.md) | A beep (Hz, ms) |
| [`system.playHaptic(duration or pattern [, strength])`](../api/system/playHaptic.md) | Vibration, e.g. `200` ms or the pattern `"- . -"` |

```lua
system.playFile("AUDIO:/en/default/lowbat.wav")   -- full path with prefix
system.playFile("SCRIPTS:/myscript/sounds/armed.wav")  -- your own sounds: absolute path
system.playNumber(11.8, UNIT_VOLT, 1)
system.playTone(1200, 150, 50)
system.playHaptic("- . -")
```

## Use the pilot's language

Voice packs live under `AUDIO:/<language>/<voice>/`. [`system.getLocale()`](../api/system/getLocale.md) gives the UI language and [`system.getAudioVoice()`](../api/system/getAudioVoice.md) the configured voice (e.g. `"en/default"`). Ship your own sounds per language and fall back to English:

```lua
local function soundPath(name)
  local voice = system.getAudioVoice and system.getAudioVoice() or "en/default"
  local lang = voice:match("^(%a+)") or "en"
  local path = "SCRIPTS:/myscript/sounds/" .. lang .. "/" .. name .. ".wav"
  if os.stat(path) then return path end
  return "SCRIPTS:/myscript/sounds/en/" .. name .. ".wav"
end
```

Look paths up once and cache them, since `os.stat` touches storage. Use absolute paths: this runs from callbacks, where relative paths don't resolve to your folder (see [The Lua environment](../getting-started/lua-environment.md#relative-paths-only-work-while-your-script-loads)).

## Don't nag the pilot

Audio from a script that runs every tick needs rate limits and hysteresis, or it repeats the same call continuously.

```lua
local INTERVAL = 10          -- seconds between repeats
local HYST = 0.1             -- volts above threshold to re-arm

local alerted, nextAt = false, 0

local function check(volts, threshold)
  local now = os.clock()
  if volts < threshold then
    if not alerted or now >= nextAt then
      system.playNumber(volts, UNIT_VOLT, 1)
      system.playHaptic(300)
      alerted, nextAt = true, now + INTERVAL
    end
  elseif volts > threshold + HYST then
    alerted = false          -- re-arm only once clearly above the threshold
  end
end
```

The complete version, as a background task with a configurable source and threshold, is the [Background alert task](../cookbook/alert-task.md) recipe.
