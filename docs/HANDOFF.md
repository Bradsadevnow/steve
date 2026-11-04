# Steve handoff

Written 4 November 2026, approximately 2:45 PM America/New_York. Runtime status below is a snapshot; re-read live files before acting.

## Start here

Read `AGENTS.md`, `PROJECT_BOUNDARIES.md`, then this document. Current references are [architecture](ARCHITECTURE.md), [running](RUNNING.md), [experiments](EXPERIMENTS.md), [Self contracts](SELF_MODEL.md), and [three-call turns](SEQUENTIAL_TOOLS.md). Historical archive documents are not implementation authority.

The user's immediate objective is to evaluate three sequential tool calls per scheduled turn on the same ten navigation routes. Leave that experiment unchanged while it runs. The longer-term objective is to connect experience, simulated affect, memory and Self revision through a bounded review opportunity. That review is not implemented or authorized for automatic activation yet.

## Status update, 4 November 2026, evening (supersedes the live-experiment snapshot below)

No experiment is running. The v8.4 timed batch finished with 0 of 10 full passes; the v8.4.1 timed batch was stopped by the operator in trial 7 (six trials archived, no full passes). Results, defects and conditions are in [EXPERIMENTS.md](EXPERIMENTS.md). The experiment-status table further down describes the v8.4 run and is historical.

State on disk, none of it committed (git reported a dubious-ownership error in this environment):

- **v8.4.4 (`shared-chat-v8.4.4-free-retry`)**, written, not yet running: exact all-at-once tool errors, optional `landmark_id` for `manual` handoffs, free single retry with a stall stop, no facing shown to the model. Built after the v8.4.3 ten-route epoch batch (7 of 10 passes); see EXPERIMENTS.md.
- **v8.4.3 (`shared-chat-v8.4.3-goal-and-tasks`)**, ran the ten-route epoch batch: the model records a goal (`intention_write`) and one task per checkable step; refused handoffs say how to add or reopen a task. Built after the epoch smoke test showed an umbrella task and a false `complete()`; see EXPERIMENTS.md. 
- **v8.4.2 (`shared-chat-v8.4.2-phase-aware-rejections`)**, loaded and smoke-tested: phase-aware `complete()` hint, compact x/y recent experiences, epoch counter and context meter in `/health`. The last backend that ran was v8.4.1; restart it to load v8.4.2.
- **Earlier fixes, loaded on the next restart:** loopback origin guard in `bridge.py`, executor error classes (`rejected_store`, `internal_error`), shared `decode_envelope()`, grid-state load guard, actionable rejection messages, and the registered clock-tool bundle with a switchable `clock_actions` counting policy (default off).
- **Epoch runner** `t-scan/live/epoch_batch.py`: built, tested against a fake bridge and smoke-tested on one live route. Next step is a restart on v8.4.3 and the ten-route run (Unity in play mode on `Observatory.unity`, LM Studio serving the model, idle loop).
- **Design drafts, not implemented:** [EPOCH_COMPACTION.md](EPOCH_COMPACTION.md) covers epoch compaction, a Steve-authored review step, a context meter in the model's context, the clock, and an affect/memory roadmap. Its checklist has the open owner decisions. Remaining build order: storage (epoch segments, hashed request log), compaction and review as v8.5, viewer phase/epoch/meter strip (hold Unity edits while a run is in progress).

Verification at this point: 235 tests pass and `Tools/verify_project_boundaries.py` passes.

## Live experiment snapshot (historical, v8.4 batch)

| Item | Current condition |
| --- | --- |
| Version | `shared-chat-v8.4-three-call-turn` |
| Provider/model | LM Studio / `google/gemma-4-e4b` |
| Provider address | `http://192.168.1.128:1234` |
| Sampling/context | Temperature 1; loaded context reported as 131072 |
| Bridge | `http://127.0.0.1:8765` |
| Batch | `t-scan/runtime_data/transit-batch-three-call-20261104-1440/status.json` |
| Scope | Ten fixed three-flag routes; 300-second caps; archived resets |
| Snapshot | Running trial 1, zero archived trial results at the initial handoff read |
| Initial run | `20261104-194015-8b77922b` |
| Monitor | Codex heartbeat `watch-steve-three-call-trials`, every five minutes |

