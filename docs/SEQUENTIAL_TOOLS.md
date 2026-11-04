# Three-call sequential turns

Approved 4 November 2026 after the operator stopped the v8.3 baseline: try three sequential calls with feedback. This supersedes the earlier deferred eight-call proposal. Implemented condition: `shared-chat-v8.4-three-call-turn`. OpenAI remains unused.

Use a bounded turn of up to three model-selected calls. Each model response may request only one tool. Execute that call, preserve its native result, then supply fresh context before another inference. Rejected requests consume the budget as well. Multiple calls emitted in one response are all rejected and end the turn. This is a call-count bound, not a token budget or an automatic learning/reflection loop.

Each movement remains a zero-argument request for one adjacent cell. Wait for its authoritative settled receipt and presentation acknowledgement before another movement. Rebind the dispatch observation ID before each subsequent inference so later calls use the observation actually presented to the model. Never queue a route or infer the next action.

End the bounded turn on `complete`, `plan_handoff`, `request_replan`, an interruption, a failed/offline/timed-out presentation, a text-only reply, or budget exhaustion. Phase changes must return to the scheduler so it builds the next phase's capability registry. Preserve the explicit distinction between ending a bounded turn and ending the interaction: reaching the call cap alone must not certify completion. Operator Stop and queued human corrections remain higher priority than further calls.

Keep task revisions explicit. Do not fix stale revisions or task arguments automatically. Every call and receipt must retain its own ID and audit entry. Decision/context records must identify the actual supplied evidence for each provider request, rather than making the last request appear to be the only decision in the turn.

Before activation, test receipt-before-next-request ordering, fresh observation binding across two settled movements, sequential task edits with revisions, phase barriers and refreshed registries, `complete`, text-only idle, rejected multi-call output, budget exhaustion, cancellation and provider truncation. Inspect assembled provider messages and native call/result IDs. Run the relevant suite and boundary verifier. Record a new prompt/configuration version.

Activate only while the backend is idle with no queued human request or pending presentation. Preserve chat, tasks, persistent memory, Self state and position. Do not restart the cancelled trials or replay a correction. The isolated real-provider smoke uses a temporary store and synthetic test world; it does not operate Steve's live state. Affect and memory review at the turn boundary remain future work, contingent on this experiment.
