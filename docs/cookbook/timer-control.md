# Timer control

A widget that displays one of the model's timers, turns green while it runs, resets on tap when stopped, and has a **Reset timer** menu entry.

## What it demonstrates

- **`model.getTimer(index)`** and the [`Timer`](../api/objects/Timer/index.md) object: `value()`, `stringValue()`, `running()`, `reset()`, `name()`.
- **Re-attaching** when the configured timer changes or doesn't exist yet.
- **Touch events.** A tap (`TOUCH_END`) is consumed by returning `true`.
- **Redrawing once a second**, because the timer value only changes per second.

## The script

```lua title="scripts/timerwgt/main.lua" linenums="1"
--8<-- "examples/cookbook/timerwgt/main.lua"
```

## API used

[`model.getTimer`](../api/model/getTimer.md) · [`Timer:value`](../api/objects/Timer/value.md) · [`Timer:stringValue`](../api/objects/Timer/stringValue.md) · [`Timer:running`](../api/objects/Timer/running.md) · [`Timer:reset`](../api/objects/Timer/reset.md) · [Events](../guides/events.md)
