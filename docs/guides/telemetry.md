# Sources & telemetry

In Ethos, almost everything with a value is a **source**: sticks, switches, channels, timers, telemetry sensors, system values like the radio battery. Lua accesses them all the same way, through [`Source`](../api/objects/Source/index.md) objects.

## Getting a source

[`system.getSource()`](../api/system/getSource.md) takes either a name or a table describing what you want:

```lua
local rssi   = system.getSource("RSSI")                           -- by display name
local radio  = system.getSource({ category = CATEGORY_SYSTEM, member = MAIN_VOLTAGE })
local ch1    = system.getSource({ category = CATEGORY_CHANNEL, member = 0 })       -- channel 1
local timer1 = system.getSource({ category = CATEGORY_TIMER, member = 0 })
local vfas   = system.getSource({ category = CATEGORY_TELEMETRY_SENSOR, appId = 0x0210 })  -- S.Port VFAS
local rxBatt = system.getSource({ crsfId = 0x08, subIdStart = 0, subIdEnd = 1 })           -- CRSF battery
local gpsLat = system.getSource({ name = "GPS", options = OPTION_LATITUDE })
```

| Look up by | When to use |
| --- | --- |
| Name (`"RSSI"`) | Quick scripts. Fragile: the pilot can rename sensors, and names are translated |
| `category` + `member` | Sticks, channels, timers, system values. Stable |
| `appId` (S.Port) / `crsfId` (CRSF) | Telemetry sensors. Stable across renames and languages |
| A source field in a form | Anything the pilot should choose. The best option for widgets |

`getSource` returns `nil` when nothing matches, for example before telemetry has been discovered. Always check.

!!! tip "Look up once, not every wakeup"
    `getSource` searches the model's sources. Do it in `create`/`read`, or after a configuration change, and keep the object. If the result was `nil`, retry occasionally (every second or two), not every tick:

    ```lua
    local function wakeup(widget)
      if not widget.src then
        local now = os.clock()
        if now >= (widget.retryAt or 0) then
          widget.src = system.getSource({ category = CATEGORY_TELEMETRY_SENSOR, appId = 0x0210 })
          widget.retryAt = now + 2
        end
        return
      end
      -- use widget.src
    end
    ```

## Reading values

```lua
local v    = src:value()        -- number (already scaled: 11.8 for 11.8 V), nil if no data
local txt  = src:stringValue()  -- formatted with unit: "11.8V"
local unit = src:unit()         -- UNIT_VOLT, ...
local dec  = src:decimals()     -- display decimals
local ok   = src:state()        -- boolean state; for switches, whether active
local age  = src:age()          -- ms since the last telemetry update (telemetry only, 1.6.2+)
local name = src:name()
```

Use `value()` for maths and comparisons and `stringValue()` for display. To show a value with the source's own unit and precision in a widget:

```lua
lcd.drawNumber(x, y, src:value(), src:unit(), src:decimals())
```

### Telemetry freshness

A sensor keeps its last value when telemetry is lost. To grey out stale data, check its age, or the telemetry-active system event:

```lua
local telemetryActive = system.getSource({ category = CATEGORY_SYSTEM_EVENT, member = TELEMETRY_ACTIVE })

local function isFresh(src)
  if telemetryActive and not telemetryActive:state() then return false end
  local age = src.age and src:age()
  return age == nil or age < 3000      -- older than 3 s counts as stale
end
```

### Options: one source, several readings

Some sources hold more than one number. Ask for the one you want with `options`:

```lua
local lipo = system.getSource("LiPo")
local cells   = lipo:value({ options = OPTION_CELLS_COUNT })
local lowest  = lipo:value({ options = OPTION_CELL_LOWEST })
local cell3   = lipo:value({ options = OPTION_CELL_INDEX(3) })

local gps = system.getSource("GPS")
local lat = gps:value({ options = OPTION_LATITUDE })
local lon = gps:value({ options = OPTION_LONGITUDE })

local minAlt = system.getSource({ name = "Altitude", options = OPTION_SENSOR_MIN })
```

See [Source options](../api/constants.md#source-options) for the full list.

## Listing sources

From Ethos 26.1, [`system.getSources(category)`](../api/system/getSources.md) returns every source in a category:

```lua
if system.getSources then
  for _, s in ipairs(system.getSources(CATEGORY_TELEMETRY_SENSOR)) do
    print(s:name(), s:stringValue())
  end
end
```

## Writing values: Lua-created sensors

Scripts can create telemetry sensors and push values into them. Other widgets, logic switches, logs and alarms then treat the value like real telemetry.

```lua
local sensor

local function ensureSensor()
  if sensor then return sensor end
  sensor = system.getSource({ category = CATEGORY_TELEMETRY_SENSOR, appId = 0x5100 })
  if not sensor then
    sensor = model.createSensor({ type = SENSOR_TYPE_DIY })
    if not sensor then return nil end       -- creation can fail; try again later
    sensor:name("Efficiency")
    sensor:appId(0x5100)
    sensor:unit(UNIT_MILLIAMPERE_HOUR)
    sensor:decimals(0)
  end
  return sensor
end

local function wakeup()
  local s = ensureSensor()
  if s then s:value(computeEfficiency()) end
end
```

!!! warning "Don't create a sensor twice"
    Look up by `appId` before creating, and keep the object. Creating a sensor on every boot (or every wakeup) fills the model's sensor list with duplicates. Real-world suites also throttle retries after a failed `createSensor`.

For a value that should appear as a *source* rather than a telemetry sensor, register a Lua source instead. See the [Lua source recipe](../cookbook/lua-source.md).

## Source categories

| Category | Members are |
| --- | --- |
| `CATEGORY_ANALOG` | Sticks, pots, sliders |
| `CATEGORY_SWITCH`, `CATEGORY_SWITCH_POSITION` | Physical switches and their positions |
| `CATEGORY_FUNCTION_SWITCH` | Function switches |
| `CATEGORY_LOGIC_SWITCH` | Logic switches |
| `CATEGORY_TRIM` | Trims |
| `CATEGORY_CHANNEL` | Output channels (member 0 = CH1) |
| `CATEGORY_TIMER` | Timers |
| `CATEGORY_TELEMETRY_SENSOR` | Telemetry sensors |
| `CATEGORY_SYSTEM` | Radio values: `MAIN_VOLTAGE`, `RTC_VOLTAGE`, ... |
| `CATEGORY_SYSTEM_EVENT` | Events/states: `TELEMETRY_ACTIVE`, `RSSI_LOW`, `THROTTLE_CUT`, ... |
| `CATEGORY_FLIGHT`, `CATEGORY_GYRO`, `CATEGORY_TRAINER`, `CATEGORY_SPECIAL`, `CATEGORY_ALWAYS_ON` | As named |

All values are on the [Constants](../api/constants.md#source-categories) page.
