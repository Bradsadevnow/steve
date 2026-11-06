# Locked stats and scaling direction

Owner-approved design and starter implementation, 6 November 2026. The latest
base-1 decision supersedes the earlier base-5 proposal. Authoritative stats,
equipment bonuses, scaling, live sheet and engine-backed draft previews have
shipped. Active affect appraisal/context and visual polling are retired;
historical affect records, identity, Self and authored memories are preserved.
Level progression, temporary effects and enemy AI remain future work. CON-based
maximum HP is implemented: 10 + (effective CON − 1).

The accompanying [UI plan](UI_STATS_AND_EQUIPMENT_PLAN.md) maps the installed
fantasy assets to a compact corner pane, expanded sheet and equipment comparison,
with confirmed/draft values and presentation ownership kept explicit.

## Locked decisions

- Level 1: 10 maximum/current HP, 10 maximum/current MP; STR, DEX, INT, WIS and
  CON each start at 1. The sword adds +2 STR; the shield adds +2 CON. Other
  prototype modules add no stats or combat abilities in this slice.
- Stats become the authoritative mechanical character sheet, replacing the
  existing affect system. Retire mood-appraisal inference calls and mood-driven
  visuals as part of that conversion. Do not relabel moods as attributes.
- Preserve identity, authored memories, Self, personality, goals, operator Stop
  and the existing authority/provenance boundaries.
- Effective stats = base stats + level gains + equipped modifiers + temporary
  modifiers. Unequipping removes its bonuses. Level gains persist within that
  character's life. No automatic practice-based stat gains are part of this slice.
- Equipment grants available actions; stats scale those actions. High STR/INT
  alone cannot grant an unequipped attack/spell. The human owns build choices.
- STR governs physical melee; DEX ranged/accuracy/evasion; INT offensive magic;
  WIS healing/protection/mana capacity; CON health/toughness/shield abilities.
  Systems beyond the starter slice are design roles, not implemented mechanics.
- Abilities use configurable sliding stat curves rather than permanent flat
  damage. Coefficients, caps and rounding are tunable data, not separate hardcoded
  formulas scattered through UI, context and execution.
- First functional scaling slice remains sword and shield. Slash scales with STR;
  Shield Bash scales with CON. Slash damage equals effective STR; Bash damage is
  max(1, floor(effective CON / 3)). With the starter pair, STR/CON are both 3:
  Slash deals 3 and Bash deals 1. Each equipped module instance contributes its
  bonuses once; duplicate compatible modules stack bonuses, not extra turns.
  Slash remains adjacent/cardinal. Bash retains its clear cardinal lane, target
  within 3 squares, stop-adjacent behavior. Scaling damage does not change range
  or grant extra actions without a separately designed rule.
- Steve levels during a run. Enemy threat escalates until it eventually outpaces
  his growth and can kill even optimized builds. Starting advantage target: Steve
  is 80% stronger, meaning 1.8 times enemy effective power (enemy about 56% of his),
  not enemies at 20% of his strength. Effective power must be calibrated through
  combat outcomes, not assumed equal to the sum of stats.
- Escalation follows encounter/zone progression, not model thinking time. Game
  ticks remain action-driven; inference epochs are operating machinery.

## Locked ownership boundaries

Owner clarification, 6 November 2026: keep the agent isolated from game machinery.
These are implementation requirements. The starter implementation separates
character stats, trusted module definitions, pure combat evaluation and human UI;
the existing grid controller continues to own position and world effect commits.

| Owner | Owns | Boundary |
| --- | --- | --- |
| Weapon/equipment module | Its own meshes, effects, attachment offsets, compatible mounts, stat modifiers and granted ability definitions | Attaches to a body socket. Declares trusted rules; cannot write character position, target HP or world time. Unequipping removes its grants and bonuses. |
| Steve character | His character sheet: base/effective attributes, current/max resources, equipped module instances and body/socket configuration | State belongs to the character domain, persisted and validated by the game. The model cannot author its own numerical stats or grant capabilities. |
| Steve perception | His current, source-linked view of the world, including observable enemies, equipment and measured action results | Receives an explicit observation projection, not direct access to the world store, hidden enemy plans or enemy controller internals. Visibility rules remain to be designed. |
| Steve agent / persistent Self | Memory, identity, intentions, decisions and choice of an available action | Reads supplied observations and submits an action request. Claims and plans never mutate simulation state. Thinking does not advance game time. |
| Game world and enemy domain | World layout, occupancy, enemy instances, enemy sheets, enemy observations, controllers and objectives | Each enemy acts through its own permitted perception/action interface. Enemy state and private context do not live in Steve's memory or planner. Current dummies remain static until enemy behavior is implemented. |
| Game engine / action resolver | Admission, equipment/resource/target/lane checks, shared scaling evaluation, damage resolution, action ordering, clock advancement and committed receipts | Computes verified effects using current authoritative state. Python remains mechanical authority; `grid_world.py` remains the sole authoritative position writer during decomposition. Unity animates accepted results and acknowledges presentation. |
| Human builder and UI | Draft world, start, body and equipment choices; previews and explicit Apply | Sends configuration choices through validated interfaces. Preview values are labeled draft; UI never becomes a second rules authority. |

The character owns its sheet and perception as domain objects; that does not give
the inference process permission to edit them. Module ownership likewise means
cohesive assets and definitions, not independent authority to apply damage.

The runtime boundary is: equipped modules expose capabilities → Steve receives
his sheet and observation → Steve requests one action → the game validates and
resolves it → committed results update the affected characters/world → fresh
observations and receipts return to the agent. Future enemy decisions use their
own corresponding boundary. One admitted action advances the world clock; the
enemy scheduling policy must be specified before autonomous combat is added.

