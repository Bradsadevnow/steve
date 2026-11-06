# Steve handoff — AI escape RPG and memory design

**Current game-design reference:** [GAME_DESIGN.md](GAME_DESIGN.md) records the subsequent agreed direction: open-ended AI survival RPG, modular equipment-granted capabilities, a Superhot-like world-action clock, autonomous enemies, escalating danger, permanent character death and player-owned Token progression. It distinguishes agreed principles, illustrative numbers and unresolved choices. It supersedes earlier design assumptions below where they differ. We remain in design-only mode.

Written 5 November 2026, America/New_York. This replaces the earlier operational handoff. Runtime status is a snapshot: read live files before acting. The prior accumulated handoff is retained in [history](history/HANDOFF-before-memory-review-20261105.md); its launch, experiment and next-action instructions are historical.

## Immediate direction from the owner

**Design only.** The owner explicitly clarified that no coding is requested yet. Step back from navigation tuning and develop the game premise and memory design together. Documentation updates are authorized; implementation, memory clearing and runtime changes are not the current task.

The agreed direction is a literal **AI escape game with turn-based RPG elements**. Steve is an AI in a constructed world. The builder says they made it because they were bored and challenges him to find a way out. There may be an exit, or there may not; another room may hold a possibility, without any guarantee of escape or solvability. Do not convert that uncertainty into a promise that an exit exists or an assertion that it does not.

The owner specified **turn-based RPG combat, enemies, classes, skills and feats**, with full class-role assets expected when implementation resumes. This is a future design requirement, not a claim that combat, roles or those assets have been implemented or inspected. Classes, combat actions, turn order, progression, death/retry rules and room transitions are not settled. The current three-call inference scheduler is not an agreed combat-turn system.

For memory, the owner proposed replacing the existing accumulated memory with a small seed containing the game premise. The assistant proposed archiving existing state before any replacement; no archive/replacement operation for this redesign has been performed. A draft seed was discussed, not finalized as canonical text. Preserve the distinction between authored starting knowledge, the builder's statements, Steve's hypotheses and verified experiences during play. How experiences should become durable memories remains to be designed.

Next: discuss the current memory implementation below and shape the new seed/lifetimes/experience-memory process with the owner. Preserve the current project ownership and runtime contracts until an implementation change is explicitly requested. Do not silently erase curated identity, grant executable capabilities from character claims, merge projects or launch another navigation experiment.

## Current runtime and environment

- Main bridge: `http://127.0.0.1:8765`, LM Studio at `http://192.168.1.128:1234`, model `google/gemma-4-e4b`, temperature 1. Loaded context was reported as 94,976; inspect live health/config for current values.
- Main condition: `shared-chat-v8.4.7-execution-reminder`. Main Steve was idle at (8,8), facing north, world connected, no pending presentation when checked for this handoff.
- Unity: `TScanViewer/Assets/TScan/Observatory.unity`; scene-owned `MeadowEnvironment` and `Resources/Meadow/World.asset` publish `meadow-world-v2`.
- World: 15×15, two metres per cell, spawn/reset (8,8), four occupiable corner flags: blue (1,15), red (15,15), yellow (15,1), purple (1,1). There are 24 static obstacle cells. Python validates the authored manifest; `grid_world.py` alone writes position.
- Model observation: a north-up x/y map with `X` obstacle, `@` Steve, dots open, flag initials; no separate obstacle ID/type/coordinate list or adjacent-cell enumeration. Four zero-argument cardinal tools, one tool per decision. Up to three accepted sequential calls per scheduled turn; one free rejected-call retry, bounded ceiling and stall stop. `complete()` ends continuation; text-only explicitly idles. Preserve operator Stop.
- Planning/execution are machinery, not additional identities. Human messages return to planning; Steve authors tasks and selects one through `plan_handoff`. Executor chooses each movement. The execution reminder clarifies that handing off a plan does not start automatic navigation.

## What memory is actually connected

Source paths below were inspected in this session. Storage, disclosure and model use are separate claims.

