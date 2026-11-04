# Running Steve

From `t-scan/` in PowerShell:

```powershell
./Start-TScan.ps1
```

The launcher uses `t-scan/.venv/Scripts/python.exe`. The active backend requires Python 3.12 and only its standard library. If the environment is missing, create it with `py -3.12 -m venv .venv` from `t-scan/`.

LM Studio must serve the configured model. Defaults are `http://192.168.1.128:1234`, model `google/gemma-4-e4b`, temperature 1, and context capacity 131072. Override the host/model through `Start-TScan.ps1 -LMStudioUrl <url> -Model <id>`. The loaded model's reported context capacity is recorded at connection time.

Open `TScanViewer` in Unity, open `Assets/TScan/Observatory.unity`, and press Play. The scene-owned meadow and flags render independently of inference. The backend listens on `127.0.0.1:8765`; `/health` reports inference status and `/grid/state` reports world/loop state.

Human chat wakes Steve. Settled actions offer another decision. `complete()` or a text-only response idles. Stop interrupts the loop. New chat archives the current run, clears working chat/task state, resets Steve to (5,5) facing north, and preserves long-term authored memory. Operator Notes and agent Goals share tabs; provider reasoning appears in Thinking.

From the workspace root, verify changes with:

```powershell
./t-scan/.venv/Scripts/python.exe -m unittest discover -s t-scan/live -p 'test_*.py'
./t-scan/.venv/Scripts/python.exe Tools/verify_project_boundaries.py
```

Boundary output is written to `t-scan/runtime_data/verification/project-boundaries.json`. Neither command wakes Steve or starts a navigation trial.
