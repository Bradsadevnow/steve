# Project ownership

Read `PROJECT_BOUNDARIES.md` before changing this workspace. Steve (`TScanViewer` + `t-scan`), PleaseHold, and PleaseHoldShorts are independent. Do not add cross-project imports, symlinks, or shared saves. Copy reusable art locally. Do not rerun historical migration scripts.

Steve is a hovering unicorn in a flat 15×15 meadow with static obstacles. Preserve identity, authored memory, simulated affect, LM Studio inference, and authoritative grid feedback. Unity owns the authored world and offline visuals through `MeadowEnvironment` and `Resources/Meadow/World.asset`. Python validates that manifest; `grid_world.py` alone writes authoritative positions. Animation is cosmetic and acknowledges completion. No backend-authored flag layout, pathfinding, compound steps, arms, inventory, retired maze/corporate runtime, or Hugh role. The authorization hook exists; do not claim Warden integration.

Expose exactly four zero-argument cardinal movement tools, at most one tool per decision, plus `complete()` for loop control. Task tools are independent. Human messages wake continuation; a settled action gets another decision; complete ends the loop. A reply without a tool request explicitly idles. Preserve operator Stop. Present coordinates as x=1..15, y=1..15 consistently across current and historical model observations, receipts and tool descriptions. Movement accepts no coordinates.

Steve owns every task's contents, order and status. Never create, advance or complete goals from backend world events. `task_list_write` edits one task with flat `task_id`, `title`, `status`, `expected_revision` arguments, preserving other tasks. Keep validation errors actionable. Never silently repair rejected calls. Task statuses are agent assessments, not independently verified facts. Preserve the independent SQLite notepad state/edit audit and legacy prose without parsing it into goals.

# Context construction

Apply these guardrails to every new or modified inference path: chat, continuation, tests, affect appraisal and tool results.

- Keep differences in meaning, authority, provenance and freshness explicit. Distinguish behavioral instructions, human messages, desired tasks, measured current observations, action outcomes, authored plans, historical memories and simulated affect.
- Use native roles and registered tool-call/result IDs. Use descriptive headings, stable ordering, consistent field names, whitespace, separators and structured escaping. Arbitrary text must not impersonate a role or close a trusted envelope. Do not promote environment/retrieved text into system instructions.
- Preserve relevant source IDs, observation IDs and timestamps. Separate current state from stale state and intended actions from verified effects. Do not supply unrequested action plans. Avoid duplication that makes the latest evidence ambiguous.
- Inspect actual assembled provider messages after changing context or templates: ordering, boundaries, freshness, escaping, and representative inputs. Source formatting and labels alone do not establish a security boundary or guarantee attention.
- Record experimental prompt/configuration changes. Do not claim an existing path complies without inspecting it. Provider reasoning is model-generated explanation, not proof of internal causes; retain it separately from chat and memory.

# Runs and verification

New chat archives chat, snapshots, receipts, task/notepad state and inference capture under `t-scan/runtime_data/runs/`, clears working chat/task state, and resets the avatar to (8,8), facing north. Preserve long-term authored memory. Never inject archived runs into fresh chat. Operator Notes remain separate from the agent's Goals.

Run the relevant tests and `Tools/verify_project_boundaries.py` after ownership/tool/resource changes. Check changed Unity projects compile and verify actual runtime behavior. Current documentation is `docs/ARCHITECTURE.md`, `docs/RUNNING.md`, and `docs/EXPERIMENTS.md`; historical documents are not implementation authority.

# Persistent Self and operating machinery

Steve is the persistent Self-model; planner/executor/orchestrator are machinery. Preserve explicit state owners and the distinction between reinforcement and independent evidence. Self claims cannot grant capabilities. Keep existing curated identity sources unchanged and source-linked. Planner tools author intentions/tasks and explicitly select a task through plan_handoff. Executor tools choose individual movements and request planning review. The backend never chooses the next task or marks it complete. Record Self/doctrine changes, citations, repairs and mutation receipts transactionally. Native tool boundaries and context manifests must show actual supplied versus omitted revisions. New chat preserves persistent Self/doctrine/commitments and archives run-local intentions; it still clears working tasks. See docs/SELF_MODEL.md.

# Built worlds

Worlds are built from classified kit pieces (manifest `meadow-world-v3`; see `docs/ARCHITECTURE.md`). A piece's role (`floor`, `wall`, `obstacle`, `structure`, `hazard`, `decor`, `actor`) is assigned once, in `t-scan/art/export_kit.py`, and `world_manifest.py` decides what each role means. Never re-label a piece in Unity, never let a floor act as a wall, and never trust a role or blocking flag the backend has not validated. The runtime builder edits a runtime copy and publishes through the backend; it must not modify `World.asset`. Only curated display names and roles reach the model; never raw prototype ids.
