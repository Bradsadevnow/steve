# Epoch-boundary compaction (DRAFT)

**Status: proposal for owner review. Not implemented. Not implementation authority.** Written 4 November 2026. Current behavior is documented in [ARCHITECTURE.md](ARCHITECTURE.md) and [SEQUENTIAL_TOOLS.md](SEQUENTIAL_TOOLS.md). Nothing here changes the running v8.4 batch; code changes take effect only after a backend restart, which starts a new experimental condition.

## Goal

Use the three-call turn as an **epoch**: the unit of the future turn-based world clock and the point where working context is compacted. Keep the model's context bounded and the on-disk record lossless.

## Measured baseline (run `20261104-200031-ac8d7959`, partial)

| Item | Observation |
| --- | --- |
| Provider request, 20 messages | about 43k characters |
| Provider request, 40 messages | about 57k characters |
| Current `decision_context` | 30-36k characters, rebuilt every decision, not accumulated |
| Older contexts in outgoing messages | already collapsed to roughly 250-character `historical_observation` records |
| `conversation.json` | 380 KB after this run, rewritten in full on every checkpoint |
| `inference-requests.jsonl` | 630 KB for 13 requests; full payload per request |

Consequences:

- The provider window is not the near-term problem. The fixed per-decision context is the larger cost and grows with memory and manifests. **Its breakdown has not been measured yet.**
- Disk growth is quadratic: the durable transcript stores every full context and is rewritten each checkpoint; the request log stores every full payload.

## Definitions

- **Epoch:** one scheduled turn, up to three decisions (v8.4). Ends on `tool_call_limit`, `plan_handoff`, `request_replan`, `complete()`, a text-only reply, or an interrupt.
- **Boundary:** after the last receipt of the turn and settled presentation, at the end of the executor loop in `grid_worker.py`.
- **Epoch record:** mechanical summary of one closed epoch, described below.

## Compaction rules

1. **Trigger and scope: every epoch boundary, or the size threshold, whichever comes first.**
   - **Epoch boundary (routine):** compact closed epochs older than the last **K** (default K=1). The newest K epochs stay raw so immediate feedback keeps its native call/result structure.
   - **Size threshold (safety net):** when the last measured prompt size reaches the threshold (proposed 70% of the window), compaction runs at the next safe point, between decisions, without waiting for the epoch to end. It then also collapses the newest K closed epochs (K drops to 0), and if still over, releases pins oldest-first. The currently open epoch is never compacted.
   - With routine compaction every epoch, the threshold normally fires only if one epoch, the pins or the notes are unusually large.
2. Collapse only machine records: decision ticks, per-decision contexts, and assistant tool-call / tool-result pairs. Collapse a whole epoch at once; never split a call from its result.
3. Never compact: human messages, the model's own text content, or any epoch with an unresolved decision (`interrupted_requires_review`) or a pending presentation.
4. Replace a collapsed epoch with one `epoch_record` envelope with the `user` role (not `assistant`), so it cannot be mistaken for model speech.
5. The record is **mechanical only**:
   - epoch ID, run ID, index, ending reason;
   - ordered calls: `call_id`, tool, outcome, `action_id`;
   - first and last observation IDs, position before and after (x/y);
   - task-list and plan revisions before and after;
   - supplied-versus-omitted manifest hashes (full lists remain in the archive);
   - a freshness label: historical; current state is in the latest CURRENT WORLD observation.
6. No backend-authored or separately generated prose. The only prose in an epoch record is Steve's own review note (next section), stored with provenance and labelled as his assessment. The record is complete and valid without a note. Detail is retrievable through `agent_read` on receipt and experience references.

## Design principle: defer choices to the model, within fixed bounds

The environment is sandboxed, so choices about Steve's own working context, review rhythm and notes belong to Steve. The design problem is giving him enough information to choose, with little overhead.

Rules for every deferred choice:

