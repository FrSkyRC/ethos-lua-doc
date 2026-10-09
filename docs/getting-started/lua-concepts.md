# Lua concepts

The [best practice](../best-practice/index.md) pages use terms like *closure*, *upvalue*, *allocation* and *hot path*. You don't need a computer-science background to write good Ethos scripts, but these ideas explain **why** the rules exist. Each section covers what the term means, why it matters on a radio, and where to read more.

!!! info "Where to learn Lua properly"
    - **[Programming in Lua](https://www.lua.org/pil/contents.html)** (*PiL*) by Lua's creator. The first edition is free online. It targets an older Lua, but every concept on this page is unchanged.
    - **[Lua 5.4 Reference Manual](https://www.lua.org/manual/5.4/)**: the exact rules for the Lua that Ethos runs.
    - **[Learn Lua in Y minutes](https://learnxinyminutes.com/docs/lua/)**: a one-page tour if you already know another language.

---

## Variables: `local` vs global

A variable declared with `local` exists only inside the block (file, function, `if`, loop) where it's declared. A variable assigned **without** `local` is **global**: it lives in a shared table (`_G`) that every script on the radio can see.

```lua
count = 0          -- global: shared with every other script, slower to access
local total = 0    -- local: private to this file, fast
```

**Why it matters on Ethos:** all scripts run in the same Lua state, so a global `line` or `config` in your widget can be overwritten by someone else's tool, and vice versa. Locals are also faster: Lua keeps them in registers, while a global is a table lookup every time.

**Rule:** always write `local`. Even for functions: `local function paint(widget) ... end`.

*Read more:* [PiL 4.2: Local variables and blocks](https://www.lua.org/pil/4.2.html)

---

## Tables and references

The **table** is Lua's only data structure. It is both an array (`t[1]`, `t[2]`) and a dictionary (`t.name`, `t["name"]`). Widgets, settings, lists and modules are all tables.

Tables are handled **by reference**: assigning a table to another variable doesn't copy it, both names point to the same table.

```lua
local a = { value = 1 }
local b = a          -- b is the SAME table, not a copy
b.value = 2
print(a.value)       --> 2
```

**Why it matters on Ethos:** it's why "clear a table in place" and "replace it with `{}`" behave differently. If another part of your code holds a reference to the old table, `cache = {}` leaves it looking at stale data, while clearing in place updates everyone. See [Code patterns → clear in place](../best-practice/patterns.md#clear-in-place).

*Read more:* [PiL 2.5: Tables](https://www.lua.org/pil/2.5.html)

---

## Allocation

**Allocating** means asking for new memory. In Lua, these all allocate:

| Code | Allocates |
| --- | --- |
| `{}` or `{ x = 1 }` | A new table |
| `function() ... end` | A new closure (see below), each time the line runs |
| `"V: " .. value` | A new string (strings are immutable; every concatenation creates a new one) |
| `string.format(...)`, `tostring(n)` | A new string |

Numbers, booleans and `nil` don't allocate.

**Why it matters on Ethos:** memory is small, and every allocation eventually becomes garbage the collector has to clean up (next section). Allocating inside code that runs many times a second is the most common cause of memory pressure in Ethos scripts.

---

## Garbage and the garbage collector

When nothing refers to a table, string or closure any more, it becomes **garbage**. Lua's **garbage collector** (GC) periodically finds garbage and frees its memory. You never free memory yourself; you just stop referring to things.

```lua
local function wakeup(widget)
  local t = { widget.x, widget.y }   -- allocated...
end                                  -- ...and garbage as soon as wakeup returns
```

Two consequences:

- **Garbage isn't free immediately.** Between collections it still occupies memory, so code that creates lots of garbage pushes memory use *up* (the "sawtooth" pattern), even though it holds nothing long-term. On a radio the peak is what gets your script killed.
- **Memory that is still referenced is never collected.** If something keeps a reference (a cache, a global, a forgotten event handler), the GC can't free it no matter how often it runs. That's a **leak**.

**Churn** is the rate at which code creates garbage. **Retention** is memory that stays referenced. Best practice is mostly about reducing both.

*Read more:* [Lua 5.4 manual §2.5: Garbage collection](https://www.lua.org/manual/5.4/manual.html#2.5) · [`collectgarbage`](https://www.lua.org/manual/5.4/manual.html#pdf-collectgarbage) · [Saving RAM](../best-practice/memory.md)

---

## Functions are values

In Lua, a function is a value like a number or a table. You can store it in a variable, put it in a table, or pass it to another function. That's how Ethos callbacks work: you hand Ethos your functions in a table, and it calls them later.

```lua
local function paint(widget) ... end
system.registerWidget({ key = "demo", name = "Demo", paint = paint })  -- passing the function itself
```

A **callback** is a function you give to someone else (Ethos, a form field, a dialog button) to call later: `paint`, `wakeup`, a field's getter and setter, a button's `press`.

*Read more:* [PiL 6: More about functions](https://www.lua.org/pil/6.html)

---

## Closures and upvalues

A **closure** is a function together with the variables it uses from the code around it. Those captured outside variables are called **upvalues**.

```lua
local function makeCounter()
  local count = 0              -- an ordinary local of makeCounter...
  return function()            -- ...captured by this inner function (a closure)
    count = count + 1          -- 'count' is an upvalue: it survives after makeCounter returns
    return count
  end
end

local next = makeCounter()
print(next(), next(), next())  --> 1  2  3
```

Form fields use closures all the time. The getter and setter "remember" which setting they belong to:

```lua
form.addNumberField(line, nil, 0, 100,
  function() return config.warn end,       -- closure capturing 'config'
  function(v) config.warn = v end)         -- another closure capturing 'config'
```

**Why closures matter on Ethos:**

1. **Creating a closure allocates.** `function() ... end` inside a function that runs repeatedly (a `wakeup`, a form rebuild) creates a new closure every time. Write the function once, at file level, and reuse it.
2. **Closures keep things alive.** A closure holds references to its upvalues, so as long as the closure exists, everything it captured exists too. That might be a large table, a bitmap, or a whole page's state. If Ethos (or your code) keeps the closure, for example as a form field's callback or a registered event handler, none of it can be collected.

```lua
-- ✗ a new closure (and new garbage) every wakeup
local function wakeup(widget)
  table.sort(widget.items, function(a, b) return a.v < b.v end)
end

-- ✓ one closure, created once
local function byValue(a, b) return a.v < b.v end
local function wakeup(widget)
  table.sort(widget.items, byValue)
end
```

*Read more:* [PiL 6.1: Closures](https://www.lua.org/pil/6.1.html) · [Lua 5.4 manual §3.5: Visibility rules (upvalues)](https://www.lua.org/manual/5.4/manual.html#3.5)

---

## Hot path

A **hot path** is code that runs very often. In Ethos that means `wakeup` (continuously), `paint` (on every redraw), event handlers, and anything they call. A small cost in a hot path is multiplied by thousands of calls a minute. The same cost in `create()` or a button press, which run once, doesn't matter.

**Rule of thumb:** be strict in hot paths (no allocation, no file access, no lookups you could cache), and relaxed everywhere else. See [Saving CPU](../best-practice/cpu.md).

---

## Caching

**Caching** means keeping a result so you don't compute it again. Look up a source once and store it; measure text once and remember the size; load an image once and keep the handle.

A cache trades memory for speed, so it needs limits. A cache whose keys can grow forever (file paths, sensor names) needs a maximum size. An **LRU** (*least recently used*) cache evicts the entry that hasn't been used for longest when it's full. See [Code patterns → bounded caches](../best-practice/patterns.md#bounded-caches-small-lru).

---

## Modules: `loadfile` and `package.loaded`

A **module** is a Lua file that returns a table of functions, so a big script can be split into files.

```lua title="lib/units.lua"
local M = {}
function M.volts(v) return string.format("%.1fV", v) end
return M
```

```lua title="main.lua"
local units = assert(loadfile("lib/units.lua"))()   -- run the file, get its table
print(units.volts(11.8))
```

`loadfile(path)` compiles the file and returns it as a function; calling that function runs the file. **Each call does it all again**, creating a fresh copy of the module. `require` would cache modules in the table **`package.loaded`**; with `loadfile` you can do that caching yourself. See [Code patterns → module loading](../best-practice/patterns.md#module-loading).

*Read more:* [PiL 8: Compilation, execution and errors (`loadfile`)](https://www.lua.org/pil/8.html) · [PiL 8.1: `require`](https://www.lua.org/pil/8.1.html) · [Lua 5.4 manual: `package.loaded`](https://www.lua.org/manual/5.4/manual.html#pdf-package.loaded)

---

## Bytecode (`.luac`)

Lua first **compiles** source text into **bytecode**, a compact form it can run directly, then executes that. A `.luac` file is precompiled bytecode. Ethos 26.1 compiles each script's `main.lua` to `main.luac` when loading it, and [`system.compile`](../api/system/compile.md) compiles other files. Loading bytecode skips the compile step and its temporary memory use.

---

## Integers and floats

Lua 5.4 has two kinds of number: **integers** (`3`) and **floats** (`3.0`, `3.5`). `/` always gives a float (`7 / 2 == 3.5`); `//` is integer (floor) division (`7 // 2 == 3`). `math.floor(x)` returns an integer. This matters when you format values (`%d` needs an integer) or compare a computed value with a stored integer.

*Read more:* [Lua 5.4 manual §3.4.1: Arithmetic operators](https://www.lua.org/manual/5.4/manual.html#3.4.1)

---

## Errors and `pcall`

When Lua code fails (calling a method on `nil`, adding a string to a number), it raises an **error** that stops the current call. `pcall(f, ...)` calls `f` in "protected mode": instead of stopping, it returns `false` plus the error message.

```lua
local ok, err = pcall(riskyUpdate, widget)
if not ok then print("[mywidget] " .. tostring(err)) end
```

*Read more:* [PiL 8.4: Error handling](https://www.lua.org/pil/8.4.html) · [Debugging](../tools/debugging.md)

---

## Stack and recursion

Every function call uses a little memory on the **call stack**, freed when it returns. **Recursion** (a function calling itself, or A calling B calling A) uses more stack the deeper it goes. On a radio the C stack is small, and running out of it resets the radio instead of raising a Lua error. Keep recursion shallow and bounded. See [Pitfalls → unbounded recursion](../best-practice/pitfalls.md#unbounded-recursion).