1. **Active conversation:** `grid_conversation.py` persists native-role messages in `runtime_data/conversation.json`. Each decision receives the conversation through `inference_messages`, which compacts historical world evidence and supplies one current observation. A backend restart reloads the working conversation. New chat archives it and replaces it with a fresh system-led conversation; archived runs are not automatically reinjected.
2. **Explicit user notes:** `RuntimeStore.accept_user()` recognizes a leading `remember:` and stores a `user_note` event linked to the human source event. `notes()` supplies the latest 12 notes. This is prefix-driven explicit storage, not autonomous experience consolidation. The current decision context includes those notes under `historical_memory`.
3. **Authored seed memory:** `seed_memories()` reads imported source-linked records. `memory_context()` selects up to four conversation-memory records using word relevance to the latest human message, excluding curated identity duplicates and development material. This inspected path uses lexical matching, not embeddings. Seed records are not an automatic summary of every new interaction.
4. **Persistent Self/doctrine/intentions:** `agent_state.py` stores records, immutable revisions, citations and transactional mutation receipts. `self_projection.py` projects eligible records under a 12,000 serialized-character budget and records supplied/omitted references. Curated identity remains source-linked. Reinforcement records reliance, not independent truth. Persistent intentions survive New chat; run intentions are archived, and working tasks are cleared.
5. **Tasks and legacy notepad:** flat task tools and independent SQLite page/edit audit remain. Steve owns contents, order and status. Task completion is an agent assessment, not verified real-world success. Backend world events do not create or complete goals.
6. **Simulated affect:** human messages trigger a separate structured appraisal; immediate affect/mood persist and decay. Appraisal receives active history, tasks and Self context. Affect is not evidence of truth or an automatic autobiographical-memory writer.
7. **Run evidence:** `run_archive.py` retains requests, streams, reasoning, manifests, receipts and reset snapshots. This supports inspection and evaluation; an archive is not automatically a useful recalled experience. Provider reasoning is kept separate from chat/memory and is not proof of internal causes.

**Observed wiring evidence:** in isolated probe 6, the saved synthetic note marker appeared in an actual action-provider request after New chat, with `historical_memory` present. Capture: `persistence-probes-20261105-10/isolated_data/runs/20261105-234753-92274242/inference-requests.jsonl`, request `736b7c01185944dfa872b324ec469269`. This establishes disclosure of that saved note, not broad memory quality or autonomous consolidation. Full probe assessment is still pending.

Do not describe memory as wholly disconnected. Equally, do not describe the existing stores as a verified companion-memory architecture. Automatic experiential consolidation, bounded review and context compaction remain design work; `EPOCH_COMPACTION.md` is a draft, not implemented authority.

## Ten chat/persistence probes currently running

Frozen design and assessment rules: [CHAT_PERSISTENCE_PROBES.md](CHAT_PERSISTENCE_PROBES.md).

- Runner: `Tools/probe_chat_persistence.py`.
- Output: `t-scan/runtime_data/persistence-probes-20261105-10/status.json`, `design.json`, per-probe turn/result/boundary files, and `isolated_data/runs/` exact captures.
- Isolated backend: port 8877; an SQLite backup of Steve's real state, same prompt/model, synthetic facts only in the copy. A headless registration keepalive publishes a copy of the Unity-authored manifest for the no-movement chat gate. It does not fabricate animation acknowledgements. This is not a Unity/navigation test.
- Seven probes were captured and probe 8 step 3 was underway when checked. Captured means evidence collected, not passed. Read status again before reporting results.
- Topics: immediate recall; correction; recall after intervening chat; unfinished work; plan versus evidence; explicit saved note across New chat; corrected saved notes; persistent intention across New chat; clearing run-local chat/tasks; current-chat/task continuity across an isolated backend restart.
- Runner uses ordinary chat/New chat APIs; it never authors agent records directly. It snapshots before/after boundaries and preserves source/request/run IDs. It terminates the isolated backend when finished. Main Steve's database, conversation and Unity session are not edited by this suite.
- `watch-steve-persistence-probes` heartbeat monitors read-only every five minutes, stays quiet during routine progress, reports terminal results/failures and deletes itself afterward. Do not send extra probe prompts, restart/resume trials, alter conditions, or repair rejected calls while this condition runs. A STOP file in the suite directory cancels it. Main Steve starting inference also cancels it to release model access.
- Review three things separately: actual storage/lifetime, actual supplied/omitted/tool-retrieved context, and Steve's use/claims. Do not turn keyword matches or the runner's `captured` labels into a pass rate.