The heartbeat monitors read-only and stays quiet during normal progress. It reports completion, failure, cancellation, missing capture or persistent rejections requiring attention, then deletes itself when finished. It must not restart trials, wake Steve, enable reflection, switch providers or alter inference conditions.

Read `status.json` and the current run's archives rather than assuming this snapshot remains current. Capture lives under `t-scan/runtime_data/runs/<run-id>/`: exact provider requests, raw streams, interpreted reasoning/events, context manifests, run configuration and reset snapshots. Backend logs are `t-scan/runtime_data/logs/backend.stdout.log` and `backend.stderr.log`; batch logs use its batch-name prefix in that directory.

Each trial is externally graded using ordered exact-cell arrivals in settled world receipts. A task marked complete is an agent claim, not proof of arrival. Multiple calls, their rejections, and per-decision evidence must remain observable.

## What changed and what owns it

Steve is the persistent Self-model. Planner, executor and orchestrator are operating machinery, not separate identities. Unity owns the world definition and offline visuals; Python validates that manifest, and only `grid_world.py` commits authoritative positions. Unity presentation acknowledges those effects. Preserve the hovering unicorn, 10-by-10 meadow, four zero-argument cardinal tools and x/y 1..10 observations. No pathfinding or backend-authored flag layouts.

Steve alone authors tasks, changes their statuses and chooses which task to hand off. The backend never selects the next goal or completes goals from world events. Planner tools edit tasks, intentions and Self/doctrine claims; `plan_handoff` explicitly selects an unfinished task, with a reason and criterion. Executor tools choose individual movements and use `request_replan` to return to planning. A separate durable intention is optional, not a mandatory duplicate of each short plan.

Important source files under `t-scan/live/`:

| Files | Responsibility |
| --- | --- |
| `grid_worker.py`, `orchestrator.py` | Human priority, scheduled turns, phase changes, per-decision journal |
| `decision_executor.py`, `lmstudio_client.py` | Tool/result execution boundary and LM Studio transport |
| `grid_conversation.py`, `grid_context.py`, `context_records.py` | Prompt version, escaped records, actual observation/memory projection |
| `agent_state.py`, `agent_state_tools.py`, `self_projection.py` | Self/doctrine/intentions, revision/citation/repair audit, supplied-versus-omitted manifests |
| `agent_task_list.py`, `agent_notepad.py` | Flat task tools and legacy SQLite page/edit audit |
| `self_view.py` | Read-only operator view of Self state, not an author of Self content |
| `grid_world.py`, `world_manifest.py` | World validation, position authority and presentation handshake |
| `runtime_store.py`, `run_archive.py` | Authored memory, affect, chat history, archives and reset |

Self/doctrine mutation records, revisions and receipts are transactional in SQLite. The world uses its own JSON/controller-log state; do not claim cross-store atomicity. Interrupted unresolved decisions return to review rather than blind replay. Reinforcement/citation counts do not establish truth or capabilities. Keep curated identity sources unchanged and source-linked.

## Three-call behavior now active

- At most three sequential tool calls per scheduled turn. Each call comes from a separate model response, after the previous result. Rejected calls consume the allowance. Multiple calls emitted in one response are rejected together and terminate that turn.
- Every movement waits for settled presentation before another decision. Dispatch rebinds to the fresh observation ID. Calls do not accept coordinates or compound routes.
- `plan_handoff`, `request_replan`, `complete()`, interruption, failed presentation and text-only responses are early boundaries. Phase changes return to scheduling to refresh the registry. Exhausting the call allowance yields to scheduling; it does not complete a goal or end the interaction.
- Native call/result IDs, per-decision journal entries and actual provider context manifests distinguish all decisions within a turn. The parent chat request ID remains distinct from subsequent decision IDs.
- Text-only responses explicitly idle even when an earlier decision in the same turn used a tool. This closes a continuation bug exposed by sequential execution.
- No automatic reflection, affect appraisal or memory consolidation happens at this boundary. No token budget has been added. The old eight-call proposal is superseded.

