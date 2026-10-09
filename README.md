# Ethos Lua Docs

Lua scripting documentation for FrSky Ethos radios: a full API reference with examples, guides, RAM and CPU best practice, a tested cookbook, and tooling for the simulator and AI agents.

**Site:** https://frskyrc.github.io/ethos-lua-doc/

## What's here

- **API reference**: one page per function, generated from FrSky's `lua-doc.zip`, with hand-written examples (`overlays/`) and real-world excerpts from open-source projects.
- **Guides**: drawing, forms, telemetry, events, storage, audio, translations.
- **Best practice**: saving RAM and CPU, based on measurements from production suites.
- **Cookbook**: complete scripts in `examples/cookbook/`, each tested in the Ethos simulator.
- **Tools**: web simulator, FrSky Suite, debugging, and AI agents with [ethos-tools](https://github.com/FrSkyRC/ethos-tools).

## Working on it

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/mkdocs serve                    # preview at http://127.0.0.1:8000
python scripts/update.py                  # pull the latest lua-doc.zip / examples / usage and regenerate
```

See [AGENTS.md](AGENTS.md) for the repository map, where the upstream sources come from (the latest `lua-doc.zip` moves with every Ethos release), and the update and review workflow.

## Credits

API content comes from FrSky's Ethos `lua-doc`. Official examples are from [FrSkyRC/ETHOS-Feedback-Community](https://github.com/FrSkyRC/ETHOS-Feedback-Community). Real-world excerpts come from the projects listed on the site's *Real-world usage* page, under their own licenses.
