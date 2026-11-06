# Navigation experiments

After operator cancellation of the v8.3 baseline during trial five (four archived trial results), the user approved a separate three-call-turn experiment. `shared-chat-v8.4-three-call-turn` changes scheduling to at most three sequential model-selected calls per turn, with settled feedback, separate decision IDs and phase barriers. It adds no reward score or automatic affect/memory review. Do not combine this condition with the stopped baseline or claim the baseline completed ten trials.

`t-scan/live/transit_batch.py` runs ten fixed three-flag requests, capped at 300 seconds each. Steve chooses every movement and task edit. The runner grades ordered exact-cell arrivals from settled world receipts, archives each run, and resets between trials.

From `t-scan/`, with idle inference and connected Unity:

```powershell
./.venv/Scripts/python.exe live/transit_batch.py --output runtime_data/<new-batch-name> --data-dir runtime_data --seconds 300
```

Choose a new output directory; existing batches are never overwritten. Operator Stop, a batch `STOP` file, inference failure, or lost Unity connection halts the batch. A live Unity poll must be no more than three seconds old. A transient polling gap can therefore interrupt an otherwise valid trial. Do not automatically resume a failed trial.

A new human message cancels batch ownership and hands control back to the conversation. Batch Stop requests are guarded by the originating request ID, including queued human corrections, so cleanup cannot interrupt a replacement human turn. The self-model batch `transit-batch-self-model-20261104-1840` halted during trial one after a human correction; the older runner incorrectly sent Stop during failure cleanup. No trials completed. Preserve this interrupted condition separately; do not resume it. The repair and the new agent-owned `task_remove(task_id, expected_revision)` tool are recorded as `shared-chat-v8.3-task-remove`. Existing tasks remain editable through `task_list_write` with the same ID; deletion retains the prior edit audit and does not certify completion.

Results live in each batch's `status.json`; per-run requests, reasoning, settled receipts, task edits and configuration are under `runtime_data/runs/<run-id>/`. Grade task claims against world receipts, not task labels alone. Preserve ambiguity in task-to-flag mappings. Multiple prompt/interface changes and stochastic sampling limit causal attribution.

The fresh `transit-batch-task-remove-20261104-1401` baseline uses the same ten routes and caps with v8.3. Evaluate it offline from the saved evidence; do not change runtime conditions to collect these metrics:

- Route completion: ordered exact-cell arrivals divided by three; full passes require all three in order. Report agent task completion claims separately.
- Timing: time from request acceptance to the final required settled arrival, and total trial elapsed/ending. A timeout or interrupted trial has no successful completion time; do not substitute its cap into averages of successes.
- Tools: counts by tool and outcome, including rejected calls and task edits; count `request_replan` calls separately from automatic phase invalidations.
- Loops/stalls: flag repeated identical rejected calls and repeated state/action cycles, with counts and timestamps. Distinguish active looping, provider latency, presentation waits, no-action idle and external interruption. Do not call a long wait a proven deadlock without supporting state evidence.
- Recovery: for observed errors/blocks, report subsequent changed action or repaired request and whether it succeeded. If there were no such events, recovery was not exercised.
- Completion accuracy: compare task-mark receipts with settled arrivals available at that time; distinguish supported, contradicted and ambiguous claims. Also report actual arrivals never recorded as complete. Never infer an uncertain title-to-flag mapping as fact.
- Explanations: qualitatively assess specificity, use of current receipts, acknowledgement of errors, and whether the stated next action matches the requested tool. Cite compact request/run references; do not reproduce lengthy reasoning.
- Consistency: compare expressed claims, explicit stored belief revisions, selected plans, task status changes and measured actions. If no relevant belief was authored or supplied, mark that comparison unavailable. Provider explanations are not proof of internal causes.

Include interrupted trials and missing captures explicitly; state denominators for every rate. Keep the interrupted v8.2 run separate from this baseline. These measures assess behavioral and memory consistency, not model-weight learning.

