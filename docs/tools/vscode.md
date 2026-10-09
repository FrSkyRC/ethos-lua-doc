# VS Code deployments

Large open-source Ethos Lua projects use the same development setup: **VS Code**, the **Ethos simulator extension**, and a **deploy script** that copies the project to the simulator or straight onto a USB-connected radio, then optionally streams the radio's `print()` output back. Press **F5** and the code is on the radio.

This page explains each part and gives you a working, tested version to copy:

- [`ethos_deploy.py`](https://github.com/FrSkyRC/ethos-lua-doc/blob/main/examples/tooling/ethos_deploy.py): a self-contained deploy tool (~250 lines)
- [`examples/tooling/vscode/`](https://github.com/FrSkyRC/ethos-lua-doc/tree/main/examples/tooling/vscode): `tasks.json`, `launch.json`, `settings.json`, `ethos-menu.json`

```mermaid
flowchart LR
  F5[F5 in VS Code] --> T[preLaunchTask:<br/>ethos_deploy.py]
  T -->|--sim| S[simulators/X20S_FCC@nightly26/scripts/]
  T -->|--radio| H[USB HID: switch to storage]
  H --> D[find drive by *.cpuid]
  D --> C[copy changed files only]
  C -->|--debug| R[USB HID: switch to serial]
  R --> P[tail print output]
  S --> E[ethos.start: simulator panel]
```

## 1. Project layout

```text
my-ethos-project/
├── src/
│   └── mywidget/            ← exactly what ends up in SCRIPTS:/mywidget/
│       ├── main.lua
│       └── gfx/icon.png
├── tools/
│   └── ethos_deploy.py
├── simulators/              ← created by the Ethos extension; git-ignore it
└── .vscode/
    ├── settings.json        ← board / protocol / release for the simulator
    ├── tasks.json           ← deploy commands
    ├── launch.json          ← makes them F5-able
    ├── ethos-menu.json      ← status-bar quick menu (optional)
    └── noop.py
```

Keep the deployable folder (`src/mywidget/`) separate from tooling, tests and docs. The deploy script then mirrors that folder and nothing else.

## 2. The Ethos simulator extension

The [Ethos extension](https://marketplace.visualstudio.com/items?itemName=bsongis.ethos) (`bsongis.ethos`) runs the Ethos WebAssembly simulator inside VS Code: display, controls and telemetry panels, audio, screenshots and a log file.

| Setting | Meaning |
| --- | --- |
| `ethos.board` | Radio board, e.g. `X20S`, `X20PRO`, `X18` |
| `ethos.protocol` | RF protocol variant, e.g. `FCC`, `EU` |
| `ethos.release` | Ethos release or branch, e.g. `nightly26` (default) |
| `ethos.simulatorsFolder` | Workspace folder holding simulators (default `simulators`) |
| `ethos.logfile` | Write the simulator console to a file |

Each simulator keeps its own radio storage in **`<simulatorsFolder>/<board>_<protocol>@<release>/`**, which is a normal folder with `radio.bin`, `models/`, `scripts/`. That's what a deploy script writes into. Downloaded firmware builds are cached in VS Code's global storage (`.../globalStorage/bsongis.ethos/cache/`), which is also what [`ethos-tools`](ai-agents.md) uses.

Useful commands (Command Palette → *Ethos: ...*): `ethos.start`, `ethos.stop`, `ethos.setSimulator`, `ethos.openDisplay`, `ethos.openControls`, `ethos.openTelemetry`, `ethos.takeScreenshot`, `ethos.openLuaDoc`.

**Status-bar menu.** Clicking the extension's status-bar item can show your own quick-pick menu from `.vscode/ethos-menu.json`. Entries run commands, or tasks such as your deploy:

```json title=".vscode/ethos-menu.json"
--8<-- "examples/tooling/vscode/ethos-menu.json"
```

!!! tip "Simulated telemetry"
    Projects keep a `sensors.json` describing simulated sensors (name, value, update interval) in the repository and copy it to the simulator folder's root on deploy, so telemetry widgets have data from the first boot.

## 3. Tasks and F5

`tasks.json` defines the deploy commands. `${config:ethos.*}` reuses the extension's settings, so the simulator target always matches the selected simulator:

```json title=".vscode/tasks.json"
--8<-- "examples/tooling/vscode/tasks.json"
```

**The F5 trick.** VS Code only lists *launch configurations* in the Run and Debug dropdown. Projects add debug configurations whose program is an empty Python file and whose `preLaunchTask` is the deploy, so F5 (or the green ▶) deploys. `postDebugTask` can then start the simulator:

```json title=".vscode/launch.json"
--8<-- "examples/tooling/vscode/launch.json"
```

`type: debugpy` needs the Python extension. `${command:python.interpreterPath}` in the tasks runs the deploy with the interpreter selected in VS Code, so dependencies installed there are found.

## 4. Talking to the radio over USB

When connected and powered on, an Ethos radio presents a **composite USB device** (VID `0483`, PID `5750`):

| Interface | Always? | Is |
| --- | --- | --- |
| 0 | Yes | **HID control channel**, the one Ethos Suite uses |
| 1 | — | **Either** USB mass storage (the radio's drive) **or** a CDC serial port (debug output) |

Switching interface 1 between storage and serial is a HID command. The radio drops off the bus and re-enumerates, which takes a few seconds.

| Request (HID report, after report id `0x00`) | Effect |
| --- | --- |
| `21 06` | Board information. Response starts `22`; byte 2 is the board id |
| `81 68` | USB mode → **serial debug** (drive unmounts, a COM/tty port appears) |
| `81 69` | USB mode → **mass storage** (serial port goes, drive mounts) |
| `61 66` | Reboot the radio |

!!! note "Verified on hardware"
    On an X20S (Ethos 26.1.2): `21 06` returned `22 06 05 ...` (board id 5, an SD-card board). `81 68` produced `COM15` within a few seconds, and `81 69` remounted the drive within about 2 s.

    The flash and storage-format commands also exist in this protocol. Leave them alone unless you are writing a flashing tool.

```python
import hid                     # pip install hidapi

dev = hid.device()
dev.open(0x0483, 0x5750)       # some firmware states re-enumerate as 0x5740
dev.write(bytes([0x00, 0x21, 6]))
print("board id", dev.read(64, 500)[2])
dev.write(bytes([0x00, 0x81, 0x69]))   # make sure we are in storage mode
dev.close()
```

### Finding the radio's drive

Don't guess drive letters. The radio's volumes carry **marker files** at their root: `sdcard.cpuid`, `radio.cpuid` or `flash.cpuid`. Scan removable drives (Windows), `/Volumes/*` (macOS) or `/media/$USER/*` (Linux) for one of these, and the `scripts/` folder next to it is your target. On radios with both internal flash and an SD card, prefer `sdcard`, then `radio`.

Ethos Suite's CLI can do the same lookups: `--get-path SCRIPTS` and `--serial start|stop`. See [Ethos Suite](ethos-suite.md#command-line). Talking HID directly removes the dependency on Suite, works on macOS and Linux, and avoids the `ELECTRON_RUN_AS_NODE` trap when called from VS Code.

## 5. Copying safely to removable storage

Writing to the radio's drive over USB is slow, and a cable bump mid-write corrupts files. Robust deploy scripts:

- **Copy only what changed.** Compare size first, then MD5 if sizes match, and delete files that no longer exist in the source (an rsync-style mirror). A typical redeploy then copies one or two files.
- **`fsync` every file** so it really lands before the radio is unplugged or switched to serial.
- **Delete stale `.luac`** next to changed `.lua`. Ethos compiles `main.lua` on load, and old bytecode can hide your change.
- **Stage first when you transform files.** If the deploy runs build steps (generating translation tables, resolving i18n tags, building sound packs), do it in a local temp folder, then mirror the result to the radio, instead of many small edits on the slow drive.
- **Throttle very large copies.** Some suites write in chunks with short pauses, because a burst of thousands of small writes has caused USB storage stalls on some systems.
- **Allow time to mount.** After switching to storage mode, Windows can take 10–30 s to mount the volume. Poll for the marker file, and re-send the storage command at most once, and only if the serial port is still present after ~20 s, because every switch command restarts the enumeration.
- **Single instance.** Keep a lock file so two deploys (an F5 double-press) can't write at once.

`ethos_deploy.py` implements the first four. The others matter once a project has hundreds of files.

## 6. Serial debug: `print()` from the radio

With the radio in serial mode, everything your scripts `print()` arrives on the serial port at 115200 baud. Find the port by VID/PID, not by name:

```python
from serial.tools import list_ports   # pip install pyserial
port = next(p.device for p in list_ports.comports() if p.vid == 0x0483 and p.pid == 0x5750)
```

`ethos_deploy.py --radio --debug` deploys, switches to serial, prints lines until **Ctrl+C**, then switches back to storage so the next deploy finds the drive.

The radio only sends what scripts print. An idle radio is silent, which is normal. Prefix your messages (`[mywidget] ...`), because every script shares the port. Ethos Suite's **Lua development tools → Debug log** is the GUI equivalent.

## 7. The deploy tool

```text
python tools/ethos_deploy.py --src src/mywidget --sim simulators/X20S_FCC@nightly26/scripts
python tools/ethos_deploy.py --src src/mywidget --radio            # incremental copy to the radio
python tools/ethos_deploy.py --src src/mywidget --radio --dry-run  # show what would change
python tools/ethos_deploy.py --src src/mywidget --radio --debug    # deploy, then tail print()
python tools/ethos_deploy.py --radio --debug-only                  # just tail print()
python tools/ethos_deploy.py --radio --info                        # board id over HID
```

Tested against an X20S on Windows: a first deploy copied the script, a second run copied nothing (`0 copied, 0 removed`), and `--debug-only` switched to `COM15` and back to the mounted drive.

??? example "ethos_deploy.py (full source)"
    ```python linenums="1"
    --8<-- "examples/tooling/ethos_deploy.py"
    ```

## Checklist for a new project

1. Install the **Ethos** extension and the **Python** extension; `pip install hidapi pyserial`.
2. Copy `ethos_deploy.py` to `tools/` and the four files from `examples/tooling/vscode/` (plus `noop.py`) to `.vscode/`. Replace `mywidget` with your folder name.
3. Run **Ethos: Set Simulator** once (picks board, protocol and release, then downloads the build).
4. Add `simulators/` to `.gitignore`.
5. Pick **Deploy & launch [simulator]** in Run and Debug and press F5.
6. Plug in a radio, choose **Deploy [radio]**, press F5.
