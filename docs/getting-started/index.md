# Getting started

Ethos runs Lua 5.4 scripts that can draw widgets on the home screens, add tools to the System menu, run tasks in the background, provide new sources, and more. This section takes you from nothing to a working script, then explains the model behind it.

1. **[Your first widget](first-widget.md)**: write a widget, install it, see it on screen.
2. **[Script types & lifecycle](script-types.md)**: widgets, system tools, tasks, sources, and which callbacks Ethos calls, and when.
3. **[Lua concepts](lua-concepts.md)**: tables, closures, garbage collection and the other ideas behind the best-practice rules, explained for non-experts.
4. **[The Lua environment](lua-environment.md)**: which standard libraries exist, the extra `os` functions, and file paths like `SCRIPTS:` and `AUDIO:`.
5. **[Files, folders & packaging](packaging.md)**: how scripts are laid out on the radio and how to ship them as an installable zip.

## What you need

| You need | Why | Where to get it |
| --- | --- | --- |
| A text editor | To write `.lua` files | Anything works. VS Code with the Ethos extension gives you a simulator in the editor. |
| A simulator **or** a radio | To run the script | [Web simulator](../tools/web-simulator.md) (nothing to install) or [FrSky Suite](../tools/frsky-suite.md) |
| This site | API details | The [API reference](../api/index.md); every call has its own page |

!!! tip "Start in the simulator"
    The simulator restarts in seconds and shows Lua errors in its **Console** panel. On a radio, a script error usually just means the widget stays blank. Develop in the simulator and copy to the radio once it works.

## The shape of every script

Every Ethos script is a folder under `SCRIPTS:` with a `main.lua` that **returns a table with an `init` function**. In `init()` the script *registers* what it provides:

```lua title="scripts/myscript/main.lua"
local function init()
  system.registerWidget({ key = "mywdgt", name = "My widget", paint = function() end })
  -- or registerSystemTool / registerTask / registerSource / ...
end

return { init = init }
```

Ethos loads every `main.lua` at boot, calls `init()` once, and from then on calls the callbacks you registered. One script can register several things. A suite, for example, often registers a tool, a widget and a background task from a single `main.lua`.
