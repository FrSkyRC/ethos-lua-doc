# Ethos Suite

Ethos Suite is FrSky's desktop companion app. For script developers it does three useful things: a **simulator with a real folder on disk**, **Lua script installation** on a connected radio, and **backups**.

## The Suite simulator

Choose the radio, Ethos release and RF protocol, then **Start Simulator**. Unlike the web simulator, its radio storage is a normal folder on your computer, shown at the top of the window as the *Current local simulator directory* (the help icon explains the layout).

That makes the edit loop simple:

1. Close the simulator (or Suite).
2. Copy your script folder into `<simulator directory>/scripts/`. Delete any stale `main.luac`.
3. Start the simulator again. Open the **Console** panel to see `print` output and Lua errors.

Pre-release (nightly) Ethos versions are offered only when **GitHub** is selected as the server location in Suite's settings.

!!! tip "Simulate your real radio"
    Make a backup of your radio (**Backup & recovery**), then, with Suite closed, replace the contents of the simulated radio's folder with the backup. On the next start the simulator boots with your models, screens and scripts.

## Installing scripts on a radio

**Lua Library → Install from local `.zip`** installs a script package on the connected radio. The zip must contain an [`ethos_lua_manifest.json`](../getting-started/packaging.md#installable-zip-packages). Suite copies only the files the manifest lists, writes the manifest into the script folder, and uses it for later upgrades. Installed scripts show their release notes from the manifest.

## Command line

Suite has a command-line mode that's handy in scripts:

| Option | Does |
| --- | --- |
| `--version` | Show the Suite version |
| `--list-radios` | List supported radios |
| `--radio-components [--radio NAME\|auto]` | List the connected radio's components and their paths |
| `--get-path SCRIPTS` | Print the path of the radio's scripts folder (also `BITMAPS`, `SCREENSHOTS`, `AUDIO`, `I18N`) |
| `--serial start\|stop` | Turn the radio's serial debug mode on or off |

For example, a deploy script can ask Suite where the radio's scripts folder is mounted and copy the build there:

```bash
SCRIPTS=$("FrSky Suite" --get-path SCRIPTS)
cp -r build/myscript "$SCRIPTS/"
```

The exact executable name depends on your platform and install. Suite won't start unless it recognises the command you pass.

### Serial debug: `print` from a real radio

`--serial start` switches the connected radio to serial debug mode, so `print()` output from scripts running **on the radio** reaches your computer over USB. Several open-source suites' deploy tools use this to tail radio logs. See [Debugging](debugging.md#on-a-radio).
