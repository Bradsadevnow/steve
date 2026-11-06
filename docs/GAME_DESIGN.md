# Steve — AI survival RPG

The owner locked the [stats and scaling direction](STATS_AND_SCALING.md): level-1
10 HP/MP and five base attributes at 1, sword +2 STR, shield +2 CON, stat-scaled abilities,
retirement of the affect machinery, and escalating enemy threat. Sword/shield
remain the implementation slice. That document distinguishes locked decisions
from proposed formulas and supersedes earlier illustrative/fixed-damage text.

Implemented HP rule, 6 November: max HP = 10 + (effective CON − 1). Shield CON 3
gives 12 max HP. Capacity increases do not heal; decreases clamp current HP.

Working design, recorded 5 November 2026, America/New_York.

Working product identity discussed by the owner: **HURT THE ROBOT**. Future proposals are recorded separately in [FUTURE_ROADMAP.md](FUTURE_ROADMAP.md); they are not authorized for implementation and do not replace the immediate equipment-action/training-target work.

The [UI and character builder plan](UI_CHARACTER_BUILDER_PLAN.md) covers the full Fantasy RPG UI replacement, frontend/backend equipment integration, and three alternate chassis with different mount layouts. Blender body renders are prototypes; equipment and combat integration remain planned.

This document records the owner's current game direction. It is a design reference, not a statement that the described mechanics are implemented. We are designing only. Existing runtime contracts stay in force until implementation is explicitly requested.

## The game

An open-ended, escalating RPG where the human builds the character, but the character plays their own life.

> You build the world. You build his character. But you don't control Steve.

> The human determines what Steve can do. Steve determines what Steve does.

Steve tries to survive and find a way out. The player explores builds, observes autonomous decisions, and unlocks possibilities for future characters. The process should be enjoyable and coherent; speed of delivery and shortest-path navigation are not the design goals.

The current direction is an AI survival RPG. Extraction was an earlier framing and remains an optional mechanic to reconsider, not a required core loop or promised victory condition.

## Premise and starting seed

Make the premise literal: Steve is an AI in a world constructed by the human. The builder says they created it because they were bored, gave him a body, and challenged him to find a way out.

An exit may exist, or it may not. There may be another room with another possibility. Neither an exit nor eventual escape is promised. The builder's statements, Steve's theories and independently verified discoveries remain distinct.

Working seed wording, still open to revision:

> I am an AI inside a constructed world.
>
> The person who built it says they did so because they were bored. They challenged me to find a way out.
>
> I don't know whether an exit exists. I don't know whether this is the only room.
>
> I can investigate, try things, talk to the builder, and remember what happens.

The game format includes enemies, equipment and RPG abilities. Exactly how much the starting seed explains about those systems remains to be decided.

The owner proposed replacing existing accumulated memory with this small premise seed. Archiving the existing state first was proposed. No replacement, deletion or identity rewrite is authorized merely by saving this design document, and none is performed by this documentation change.

## Player control and character agency

The human chooses equipment, stat investment, skills and combinations of capabilities. The human can build and change the authored environment. Steve decides how to use the options provided: where to go, what to investigate, which abilities to use and how to respond to danger.

His choices can be clever, mistaken, surprising or cautious. We should be able to understand their consequences without requiring him to follow a predetermined route or perform optimally.

When and where the human may change a build or edit a live world remains open. Do not assume equipment changes are freely available mid-fight, restricted to safe areas, or limited to pre-run preparation.

## World clock — the agreed rhythm

**Time moves when Steve acts in the game world. Think Superhot.**

Thinking, talking, reading memory, updating tasks and planning can continue while the simulation is frozen. An actual world action advances simulation time. Movement, attacks, item use and deliberate waiting are examples.

> Steve acts → the world advances → he observes the consequences → time waits for his next action.

Enemies, projectiles, hazards and other time-dependent world effects share that simulation clock. They do not gain free attacks while the model thinks or while the human talks to Steve. There is no agreed three-action combat window and no separate enemy-turn phase in this design.

The current inference epoch is operating machinery, not the gameplay clock. Do not carry its three-call allowance, planner/executor handoffs or telemetry counter into the fiction as a combat-round rule. A handoff does not spend game time or refill a character's gameplay resources. Implementation may still need technical limits, but those do not define the game clock.

Exact time costs, simultaneous resolution/initiative rules, interrupted actions, cooldown units, animation timing and long actions remain open. Distinguishing a valid physical failure (such as a miss or wall bump) from a malformed/rejected request was discussed; exact cost rules have not been finalized. Operator pause/Stop must remain available.

