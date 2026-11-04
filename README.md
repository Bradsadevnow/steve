# Steve workspace

Steve is an embodied local agent: LM Studio supplies decisions, Python owns authoritative runtime state, and Unity owns and renders a 10×10 meadow with a hovering unicorn.

- [Run Steve](docs/RUNNING.md)
- [Architecture and state ownership](docs/ARCHITECTURE.md)
- [Navigation experiments](docs/EXPERIMENTS.md)
- [Project boundaries](PROJECT_BOUNDARIES.md)

| Directory | Purpose |
| --- | --- |
| `t-scan/live/` | Active Python backend, task tools, run capture, and tests |
| `t-scan/runtime_data/` | Private memory database, current state, run captures, trial results |
| `TScanViewer/` | Unity viewer and authored meadow |
| `t-scan/research/` | Original activation research, independent of the current harness |
| `hsp_review/` | Authored identity seed sources and provenance |
| `Tools/` | Workspace boundary verification |
| `PleaseHold/` | Independent human-playable game |
| `PleaseHoldShorts/` | Independent Blender production |

Start from the running guide. Historical material in `Archive/` is not a setup procedure.

The Git repository contains Steve source and current art. Private memory, run captures, original research, and the independent PleaseHold projects remain local and are excluded from commits.
