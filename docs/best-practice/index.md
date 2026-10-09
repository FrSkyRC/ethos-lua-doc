# Best practice

An Ethos radio is an embedded device. Lua memory is a few hundred KB to a few MB, shared between the Lua heap and decoded bitmaps. Each script also gets a fixed instruction budget per cycle. Scripts that ignore this get killed (*"Lua has used too much RAM"*), make the UI stutter, or drain the battery.

Most of this section comes from measurements on real radios, made by large open-source Ethos Lua projects that hit these limits first.

- **[Saving RAM](memory.md)**: what uses memory, what doesn't come back, and the habits that keep a script small.
- **[Saving CPU](cpu.md)**: hot paths, redraw discipline, throttling, and spreading work across cycles.
- **[Code patterns](patterns.md)**: module loading and caching, in-place table reuse, change detection, cleanup.
- **[Measuring](measuring.md)**: how to get honest RAM and CPU numbers, and the measurement traps that fool people.
- **[Pitfalls](pitfalls.md)**: bugs that cost real projects days.

## The checklist

Print this and tick it off before every release.

### Hot paths (`wakeup`, `paint`, event handlers)

- [ ] No table, closure or string is created per call unless its content changed
- [ ] `lcd.invalidate()` is called only when something visible changed
- [ ] Sources, bitmaps, masks, fonts and colors are looked up/loaded once and cached
- [ ] Text that rarely changes is formatted (and measured) once, not every paint
- [ ] Field `:enable()` / `:value()` calls are made only when the state changes
- [ ] Slow work (file I/O, scans, discovery) is throttled with `os.clock()`
- [ ] Long jobs are split across wakeups and check `system.getInstructionsUsage()`

### Memory

- [ ] Images are sized to how they're shown; icons are masks, not full-color bitmaps
- [ ] Rarely-used UI is loaded when opened, not at boot
- [ ] Modules loaded repeatedly are cached (`package.loaded`), and that cache is released on close
- [ ] Caches with open-ended keys are bounded (LRU) or cleared on lifecycle events
- [ ] Reusable tables are cleared in place, not replaced
- [ ] Forms are rebuilt only when their structure changes

### Lifecycle

- [ ] Tool `close()` releases bitmaps, caches, file handles, dialogs and subscriptions
- [ ] Anything subscribed or registered in `create()` is undone in `close()`/`destroy()`
- [ ] Each widget instance keeps its state in its own table, not in file-level locals

### Robustness

- [ ] Every `getSource`, `createSensor`, `loadBitmap` and dialog handle is nil-checked
- [ ] New API calls are guarded (`if lcd.setWindowTitle then ... end`) for older firmware
- [ ] No unbounded recursion (the C stack overflows silently)
- [ ] `collectgarbage("setpause")` is never called without a value
