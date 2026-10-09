```lua
system.playFile("AUDIO:/en/default/system/hello.wav")          -- a system voice file
system.playFile("SCRIPTS:/myscript/sounds/armed.wav")          -- your own sound: absolute path
```

From callbacks, use absolute paths: relative paths only resolve to your script folder while `main.lua` loads ([details](../../getting-started/lua-environment.md#relative-paths-only-work-while-your-script-loads)). Rate-limit anything triggered from `wakeup`; see [Audio](../../guides/audio.md#dont-nag-the-pilot).
