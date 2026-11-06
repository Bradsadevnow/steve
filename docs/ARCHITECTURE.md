# Steve architecture

The active world is now the [15×15 meadow course](MEADOW_COURSE.md), with four corner flags, 24 blocked obstacle cells and an authored spawn at (8,8). Unity owns placements; Python validates them and reports collision outcomes.

## Ownership

Unity authors `TScanViewer/Assets/Resources/Meadow/World.asset`. The scene-owned `MeadowEnvironment` renders it without backend-authored flag placement. Python validates the published manifest. `grid_world.py` alone commits logical positions; Unity animates those effects and acknowledges settled presentation. Animation cannot select or change the authoritative destination.

Steve is the persistent Self-model. Planner and executor are machinery through which that model operates; the deterministic orchestrator schedules those phases. The model chooses actions and manages its own goals. The backend validates, stores, and returns receipts. It does not infer a route, create goals, advance tasks, or certify task completion claims. The authorization hook is injectable; Warden is not integrated.

## Runtime modules

| Module | Owns |
| --- | --- |
| `bridge.py` | Loopback HTTP interface and launch wiring |
| `grid_worker.py`, `orchestrator.py` | Serialized inference, phase scheduling, human interruption, durable decision journal |
| `grid_world.py`, `world_manifest.py` | Position, action admission, presentation handshake, manifest validation |
| `grid_conversation.py`, `context_records.py` | Durable native-role conversation and escaped harness records |
| `grid_context.py` | Model-facing current observations, historical evidence projection, memory selection |
| `movement_tools.py` | Exactly four zero-argument cardinal tools and `complete()`, plus task tools |
| `agent_task_list.py`, `agent_notepad.py` | Agent-authored task edits and legacy notepad storage compatibility |
| `runtime_store.py` | Authored memory, simulated affect, chat events, SQLite working-page audit |
| `lmstudio_client.py`, `decision_executor.py` | Provider transport separately from one-decision validation, dispatch, and native receipts |
| `agent_state.py`, `agent_state_tools.py` | Persistent Self, doctrine, intentions, explicit plan handoffs, revisions, citations, and mutation receipts |
| `self_projection.py` | Decision-specific Self/knowledge projection and disclosure manifest |
| `run_archive.py`, `atomic_json.py` | Run snapshots, reset, operator notes, configuration records, atomic JSON writes |

There is one inference connection. No native model loader or activation-capture code is imported by the meadow runtime. The original activation-research scripts live under `t-scan/research/scripts/` and have separate dependencies.

## Movement and tasks

Positions presented to the model use x=1..15, y=1..15. East/west change x; north/south change y. Internal persisted col/row fields remain compatible with existing saves and Unity messages. `move_north`, `move_south`, `move_east`, and `move_west` take no arguments. At most one tool call executes per decision. Planning has task/claim/intention tools and `complete`; execution has cardinal movement, bounded record retrieval, `request_replan`, and `complete`. Only Steve selects the task through `plan_handoff`. `complete()` ends the loop; human messages wake it. Text-only responses explicitly idle. The operator can Stop.

Steve authors task IDs, titles, order, and statuses. `task_list_write(task_id, title, status, expected_revision)` adds or updates one task while preserving others. `task_list_read()` reads the list. `task_mark_complete(task_id, expected_revision)` records Steve's assessment. `task_remove(task_id, expected_revision)` removes one task while preserving its prior versions in the edit audit. Revision conflicts and malformed requests return actionable errors; rejected arguments are not silently repaired. Statuses are claims, not measured facts. The legacy SQLite notepad page and audit remain independent of authored long-term memory; old prose is retained without parsing it into goals.

## Context and evidence

Keep instructions, human messages, desired outcomes, current observations, action results, authored plans, historical memory, and simulated affect distinct. Use native message roles and tool-call/result IDs. Serialize arbitrary content so it cannot close a trusted record. Preserve provenance and observation IDs; current and historical state must be labeled separately.

The final provider payload is the verification target. Formatting in source code is insufficient. Inspect representative assembled messages after any context change. Record prompt version/configuration changes; do not silently change experimental conditions.

Provider reasoning is captured as model-generated explanation, separately from conversation and memory. It is not proof of internal causes. Requests, raw stream payloads, interpreted reasoning, receipts and state snapshots are retained under `runtime_data/runs/`. New chat never reinjects archived runs.