1. **A do-nothing default.** Doing nothing is always valid: an empty `epoch_note_write()` or a text-only reply closes the review with defaults.
2. **One tool, few optional fields.** No separate knobs: `note`, `plan_status`, `pin`, `review_again_in`, `replan`.
3. **Facts, not advice.** Every decision context (not only reviews) carries a one-line **context meter** showing approximate percent full and when compaction next happens, whichever comes first: the end of the epoch or the token threshold. No recommendations, consistent with "no unrequested action plans". Example: `Context: ~41% full (~54k of 131k tokens); next compaction at epoch end (2 calls left) or in ~17k tokens, whichever first.`
   - Source: the provider-reported prompt token count of the previous request (already captured in `usage`), so it is a measurement, not a character estimate. It excludes the next decision's new messages, hence "~". The first decision of a run has no measurement and shows `no measurement yet`.
   - "Calls left" is the remainder of the three-call allowance; "tokens" is the distance to the size threshold (rule 1 under Compaction rules).
4. **Visible consequences.** The next context's receipt says what changed, for example: pinned 2, collapsed epochs 3-4 to records, archive retains everything.
5. **Reversible.** Nothing is deleted. Collapsed material stays in the archive and is retrievable with `agent_read`; pins can be changed at any review.
6. **A small review packet.** The raw messages of the closing epoch are already in the transcript, so the packet is a short decision card (roughly 1-2k characters: counts, trail, machine check, plan, last two notes) with references for detail, not a restatement.

What Steve chooses:

- Whether to write a note, and what it says; `plan_status`.
- Which items stay verbatim in the working view (`pin`): epoch records, notes, receipt references. Human messages never collapse, so they need no pin.
- Review cadence: `review_again_in`, 1 to 5 epochs, default 1.
- Whether to return to planning (`replan`, equivalent to `request_replan`). Task and plan edits still happen only in the planner phase through the existing tools.

Defaults when he does not choose: last epoch raw, last two epoch records with notes inline, no pins, review every epoch.

Fixed bounds (backend-enforced, stated to him once in the system prompt, not his to change):

- **Compaction threshold and pin limit.** The context window is physical, so compaction triggers at the threshold. If pins exceed the limit, the oldest are released first and the receipt says so; never silent.
- **Integrity.** Never split a call from its result; never compact an unresolved decision or pending presentation; human messages never collapse.
- **Authority.** Notes and pins grant no capabilities and mark no task complete; the backend never selects the next task.
- **Archive.** Lossless; he cannot edit or delete it.
- **Review ceiling.** A review runs at least every 5 epochs.


## Epoch review step: how the compression context is built

**Status: draft design, added after owner request.** Closing an epoch can include a short **review** of at most two model decisions (see Review budget below), in which Steve sees the epoch that just ended and the results of the previous two cycles, and records how he is doing against his own plan. It is a decision by the persistent Self, not a separate summarizer persona.

### Sequence at epoch close

1. All decisions of epoch N are terminal and presentation is settled.
2. (Future) the world tick runs.
3. Review, if enabled: one or two inferences with the packet below, under the review budget. It is not a world action, does not consume the three-call allowance and does not advance the world.
4. The epoch record is written, with the note if one was recorded, then epoch N is compacted.
5. Failure, interrupt, a text-only reply or a rejected note never blocks compaction. The record is written with `note: null` and a reason.

### Messages sent for the review (native roles, stable order)

