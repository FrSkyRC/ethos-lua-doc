# Writing examples

## API page examples (overlays)

Each generated API page can include hand-written content from an **overlay** file:

```text
overlays/api/<owner>/<member>.md      → examples & notes for one function
overlays/api/<owner>/index.md         → extra intro for a namespace or object page
```

`<owner>` is the namespace (`lcd`, `system`, `form`, ...) or object (`Source`, `Timer`, ...). For example, `overlays/api/lcd/drawText.md` appears on [lcd.drawText](../api/lcd/drawText.md).

The **✏️ edit button** on any API page opens the matching overlay on GitHub, or a pre-filled "new file" form if it doesn't exist yet.

The overlay is plain Markdown, inserted under **Examples** above FrSky's own examples:

````markdown title="overlays/api/lcd/drawText.md"
```lua
lcd.font(FONT_L)
lcd.drawText(w / 2, 10, "Centered", CENTERED)
```

!!! tip
    Measure first with `lcd.getTextSize` when you need the height for vertical centring.
````

After editing, regenerate: `python scripts/gen_api_pages.py` (seconds, no network).

### What makes a good example

- **Runnable in context.** Show where the call lives (`paint`, `wakeup`, `create`) when that matters.
- **Short.** Five to fifteen lines. Link to a cookbook recipe for the full picture.
- **Correct by our own rules.** No allocation in hot paths, nil checks, absolute paths in callbacks. See [Best practice](../best-practice/index.md).
- **Verified.** Test it in a simulator ([how](../tools/ai-agents.md)) or base it on code that runs in a real project.

## Cookbook recipes

Recipes are real scripts in `examples/cookbook/<folder>/main.lua`, embedded into `docs/cookbook/<page>.md` with:

````markdown
```lua title="scripts/<folder>/main.lua" linenums="1"
;--8<-- "examples/cookbook/<folder>/main.lua"
```
````

Every recipe must boot without errors in the simulator. Widgets and tools should also be placed or opened and checked on screen. Add it to `docs/SUMMARY.md` and the table on the [cookbook index](../cookbook/index.md).