## Persistent Self

See [Self model and phase contracts](SELF_MODEL.md). The v8.2 condition added explicit Self ownership, revisioned beliefs, intentions, and phase-specific capabilities. The current `shared-chat-v8.4-three-call-turn` condition permits three sequential calls with feedback and separate decision/context records, while retaining one call per model response. See [turn contract](SEQUENTIAL_TOOLS.md). Model and sampling settings remain unchanged.

Self/doctrine edits, revision history and mutation receipts commit in one SQLite transaction. World position still commits through GridWorld's JSON state and controller log. The decision journal records dispatch intent and receipts, but this is not cross-store atomicity. Interrupted unresolved decisions return to planning review and are not blindly replayed. Historical full-state replay and generalized semantic truth adjudication are not implemented.

## Built worlds and the asset kit

The world is built from classified kit pieces and published as manifest `meadow-world-v3` (v1 and v2 still validate). Unity authors it; Python validates it; `grid_world.py` alone writes positions.

- **Kit.** `t-scan/art/export_kit.py` (Blender's Python, headless) bakes each `PIECE_*` object of a kit `.blend` into one vertex-coloured mesh in `Resources/Meadow/kit/kit_<pack>.bytes`, plus `catalog_<pack>.json`. Emissive materials lower vertex alpha, which `MeadowVertex.shader` draws as glow. Floors are decimated to a triangle budget because they are instanced 225 times.
- **Roles.** A piece's role is assigned once, in the exporter, from its Blender category and `blocks_movement`: `floor`, `wall`, `obstacle`, `structure` (doors block; archways and stairs do not), `hazard`, `decor`, `actor` (reserved, not placeable yet). Curated display names live in the exporter too, because the model reads them.
- **Manifest v3.** `floors` (one piece per cell, row by row from (1,1)), `obstacles` (blocking placements), `props` (walkable placements), `landmarks`, `spawn`, and a `catalog` listing exactly the pieces in use with their role, name and `blocks`. `world_manifest.py` owns what each role means (`ROLES`) and rejects a floor used as a wall, a wall used as decor, a catalog that misstates blocking for a role, two blockers in one cell, a hazard on the spawn or a flag, an unused or missing catalog entry, and any flag that cannot be reached from the spawn. The backend never trusts a role or blocking flag from Unity beyond that table.
- **Model view.** `visible_obstacles` carry catalog `name` and `role`; `visible_hazards` and `hazard_here` are new. `grid_context.coordinate_world` lists obstacles grouped by curated name and role, hazards as walkable cells whose effects are not stated, and marks `X` and `!` on the map. A raw prototype id is never shown in place of a name, and decor is cosmetic and not context.
- **Builder.** `WorldBuilder.cs` owns the draft and the placement rules (mirroring the backend), `WorldBuilderPanel.cs` is the runtime UI (Build button in the world panel). Edits preview as a draft on a runtime copy of the definition, so the shipped `World.asset` is never modified. Apply publishes revision +1, refuses while Steve's loop is running, and is re-validated by the backend. The last applied world is remembered in `Application.persistentDataPath/Worlds/_current.json` and resumed at startup, because the backend refuses a lower revision than it confirmed. Named saves go in the same folder.

## Unity interface (UI Toolkit)

The world camera fills the screen; the interface is two runtime UI Toolkit documents created in code (`ShellUI.cs`, `WorldBuilderUI.cs`) and styled by `Resources/UI/builder.uss` and `shell.uss`. IMGUI no longer draws anything.

- **Shell.** A Steve card (state, position), a Watch/Build switch, chat, camera and menu buttons, a right rail whose icons open one tabbed panel (Goal, Self, Log, Debug), a chat drawer, and a transport and message bar. Data comes from the existing viewer state: `/frame`, `/self-view`, `/history`, `/memory_graphs` and the grid snapshot. Nothing here writes world state.
- **Bubbles.** Steve's provider reasoning streams in a thought bubble anchored above him, with a short trail of earlier thoughts; his replies use a different speech bubble. The expanded thought says it is a model-generated explanation. Reasoning is displayed only; it is not stored in chat or memory.
- **Builder.** Build mode swaps the docks for the tool rail, thumbnail palette, hotbar, overview map and Apply bar. Camera and paint input ignore pointer positions over either document (`OverUI`).
- **Not yet done.** Custom fonts, and removal of the unused IMGUI draw methods.