Task tools: `task_list_read()`, `task_list_write(task_id, title, status, expected_revision)`, `task_mark_complete(task_id, expected_revision)`, and new `task_remove(task_id, expected_revision)`. Writing an existing ID edits/reopens that task. Removal preserves prior versions in the audit and does not complete it. Keep actionable schema/stale-revision errors; never silently repair calls.

## Human corrections and the stopped baseline

The previous runner detected a new human request, then its generic failure cleanup sent Stop and interrupted the correction. The received correction is preserved in the interrupted run. Fixed in `transit_batch.py` and `bridge.py`: human takeover cancels batch ownership without Stop; cleanup Stop requests carry `expected_origin_request_id`. The backend checks both loop origin and queued human input under its lock. Operator Stop itself remains unconditional.

Keep these conditions separate:

| Batch | Interpretation |
| --- | --- |
| `transit-batch-self-model-20261104-1840` | Interrupted during trial 1 by human correction and old cleanup bug; zero completed trials |
| `transit-batch-task-remove-20261104-1401` | Operator-cancelled during trial 5; four archived results, all timeouts, 0/4 full passes; ordered progress 2/3, 1/3, 2/3, 2/3; 56 moved steps and zero boundary blocks |
| `transit-batch-xy-flatwrite-20261103` | Older repaired x/y condition: nine completed trials, eight passes, one timeout; trial 10 interrupted. Not a completed ten-trial batch |
| `transit-batch-three-call-20261104-1440` | Current fresh v8.4 experiment; read live status for results |

The older baseline heartbeat was deleted after cancellation. No delayed eight-call activation remains queued.

The comparison scorecard should include ordered task/route completion, time to verified final arrival versus total elapsed, tools by outcome, replans, blocks, loops/stalls, recovery, completion-claim accuracy, explanation quality and consistency across explicit beliefs/plans/tasks/actions. Separate provider latency, presentation waiting, active loops and no-action idle. Use matching routes when comparing the stopped four-trial baseline. State denominators and unavailable measures. Do not infer an ambiguous title-to-flag mapping as fact. Provider reasoning is explanation text, not proof of internal causes; summarize with compact evidence references instead of long transcripts.

## Affect, memory and intended next design discussion

Current affect is 17 simulated dimensions. Each incoming human message gets a separate structured LM appraisal proposing up to three integer deltas in -2..2. A delta changes immediate affect by 0.12 and mood by 0.024, clamped to 0..1. Immediate affect decays toward baseline with a 180-second half-life, mood with an 1800-second half-life; exposed affect blends them 75/25. SQLite persists the state and appraisal event/source references. New chat preserves affect.

Current chat/continuation context supplies labeled simulated affect, retrieved historical memory, tasks, Self projections and measured world evidence separately. Affect appraisal receives recent active conversation, current user input, tasks and a Self projection. World moves, blocked attempts and task completions do not currently trigger affect appraisal. Unity polls/smooths affect values, but the inspected active code has no visual behavior consuming them.

The user explicitly does not want a reward score. Affect is intended as experiential feedback. First evaluate three-call turns; if reliable, consider a review/epoch boundary there. A future design may connect the same receipts to affect appraisal, agent-authored memory/Self revisions and replanning. Do not generate forced lessons, auto-complete goals, treat emotion as evidence of truth, or claim model-weight learning. Distinguish measured episode evidence from Steve's interpretation and affect response. No automatic review is currently implemented.

## UI and naming

The Unity product/app name is now **Steve**. Launch the backend through `t-scan/Start-Steve.ps1`. The user chose branding/launcher changes only: retain `t-scan`, `TScanViewer`, `Assets/TScan`, namespaces and internal identifiers. Do not initiate a folder/code migration.

The full bottom panel displays Steve's provider thinking, with Stop in its header. Right tabs are Activity, Self and View. Self is a single view showing position, selected focus, unfinished and agent-marked finished goals, commitments, authored assessments/beliefs, recent experience and capabilities. The separate Goals view, Run notes, Current run/status area, State/Inspect selector and Details/revision inspector were removed at the user's request. Do not restore curator prose or metadata counters as personality theater. Backend audit/history storage remains intact.