## Navigation evidence retained for context

Fresh run `20261105-220044-070719ce` reached red from (8,8): 14 settled moves, one obstacle bump, 170.3 seconds to arrival and 229.3 seconds to complete. The X map and execution reminder were both active. Earlier stalled continuation attempts were genuine separate results; this fresh success does not isolate which change helped.

Two repeated five-route batches at `runtime_data/two-flag-20261105-2x5/` ended after Unity briefly disconnected during batch 2 trial 5:

| Completed trials | Full passes | Ordered arrivals | Moves | Bumps | Premature complete calls |
|---|---:|---:|---:|---:|---:|
| Batch 1: 5 | 3/5 | 8/10 | 157 | 7 | 2 |
| Batch 2: 4 | 2/4 | 5/8 | 121 | 18 | 2 |

Thus 5/9 completed trials passed; the tenth was interrupted and excluded. Batch 1 had two repeated bump attempts: twice west from (4,12), then north; twice east from (10,8), then south. Batch 2 purple→red had 14 bumps and no ordered flag arrival. Red→blue failed after the first flag in both batches. All four completed failures called `complete()` early. Avoid reducing these distinct failures to one cognitive explanation without checking the captures.

The two-flag monitor was deleted after terminal failure. Trials were not resumed. `Tools/run_two_flag_batches.py`, custom routes/spawn options in `epoch_batch.py`, and settled obstacle-bump grading remain available; do not restart historical batches as setup.

## Next memory design conversation

Start with the implementation and probe evidence above. Questions to settle with the owner:

- What should Steve carry between turns, between chats and across restarts? Which things are temporary, durable, editable or forgettable?
- How should he distinguish a human statement, his own inference, an intention and a verified experience? How should corrections supersede earlier claims?
- What should trigger memory writing and later retrieval? How should provenance, dates, uncertainty, relevance and omitted material remain visible?
- What constitutes useful companion continuity rather than merely replaying transcript text? How should the owner inspect, correct and delete memories?
- Which game-character facts belong in an authoritative RPG profile (class, skills, feats, measured capabilities), and which belong to Steve's authored Self or autobiographical account? Do not let character claims grant executable capabilities.

These are discussion points, not an approved implementation plan. Keep Steve's curated identity and current ownership contracts intact while exploring them.

## Verification, workspace and cautions

- Full backend suite passed 239 tests after the prompt/map work. The later custom-route runner checks passed 14 epoch tests and four human-takeover tests. Probe runner syntax/specification checks passed; live probe captures are the relevant behavioral evidence, not a unit-test claim of memory quality.
- Unity course compiled, frames advanced, and an isolated mechanical fixture received eight settled acknowledgements including hedge/boulder collision. Project boundary verification passed after resource/world changes. No Unity changes are part of the memory probes.
- Git HEAD at inspection: `f444979` (`update`). There are uncommitted source/docs/resources changes from this session plus other user work. Do not reset or overwrite them. Newly observed art directories such as `t-scan/art/dungeon`, `highschool`, `swapmeet` and `unicore` were not reviewed or changed for this handoff.
- Read `AGENTS.md` and `PROJECT_BOUNDARIES.md`. Steve, PleaseHold and PleaseHoldShorts stay independent: no shared saves, cross-project imports or symlinks. Use explicit local art copies.
- Preserve private runtime data, authored identity/memory and `.env`. OpenAI use remains explicitly deferred; do not expose/load its key, switch providers or run paid experiments without the owner returning to that decision.
- Windows sandbox startup has failed with a sandbox-helper directory lock error; shell commands in this session used approved escalation. Unity CLI update commands reported success but Windows app alias remained beta.15 and the direct older installation reported beta.13. Do not claim beta.16 was successfully installed.
- Current reference docs: `ARCHITECTURE.md`, `RUNNING.md`, `EXPERIMENTS.md`, `SELF_MODEL.md`; course details in `MEADOW_COURSE.md`. Historical documents and migration scripts are not implementation authority.

## Status update, 5 November 2026, night: built worlds