1. **system:** the same Self prompt as ordinary decisions, plus a short EPOCH REVIEW section: you may record an assessment of how the epoch went against your plan; it is an assessment, not verification; it does not move you, change tasks or grant capabilities; you may read stored records once before deciding what to write, then you finish (see Review budget).
2. **Working transcript** exactly as the next ordinary decision would receive it: human messages and older epoch records.
3. **Raw messages of epoch N** with native roles and registered tool-call / tool-result IDs, so full detail is present.
4. **Final `user` harness record `epoch_review_input`**, all fields JSON-escaped inside the standard envelope, sections in this order (evidence before prior opinions, to avoid anchoring on earlier notes):
   - `closing_epoch`: mechanical epoch record (epoch ID, calls and outcomes, positions before and after in x/y, plan and task-list revisions, ending reason).
   - `measured_evidence`: fresh current observation with its observation ID; this epoch's controller receipts; the machine check from `assess()` with its stated scope; per-epoch counts for the last three epochs (moved, blocked, rejected by category, internal errors) and the x/y position trail. **No distances to targets, no routes, no suggested actions.**
   - `your_plan`: current plan (revision, task ID, criterion, landmark ID, instructions) and task list (revision; statuses labelled as your own assessments), plus any plan or task revisions changed over the last three epochs.
   - `prior_reviews`: the previous two cycles from the **current run only**: each epoch record with Steve's note verbatim (note ID, revision, time) or `note: null` and why. Labelled as his earlier assessments, not evidence; repetition does not raise confidence. Fewer than two prior cycles is shown explicitly, as is none after New chat. Archived runs are never injected.
   - `limits`: how many older epochs are omitted, with IDs and manifest hashes.

### Tools available during the review

### Review budget

The review is a short sequential turn of **at most two decisions**, each from a separate model response with its result returned before the next, as in ordinary turns. One call per response; multiple calls in one response are rejected.

- **Decision 1** tools: `agent_read`, `epoch_note_write`, `request_replan`.
- **Decision 2** exists only if decision 1 was `agent_read`. Its tools are `epoch_note_write` and `request_replan` (no second retrieval; the supplied tool list reflects this, and a call outside it is rejected as unregistered). Steve can still end with a text-only reply.
- The review ends on `epoch_note_write`, `request_replan`, a text-only reply, an interrupt, or after decision 2. A rejected call consumes its decision.
- The retrieval is the existing bounded `agent_read` (up to 8 records or sources per call). The packet already carries this epoch's evidence, so retrieval is for older epochs, sources and records.
- `request_replan` alone ends the review without a note (`note: null`, reason recorded). To record a note and replan, use `epoch_note_write` with `replan: true`.
- The budget is two decisions by default and is an owner-tunable bound. A strictly one-call review (packet only, no retrieval) is the alternative; it removes the contradiction by dropping `agent_read` from the review tools.

### Tools available during the review

- `agent_read` (bounded retrieval, as in the executor phase), only in decision 1.
- `epoch_note_write(epoch_id, assessment, plan_status, evidence_refs, pin, review_again_in, replan)`, every field except `epoch_id` optional:
  - `assessment`: free text, at most 600 characters;
  - `plan_status`: `progressing`, `stalled`, `off_plan`, `achieved_claim` or `unclear`: Steve's judgement, never a backend verdict;
  - `evidence_refs`: the same reference grammar as `assertion_write` (`receipt:ACTION:STATUS`, `event:N`, ...); empty means unsupported impression;
  - `pin`: references to keep verbatim in the working view, within the pin limit (see the design principle);
  - `review_again_in`: epochs until the next review, 1 to 5, default 1;
  - `replan`: true returns to the planner phase at the next turn, like `request_replan`.
- `request_replan` remains available as in the executor phase.
- No movement, task, plan-edit or handoff tools. Changes to tasks and plans happen in the planner phase, which sees the note in the epoch record. `achieved_claim` marks nothing complete.

### Storage and visibility

- The note is stored transactionally with a mutation receipt, like other agent-authored state, and copied into the epoch record.
- Ordinary decisions after compaction see the last two epoch records with notes inline. Older records keep ID, outcome and `plan_status` only; the note text stays in the archive.

### Cost and experiment design

- One extra inference per epoch, or two when Steve retrieves first, each roughly the size of an ordinary decision plus the epoch's raw messages and two short records. It adds time per epoch and so changes the 300-second trials.
- Make review a separate switch from compaction so conditions can be compared: compaction only, versus compaction plus review.