The repaired x/y batch `transit-batch-xy-flatwrite-20261103` finished nine trials: eight passes, one timeout, zero boundary blocks. Trial ten was interrupted by the connection check. Its saved status is failed; it is not a ten-trial completed result. The earlier interrupted x/y batch is a separate condition. The task-completion reminder was added afterward as `shared-chat-v7.4-task-completion-reminder` and has not been trialed in that batch.

`verify_unity_world.py` is a separate mechanical presentation check using a fresh data directory and no model. Its fixed movement fixtures are test inputs, not an agent navigation policy. Read its CLI before using it and keep it isolated from Steve's live state.

## Result: `transit-batch-three-call-20261104-1440` (v8.4)

Ten fixed routes, 300-second caps, graded offline from controller logs and tool receipts (ordered exact-cell arrivals on `moved` outcomes; arrival time per trial was not computed).

| Measure | Value |
| --- | --- |
| Full passes | 0 of 10; every trial ended `timeout` |
| Ordered arrivals | 17 of 30 (57%); the stopped v8.3 baseline was 7 of 12 (58%) |
| Moves | 132, all `moved`; no blocked boundaries; 3 extra moves in total (trials 3 and 9) |
| Share of tool calls that were moves | 132 of 264 (50%): 48 `task_list_write`, 29 `plan_handoff`, 19 `request_replan`, 16 `task_mark_complete`, 12 `complete` |
| Pace | about 26 to 29 requests per trial, median gap about 11 s, about 330 completion tokens per decision |
| Moves needed | 16 to 25 per route (mean 21.4), against 6 to 17 achieved |

Comparison on the same routes and cap: `transit-batch-xy-flatwrite-20261103` completed 8 of 9 trials in 200 to 270 s; `transit-batch-task-remove-20261104-1401` was 0 of 4. The drop appears with the planner/executor and Self-model layer, not the three-call change. This is an inference from counts and timing, not a tested cause.

Observed defects:

- Twelve `complete` calls (trials 2, 3, 9, 10) were rejected `rejected_schema` because Steve sent a `description` argument, using `complete` to mean "this step is done". The error said only "Only registered zero-argument actions are supported".
- Trial 4 made 15 `task_list_write` calls and 6 moves. Three responses of three parallel `task_list_write` calls were rejected `rejected_conflict` with no explanatory text, and the receipt was labelled "Historical agent-authored task-list edit". Steve then used revisions that were not current, and later `plan_handoff` calls for a task that had never been saved were rejected with a generic message. Cause is inferred from the receipts; provider reasoning was not inspected.

## Condition: `shared-chat-v8.4.1-actionable-rejections` (not yet run)

Prompt and message changes only. Model, sampling, tools, three-call turn and the epoch counting policy are unchanged.

- **System prompt:** new `REJECTED CALLS` section between `YOUR TASK LIST` and `CONTEXT AUTHORITY`, in the existing heading, underline and blank-line style: a rejected call executes and saves nothing and still uses one of the three calls; one call per response; movement tools and `complete()` take no arguments; `complete()` does not mark a task done.
- **Tool description:** `complete` states it takes no arguments and does not mark a task done.
- **Rejection results:**
  - zero-argument calls with arguments name the arguments received and, for `complete`, point to `task_mark_complete`;
  - invalid JSON arguments are explained;
  - multi-call responses say how many calls arrived and that none executed;
  - stale `plan_handoff` names which part is wrong (unknown task, completed task, stale revision) and gives the current revision and unfinished task IDs;
  - a rejected task-list receipt is labelled as a rejected call, not an edit.
- **Verification:** assembled prompt section and compacted receipts inspected directly; 173 tests pass.

Compare against the v8.4 batch on the same ten routes and cap. Expect `rejected_schema` to include store refusals separately as `rejected_store`, and harness faults as `internal_error`, from the earlier reliability fixes; do not compare raw rejection counts with v8.4 without that distinction. Keep the pace finding in view: a 300-second cap may remain too short for 21-move routes even with no wasted calls.

