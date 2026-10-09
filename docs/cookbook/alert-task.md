# Background alert task

A task that speaks a source's value when it drops below a threshold. It repeats at a set interval while the value stays low, and re-arms only once the value has clearly recovered.

## What it demonstrates

- **A throttled task.** `wakeup` returns immediately on most ticks and checks four times a second.
- **Hysteresis.** Small oscillations around the threshold don't re-trigger the alert.
- **Rate-limited audio** with `system.playNumber` plus a haptic pulse.
- **Task settings** through `configure`/`read`/`write`. Tasks have one instance per model, so state lives at file level.

## The script

```lua title="scripts/lowalert/main.lua" linenums="1"
--8<-- "examples/cookbook/lowalert/main.lua"
```

## Enable it

Tasks are enabled per model: **Model → Lua**, turn the task on, then open its settings to choose the source and threshold.

## Variations

- **Several thresholds**: keep a small array of `{ threshold, file }` and play a different `.wav` per level.
- **Only when flying**: also read a switch source and skip alerts while disarmed.
- **Capacity alerts**: point it at a mAh-consumed sensor and alert *above* a threshold. Flip the comparison and the hysteresis.

## API used

[`system.registerTask`](../api/system/registerTask.md) · [`system.playNumber`](../api/system/playNumber.md) · [`system.playHaptic`](../api/system/playHaptic.md) · [`Source:unit`](../api/objects/Source/unit.md) · [`Source:decimals`](../api/objects/Source/decimals.md)