## Base character and equipment-driven capabilities

Steve starts mechanically simple. He does not inherently know every attack or spell. Equipped modules supply stat changes and available abilities; he decides how to use them.

Locked level-1 baseline (growth formulas remain open):

| Attribute | Example |
|---|---:|
| HP | 10 / 10 |
| MP | 10 / 10 |
| STR | 5 |
| DEX | 5 |
| INT | 5 |
| WIS | 5 |
| CON | 5 |

Attribute names and base values above are locked. Growth formulas and equipment
bonus values remain open; see STATS_AND_SCALING.md.

Class names describe recognizable loadouts rather than mandatory permanent identities. Equipment is modular and cross-class builds are intended. Skills and feats can further modify capabilities; their rules and whether they require particular equipment or proficiency are still to be designed.

Examples discussed, all illustrative:

| Equipment | Possible unlocked actions |
|---|---|
| Sword and shield | Slash, Block, Shield Bash |
| Mage staff | Arcane Bolt, Mana Shield |
| Ranger bow/bowgun | Shoot, Aimed Shot |
| Cleric orb | Heal, Cleanse |
| Rogue blades | Stab, Dual Strike |
| Rocket launcher | Fire Rocket, Reload |

These are design examples, not implemented action definitions. A horn-mounted rocket launcher is an example of the intended absurd combinations, not a verified imported asset.

The intended authority rule is firm: registered game actions come from actual equipment and other authoritative character capabilities. A remembered ability, claimed class or Self belief cannot grant an action. Removing equipment removes its equipment-granted actions. The game independently checks the equipment, resources, targets and cooldowns when an action is attempted.

## Modular art already inspected

`t-scan/art/unicore/unicore_chassis.blend` contains a shared unicorn robot chassis and separate equipment groups with socket metadata. At inspection, twelve module groups were present:

| Right-arm modules | Left-arm modules |
|---|---|
| Warrior blade | Warrior shield |
| Mage staff | Mage tome |
| Cleric mace | Cleric orb |
| Ranger bowgun | Ranger coil |
| Rogue dagger | Rogue hook |
| Greatstaff variant | Lens variant |

Named mounts also exist for the back, shoulders and horn. These groups establish modular art organization, not a completed equipment/ability runtime. In particular, both shield and orb currently specify the left socket; staff and dagger specify the right. Side-swapping, mounting adapters, two-handed occupancy and compatibility rules remain design questions. Do not promise every example combination physically fits unchanged.

## Autonomous enemies and escalating danger

Enemies have their own observations, decision systems and combat objectives. They actively try to kill Steve, within the world's rules and action-driven clock. They do not simply wait as passive targets.

Steve begins significantly stronger than early enemies. As he progresses, enemies become increasingly dangerous through equipment, capabilities and tactical behavior as well as numerical strength. Eventually even optimized builds face lethal threats.

Any specific advantage percentage, strength ratio or difficulty curve discussed so far was illustrative, not measured balance. The architecture for enemy AI, what enemies can perceive, how much they know and how their actions are scheduled remain open. "Agent" does not yet require a separate language-model request for every enemy action.

## One life per character

Death is permanent for that character. Steve does not automatically respawn, prestige or secretly return as the same character with better stats. A future character is a new agent.

The technical treatment of the dead character's persistent Self, records and memories remains to be designed. Preserving an archive, letting a later character learn about a predecessor, and giving that later character the predecessor's firsthand memories are different decisions. Do not silently equate them.

## Run progression and persistent module unlocks

During a life, XP develops weapons/equipment and their capabilities. Equipment
progression is separate from the character's own level and baseline stats; how XP
is allocated to these tracks remains to be designed. The human retains control
over build decisions; the exact procedure for equipping found items is unresolved.

Outside that life, the human owns a persistent **Token** balance. Tokens are game currency, separate from model inference tokens. They fund new possibilities for future characters without resurrecting previous ones.

