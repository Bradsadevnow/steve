# Steve architecture

## Cleanup ownership and persistence

`combat_rules.resolve_attack` computes a proposed admitted/rejected effect without
mutating actors or targets. `grid_world.py` remains the sole writer and rolls back
failed saves. `training_targets.py` initializes passive targets and retains HP on
unchanged placements across unrelated world edits. A new run intentionally
initializes its targets. No enemy levels, scaling sheet or controller is implied.

Character visuals cache by body/equipment rather than resource values. Named
preview studios own their render targets and temporary materials; shared cleanup
traverses the viewer's hierarchy so `DontSave` objects are reclaimed on reload.
Catalog meshes remain shared and are never destroyed by an unsuccessful lookup.
See [CLEANUP_REVIEW.md](CLEANUP_REVIEW.md) for verification and open work.

## Additional bodies and world presentation fixes — 6 November 2026

Body selection now includes Duelist (`hand_L`, `hand_R`, `horn`) and Mantle
(`shoulder_L`, `shoulder_R`, `horn`), for seven bodies total. Hands are standard
tool sockets, shoulders are utilities and horns are focus sockets. Duelist has a
right-primary two-hand pair; Mantle has no hand mounts. Body geometry does not
grant stats, actions or a larger collision footprint. Source/export metadata lives
under `t-scan/art/unicore/starter_chassis/`; both local catalogs and the mesh blob
include the new bodies. Existing equipment catalog v2 remains compatible.

Watch camera input gates on actual `CharacterBuilderVisible`, not the remembered
Character workspace selection. Returning from Character to Watch permits camera
gestures while retaining the last workspace preference. `GridWorkbench` recovers
its owned target-label objects after reload, removes duplicates and cleans them
up on destruction. HP remains measured backend state.

Watch draws the published world: closing Build clears only the visual draft
override. Reopening Build restores its saved draft. A shared draft-initialization
path prevents an immediate post-reload Build toggle from replacing cached edits.
Draft geometry suppresses HP labels for deleted/replaced/moved preview targets;
it does not delete authoritative targets or publish the draft automatically.

`WorldMinimapView` is a read-only Watch projection of measured board dimensions,
obstacles/hazards, flags, Steve and target HP state. North is up. It marks cached
state stale when disconnected and reports an unapplied world draft separately.
Its top-right steel frame uses the pack's `Panel_rect_40_empty` artwork, copied
locally as `Resources/UI/FantasyArt/board_41.png`, fitted at authored proportions
around a square grid. Inspecting the map cannot move Steve, edit a world or tick time.

## Authoritative starter stats and scaling — 6 November 2026

Current condition `shared-chat-v8.8.0-character-stats` and equipment catalog v2
replace flat damage and the active affect path. `character_stats.py` owns source
attributes/resources, `character_mechanics.json` owns module bonuses/abilities,
`combat_rules.py` evaluates trusted integer curves, and `character_rules.py`
validates/composes the sheet. `grid_world.py` still alone writes position and
commits world effects. Unity and Steve's inference consume public projections;
neither can submit arbitrary stats or damage. Enemy state remains world-owned.
`world_perception.py` projects measured entities for the agent, retaining stable
target IDs, positions, HP and curated names while omitting art prototype IDs.

Base attributes are all 1; sword +2 STR, shield +2 CON. HP/MP are 10/10 initially.
Slash equals STR; Bash is max(1, floor(CON/3)). Starter pair yields STR/CON 3,
Slash 3 and Bash 1. Maximum HP is 10 + (effective CON − 1), so the shield gives
12 max HP. Capacity increases do not heal; decreases persistently clamp current
HP, preventing swap healing. MP stays 10. Resource rules are versioned separately
as `steve-resources-v2-con-hp`. Other attributes have no new starter actions.
No XP, temporary-effect semantics or autonomous enemy AI is implied.

Private `character.stats` persists source values; public `character.sheet` includes
revision, resources, stat breakdown and evaluated abilities/rule versions. Gear
Apply, restart and New Chat preserve current resources. Validated module instances
stack bonuses once each; multiple copies do not grant extra turns. Receipts retain
scaling stat, effective value, coefficients, versions, nominal/actual damage and
target HP/tick evidence. Saved v1 loadouts migrate explicitly once to v2 with a
character-revision bump; the run and authored continuity are preserved.

Read-only `POST /character/preview` accepts character ID, expected revision,
catalog version, body ID and equipment. It uses the same evaluator as Apply,
returns a marked preview, and cannot write state or advance time. The Character
builder displays proposed effective values and ability damage, discarding stale
responses. The HUD remains bound to confirmed state. Legacy v1 presets are
upgraded to a clearly identified review draft before Apply.

Active worker appraisal calls, decision-context affect fields and Unity body
affect polling are removed. Historical records and legacy appraisal formatting
remain for audit compatibility; `/runtime` marks its old projection retired.
Identity, curated sources, memory, Self, tasks, native tool IDs and Stop are intact.
The earlier UI-only notes below describe the state before this conversion.

## Compact character presentation — 6 November 2026