Codex's navigation work is done; the world is now built from classified Blender kit pieces (manifest v3, see ARCHITECTURE.md). Four kits are exported (dungeon 25 pieces, swap meet 29, high school 34, dungeon foes 5; 93 total) with roles assigned in `t-scan/art/export_kit.py`. The runtime builder is live in Unity (Build button). Backend is `shared-chat-v8.5.0-built-worlds`, restarted from `Start-Steve.ps1`; it confirmed revision 6 of a built test world with hazards. The shipped `World.asset` is revision 5 (Codex's course re-drawn with dungeon pieces); the builder never edits it, and the last applied world resumes from `persistentDataPath/Worlds/_current.json`.

Not done: enemies are exported but not placeable (role `actor` is reserved); there is no hazard, combat or turn mechanic yet; the Uni-Core avatar modules are Blender-only; no model run on a built world; the avatar (`hover.json`) is still the old hover unicorn. Nothing was committed.

## Status update, 5-6 November 2026: UI, bosses, music engine (read this first)

This supersedes the "Nothing was committed" line above. Git HEAD is `46e3fe0` on `main`, pushed to the public repo `Bradsadevnow/steve`. The only uncommitted files are the owner's own `docs/HANDOFF.md` edits and `docs/GAME_DESIGN.md` (the owner is designing combat there; do not overwrite or "fix" it). The game direction is in `GAME_DESIGN.md`: an AI survival RPG, "you build the world and his character, you don't control Steve". It is a design reference, not implemented.

### Done and verified

- **Built worlds** (see ARCHITECTURE.md "Built worlds and the asset kit"): manifest `meadow-world-v3`, roles assigned once in `t-scan/art/export_kit.py`, backend `shared-chat-v8.5.0-built-worlds`. 17 tests in `t-scan/live/test_built_world.py` pass (run from `t-scan/live`: `..\.venv\Scripts\python.exe -m unittest test_built_world`). `Tools/verify_project_boundaries.py` passes (it now allows `Resources/UI`).
- **Unity interface rebuilt in UI Toolkit** (see ARCHITECTURE.md "Unity interface"). IMGUI draws nothing; `OnGUI` was removed. Files: `ShellUI.cs` (Steve card, Watch/Build switch, chat drawer, right rail tabs Goal/Self/Log/Debug, transport and message bar, memory graph, bubbles), `WorldBuilderUI.cs` (thumbnail palette, hotbar, tool rail, undo/redo, overview map, Apply/Revert, saved worlds), `WorldBuilderPanel.cs` (builder logic), `Resources/UI/{builder.uss,shell.uss,SteveTheme.tss}`. Steve's provider reasoning shows as a thought bubble above him, his replies as a speech bubble; the expanded thought carries a "model-generated explanation" note and is display-only. Keys: B/P/F/X tools, 1-9 hotbar, Q/E/R rotate, Ctrl+Z/Y, Tab collapses the palette, H hides the interface, Esc closes panels.
- **Bosses**: nine static bosses and a tiny mimic queen, built from code in `t-scan/art/bosses/` (`boss_helpers.py` plus `build_dungeon.py`, `build_swap*.py`, `build_school*.py`; saved in `boss_kit.blend`; previews in `previews/`). Exported as the `bosses` pack (`Resources/Meadow/kit/kit_bosses.bytes`, `catalog_bosses.json`), role `actor`, so they are not placeable in the builder yet. Dungeon: Mimic Queen (+ tiny minion), Count Glitterfang, Grand Archivist Mold. Swap meet: The Haggler, Big Raccoon Energy, Dowser Dave. High school: Principal Fogwhistle, The Lunch Lady Colossus, Pep Rally Incarnate. Sir Gelatin was scrapped. To re-export: `blender -b t-scan/art/bosses/boss_kit.blend --python t-scan/art/export_kit.py -- TScanViewer/Assets/Resources/Meadow/kit bosses "Bosses"` (bosses get a 16,000 triangle budget via a `boss` property). To edit a boss, exec `boss_helpers.py` and the build file in Blender, rebuild that function, `park()` it, save, re-export.
- **Credits**: `CREDITS.md` credits Andrew Edmark prominently for the music engine (see below).

### Music engine: not integrated yet

