# Lua source

A source that computes electrical power (W) from a voltage and a current source. Once registered, it appears in **every** source picker: mixes, logic switches, special functions, other widgets, telemetry screens.

## What it demonstrates

- **`registerSource` callbacks.** `init` sets the unit and decimals; `wakeup` computes and stores the value with `source:value(v)`.
- **Write only on change.** The value is set only when the rounded result differs.
- **Settings per model** with `configure`/`read`/`write`.

## The script

```lua title="scripts/powersrc/main.lua" linenums="1"
--8<-- "examples/cookbook/powersrc/main.lua"
```

## Use it

Enable it under **Model → Lua**, pick the voltage and current sources in its settings, then choose **Power (W)** anywhere a source is offered. For example, a logic switch that turns on above 1500 W, or the built-in Value widget.

## Source vs sensor

| | Lua source (`registerSource`) | Lua-created sensor (`model.createSensor`) |
| --- | --- | --- |
| Appears as | A source in pickers | A telemetry sensor |
| Logged, alarms, min/max | Like other sources | Like real telemetry (sensor page, logging) |
| Lifetime | While the script runs | Saved in the model |
| Best for | Derived values for mixes and switches | Feeding values into the telemetry system |

See [Sources & telemetry](../guides/telemetry.md#writing-values-lua-created-sensors) for sensors.

## API used

[`system.registerSource`](../api/system/registerSource.md) · [`Source:value`](../api/objects/Source/value.md) · [`Source:unit`](../api/objects/Source/unit.md) · [`Source:decimals`](../api/objects/Source/decimals.md)
