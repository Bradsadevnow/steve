# Running Steve

The app/product name is Steve. The existing `t-scan` and `TScanViewer` folder names and internal code identifiers are retained; they do not select a separate TScan runtime.

From `t-scan/` in PowerShell:

```powershell
./Start-Steve.ps1
```

The launcher uses `t-scan/.venv/Scripts/python.exe`. The active backend requires Python 3.12 and only its standard library. If the environment is missing, create it with `py -3.12 -m venv .venv` from `t-scan/`.

LM Studio must serve the configured model. Defaults are `http://192.168.1.128:1234`, model `google/gemma-4-e4b`, temperature 1, and context capacity 131072. Override the host/model through `Start-Steve.ps1 -LMStudioUrl <url> -Model <id>`. The loaded model's reported context capacity is recorded at connection time.

Open `TScanViewer` in Unity, open `Assets/TScan/Observatory.unity`, and press Play. The scene-owned meadow and flags render independently of inference. The backend listens on `127.0.0.1:8765`; `/health` reports inference status and `/grid/state` reports world/loop state.

Human chat wakes Steve. Settled actions offer another decision. `complete()` or a text-only response idles. Stop interrupts the loop. New chat archives the current run, clears working chat/task state, resets Steve to (5,5) facing north, and preserves long-term authored memory. Provider reasoning fills the bottom Thinking panel, with Stop in its header. The right panel has Activity, Self and View tabs. Self shows position, selected focus, unfinished and agent-marked finished goals, commitments, authored assessments and beliefs, recent experience and capabilities. Operator Notes and the separate Current run area are retired from the viewer.

The v8.4 runtime allows up to three sequential tool calls per scheduled turn. Every call is a separate model decision with fresh feedback; multiple calls in one response are rejected. Handoffs and `complete()` end the turn early. Exhausting the three-call allowance yields to scheduling without marking tasks complete. The boundary does not automatically appraise affect or write memory. See [sequential turns](SEQUENTIAL_TOOLS.md).

The epoch runner (`live/epoch_batch.py`) runs each fixed route until Steve completes it instead of until a clock expires. It needs a backend on v8.4.2 or later. See [EXPERIMENTS.md](EXPERIMENTS.md) for its end conditions and a smoke-test command. Besides `complete`, `no_action`, the epoch cap, grace and wall-clock endings, a trial ends `stalled` when the backend hands control back after three turns in a row ending `repeated_rejection`.

From the workspace root, verify changes with:

```powershell
./t-scan/.venv/Scripts/python.exe -m unittest discover -s t-scan/live -p 'test_*.py'
./t-scan/.venv/Scripts/python.exe Tools/verify_project_boundaries.py
```

Boundary output is written to `t-scan/runtime_data/verification/project-boundaries.json`. Neither command wakes Steve or starts a navigation trial.