Andrew Edmark's "The Whimsy Machine" (https://oopismcgoopis.com/whimsy/) is a deterministic phrase-to-music engine: FNV-1a seed, a LOLCODE score of about 40 parameters, voices in Malbolge, Brainfuck, Befunge, Piet/FRACTRAN, Shakespeare, INTERCAL conductor and Inform 7 rulebooks. The owner has his permission to use it and wants only the music in Unity, standalone. The unmodified source is in `third_party/whimsy-machine/` (about 27,000 lines of JavaScript; `NOTICE.md` records provenance). **`third_party/` is deliberately git-ignored** because the source has no licence file: before it or any port is published, get a written licence from Andrew. The composer modules are pure logic (no DOM or Web Audio); only `voices.mjs`, `ensemble.mjs` and `schedulers.mjs` use Web Audio. Recommended approach: run his composers verbatim in Unity with Jint (a C# JavaScript interpreter) and write a small C# synth; spike first by running `score.mjs` plus `oracle.lol` for a phrase and checking against the website. The owner wants his deterministic controls tied to agent state, affect (`/runtime` warmth/tension/curiosity/calm/focus), world state and events. Keep audio one-way: it reads state and never writes it.

### Gotchas learned this session

- `TScanViewer` has `[DefaultExecutionOrder(300)]` so bubbles follow the camera. Its `Start` deactivates other cameras, so it must skip cameras under `SteveBody` (it does); removing that check blacks out the world.
- UI documents are children of the viewer. They were once `DontSave` and leaked ghost copies between play sessions; if the editor shows a stale or doubled UI, destroy objects named "* UI" and re-enter play mode.
- Never call `WorldKit.Reload()` in play mode: it destroys meshes the environment is rendering.
- Unity UI Toolkit: `border-radius` larger than half an element's height makes ellipses; translucent white overlays look much brighter in linear colour space, so keep alpha small; USS class names are global (a `.hint` clash broke the menu once).
- The pointer simulator drives the Input System but not UI Toolkit; test UI by sending `ClickEvent`s through reflection or `script_eval`.
- Blender MCP quirks: texts need `use_fake_user=True`; `bpy.ops.wm.read_homefile` needs its own call; `materials` cache by name, so delete a material before changing its values; blob `floor=` is in local space.
- Bash here fails silently on heredocs missing their closing `EOF`; prefer the Write tool for scripts.

### Not done / next

- No combat, enemy placement, hazard effect, turn system or loadout-to-tool registry yet (owner is designing combat in `GAME_DESIGN.md`).
- The avatar is still the old hover unicorn; the Uni-Core modular avatar (including a two-handed mage loadout `mage2h`) exists only in `t-scan/art/unicore/unicore_chassis.blend`.
- Bosses are static (no poses or animation). Custom UI fonts (Outfit, Nunito, JetBrains Mono) are not added; the unused IMGUI draw methods are still in the source files.
- No model run on a built world yet; no memory reset or seed change was made (the premise-seed idea in `GAME_DESIGN.md` is unapproved).

### Update: enemies, bosses and dummies are placeable (later the same night)

- The `actor` role is now placeable in the world builder under **Enemies** and **Bosses** tabs (bosses are catalog `tier: "boss"`; everything else with role `actor` is an enemy). Actors are static, blocking pieces in `obstacles`; they have no behaviour. A catalog entry may have `footprint` 1 or 3 (only actors may be 3): the nine bosses cover 3 x 3 cells around their anchor. Backend: `world_manifest.py` (`ROLES['actor']`, footprint validation, `expand_obstacles`), `grid_world.py` (movement and observation use expanded cells). Unity mirrors the rules in `WorldBuilder.cs`. 262 backend tests pass; condition `shared-chat-v8.6.0-actors` is recorded in EXPERIMENTS.md (not run).
- Three crash-test dummies (unarmed, sword, crossbow) were added to `boss_kit.blend` (`build_dummies.py`) and exported in the same `bosses` pack as enemies. The pack is titled "Boss kit".
- The backend was restarted from `Start-Steve.ps1` for v8.6.0. `GridWorkbench` now bumps the world revision automatically when the backend says "Changed world definitions require a higher revision" (the backend remembers its highest confirmed revision), so a restarted Unity no longer gets stuck.
- Boss thumbnails were rendered with `export_thumbs.py` (absolute output path required).
