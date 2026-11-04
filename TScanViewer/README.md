# Steve Unity viewer

Open this project in Unity and run `Assets/TScan/Observatory.unity`. Start the backend using `../t-scan/Start-Steve.ps1`. See [running](../docs/RUNNING.md) and [architecture](../docs/ARCHITECTURE.md).

Unity owns `Assets/Resources/Meadow/World.asset` and renders it through scene-owned `MeadowEnvironment`, independently of inference. `GridWorkbench` presents backend-confirmed movement and acknowledges animation completion. Chat, Thinking, Memory, operator Notes and agent Goals expose runtime records.

This project is independent of PleaseHold and PleaseHoldShorts. The viewer contains only the hovering-unicorn meadow path. Robot arms, hex workbenches, native activation displays and their fallback assets have been removed.