Keep presentation, module definitions, character state, perception, agent context
and simulation resolution independently replaceable and testable. Shared trusted
rule definitions may be read across these boundaries; mutable state has one owner.
Do not put combat execution inside prompts, model-specific code, UI widgets or
individual visual scripts. Do not duplicate stat formulas between these layers.

## Implemented starter slice

`character_stats.py` owns versioned character attributes/resources and their
projection. `character_mechanics.json` owns sword/shield modifiers and ability
definitions; the generated local character catalogs carry those module records.
`combat_rules.py` evaluates the integer numerator/denominator curve, rounds down
and applies its minimum. `character_rules.py` validates equipment and composes
the public sheet. `grid_world.py` validates/commits actions and is still the only
position writer. The model cannot submit stat totals, damage or new capabilities.

The state file retains private `character.stats` source state; public observations
and receipts expose `character.sheet`, including base/level/equipment/temporary/
effective values and evaluated abilities. Current temporary bonuses are always
zero; no effect stacking or expiry semantics were invented. Level is initially 1;
there is no XP, level-up allocation or growth loop yet.

Max HP is 10 + (effective CON − 1): base CON 1 gives 10, shield CON 3 gives 12.
MP maximum remains 10. Increasing capacity never heals; decreasing it clamps
current HP to the new maximum and persists the clamp, preventing gear-swap healing.
Restart and New Chat preserve current resources. Resource rules are versioned as
`steve-resources-v2-con-hp`; old saves reconcile once without resetting the run.
These attacks retain their existing no-MP-cost behavior. Enemy dummies remain
world-owned stationary 10 HP targets.

`POST /character/preview` accepts only versioned configuration choices and an
expected character revision. It validates and evaluates without saving, granting
abilities, affecting targets or ticking time. Apply uses the same evaluation and
preserves character resources. Unity renders returned values and never evaluates
the damage curve. Stale asynchronous preview responses are discarded.

Attack receipts retain curve coefficients, scaling stat/effective value, sheet/
loadout/rule revisions, nominal versus actually applied damage, target HP before/
after and tick. Overkill cannot remove more HP than the target has. Range, lane,
unequipped and stale-call admission rules remain unchanged.

Legacy v1 equipment saves migrate to v2 once, retaining body/equipment, session,
position and clock. Missing stats initialize explicitly to the new baseline;
character revision increments so old plan handoffs require review. The migration
record commits in the world snapshot; the receipt journal remains a separate
append. Unknown save versions fail instead of silently discarding character state.
Known v1 presets become visibly reviewable v2 drafts before Apply.

Condition: `shared-chat-v8.8.0-character-stats`. Active inference no longer schedules
affect appraisal or supplies `simulated_affect`; Unity no longer polls affect for
the body. Legacy formatting and `/runtime` affect projection remain marked
retired for historical compatibility, without being used as current game stats.

## Historical implementation proposal — superseded by the shipped slice above

1. Define the character, module, perception and engine interfaces above first.
   Add versioned base/effective stat and resource state owned by the character
   domain and persisted in the authoritative snapshot. Preserve accepted equipment and existing saves; initialize
   missing fields explicitly and record the migration. Define reset/death/level
   semantics independently rather than silently altering New Chat.
2. Add trusted module stat modifiers to the shared equipment catalog. Calculate
   effective values only in Python; Unity previews the same rule definitions and
   displays confirmed values after Apply. Recommended first pass: starter sword
   and shield grant actions without bonus stats so the level-1 anchors are easy
   to verify. This zero-bonus recommendation is not a finalized item balance rule.
3. Add one bounded curve evaluator. A candidate data shape is reference_stat=5,
   damage_at_reference=3/1, per-stat weights, minimum/maximum and a rounding policy.
   A candidate curve is anchor + coefficient * (effective_stat - 5), clamped to
   configured bounds. Linear/piecewise curves, actual coefficients, rounding and
   caps remain to be chosen. Do not accidentally lock these examples as balance.
4. Route Slash and Bash through that evaluator. Record relevant effective stats,
   loadout/rule revisions, evaluated damage, HP before/after and actual damage
   applied. Validate current equipment and target again at execution.
5. Wire the real character sheet to base/bonus/effective stats and authoritative
   HP/MP. Specify how maximum-resource changes affect current resources; avoid an
   equipment-swap healing exploit. Resource formulas and sword/shield MP costs
   are not settled by this document.
6. Remove affect appraisal scheduling, mood context and mood-driven presentation
   deliberately. Keep historical affect records as historical data; do not rewrite
   them into stats or let their values leak into combat calculations. Inspect
   actual assembled model messages after changing context.
7. Run sword/shield dummy probes over several stat values, including equipment
   removal, temporary modifiers, bounds, stale calls, restart and clock behavior.
   Then calibrate one enemy archetype to the intended starting advantage before
   designing broad skill trees, leveling allocation or an escalation formula.

Remaining balance choices: XP thresholds, gains/allocation per level, player/enemy
growth curves, encounter rewards and escalation triggers, exact stat/resource
formulas, temporary-effect stacking/durations, armor/accuracy/evasion rules,
ability costs and future caps. Starter damage rounding/formulas are locked above;
the earlier candidate curves and base-5 examples below are not current rules.

## World-builder start position

The World workspace exposes Start (P), in addition to the pin rail tool. Click a
valid cell, then Apply the world. Applying a changed start moves Steve there and
saves the location for New Chat/reset, without clearing the current chat or run.
Draft edits do not move him until applied. Existing occupancy/hazard and
reachable-flag validation, Undo/Redo and backend-confirmed publication still apply.
