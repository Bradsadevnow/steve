# Project boundaries

This workspace contains three independent projects:

| Project | Entry point | Owns |
| --- | --- | --- |
| Steve | `t-scan/Start-Steve.ps1`; Unity `TScanViewer/Assets/TScan/Observatory.unity` | Embodied agent, LM Studio inference, identity, authored memory, simulated affect, meadow interaction |
| PleaseHold | Unity `PleaseHold/Assets/Scenes/PleaseHold.unity` | Human-playable game; point-and-click jobs/progression direction |
| PleaseHoldShorts | `PleaseHoldShorts/Production/Episode_001/episode_001_filming_set.blend` | Independent Blender production |

Steve uses a hovering unicorn in a flat 15×15 meadow with static obstacles. Unity authors and renders `Resources/Meadow/World.asset`; Python validates its manifest and owns logical position. The model chooses cardinal movement and maintains its own task list. See [architecture](docs/ARCHITECTURE.md) and [running](docs/RUNNING.md).

PleaseHold has no Steve inference, chat UI, or authored-memory dependency. PleaseHoldShorts has no game-runtime dependency. Never add sibling runtime imports, shared saves, or cross-project symlinks. Reuse art through explicit local copies and keep launch paths independent.

Original activation-research scripts and their results belong under `t-scan/research/` and existing research-data directories, outside the active backend. Authored seed sources remain in `hsp_review/`. Root art directories contain source assets; the independent projects use explicit local copies. Historical `Archive/` is recovery material, not a setup procedure; do not rerun old migration scripts.

Run `Tools/verify_project_boundaries.py` after changes to ownership, tools, or resource paths. Check compilation and actual runtime behavior when changing Unity code or assets.