`CharacterHudView.cs` replaces the old Steve shell card with the corner pane and
bounded, scrollable sheet. `CharacterPresentation.cs` projects confirmed character
data and formats draft equipment/capability differences; it does not calculate
combat stats or write game state. `CharacterPortrait.cs` renders only confirmed
body/equipment on a dedicated cosmetic layer. The portrait studio and texture are
disposed when the view is rebuilt or destroyed. `ShellUI.cs` only supplies fresh
snapshots/status and handles navigation. The shell is above builder UI so the
sheet remains interactive; decorative bar subtrees ignore input.

The pane uses the pack's uniformly fitted board 31 and native red/blue linear
resource controls, with locally copied UXML under `Resources/UI/CharacterHud`.
Artwork dependencies stay in this Unity project. No resource callback writes HP,
damage or time. Missing/invalid resources display unavailable; actual zero HP is
distinct. Disconnection keeps cached confirmed character values and marks them
stale. Expanded sheet state and UI inspection do not enter agent context.

An optional read-only `CharacterState.sheet` projection is reserved for a future
versioned character sheet (`revision > 0`, level, resources, attribute breakdown).
Python does not currently emit it: the live UI shows dashes for RPG values. This
is a frontend binding shape, not a claim that the stats backend contract has
shipped. Do not populate it from affect or infer values from the visual loadout.

Character Build has a collapsible draft comparison: changed modules/body plus
gained/lost actions, evaluated from validated trusted module definitions. Invalid
mount drafts show the error without claiming new abilities. Numeric stat previews
still require the future authoritative evaluator; there is no UI-owned formula.
The existing accepted loadout remains the pane's source while drafts are edited.

## Equipment and fantasy interface — 6 November 2026

The current UI adds `Resources/UI/fantasy.uss` to the existing shell/builder
layout sheets, using local Fantasy RPG UI Pack artwork. Build has World and
Character workspaces. `CharacterBuilderUI.cs` owns the operator draft, presets and
RenderTexture preview; `CharacterCatalog.cs` supplies body/module art and mount
compatibility. Original Hover, Uni-Core, Skimmer, Bulwark and Wisp are selectable.
Presets live in `Application.persistentDataPath/Characters/`, separately from world
saves. Body swaps retain unresolved equipment and block Apply until it is resolved.
Quick click places; half-second left hold/drag rotates; right/middle pans; scroll zooms.

Python `character_rules.py` loads trusted `character_catalog.json`. Its Unity copy
and meshes are generated by `t-scan/art/unicore/export_character.py`. Five bodies
and twelve modules are included. Only sword/Slash and shield/Shield Bash grant
combat actions; other equipment is explicitly a visual prototype with no spell or
stat progression implied.

`POST /character/apply` checks stopped/settled state, no active/queued inference,
expected character revision, catalog version, body sockets, mount types and
multi-socket conflicts. Clients supply choices, not damage values or tool schemas.
Character configuration and bounded idempotency receipts commit together in
`grid-world.json`. The append-only journal and SQLite remain separate commits.
`GET /character/catalog` and `/character/state` expose definitions/configuration.
The confirmed receipt is authoritative; preview state is not.

Equipment and loadout revision are supplied in current observations and receipts.
Equipped attacks register only in executor phase. A changed loadout invalidates a
prior handoff for agent review. Cardinal moves remain four zero-argument, one-cell
tools; combat tools take exactly a measured `target_id`. One tool per response and
operator Stop remain in force.

Unity-authored `bosses_dummy_unarmed`, `bosses_dummy_melee` and
`bosses_dummy_ranged` placements become stationary 10 HP training targets. They do
not retaliate. Slash deals 3 adjacent cardinal damage. Bash deals 1 through a clear
cardinal lane to a target within 3 squares, ending adjacent. Position, HP and game
tick commit in the world snapshot before cosmetic presentation acknowledgment.
Defeated training models remain blocking scenery; further attacks are rejected.
Rejected schema/range/lane/unequipped requests spend no tick. Admitted movement,
including physical wall/boundary bumps, and attacks spend one tick. Thinking, chat,
memory, task edits and operator loadout changes spend none. Inference epochs are
scheduler telemetry, not combat turns. New chat preserves equipment and resets
run-local dummy HP/game ticks; archived world snapshots retain equipment revisions.

World Apply waits for backend confirmation before marking the draft clean or
saving it. Rejected definitions are not silently revised/repaired. See the
[implementation plan](UI_CHARACTER_BUILDER_PLAN.md) and experiment notes.

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

## Enemies and bosses in worlds

The `actor` role is now placeable. Actors are static, blocking pieces that live in `obstacles` (they have no behaviour yet; combat is still being designed). A catalog entry may carry `footprint` (1 or 3; only actors may be 3): a footprint of 3 covers the 3 x 3 cells around the placement's anchor. `world_manifest.py` expands footprints to cells, rejects overlap, edges, spawn, flags and props inside them, and counts every covered cell in the reachability check. `world_manifest.expand_obstacles` gives `grid_world.py` one entry per blocked cell, so movement, `visible_obstacles` and the model's OBSTACLES lines all see the whole footprint. The Unity builder mirrors the rules (`WorldBuilder.cs`) and shows actors under an "Enemies" tab with thumbnails; a 1 x 1 piece cannot be put on a boss, and a boss cannot be put on other pieces ("erase it first").
