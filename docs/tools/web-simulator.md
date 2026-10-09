# Web simulator

FrSky's browser simulator runs the real Ethos firmware compiled to WebAssembly, so there's nothing to install. Chrome is recommended.

**[ethos-simulator.frsky-rc.com](https://ethos-simulator.frsky-rc.com/)**

You pick the Ethos release, the radio and the RF protocol, and get the radio's screen, its controls, and optional panels such as the **Console** and **Telemetry**.

## Running your script

1. Zip your script. Include an [`ethos_lua_manifest.json`](../getting-started/packaging.md#installable-zip-packages) at the root; it's the package format Ethos installers understand.
2. **Upload → Upload a Lua plugin (.zip)**.
3. If your script doesn't show up straight away, use the toolbar's **Restart simulator**. Scripts are loaded at boot. Your widget, tool or task is then available as on a radio.

To start from your real setup instead of a blank radio, make a backup in Ethos Suite and use **Upload → Upload a radio backup**. You get your models, screens and scripts.

## Panels worth opening

| Panel | Why |
| --- | --- |
| **Console** | Boot log, `print()` output and **Lua errors**. Drag it to the bottom of the window so long lines are readable. Open it before anything else when developing |
| **Telemetry** | Add simulated sensors (**Add a new sensor**) and set their values, so telemetry widgets have data. Save the set with **Download → Save telemetry settings** and restore it later with **Upload → Upload a JSON telemetry file** |
| **Controls** | Sticks, switches, pots and trims. Gimbals can be locked to one axis or set to auto-centre, and momentary switches can be latched, which helps when testing |

The panel layout is remembered by the browser.

## Upload and Download menus

| Upload | Download |
| --- | --- |
| Model file (`.bin`) | Current model (`.bin`), or edit it as JSON |
| Radio backup | Radio backup (`.zip`) |
| Audio pack (`.zip`) | All screenshots |
| **Lua plugin (`.zip`)** | Telemetry settings (`.json`) |
| CSV translations | |
| JSON telemetry file | |
| Start a macro (`.zip`) | |

The toolbar also has screenshot, macro recording, audio on/off, restart and light/dark mode.

## Testing across radios and versions

Switching the release lets you check a script against the firmware your users run. Switching the radio checks layout on different screen sizes. Two habits:

- Test on the **smallest** screen you support (X18 family, 480×320) as well as the largest.
- Before relying on a new API, check its **since** version on its [API page](../api/index.md), then load an older release in the simulator to confirm your fallback works.

!!! note "Command-line and AI use"
    The same WebAssembly builds can run headless from a terminal with [`ethos-tools`](ai-agents.md), which also lets an AI agent drive the radio.
