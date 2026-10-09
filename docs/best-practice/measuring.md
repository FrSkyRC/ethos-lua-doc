# Measuring

Opinions about performance are cheap; measurements are not. This page covers how to get numbers you can trust.

## The tools

| Measure | Call |
| --- | --- |
| Free Lua heap / bitmap RAM / system RAM / main stack | [`system.getMemoryUsage()`](../api/system/getMemoryUsage.md) |
| Lua heap in use (KB, includes garbage not yet collected) | `collectgarbage("count")` |
| Instruction budget used this cycle (0–100) | [`system.getInstructionsUsage()`](../api/system/getInstructionsUsage.md) |
| Time | `os.clock()` (seconds, float) |

The [memory monitor recipe](../cookbook/memory-monitor.md) is a ready-made task that prints these every few seconds, with deltas. FrSky's [memstatus example](../examples/official/memstatus.md) is a minimal version.

## Live vs churn

`collectgarbage("count")` is **live data plus garbage that hasn't been collected yet**. Two readings tell you how much was allocated between them only if no collection ran in between. To see what's actually *retained*:

```lua
collectgarbage("collect")
collectgarbage("collect")              -- second pass catches finalizer leftovers
local live = collectgarbage("count")   -- KB really held
```

Do this only in a measurement build or on a button press, never on a hot path.

- **Live** (after a full collect): what your script holds. Growth here across repeated actions is a leak or an unbounded cache.
- **Churn** (count rising between collections): garbage your hot paths create. It drives the heap's peak.

## A/B testing on the radio

To compare two versions:

1. Same radio, same model, same screen, same telemetry state.
2. Read memory at the same point: for example after boot, before any navigation, with the tool closed.
3. Repeat each run. Compare **peaks** over a realistic session, not single samples.

!!! warning "When the numbers don't add up, add a measurement"
    One project measured a change as saving 523 KB. A third run showed the real breakdown: 463 KB came from Lua files deleted from the card between runs, 60.4 KB came from the change, and the residue was 0. If a delta looks too good, the radio state probably differed. Check `luaBitmapsRamAvailable` too: if it differs between runs, the screens differed and the comparison is void.

## Desktop measurement traps

Measuring allocation in desktop Lua is useful, but:

- **The collector can run during your measurement** and make later readings smaller. Raise the pause and keep a ballast allocation so a collection can't trigger mid-test.
- **Parsing two versions of a file in one process shares interned strings**, so the second looks cheaper than it is.
- `loadfile()` without running the chunk measures the parser's temporary allocations, not what the module keeps.

## Watch for retained-memory regressions

The strongest check is a **census**: count the tables and strings reachable from `_G` and `package.loaded` after each open/close cycle of a page or tool. If the count is flat from the second cycle on, Lua is retaining nothing. Any remaining growth is platform retention (see [forms](memory.md#forms-retain-memory)), not your code. Byte counts are noisier; the object census is exact.
