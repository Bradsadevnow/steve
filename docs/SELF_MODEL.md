# Persistent Self and operating machinery

Steve is the persistent Self-model. Planning, execution, orchestration, retrieval and presentation are machinery through which it operates.

## Representation and authority

Self records have stable IDs, dimensions (identity, agency, continuity, competence, beliefs, intentions), scope, current revision, source references, status and a change reason. Initial curated identity statements are preserved verbatim with their original event references. Existing source memories are not rewritten. No old prose is automatically reclassified as competence, commitments or firsthand experience.

The projection combines those records with independently owned inputs: current registered capabilities, controller receipts, agent-authored intentions, the current explicit plan, task state and scoped doctrine. A capability self-claim cannot register a tool. Attempt counts are controller measurements for the current run, not general competence estimates. Authored assessments can disagree with the measurements and remain inspectable.

A belief's held/contested/retired status is distinct from its emergent/provisional/established reinforcement status. One distinct decision's citation makes a revision provisional; three make it established. Repeating the same citation in one decision counts once. This records reliance, never truth. Changes to the statement create immutable revisions. Explicit supports/contradicts/derived_from links retain source and assertion-revision references. Repairs require a current revision and a reason; invalid or stale writes leave the accepted record unchanged. Mutation call IDs are idempotent and cannot be reused with different arguments.

## Intention, plan and execution

An intention records what Steve wants and why, with agent-authored status and either run or persistent lifetime. A task records work. A plan handoff selects an existing unfinished task, its task-list revision, an agent-authored reason, an explicit criterion and execution instructions, optionally linked to a durable intention. The backend never turns a human sentence into these records.

New human messages route to planning. The planner authors or revises records, chooses a task, supplies its reason and calls `plan_handoff`. A short plan itself represents an intention; creating a second intention record is optional, for commitments that warrant their own lifecycle. The executor receives that plan and current observations and requests one cardinal step at a time. It calls `request_replan` when achievement, failed progress or another issue needs review. The planner decides task updates and the next handoff. `complete()` ends continuation; text-only replies idle; operator Stop remains available. A stale task revision, linked commitment revision, run identity or world manifest routes the existing plan to review without selecting a replacement.

The built-in visit criterion assesses settled exact-cell occupancy for the explicitly named landmark, current run and matching manifest. It does not infer a criterion from a task title, change task statuses, prove arbitrary instruction text, or prove an unspecified ordering constraint. Manual criteria remain unverified. A completion claim may therefore remain unsupported.

## Disclosure and context

Every decision projects eligible Self/doctrine/intention records under a 12,000 serialized-record-character budget. Its manifest lists eligible, supplied and omitted revision references; task/plan revision; current observation and world manifest; capability schema hash; recent controller evidence; and historical tool-retrieved references that remain in native messages. Eligibility is scoped by run/world/global identity. Supplied does not mean understood.

Actual outgoing provider requests and separate `context-manifests.jsonl` record disclosure. Appraisal and action requests are distinguished, including actual registered tools for the request. Provider thinking remains separate from conversation and autobiographical records. The orchestrator journals phase, supplied context, command and receipt; unresolved dispatches are flagged for review after restart instead of replaying effects.

## Persistence and reset

Agent records, revisions, citations, evidence and decision journals are additive tables in the existing private runtime SQLite database. New chat preserves Self, doctrine and persistent intentions; it archives run intentions and clears working tasks as before. Run-scoped claims remain historical and are excluded from another run's projection. Previous plans cannot execute in a new run. This preserves distinct lifetimes without promoting temporary flag tasks into permanent identity.

## Inspection

Unity's Self tab opens on a read-only State view: selected focus and reason, unfinished tasks, commitments, agent-authored self-assessments and beliefs, measured recent experience, and capability summaries. It never selects a pending task automatically. Curator-written identity descriptions, machinery labels, reinforcement counters, disclosure metadata and revision history are under Inspect. Empty assessment sections stay empty; presentation does not create Self records. The /self-view endpoint is an operator projection and is not supplied to inference.

Read-only loopback endpoints:

- `/self-view`: read-only display projection with human-readable summaries and separate inspection data.
- `/agent-state`: stored records, current phase, plan, capabilities and recent decision journals.
- `/agent-state/graph`: assertion/source/revision nodes and typed edges.
- `/agent-state/history?owner=self&id=<id>`: immutable revision history. Other owners include doctrine, intention, plan and orchestration.

`Tools/verify_agent_interfaces.py --output <new-directory>` exercises real LM Studio assertion/read/cite/repair tools in an isolated store. It is bounded and does not grant movement tools. Its synthetic assessment is not a real competence finding. New architecture behavior has not been established by the earlier ten-trial batches.

World state still uses GridWorld's existing JSON/log persistence. Its effects and SQLite journals are not one atomic cross-store transaction. This implementation supports safe review after interrupted dispatch, not historical full-state replay or automatic semantic verification of arbitrary claims.

## Initial live verification

The isolated real-provider assertion/read/cite/repair check passed. The initial v8 and v8.1 movement smokes stalled before movement on the mandatory separate intention prerequisite; these attempts remain separate local captures. v8.2 removes that duplication by requiring an agent-authored reason in the handoff and making the durable commitment link optional. This is a recorded interface change, not evidence that navigation reliability improved.

The v8.2 real-model smoke subsequently passed with the ordinary request to visit blue and record completion: task authored â†’ plan and reason handed off â†’ three east steps and two north steps â†’ agent-requested planning review â†’ agent task completion â†’ complete. All movement presentations settled in Unity. This is one smoke test, not a new ten-trial success-rate estimate. The final disclosure policy adds explicit historical-memory eligibility/supply, reinforcement snapshots and hashes of actual provider messages.