Removed Unity assets: `AgentGoalsPanel.cs`, `OperatorNotesPanel.cs`, `GridDashboard.cs`, with their `.meta` files through the Editor. `SelfModelPanel.cs` is new. Notes backend storage/archive compatibility still exists; removing its UI did not delete private notes or authored memory. New chat still archives the full run, clears working chat/tasks and resets to (5,5), north, while retaining persistent Self/doctrine/commitments and long-term memory.

## Credentials, Git and launch cautions

The user supplied an OpenAI key. It is stored locally as `OPENAI_API_KEY` in `t-scan/.env`, verified untracked and ignored. Never print it, place it in a handoff/capture, commit it or send it to an unrelated provider. **The user explicitly deferred OpenAI use.** The running backend neither loads that file nor uses OpenAI. Do not switch providers, run charged API tests or silently enable the key. Source credential document was left unchanged.

Private remote: `https://github.com/Bradsadevnow/steve.git`. HEAD remains the pre-refactor checkpoint `dcf85fe318c73fa590b7a6f66b8cd5e4d3821a8c`, with tag `checkpoint/pre-self-model-20261104`. The Self architecture, UI work, task deletion, correction fix, branding and three-call changes are **local, uncommitted and unpushed** at this handoff. Do not mistake the remote checkpoint for current runtime source or reset the working tree. Runtime captures, private memory, `.env`, original research and independent sibling projects are excluded from Git.

Git commands may require `git -c safe.directory=C:/Users/bradl/OneDrive/Desktop/steve ...` due workspace ownership. Avoid changing global Git trust settings. When reviewing/committing, include the new modules/tests/docs and preserve intended Unity `.meta` GUIDs; do not add private state. User requested this handoff, not a push.

The backend uses `.venv/Scripts/python.exe -S live/bridge.py`, standard-library runtime, port 8765. It runs hidden with redirected logs. Do not launch a second backend on that port. Restart only after checking inference and loop idle with no queued human turn or presentation; preserve state. Do not restart during this batch. Use Unity tools/CLI for live Editor changes; never hand-edit scenes or serialized assets. No Unity code changed for the three-call feature.

## Verification already performed

- Full backend suite: **137 tests passed** after three-call implementation, including receipt-before-choice ordering, fresh observation binding across settled movements, revision-aware task edits, rejections consuming the cap, phase barriers, multiple-call rejection, interruption, presentation timeout, output truncation and text-only-after-tool idle.
- Real worker fixture verifies six separate decision/context records across planner handoff, movements and completion.
- `Tools/verify_project_boundaries.py`: passed after tool changes.
- Isolated real LM Studio smoke: `Tools/verify_three_call_turn.py`. Three provider requests, three successful task writes, revisions 0 to 1 to 2 to 3, capped at three calls, no world movement. Evidence: `t-scan/runtime_data/verification/three-call-smoke-20261104-193435/`. Actual rendered provider requests were inspected: one current context, native call/results before the next choice, current revisions 0/1/2. This is a smoke, not navigation-success evidence.
- Activation verification: `t-scan/runtime_data/verification/three-call-activation.json`; position, goals and Self records preserved; idle, world connected, v8.4 and limit three confirmed before the new batch started.
- Unity has been compiling cleanly and advancing frames with a connected viewer. UI layouts were visually checked after edits; screenshots are under `runtime_data/verification/`. Branding is Steve; launch script syntax and project boundaries passed. Do not stop Play just to repeat a check while trials run.

Run future source checks from workspace root, without launching model trials:

```powershell
./t-scan/.venv/Scripts/python.exe -S -m unittest discover -s t-scan/live -p 'test_*.py'
./t-scan/.venv/Scripts/python.exe -S Tools/verify_project_boundaries.py
```

`Tools/verify_three_call_turn.py` does invoke LM Studio; do not run it concurrently with a trial. No extra testing is needed just to read this handoff.

## Next operator/agent actions

1. Preserve and monitor the current ten-trial condition. Do not edit experimental conditions mid-run or resume stopped batches.
2. On completion, analyze the scorecard from settled receipts and captured calls/manifests, not just pass/fail. Verify three-call sequencing and phase barriers before attributing differences to model cognition.
3. Discuss whether the three-call boundary is useful for affect-driven review and memory/Self updates. Keep that design separate from the measured condition.
4. Keep OpenAI unused until the user explicitly returns to it. Any provider experiment should be a distinct, recorded condition.
