```lua
local NAMES = { en = "Battery", fr = "Batterie", de = "Akku" }

local function name()
  return NAMES[system.getLocale()] or NAMES.en
end

system.registerWidget({ key = "batt", name = name, create = create, paint = paint })
```

See [Translations](../../guides/i18n.md) for a translation-file pattern.
