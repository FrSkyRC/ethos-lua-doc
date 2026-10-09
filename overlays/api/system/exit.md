```lua
-- close a system tool from a button
form.addButton(line, nil, { text = "Done", press = function() system.exit() end })
```

In a widget's `configure` form, `system.exit()` leaves the configuration page, as FrSky's gauge example does with an *Exit configuration* button.
