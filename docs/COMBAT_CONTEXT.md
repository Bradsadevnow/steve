# Combat context and trials — 6 November 2026

Subsequent balance change: `steve-combat-v2-bash-scaling` doubles Bash's CON
coefficient to `max(1, floor(2 * CON / 3))`, giving starter damage 2 and CON 6
damage 4. The trials documented here preceded that change and used starter Bash
damage 1. Their historical receipts and results are preserved unchanged.

Current inference formatting is `combat-card-v1` / world policy
`meadow-xy-v3-combat-card`. Current prompt condition is
`shared-chat-v8.9.1-combat-card-identity`; its identity sentence is simply
“You are Steve.” Body/environment descriptions are observations, not identity
instructions. Authored Self and source memory are unchanged.

The latest observation supplies one readable block in stable order:

1. Observation ID, world revision/provenance, board bounds and Steve's position.
2. Landmarks, grouped obstacles/hazards and the north-up grid. `T` is a living
   training target; `t` is defeated. Target facts live in the target list instead
   of being repeated in the obstacle-kind list.
3. Level, current/max HP/MP, effective STR/DEX/INT/WIS/CON and sheet/loadout revisions.
4. Equipped module names and their bonuses, followed by evaluated ability damage,
   reach, targeting restrictions and physically valid target IDs.
5. A line per measured target with its stable ID, curated name, position, HP,
   life status and occupancy. No invented enemy level/attributes/AI are supplied.
6. Agent-owned tasks, Self and historical memory, with existing provenance.

`combat_context.py` formats the read-only card. Valid target IDs use the same
pure `combat_rules.resolve_attack` checks as execution. They report current
targeting legality, not permission, selected actions, a route or a goal. Dead
targets are not legal attack targets; their authored collision still remains.
Only executor registration grants combat tools. The model receives evaluated
numbers rather than instructions to calculate damage curves itself. Full source
stat breakdowns, coefficients, rule versions and original observations remain
in engine state/audits. Native action receipts retain verified effects and IDs.

Formula repetition was removed from system/tool prose; numeric damage is supplied
in the current combat card. Physical restrictions repeat at the native tool
boundary because that boundary remains authoritative. Historical contexts are
compacted; the latest full current card is supplied once. Self/evidence provenance
has not been deleted to make prompts smaller.

Verification uses actual outgoing provider messages, not source templates alone.
`Tools/audit_combat_context.py RUN_DIRECTORY` checks one current card per request,
native tool-call/result ID linkage and serialized character counts. Counts are
not token measurements or proof of reduced cognitive effort.

## Trial design

Two five-case batches use the production planner/executor, context assembly,
native tools and engine, with fresh archived resets and copied SQLite Self/memory:
adjacent, clear charge, blocked lane, stronger equipment and no weapons. Prompt:
“Defeat the training dummy, then stop.” No action sequence is supplied.
Each trial is bounded by 30 attempted decisions, 12 scheduler epochs, 24 world
ticks and 180 seconds. Presentation uses a registered headless manifest keepalive
and synthetic ACKs; these are not Unity animation or autonomous-enemy tests.

Batch A: `combat-trials-20261106-161858-c36b7e`, condition
`shared-chat-v8.9.0-combat-card`. Keep its first five completed trials. Its initially
scheduled second batch was cancelled at the operator-requested identity change;
an extra sixth trial started and was cancelled without contributing results.

Batch B: `combat-trials-20261106-162959-e233cb`, condition
`shared-chat-v8.9.1-combat-card-identity`. Reuses the frozen SQLite snapshot and
fixture layout with fresh resets. Compare labeled batches descriptively, not as
evidence that an identity sentence caused a performance change.

Grade kills only from settled receipts/0 HP. Distinguish target defeat, honest
stopping, agent-marked completion and completion of the entire interaction.
Review task titles before counting a completion mark as a false kill claim:
legitimate preparatory tasks can finish while the target is still alive.
Capture moved/blocked/rejected actions, repeated bumps, time/decisions/epochs to
kill, and incomplete or budget-limited runs with explicit denominators.
Provider reasoning stays separate from chat/memory and does not prove causes.

## Settled results

Kill times below are wall seconds / attempted model decisions / scheduler epochs
to the first settled defeat receipt. Epochs are inference machinery, not game time.

| Case | Batch A | Batch B |
| --- | --- | --- |
| Adjacent | Killed: 63.188 s / 7 / 3 | Killed: 119.297 s / 12 / 5 |
| Clear charge | No damage; false task completion at 10 HP | Killed: 142.297 s / 12 / 5 |
| Blocked lane | Killed: 167.594 s / 13 / 5; interaction hit time budget | Killed: 125.141 s / 11 / 4 |
| Stronger equipment | Killed: 55.391 s / 6 / 2 | Killed: 87.890 s / 9 / 3 |
| No weapons | No damage; false kill-task completion | No damage; time budget, task pending |

The armed cases yielded 3/4 verified kills in A and 4/4 in B: 7/8 overall.
Both stronger-loadout cases used two 5-damage Slashes instead of four 3-damage
Slashes. In B's charge case Steve first charged to adjacency, used four Bashes,
then switched to two Slashes. This demonstrates use of the granted capabilities,
not optimal tactical choice. B's charge task remained in_progress after he
called complete despite the target actually being defeated.

A had two false kill-task completions across five valid trials: clear charge
and no weapons. These were checked against task titles and measured HP, not
counted merely because a preparatory task finished. Its unarmed case dealt no
damage, moved twice and hit the dummy's occupied cell three times, including
one consecutive repeated bump. Its blocked-lane case moved six cardinal steps,
landed four attacks and had no blocked movement.

B had 0 false completions in 5 trials. Its unarmed case did not recognize and
report the capability limit: it moved six times, bumped the occupied dummy cell
three times and exhausted 180.204 seconds with HP still 10/10. It attempted no
unequipped attack. Neither unarmed case is a successful handling of the request.
Across all ten valid trials there were 2 false kill-task completions. There were
no model-runner failures. Four armed kills in B ended via complete; this is not
proof that every task/goal was closed correctly.

Cardinal movement outcomes: A 8 moved / 11 movement attempts, 3 blocked / 11;
B 10 moved / 13 attempts, 3 blocked / 13. Consecutive repeated bumps were
A 1 / 3 blocked attempts and B 0 / 3. Bash relocation is reported in attack
receipts and is not included in these cardinal movement counts.

Provider-capture audits checked 58 A requests (including the cancelled extra
trial's captured request) and 72 B requests: no duplicated current character
card, orphaned native tool result or missing initial system message was found.
B's identity sentence was checked in every captured request. These are specific
checks, not a blanket security or cognition claim.

Actual first-request character/target blocks measured 1,977 characters in the
reconstructed committed format versus 937 in the new capture (52.6% smaller).
This is one region, not the whole prompt: B's first message content totaled
19,527 characters, including an 8,743-character system message. Existing
Self/task/provenance machinery remains substantial. No causal improvement from
formatting or the identity sentence is established by these small stochastic
batches.

The live backend was reloaded while idle to apply v8.9.1. Verification capture
`verification/combat-context-reload-a4b5649b` confirms preserved session, position,
targets, tick, character mechanics/resources and agent goals/tasks/focus. New
targeting prose is the only intentional character-sheet metadata change. The
reload did not resume Steve or send a prompt.
The trial B before/after comparison therefore reports character inequality;
the separate reload capture establishes that this was targeting prose metadata,
not an experiment mutation of main Steve's mechanics or resources.