## Condition: `shared-chat-v8.4.2-phase-aware-rejections` (not yet run)

`transit-batch-actionable-rejections-20261104-2055` ran v8.4.1 until the operator pressed Stop during trial 7 (status `cancelled`, reason `Operator Stop`); six trials were archived. All six timed out, with no full passes. Ordered arrivals were 10 of 18 (56%), against 9 of 18 for v8.4's first six trials. Trial 5 used 21 moves, 4 beyond the optimal route to its last arrival; the other five trials had none. Trial 4's thrash did not recur. Rejected calls: 14 `complete` (12 of them in trial 1), 2 stale `plan_handoff` (now with specific reasons) and 1 stale task-list write. Median prompt size was about 20k to 22k tokens per decision, maximum 29.3k (provider-reported). Trial 1 made 12 rejected `complete` calls such as `complete({"tool_name":"task_mark_complete","args":{"task_id":"visit_blue"}})`. The v8.4.1 hint told Steve to call `task_mark_complete`, which exists only in the planner phase; the executor phase has `complete`, the four moves, `agent_read` and `request_replan`.

Changes from v8.4.1:

- **Phase-aware hint:** the registry builds its validator with the tool names visible in the current phase. In the executor phase a rejected `complete` says `task_mark_complete` is not available and to call `request_replan` to return to planning; in the planner phase it says to call `task_mark_complete`. The system prompt line and the `complete` tool description say the same, without pointing the executor at a tool it lacks.
- **Compact recent experiences (Self projection policy v1.2):** measured on a v8.4 trial-1 request (93.8k characters, 73 messages), `decision_context` was 35.2k characters, of which `self_model.continuity` was 14.6k. Each of the four `recent_experiences` carried a full 2.4k-character world snapshot (board, targets, surroundings) in internal `col`/`row` names, repeating the CURRENT WORLD block and contradicting the x/y rule. They are now compact receipts in x/y (the same projection used for tool results), labelled `receipt_form`; the full snapshot stays in the evidence store and run archive. Test: the compact form is under half the size and has no observation.
- **Observability only, no model input:** `/health` now carries `epoch` (run, index, request ID, phase, calls, clock spent, ending) and `context` (provider-reported prompt tokens, window, percent full, tokens until a 70% threshold). The epoch index restarts with each run. Nothing is sent to the model.

Unchanged: model, sampling, tools, three-call turn, `all_calls` counting. Verification: 184 tests pass. These are two prompt-visible changes in one condition; the compact-experiences change should be attributed separately in the analysis by comparing prompt tokens per decision as well as outcomes.

## Epoch-based runner: `live/epoch_batch.py`

Built and tested against a scripted fake bridge; not yet run against a live model. Timed 300-second trials measure pace more than capability: the routes need about 21 moves (16 to 25) and the v8.4 batch managed about 13 in 300 seconds with moves near-optimal. Behavior:

- Run until the graded ordered arrivals reach 3 of 3, then until Steve calls `complete()`, with a short grace of a few epochs after the last arrival.
- Backstops: an epoch cap (proposed 40) and a generous wall-clock stop, so a stuck run cannot loop forever.
- Headline: decisions and tokens to the final arrival. Record calls and moves per epoch as well, since an epoch counts differently under `all_calls` and `clock_actions`. Wall-clock time is a secondary column.
- Keep the same ten routes. The epoch index comes from `/health.epoch`, which requires a backend on v8.4.2 or later; the runner halts if the backend reports no epoch state.
- A trial ends on: Steve's `complete()` (`complete`), a text-only idle (`no_action`), the operator (`cancelled`), or a backstop: `epoch_cap` (default 40 completed epochs), `grace_expired` (default 3 completed epochs after the final ordered arrival without a `complete()`), `wall_clock` (default 3600 s). Backstops send Stop; the trial is still graded.
- Each result keeps the usual grade plus `arrived_epoch`, `arrived_elapsed_seconds`, `epochs_completed`, `epochs_after_arrival`, a `progress_timeline` (elapsed, epoch, ordered flags, moved steps) and the last epoch snapshot seen for each epoch. Epoch counts come from the latest epoch index, so a poll that misses a fast epoch cannot undercount it. An epoch cut short by Stop has no ending and is not counted as completed.
- Decisions and tokens to the final arrival are derived offline from `runs/<run-id>/inference-events.jsonl` and `tool-receipts.jsonl`; the runner does not compute them.
- Same safeguards as the timed runner: idle loop and live Unity required, reset verified before each trial, a human message releases control without stopping the conversation, and a `STOP` file in the output folder halts it.