The owner-confirmed persistent hook is unlocking additional equippable secondary
modules: for example, adding a mage shoulder/back module alongside a sword and
shield. This creates multiclassing through hardware and a second equipment
progression track. The human purchases/equips; Steve chooses how to use the
resulting capabilities. A persistent unlock is separate from an item's run XP or
rank; cross-death persistence of those levels/upgrades remains undecided. See
[the roadmap addition](FUTURE_ROADMAP.md#6-equipment-xp-and-persistent-hardware-multiclassing).

The core loop:

1. The player uses available progression options to prepare a character and shape/select a world.
2. The character explores, investigates and fights autonomously.
3. Verified progress contributes to player rewards while the world becomes more dangerous.
4. The character's life ends permanently.
5. The player's earned progression remains available when building a future character.

Possible unlocks include equipment modules, build options, starting resources, regions and enemy types. Favoring a broader range of tactical possibilities over unlimited guaranteed-survival multipliers was discussed as a balancing direction, not a finished economy formula.

Rewards must be grounded in authoritative events, not Steve's claims or task completion marks. A single defeat must not produce duplicate awards. Numerical examples such as 500 or 600 Tokens for a boss were jokes/illustrations, not prices or payouts.

**Unresolved Token rules:** an earlier version banked currency immediately per defeated enemy; a later version awarded Tokens after the run based on progress. Payout timing and formula have not been settled. Persistent secondary-module unlocks are now the agreed hook; whether a purchase unlocks a module, equip capacity or both, and how expendable items/manufacturing might fit, remain open. Equipment loss and XP/rank carryover on death, and any purpose for extraction, still require design.

## Tone and available worlds

The tone combines sincere character agency and consequences with cheerful, increasingly ridiculous environments and equipment. Steve can form opinions about the situations and builds the human gives him. Familiar fantasy and cursed everyday places belong in the same game.

Inspected Unity catalogs contain 93 pieces across:

- Dungeon: 25 environment pieces and five enemies: goblin bomber, stone golem, mimic, skeleton knight and slime.
- Cursed swap meet: 29 pieces including five enemies: cart monster, gnome walker, haggler, possessed mannequin and bootleg mascot.
- Cursed high school: 34 pieces including five enemies: hall monitor, rogue locker, mystery-meat blob, pep-rally wombat and substitute teacher.

Environment meshes/catalogs/thumbnails are imported into the builder system. Enemy meshes are cataloged as actors, with actor placement excluded by the inspected builder. The class chassis/modules are Blender source art. Imported art does not establish combat mechanics, animation readiness or ability integration. A royal mimic/Mimic King and forehead ballistics are part of the discussed flavor; specific boss art/rules remain unverified.

## Memory and character history

The seed gives authored starting knowledge. Experiences during play should give the character a history, with provenance separating observations, human statements, plans, beliefs and verified effects. The character may remember a lost weapon without regaining its abilities through memory.

How experiences are selected, written, corrected, retrieved and forgotten is still a central design task. Existing backend memory rules are implementation defaults, not a settled design for this game. The constellation currently displays imported records by category; it is not a complete view of current memory or a semantic map of the character's mind.

The ten isolated probes documented in [CHAT_PERSISTENCE_PROBES.md](CHAT_PERSISTENCE_PROBES.md) completed. They demonstrated specific chat recall, note/commitment persistence, working-state clearing and restart behavior. They also exposed inaccurate explanations of those mechanisms. Do not label those narrow checks proof of general companion continuity or automatic experience consolidation.

## Demonstration idea, not a delivery deadline

A possible 90-second demonstration: Steve wakes in a room; the human explains the premise; the human edits the world; Steve investigates and encounters an enemy; a concrete callback shows remembered experience; the character builder reveals modular builds and increasingly absurd zones.

The owner explicitly prefers a happy, correct, joyful design process over the quickest route to a demo. This sequence is a pitch illustration, not an implementation order or minimum-feature mandate.

## Open decisions for further discussion

- Final seed text, starting knowledge and the archive/replacement procedure for existing memory.
- Character identity/Self lifecycle after death, archives and any information inherited by later characters.
- Memory writing, provenance, correction, retrieval, forgetting and owner inspection.
- Final attributes, leveling, skills, feats and equipment/proficiency requirements.
- Equipment slots, side-swapping, multi-mount modules and compatibility.
- When the human can alter builds or the world during play.
- World-action time costs, resolution order, enemy perception/AI and projectiles/effects.
- Token award timing/formula, purchase permanence and item loss on death.
- Room/zone transitions and any extraction mechanics.

Current implementation references remain [ARCHITECTURE.md](ARCHITECTURE.md), [RUNNING.md](RUNNING.md) and [EXPERIMENTS.md). This design may guide explicitly authorized future changes; it does not by itself alter current ownership, source identities, saved state or runtime capabilities.
