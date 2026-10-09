# Memory monitor

A development task that prints Lua heap, bitmap memory and the lowest main-stack headroom every five seconds, with the change since the previous line. Run it next to your own script in the simulator and watch the console while you use your script.

Each line looks like this (numbers illustrative; yours depend on radio and scripts):

```text
[mem] luaFree=812.4kB (-3.1) bmpFree=6020.0kB (+0.0) heapUsed=402.7kB (+3.0) minStack=14.2kB
```

## What it demonstrates

- **`system.getMemoryUsage()`** fields and what they mean (see [Saving RAM](../best-practice/memory.md#know-the-budget)).
- **Tracking a minimum.** Stack headroom matters at its worst moment, not its average.
- **Guarding optional APIs** (`system.getMemoryUsage and ...`).

## The script

```lua title="scripts/memmon/main.lua" linenums="1"
--8<-- "examples/cookbook/memmon/main.lua"
```

## Reading the numbers

- `heapUsed` is `collectgarbage("count")`: live data **plus** garbage not yet collected. A sawtooth here is churn; a rising floor is retention. See [Measuring](../best-practice/measuring.md#live-vs-churn).
- `luaFree` and `bmpFree` come from one shared memory region on current radios. A drop in one can cause failures in the other.
- Don't ship this task enabled. `print` every five seconds is cheap, but it's noise for users.