```powershell
./.venv/Scripts/python.exe live/epoch_batch.py --output runtime_data/<new-batch-name> --data-dir runtime_data --routes 1
```

Start with `--routes 1` as a smoke test. Defaults: `--max-epochs 40 --grace-epochs 3 --max-seconds 3600`.

## Smoke test: epoch runner on v8.4.2, one route (`epoch-smoke-*`)

Route blue, red, yellow; backend `shared-chat-v8.4.2-phase-aware-rejections`; LM Studio loaded with a 94,976-token context (chosen by the owner). The runner counted 10 epochs and recorded a progress timeline, so it works end to end against the live model.

- **Arrivals:** blue in epoch 3 (5 moves, 70 s), red in epoch 7 (12 moves total, 152 s), both optimal; yellow never reached. Not a pass (2 of 3).
- **Ending:** Steve called `complete()` at 241 s, 24 decisions, 15 moves, 0 blocked. That is a false completion claim.
- **Cost:** 349k prompt tokens and 8.6k completion tokens in total; median prompt 14.7k tokens, maximum 22.6k (v8.4.1: about 20k to 22k median, 27k to 29k maximum). Fewer decisions also means less history, so attribute the drop to compact experiences only tentatively.
- **Calls:** 24, of which 9 were not moves (38%; v8.4.1 about 50%). No wrong-phase `complete` rejections (v8.4.1 trial 1 had 12); 2 stale `plan_handoff` rejections.
- **Cause of the false completion:** Steve wrote one umbrella task, `visit_flags` ("Visit Blue flag, then Red flag, then Yellow flag in order. Complete afterwards."), and marked it complete after the second flag. Two `plan_handoff` calls for yellow were then rejected because the task was completed ("Unfinished task IDs: none"). His reasoning noted that the world state did not confirm occupancy of yellow, then concluded that the completed task implied it, and called `complete()`. No goal (intention) was recorded.
- **Not a mechanical dead end:** at those rejections he was in the planner phase with `task_list_write` and `intention_write` registered (checked in the run's context manifests), and `task_list_write` with a new ID adds a task while an existing ID reopens one. The gap was signposting at the moment of refusal, a prompt that called a separate goal optional, and no prompt guidance on task granularity.

## Condition: `shared-chat-v8.4.3-goal-and-tasks` (not yet run)

Prompt, tool-description and rejection-message changes only. Model, sampling, tools, three-call turn and `all_calls` counting are unchanged.

- **Goal and tasks both recorded by Steve:** a new `YOUR GOAL` prompt section, in the existing heading, underline and blank-line style, says to record the goal with `intention_write` (lifetime run, status active) when a human request arrives, write each checkable step as its own task, mark a task complete only when its whole criterion is met, link the goal with `intention_id` at handoff, and set the goal fulfilled only after checking receipts. It states that an active goal with no unfinished task means the task list is missing a step or the goal is finished. The planner-phase line no longer calls the goal optional. The backend still creates no goal, task or status.
- **Tool descriptions:** `intention_write` is described as the planner's goal record; `plan_handoff` says `intention_id` links the active goal.
- **Refusal text:** a `plan_handoff` refused for an unknown or completed task, or a stale revision, now also states that `task_list_write` adds a task with a new `task_id` or reopens one by rewriting its `task_id` with status `pending` or `in_progress`. This states mechanics and selects nothing.
- **Verification:** tests reproduce the smoke-test scenario (all tasks completed, handoff refused) and show that adding a task or reopening one gets past it, with and without a linked goal; the assembled prompt, the projected goal and the refusal text were inspected directly. 203 tests pass.

Side effect to watch: the executor's plan is invalidated when its linked intention changes revision or leaves `active`, which sends Steve back to planning. Expect some extra planner turns when he fulfils a goal.

Compare against the v8.4.2 baseline on the same ten routes, with the epoch runner. Measures: false completion claims (a `complete()` before 3 of 3), umbrella tasks versus one task per flag, whether a goal was recorded, extra planner epochs, decisions and tokens to the final arrival.

## Result: epoch batch on v8.4.3, ten routes (`epoch-batch-v843-*`)

`epoch_batch.py`, defaults (40 epochs, 3 grace epochs) with a 1200 s per-trial backstop; LM Studio context 94,976.

| Measure | Value |
| --- | --- |
| Full passes | 7 of 10 (the timed runs: 0 of 16 across v8.4 and v8.4.1) |
| Ordered arrivals | 24 of 30 |
| Endings | 9 `complete`, 1 `no_action` |
| Passing trials | median 467 s, 18 epochs, 2 epochs after the final arrival, about 36 to 50 decisions |
| Moves in passing trials | optimal in 5 of 7; trial 7 +1, trial 10 +2 |
| Failures | trial 3 (1 of 3), trial 5 (0 of 3, 0 moves), trial 9 (2 of 3) |

- **False completions (trials 3 and 9):** Steve called `complete()` with flags still unvisited. In trial 3 his goal was `active` and his one task `pending` at that moment. Recording a goal and tasks did not prevent it.
- **Stall (trial 5):** 0 moves, 42 decisions, 37 rejections, ended `no_action` at 538 s.
- **Handoff rejections:** 72 of 104 `plan_handoff` calls were rejected as schema errors. Two causes: (a) `landmark_id` was a required string even for the `manual` criterion, so `null` produced "Invalid landmark_id" (34 times, uninformative); (b) 38 times the call linked an `intention_id` that had never been recorded, because the preceding `intention_write` had been rejected `rejected_stale_revision` (he sent `expected_revision` 1 for a new goal; the error said to use 0, and he linked the goal anyway). In trials 1 and 2 no goal was ever recorded.
- **Goal and tasks:** in passing trials Steve typically wrote one task per flag (trial 6: three per-flag tasks and a goal). Trial 3 and the early ones show the structure is not enforced, only visible.
- **Cost:** about 0.65 to 1.1 million prompt tokens per trial and 10k to 26k completion tokens (the prompt grows with the epoch count).

## Condition: `shared-chat-v8.4.4-free-retry` (ran: ten-route epoch batch, 8 of 10 passes)

Model, sampling, tools and the world are unchanged. Model-visible changes:

- **`plan_handoff` schema:** `landmark_id` is optional and required only for `visit_landmark`; `manual` takes none (omit or `null`). The description says so.
- **Exact errors, all at once:** tool-argument validation for the agent-state tools reports every violation in one message, each naming the field, the rule and what was received (bounded), with the valid values; a cross-field rule covers `visit_landmark`. Execution refusals are exact too: an unrecorded or inactive goal link names the goals recorded for this run and how to record one (`intention_write`, `expected_revision` 0 for a new goal); an unknown landmark lists the real landmark IDs. `intention_write` says to use `expected_revision` 0 when creating.
- **Free single retry (`accepted_calls` policy):** a rejected call does not spend the turn's three calls and may be retried once. A second consecutive rejection of the same tool ends the turn with `repeated_rejection`; the total-call ceiling (8) still applies. Three such turns in a row make the loop yield with `pause_reason` `stalled` (new `GridWorld.stall()`, logged as `decision_loop_stalled`), which the epoch runner records as the trial ending. The backend chooses nothing; it only stops a loop that is not progressing. The epoch snapshot now carries `accepted` and `rejected` counts.
- **No facing for the model:** facing is removed from the current-world text, action receipts, historical observations, the prompt and the four movement tool descriptions. It stays in the authoritative state, the archives, the Unity visuals and the operator's Self view.
- **Prompt:** the `ACTIONS AND CONTINUATION` allowance wording, the `FIXED COMPASS` and `CURRENT STATE` lines, and the `REJECTED CALLS` section were reworded for the above, in the existing heading, underline and blank-line style.

Not included: a factual line about an active goal and unfinished tasks at the moment of `complete()`. It would target the two false completions but adds to what the model is told about itself, so it waits for the owner's decision.

Verification: 235 tests pass. The assembled prompt sections and sample errors were inspected directly.

Compare with the v8.4.3 table above on the same ten routes: full passes, handoff rejections per trial, trials ending `stalled`, false completions, decisions and tokens to the final arrival.

### v8.4.4 results (`epoch-batch-v844-20261104-1829`, same ten routes, 1200 s ceiling per trial)

| Measure | v8.4.3 | v8.4.4 |
| --- | --- | --- |
| Full passes | 7/10 | 8/10 |
| Ordered flags reached | 24/30 | 26/30 |
| Trials ending `stalled` | 0 (one `no_action`) | 1 (trial 8) |
| False completions | 2 (trials 3, 9) | 1 (trial 5, 2 of 3 flags) |
| Passing trials | median 467 s | median 439 s, 11 to 19 epochs, 1 to 2 epochs after the final arrival |

- **Trial 8 (stalled, 0 moves, 3 epochs):** run-scoped goal ID `visit_flags_sequence` had been used in trial 5 and left archived. `intention_write` with `expected_revision` 0 was rejected as stale (revision 2 existed), so the goal was never recorded. Every handoff linking it was rejected ("archived, not active... Goals recorded for this run: none"); he never tried omitting `intention_id`, which the error offered. The stall stop ended it as designed.
- **Trial 5 (`complete` at 2 of 3 flags):** same false-completion class as v8.4.3.

### New environment condition, 5 November 2026

Chat/memory/persistence suite: the owner requested ten diagnostic probes after reviewing navigation. See [frozen design and assessment criteria](CHAT_PERSISTENCE_PROBES.md). Uses an isolated SQLite backup of Steve, ordinary chat/reset APIs, the current prompt/model, and a headless copy of the authored world for the no-movement chat gate. Synthetic test memories do not enter the main store. Tests visible-history recall, corrections, unfinished work, plans/evidence, saved notes across reset, corrected notes, persistent intentions, run-local clearing and backend restart. Storage, actual disclosure and model behavior are separate observations; captures are not automatic semantic passes.

Two-flag repetitions requested by the owner: two consecutive batches of five fresh-chat trials, repeating the same ordered pairs: red→blue, blue→yellow, yellow→purple, purple→red, red→yellow. Every trial archives/resets through New chat to the authored (8,8), north. Condition stays `shared-chat-v8.4.7-execution-reminder`, with the X map and existing model/sampling/world. Limits: 40 completed epochs, 3 grace epochs after the final arrival, 1200 seconds. `epoch_batch.py` accepts an explicit route file and reset cell; settled obstacle bumps now count in blocked steps. `Tools/run_two_flag_batches.py` sequences both batches and does not start batch 2 after cancellation/failure. Human takeover and operator Stop remain authoritative. These routes differ from the historical 10×10 three-flag routes; compare only matching pairs and state denominators.

Execution clarification: `shared-chat-v8.4.7-execution-reminder` adds one short executor instruction: Steve executes the task himself by choosing a movement tool; handing off a plan does not start movement. Approved after red-flag requests produced handoff/replan calls and text-only waiting without moves. X map, world, tools, sampling and scheduler remain unchanged. The earlier request captures show cardinal tools registered in executor phase; lack of movement was not a missing-tool result. Retry red under this separately recorded prompt condition.

The approved retry (`3446a39e934640a1ae9431571217364f`, "Please resume going to the red flag.") ended `no_action` in its first planner epoch, with no tool calls and no movement from (8,8). Steve's reply claimed the plan was guiding movement and that he was waiting for observations. The captured system message included the execution reminder; this attempt never entered executor phase. It does not establish whether the reminder would help a fresh executor decision or whether the X map helps navigation. 239 tests passed and assembled messages were inspected before activation. No further prompt change was made after this result.

Follow-up presentation condition: `shared-chat-v8.4.6-x-map`, requested by the owner, replaces the obstacle ID/type/coordinate list and adjacent-cell enumeration with a north-up x/y map: `X` obstacles, `@` Steve, dots open, flag initials. The world, movement tools and collision mechanics are unchanged. No model-navigation result is implied by formatting verification.

`shared-chat-v8.4.5-meadow-course` installs the owner-approved [15×15 obstacle course](MEADOW_COURSE.md). Bounds, world/obstacle observations, blocked outcomes, movement descriptions and prompt version changed. Four corner flags replace the old five interior flags; New chat resets to the authored (8,8) spawn. No navigation model trial has run under this condition. The previous ten-route scorecards describe the old world and are not directly comparable. Backend verification: 239 tests passed; isolated Unity presentation: eight settled acknowledgements, including two obstacle bumps; boundary and compilation checks passed.
- **Fix after the batch (state-level, version string unchanged):** a run-lifetime goal from an earlier run is not this run's record. `intention_write` with `expected_revision` 0 on such an ID now succeeds and continues that ID's revision history; a handoff linking it reports "has no goal record". Persistent goals are unchanged. Test: `test_v844.py`. 236 tests pass. Not yet re-run on live routes.

## Condition: `shared-chat-v8.5.0-built-worlds` (not yet run)

Model, sampling, tools and the epoch rules are unchanged. Model-visible changes, all caused by worlds being built from classified pieces:

- **Obstacles by name.** The current-world text lists obstacles grouped by curated catalog name and role (`{"name":"Stone wall","role":"wall","cells":[[3,5],...]}`) instead of only `X` on the map. Pieces without a curated name are not listed, so raw prototype ids (`stone_wall`) are never shown.
- **Hazards.** Walkable cells marked as hazards appear in their own section ("effects are not stated here") and as `!` on the map. No hazard mechanic exists yet; the receipt for entering one is an ordinary `moved`.
- **Surroundings.** An adjacent obstacle or hazard cell now carries `feature` (its name) beside `terrain`.
- **Prompt.** One clause in `CURRENT STATE AND ACTION RESULTS` explains `!`. The `YOUR GOAL`, `REJECTED CALLS` and other sections are unchanged.
- **Decor and floors** are cosmetic and not part of the model's context.

Verification: 258 tests pass, including role-rule tests and a test that every exported catalog piece validates in its own world. The assembled observation text was inspected on a live v3 world (revision 6) and contains only curated names, roles, hazards and the two map symbols. No navigation batch has been run on a built world; compare against the v8.4.7 15x15 result only after one is.

## Condition: `shared-chat-v8.6.0-actors` (not yet run)

Everything in `shared-chat-v8.5.0-built-worlds` is unchanged except what the model can see of a world that contains enemies or bosses. Those pieces appear in the OBSTACLES section like any blocker, grouped by curated name with role `actor` (for example `{"name":"Mimic Queen","role":"actor","cells":[[4,4],[4,5],...]}`), every covered cell listed and marked `X` on the map. They have no behaviour, do not move, and the prompt does not explain the `actor` role. No prototype ids are shown. Compare against v8.5.0 only on worlds with actors; worlds without them produce the same context.
