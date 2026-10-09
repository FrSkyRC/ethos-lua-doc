*[closure]: A function together with the outside variables it uses (its upvalues). Creating one allocates memory, and it keeps its upvalues alive. See Getting started → Lua concepts.
*[closures]: Functions together with the outside variables they use (their upvalues). Creating one allocates memory, and it keeps its upvalues alive. See Getting started → Lua concepts.
*[upvalue]: A local variable from an enclosing function that a closure captured and keeps alive.
*[upvalues]: Local variables from an enclosing function that a closure captured and keeps alive.
*[hot path]: Code that runs very often: wakeup, paint, event handlers and what they call. Small costs here add up fast.
*[hot paths]: Code that runs very often: wakeup, paint, event handlers and what they call. Small costs here add up fast.
*[churn]: The rate at which code creates short-lived garbage (tables, strings, closures). Raises peak memory use.
*[GC]: Garbage collector: frees memory that nothing refers to any more.
*[LRU]: Least recently used: a size-limited cache that evicts the entry unused for longest.
*[bytecode]: Compiled Lua (.luac) that loads without parsing the source again.
*[HID]: USB Human Interface Device: the radio's always-present USB control channel, used to switch USB modes.
*[CDC]: USB Communications Device Class: the virtual serial port the radio exposes in debug mode.
*[VID]: USB vendor ID. FrSky radios use 0483.
*[PID]: USB product ID. Ethos radios use 5750.
