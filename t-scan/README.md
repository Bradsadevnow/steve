# Steve backend

The active meadow harness is `live/bridge.py`, launched by `Start-TScan.ps1`. It uses Python's standard library and calls LM Studio for inference.

- [Run and verify](../docs/RUNNING.md)
- [Architecture](../docs/ARCHITECTURE.md)
- [Navigation trials](../docs/EXPERIMENTS.md)

`live/` holds the runtime and its tests. `runtime_data/` contains private authored memory, current state, operator notes and run/trial evidence. `art/` contains current meadow/unicorn source art. `research/` holds original activation research, independent of the current harness; its dependencies and historical findings do not describe this runtime.