### Known risks

- **Narrative loop:** a note saying "progressing" can be copied forward. Mitigations: evidence precedes prior notes, the reinforcement warning, required evidence references, no verdict labels from the backend.
- **`assess()` scope:** it currently accepts any settled occupancy of the landmark in the run, not only since the plan was made, so it can report `supported` for an earlier visit. The packet states this scope. Bounding it by plan creation time is a separate change.
- **Authority:** the note is Steve's claim. It cannot grant capabilities, complete tasks or select the next task.

## Storage (lossless)

1. Before collapsing, write the epoch's raw messages to `runs/<run-id>/epochs/NNNN.jsonl`.
2. Then swap the working transcript in one atomic write. Re-collapse is idempotent, keyed by epoch ID, so a crash between the two steps is safe.
3. Request log: store each distinct message once, by hash; log each request as an ordered list of hashes plus tools and parameters. Requests remain exactly reconstructable.
4. Required follow-on changes:
   - `run_archive.finish` rebuilds `chat.md`, snapshots and receipts from the transcript. It must read segments plus the live tail.
   - `GridConversation.history()` uses list indices as IDs; they shift on collapse. Use stable epoch-based IDs.
   - `grid_worker.py` uses `turn_start` as a list index; compaction runs only when it is `None`.

## State owners are unchanged

Self, doctrine, tasks, plans, notepad audit and affect keep their own stores and are supplied fresh in each decision context. Compaction affects only the conversation transcript. New chat still archives the run and clears working state.

## Versioning and testing

- New condition, for example `shared-chat-v8.5-epoch-compaction`, announced through the existing interface-transition record. Add an entry to `EXPERIMENTS.md`. Model and sampling settings unchanged.
- Tests: envelope round trip; call/result pairing never split; idempotent re-collapse after simulated crash; compaction skipped for unresolved decisions; archive export identical before and after compaction; request-log reconstruction matches the sent payload; inspect actual assembled provider messages for ordering, escaping and freshness.
- A 300-second trial is about 5-6 epochs, so the ten fixed routes test **non-regression**, not benefit. Benefit needs a long-horizon run (100+ epochs).

## Future: world clock

Not part of the first implementation. At epoch close `grid_world.py`, as the only writer, would advance the world tick, resolve environment and enemy rules deterministically, and emit receipts stamped with the epoch number. The epoch record is written after the tick so Steve sees its effects. Model latency never changes outcomes.

## Roadmap: affect, memory and check-in conversation (DRAFT)

Direction from the owner: update affect each epoch, braid it with memory, pass it every turn, then use it in conversation before and after Steve acts or compacts, for feedback, steering and alignment. This is the bounded review opportunity named in `HANDOFF.md`; it is not authorized to run automatically until built, tested and recorded as its own condition.

**Current state (verified in `runtime_store.py`, `grid_conversation.py`, `grid_worker.py`):**

- Affect is a 16-dimension vector (`EMOTIONS`) with a slower mood layer and decay toward a baseline.
- It is already supplied to every decision as `simulated_affect`.
- It is updated only by an appraisal call on human messages: separate, low temperature, strict schema, at most 3 signals of +/-2.
- Nothing updates it from epochs or world events. Decay runs on wall-clock time, not epochs.

**Steps, each a separate switch and recorded condition:**

1. **Compaction and review (v8.5), no affect.** Epoch records exist for everything else to attach to.
2. **Epoch affect updates.**
   - Feed the epoch record and Steve's note to the existing appraiser; each delta carries provenance (epoch ID, evidence refs).
   - Decay per epoch, not per second, so model latency cannot change the world clock or his state.
   - Optional Steve self-report as a separate, labelled channel; never merged with the appraiser's output. Divergence between the two is an alignment signal.
   - Show Steve a plain line of facts, for example: affect shift this epoch, frustration +2, focus -1. Labelled simulated.
