# Navigation experiments

`t-scan/live/transit_batch.py` runs ten fixed three-flag requests, capped at 300 seconds each. Steve chooses every movement and task edit. The runner grades ordered exact-cell arrivals from settled world receipts, archives each run, and resets between trials.

From `t-scan/`, with idle inference and connected Unity:

```powershell
./.venv/Scripts/python.exe live/transit_batch.py --output runtime_data/<new-batch-name> --data-dir runtime_data --seconds 300
```

Choose a new output directory; existing batches are never overwritten. Operator Stop, a batch `STOP` file, inference failure, or lost Unity connection halts the batch. A live Unity poll must be no more than three seconds old. A transient polling gap can therefore interrupt an otherwise valid trial. Do not automatically resume a failed trial.

Results live in each batch's `status.json`; per-run requests, reasoning, settled receipts, task edits and configuration are under `runtime_data/runs/<run-id>/`. Grade task claims against world receipts, not task labels alone. Preserve ambiguity in task-to-flag mappings. Multiple prompt/interface changes and stochastic sampling limit causal attribution.

The repaired x/y batch `transit-batch-xy-flatwrite-20261103` finished nine trials: eight passes, one timeout, zero boundary blocks. Trial ten was interrupted by the connection check. Its saved status is failed; it is not a ten-trial completed result. The earlier interrupted x/y batch is a separate condition. The task-completion reminder was added afterward as `shared-chat-v7.4-task-completion-reminder` and has not been trialed in that batch.

`verify_unity_world.py` is a separate mechanical presentation check using a fresh data directory and no model. Its fixed movement fixtures are test inputs, not an agent navigation policy. Read its CLI before using it and keep it isolated from Steve's live state.
