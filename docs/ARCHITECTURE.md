# Steve architecture

## Ownership

Unity authors `TScanViewer/Assets/Resources/Meadow/World.asset`. The scene-owned `MeadowEnvironment` renders it without backend-authored flag placement. Python validates the published manifest. `grid_world.py` alone commits logical positions; Unity animates those effects and acknowledges settled presentation. Animation cannot select or change the authoritative destination.

The model chooses actions and manages its own goals. The backend validates, stores, and returns receipts. It does not infer a route, create goals, advance tasks, or certify task completion claims. The authorization hook is injectable; Warden is not integrated.

## Runtime modules

| Module | Owns |
| --- | --- |
| `bridge.py` | Loopback HTTP interface and launch wiring |
| `grid_worker.py` | Serialized inference, human interruption, continuation scheduling |
| `grid_world.py`, `world_manifest.py` | Position, action admission, presentation handshake, manifest validation |
| `grid_conversation.py`, `context_records.py` | Durable native-role conversation and escaped harness records |
| `grid_context.py` | Model-facing current observations, historical evidence projection, memory selection |
| `movement_tools.py` | Exactly four zero-argument cardinal tools and `complete()`, plus task tools |
| `agent_task_list.py`, `agent_notepad.py` | Agent-authored task edits and legacy notepad storage compatibility |
| `runtime_store.py` | Authored memory, simulated affect, chat events, SQLite working-page audit |
| `lmstudio_client.py` | Provider messages, streaming tools, usage and separate reasoning capture |
| `run_archive.py`, `atomic_json.py` | Run snapshots, reset, operator notes, configuration records, atomic JSON writes |

There is one inference connection. No native model loader or activation-capture code is imported by the meadow runtime. The original activation-research scripts live under `t-scan/research/scripts/` and have separate dependencies.

## Movement and tasks

Positions presented to the model use x=1..10, y=1..10. East/west change x; north/south change y. Internal persisted col/row fields remain compatible with existing saves and Unity messages. `move_north`, `move_south`, `move_east`, and `move_west` take no arguments. At most one tool call executes per decision. `complete()` ends the loop; human messages wake it. Text-only responses explicitly idle. The operator can Stop.

Steve authors task IDs, titles, order, and statuses. `task_list_write(task_id, title, status, expected_revision)` adds or updates one task while preserving others. `task_list_read()` reads the list. `task_mark_complete(task_id, expected_revision)` records Steve's assessment. Revision conflicts and malformed requests return actionable errors; rejected arguments are not silently repaired. Statuses are claims, not measured facts. The legacy SQLite notepad page and audit remain independent of authored long-term memory; old prose is retained without parsing it into goals.

## Context and evidence

Keep instructions, human messages, desired outcomes, current observations, action results, authored plans, historical memory, and simulated affect distinct. Use native message roles and tool-call/result IDs. Serialize arbitrary content so it cannot close a trusted record. Preserve provenance and observation IDs; current and historical state must be labeled separately.

The final provider payload is the verification target. Formatting in source code is insufficient. Inspect representative assembled messages after any context change. Record prompt version/configuration changes; do not silently change experimental conditions.

Provider reasoning is captured as model-generated explanation, separately from conversation and memory. It is not proof of internal causes. Requests, raw stream payloads, interpreted reasoning, receipts and state snapshots are retained under `runtime_data/runs/`. New chat never reinjects archived runs.

## Iris concepts

Future work can adopt context projection, memory-channel separation, state-owner boundaries, and atomic evidence records from Iris independently. No Iris package is imported and no additional mechanism is claimed as implemented by this cleanup.