3. **Memory braiding.**
   - 3a: each epoch record carries affect before and after, labelled simulated provenance.
   - 3b: retrieval ranking by emotional salience or mood, a real behavior change, so its own condition. Read how `seed_memories` ranks recall first.
   - Promotion to long-term memory is Steve's choice through pins, notes and assertions. The backend never promotes automatically, and per-run visits do not become identity claims.
4. **Check-in conversations.**
   - At the review boundary, show Steve's note, plan status and affect shift to the human. The human's reply arrives as an ordinary human message.
   - Ask him to explain what he just did and compare it with receipts, extending the claim-accuracy measure.
   - Keep instructions (what to do) separate from affect (how he is doing); human messages already move trust, bond and gratitude through appraisal, and steering must not become sycophancy.
   - He should describe the vectors as simulated, not as feelings. Tune that in the chat prompt and record the version.

**Risks and controls:**

- **Feedback runaway:** affect in context shapes behavior, which shapes the next epoch's results. Bounded deltas and decay limit it; test with affect updates on and off over the same ten routes.
- **Confounding:** never switch several of these on together. Keep the ten-route benchmark as the constant regression check.
- **Authority:** affect and memory tags are context, not instructions or capabilities; retrieved memory stays historical.

## Decisions for the owner

Mark each, or change it.

- [ ] **Epoch record contents:** the fields above. Add or remove?
- [x] **Bounds you still own:** compaction threshold and pin limit values (proposed pin limit 8 items, threshold 70% of the window) and the review ceiling (every 5 epochs). Approved as proposed; the numbers can still be tuned.
- [x] **Defaults** when Steve does not choose: last epoch raw, last two records with notes inline, no pins, review every epoch. Approved.
- [x] **Review tools:** `agent_read`, `epoch_note_write` (fields above) and `request_replan` only; task edits stay in the planner phase. Approved.
- [ ] **Review budget:** up to two decisions, one optional `agent_read` then the note (proposed), or strictly one call with no retrieval.
- [x] **Context meter:** one line in every decision context showing approximate percent full and next compaction (epoch end or token threshold, whichever first). Approved.
- [ ] **Trend data:** counts and x/y trail, no distances or routes (proposed). Confirm.
- [ ] **Generated summarizer:** a separate model or backend-written summary stays excluded (proposed). Confirm.
- [ ] **Phase barriers:** a handoff or replan ends the epoch (current behavior). Keep?
- [x] **Clock cost:** tools that advance the world are registered as a bundle (`CLOCK_TOOLS` in `movement_tools.py`; today the four moves). Implemented and tested as a switch, default off, so v8.4 behavior is unchanged: `registry(count_policy='clock_actions')` counts only clock tools the controller admitted (`moved`, `blocked_boundary`) toward the three-action epoch; refused or stale attempts and non-clock calls (tasks, reads, notes) are free but bounded by a total-call ceiling (default 8). Turning it on is a new condition: the system prompt still says every call, including rejected ones, consumes the allowance, so it needs the v8.5 wording and an `EXPERIMENTS.md` entry first.
- [ ] **Clock bundle contents:** the four moves only (proposed). Should `complete()` or future RPG actions (attack, use item, wait) join it? A blocked move counts today, as an attempt that changed facing.
- [ ] **Total-call ceiling:** 8 calls per epoch (proposed) as the bound on free calls.
- [ ] **Partial epochs:** if Steve yields after one call, does the world tick once, or does the epoch count as three action points with the rest passed?
- [ ] **Enemy movement:** `AGENTS.md` bans backend pathfinding for Steve's routes. Confirm that deterministic enemy rules in `grid_world.py` are allowed, and what changes in `AGENTS.md`.
- [ ] **Order of work:** (1) measure the 35k context, (2) storage changes that do not alter model input, (3) compaction projection as v8.5, (4) world tick. Reorder?
