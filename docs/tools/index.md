# Tools & testing

You can develop most of a script without touching a radio. Pick the environment that suits the job:

| Tool | Install | Best for |
| --- | --- | --- |
| [Web simulator](web-simulator.md) | Nothing, it runs in Chrome | Quick tries, sharing a reproducible setup, loading a script zip |
| [FrSky Suite](frsky-suite.md) | FrSky's desktop app | Simulator with a real folder on disk, installing scripts on a radio, backups |
| [VS Code + deploy script](vscode.md) | VS Code, the Ethos extension, Python | F5 to deploy to the simulator or a USB radio, with live `print()` output from the radio |
| [`ethos-tools` + an AI agent](ai-agents.md) | Node.js + a clone or Claude Code plugin | Letting Claude (or another agent) boot a radio, deploy your script, screenshot and drive it, and read its errors |

Whatever you use, read [Debugging](debugging.md) for how to see `print` output and Lua errors.

## A typical loop

1. Edit `scripts/<yourscript>/main.lua` in your editor.
2. Copy the folder into the simulator's radio directory. Delete any stale `main.luac` in it, because Ethos compiles `main.lua` on load.
3. Restart the simulator. Scripts only load at boot, and cached modules stay cached until a restart.
4. Watch the console for errors, then exercise the script.
5. When it behaves, test on the smallest screen you support (an X18 is 480×320), then on a real radio.
