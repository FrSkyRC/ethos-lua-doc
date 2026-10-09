# Forms & configuration UI

Forms are Ethos's built-in UI toolkit: labelled lines holding native fields (numbers, choices, sources, switches, colors, ...). They look and behave like the rest of the radio's menus, handle touch, encoder and keys for you, and are the right tool for every settings screen.

You build a form in:

- a widget's **`configure(widget)`** callback (the widget settings page),
- a system tool's **`create()`** callback (the tool's page),
- a task's or source's `configure` callback.

## Lines and fields

Every field sits on a **line**. The line has a label on the left; fields go on the right.

```lua
local line = form.addLine("Max RPM")
form.addNumberField(line, nil, 0, 20000,
  function() return config.maxRpm end,            -- getter: current value
  function(v) config.maxRpm = v end)              -- setter: called on change
```

Every field takes a **getter** and a **setter** instead of a variable. Ethos calls the getter whenever it needs to show the value, and the setter when the pilot changes it. Passing `nil` as the rect lets Ethos place the field.

| Field | Call | Value type |
| --- | --- | --- |
| Number | [`form.addNumberField(line, rect, min, max, get, set)`](../api/form/addNumberField.md) | integer |
| Choice | [`form.addChoiceField(line, rect, values, get, set)`](../api/form/addChoiceField.md) | value from `values` |
| On/off | [`form.addBooleanField(line, rect, get, set)`](../api/form/addBooleanField.md) | boolean |
| Source | [`form.addSourceField(line, rect, get, set)`](../api/form/addSourceField.md) | [Source](../api/objects/Source/index.md) |
| Switch | [`form.addSwitchField(line, rect, get, set)`](../api/form/addSwitchField.md) | Source |
| Sensor | [`form.addSensorField(line, rect, get, set [, filter])`](../api/form/addSensorField.md) | Source |
| Color | [`form.addColorField(line, rect, get, set)`](../api/form/addColorField.md) | color |
| Text | [`form.addTextField(line, rect, get, set)`](../api/form/addTextField.md) | string |
| Time | [`form.addTimeField(line, rect, get, set)`](../api/form/addTimeField.md) | seconds |
| Slider | [`form.addSliderField(line, rect, min, max, get, set)`](../api/form/addSliderField.md) | integer |
| File | [`form.addFileField(line, rect, path, type, get, set)`](../api/form/addFileField.md) | path |
| Button | [`form.addButton(line, rect, { text=, icon=, press= })`](../api/form/addButton.md) | |
| Static text | [`form.addStaticText(line, rect, text)`](../api/form/addStaticText.md) | |

### Choice values

A choice field's `values` is a list of `{label, value}` pairs:

```lua
local MODES = { { "Off", 0 }, { "Beep", 1 }, { "Voice", 2 } }   -- built once, at file level

local line = form.addLine("Alert")
form.addChoiceField(line, nil, MODES,
  function() return config.alert end,
  function(v) config.alert = v end)
```

### Tuning number fields

The field objects returned by `add*Field` have methods. Number fields have the most:

```lua
local f = form.addNumberField(line, nil, 0, 500, getV, setV)
f:decimals(1)         -- 0..500 shows as 0.0..50.0
f:suffix("V")
f:step(5)
f:default(111)        -- long-press resets to this
f:help("Cell voltage that triggers the low-battery call")
```

[`NumberEditLib`](../api/objects/NumberEditLib/index.md) has the full list. All fields share `field:enable(bool)` and `field:focus()` from [`FormFieldLib`](../api/objects/FormFieldLib/index.md).

!!! tip "Enable/disable only when it changes"
    `field:enable()` is one of the most-called methods in real projects. Calling it from `wakeup` every tick with the same value causes needless redraws. Track the last state and call it only when it changes.

## Several fields on one line

[`form.getFieldSlots(line, specs)`](../api/form/getFieldSlots.md) splits the right side of a line into rects. A number is a fixed width, `0` means "share the remaining space", a string reserves room for that text:

```lua
local line = form.addLine("Range")
local slots = form.getFieldSlots(line, { 0, "-", 0 })
form.addNumberField(line, slots[1], -1024, 1024, function() return w.min end, function(v) w.min = v end)
form.addStaticText(line, slots[2], "-")
form.addNumberField(line, slots[3], -1024, 1024, function() return w.max end, function(v) w.max = v end)
```

## Expansion panels

Group advanced settings so the page stays short:

```lua
local panel = form.addExpansionPanel("Advanced")
panel:open(false)                                  -- start collapsed
local line = panel:addLine("Smoothing")            -- or form.addLine("Smoothing", panel)
form.addNumberField(line, nil, 0, 10, getS, setS)
```

## Dialogs

```lua
form.openDialog({
  title = "Reset stats?",
  message = "This clears min/max for every sensor.",
  buttons = {
    { label = "Reset",  action = function() resetStats(); return true end },  -- true closes the dialog
    { label = "Cancel", action = function() return true end },
  },
  options = TEXT_LEFT,
})
```

Buttons are laid out **right to left**: the first entry in `buttons` is the rightmost, and the initial focus goes to the leftmost (last) one. In the example above "Cancel" sits on the left and has focus, which is the safe default for a destructive action.

For long operations, a wait dialog with progress:

```lua
local dlg = form.openWaitDialog({ title = "Saving", message = "Writing settings...", progress = true })
-- later, from wakeup:
if dlg then                         -- guard: it can be nil (see warning below)
  dlg:value(percent)
  if percent >= 100 then dlg:close(); dlg = nil end
end
```

!!! warning "Guard dialog handles"
    In practice `openWaitDialog` has been seen returning `nil` during a page reload, and code that then called `dlg:value()` crashed with *attempt to index a nil value*. Always check the handle, and close dialogs in your tool's `close()` callback.

## Rebuilding a form

To redraw a page with different content (for example after the pilot picks a mode), clear it and build it again:

```lua
local function build(state)
  form.clear()
  local line = form.addLine("Mode")
  form.addChoiceField(line, nil, MODES, function() return state.mode end,
    function(v) state.mode = v; build(state) end)   -- rebuild for the new mode
  if state.mode == 2 then
    -- extra lines for mode 2 only
  end
end
```

!!! warning "Rebuilding is not free"
    Ethos keeps some form allocations alive after `form.clear()`, outside the reach of Lua's garbage collector. Measured on an X18RS, each rebuild of a complex page retains RAM that `collectgarbage()` can't recover. Rebuild only when the structure actually changes, use `field:enable()` to show and hide options instead, and reuse getter/setter closures rather than creating new ones on every build. See [Saving RAM](../best-practice/memory.md#forms-retain-memory).

## Widget configuration example

```lua
local function configure(widget)
  local line = form.addLine("Source")
  form.addSourceField(line, nil, function() return widget.source end,
    function(v) widget.source = v end)

  line = form.addLine("Warning below")
  local f = form.addNumberField(line, nil, 0, 1000, function() return widget.warn end,
    function(v) widget.warn = v end)
  f:decimals(1)

  line = form.addLine("Color")
  form.addColorField(line, nil, function() return widget.color end,
    function(v) widget.color = v end)
end
```

Pair it with `read`/`write` so the settings survive a restart. See [Saving settings](storage.md).
