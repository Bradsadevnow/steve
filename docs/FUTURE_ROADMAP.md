# HURT THE ROBOT — Future Roadmap Additions

**Status: Design proposals only. Not authorized for implementation.**

Add the following concepts to the game's future roadmap. Preserve existing architecture and current development priorities. Do not implement these features yet.

## 1. Autobiographical Run Export

**Priority: Planned — before external agent import**

Every completed roguelike run should eventually generate a portable record of the character's experience.

### Export contents

**Autobiographical PDF**
- Run identity, environment, equipment and character configuration.
- Significant encounters, discoveries, battles, accomplishments and failures.
- Verified actions and outcomes derived from authoritative controller receipts.
- Agent-authored reflections, beliefs, intentions and assessments.
- Final run outcome, including death when applicable.
- Clear distinctions between verified events, agent interpretations and unverified claims.

**Persistence Snapshot**
- Relevant Self records and their immutable revisions.
- Beliefs, intentions, memories and supporting evidence.
- Agent-authored assessments and provenance references.
- Run-specific continuity information.
- Referenced controller receipts and event IDs.

Exclude secrets, credentials, authentication tokens and unrelated private runtime data.

### Purpose

Allow players to export an adventure and discuss it afterward with an AI assistant.

The package should supply enough context for an AI to examine what occurred, what the character believed, and why particular decisions may have been made.

**Important limitation:** Supplying the export to an external AI does not guarantee identity continuity, genuine memory inheritance or that the external AI is the original character.

The promise is portable, inspectable experience data—not universal agent persistence.

## 2. Bring Your Own Agent (BYOA)

**Priority: Future expansion — explicitly out of current scope**

Eventually allow users to connect or import their own AI agents into *Hurt the Robot*.

### Intended experience

- Connect an externally operated agent to the game.
- Provide the agent with a compatible game body and registered capabilities.
- Let the agent navigate, interact, fight and experience the simulated world.
- Keep authoritative physics, combat rules, equipment and action execution under the game controller.
- Generate an autobiographical record and persistence snapshot after the run.
- Return portable experience data to the owner for independent ingestion into their agent's memory system.

### Architectural considerations

- Model-agnostic agent interfaces and adapters.
- Agent identity and session isolation.
- Bounded, sandboxed tool access.
- Separation of imported agent memory from authoritative world state.
- Explicit user control over memory import/export.
- No assumption that third-party agents share Steve's Self architecture.

**Constraint:** External agent compatibility is not a prerequisite for launching the Steve-based game. Support can be added incrementally after the core experience works.

## 3. The Sims–Style Agent Sandbox

**Priority: Future gameplay expansion**

Expand *Hurt the Robot* beyond combat encounters into a persistent, player-authored sandbox.

### Core concept

**The human controls the world and character configuration. The AI controls its own behavior.**

Players can construct environments, furnish spaces, place objects and characters, establish challenges, and observe what autonomous agents decide to do.

### Possible features

- Homes, rooms, furnishings and interactive objects.
- Modular environments and custom world layouts.
- Character equipment, customization and progression.
- Autonomous interactions with environmental objects.
- Agent-to-agent communication and social interactions.
- Persistent world objects and environmental consequences.
- Player-authored scenarios with or without combat.
- Rube Goldberg contraptions, traps, triggers, machinery and environmental puzzles.
- Multiple independently instantiated agents occupying a shared world.

The sandbox should support peaceful, absurd, challenging and hostile environments without requiring every scenario to involve combat.

### Intended player experience

The player acts as a world builder, character designer and scenario creator.

The agent independently decides what to investigate, how to interact, whether to cooperate, and how to respond to the circumstances it encounters.

The player may create unfair scenarios, but physical outcomes should remain governed by consistent simulation rules.

### Connection to the core game

The existing world builder and Steve's autonomous character architecture form the starting foundation.

The Sims–style sandbox is an expansion of that foundation, not a replacement for the survival RPG.

## 4. Portable Character Histories and Community Features

**Priority: Long-term exploration**

Autobiographical exports could eventually support:

- Shareable adventure journals.
- Collectible run histories.
- Character memorials after permanent death.
- Community-created worlds and challenge courses.
- Shared scenarios that different agents can independently attempt.
- Comparisons of how different agents approach the same environment.
- Optional continuity packages for future agent sessions.

These are potential features, not committed deliverables.

## 5. Product Positioning

*Hurt the Robot* may eventually support several overlapping audiences:

**RPG players:** Build Steve's capabilities and watch him survive increasingly difficult encounters.

**Sandbox players:** Create worlds, homes, traps, puzzles and strange scenarios for autonomous characters.

**Agent enthusiasts:** Observe their own agents operating inside an interactive simulation, once BYOA is supported.

**Creative communities:** Build and share environments, challenges and adventure histories.

**AI researchers and hobbyists:** Examine bounded agent behavior, decision-making, memory and adaptation using authoritative execution records.

These audiences are hypotheses to validate, not established markets.

### Central identity

**HURT THE ROBOT**

*You build the world. You build his character. But you don't control Steve.*

The initial product remains centered on Steve and a functioning autonomous RPG experience.

The larger vision is an extensible sandbox where players create environments, configure characters, observe autonomous behavior, and preserve the stories that emerge.

## 6. Equipment XP and persistent hardware multiclassing

**Priority: Future progression design — owner-confirmed direction, 6 November 2026.
Not authorized for implementation.**

Separate progression within a run from persistent expansion of the player's build
options:

- **Run XP develops equipment.** Weapons and other equipped modules can level
  during a run. This is distinct from Steve's character level and baseline stats;
  do not treat every progression track as one global level counter.
- **Persistent Tokens unlock additional equippable modules.** Secondary modules
  provide the persistent progression hook and expand the capabilities the human
  can assemble around a character's main weapon loadout.
- **Multiclassing comes from hardware.** A sword/shield character could add a mage
  module on a compatible shoulder or back mount. The extra module supplies its own
  capabilities alongside the weapons; no permanent Warrior/Mage menu selection
  is required. This is a second equipment progression track, not a second agent.

Example future build: Warrior Blade and Warrior Shield on the arm mounts, a Mage
module on a compatible shoulder, with remaining mounts empty. The human chooses
what to unlock and equip; Steve decides how to combine the available abilities.
The quoted idea of Steve independently shopping with Tokens is not adopted:
Tokens remain player-owned and purchasing decisions remain human-controlled.

Equipment XP/rank belongs to the relevant equipment instance or progression
record, not Steve's memory or a UI widget. Unequipping must not silently erase an
item's earned progression; define its lifetime explicitly. A persistent module
unlock and its current run's XP/rank are separate records. **Whether equipment XP,
module levels or upgrades survive death is still unresolved.** Persistent Token
ownership does not by itself settle those questions or resurrect a dead character.

The game engine must award XP/Tokens from verified events, validate unlocks and
mount compatibility, derive abilities from the actual equipped module/rank, and
revalidate at execution. Character stats still scale the supplied abilities;
owning an unlock or remembering a former ability cannot grant an unequipped tool.
Thinking, chat, memories and task completion claims do not generate rewards or
advance the game clock.

Design questions for a later pass:

- XP sources and allocation between weapons, support modules and character level.
- What equipment ranks change: modifiers, ability parameters or new capabilities.
- Whether a Token unlock buys the module, extra equip capacity or a combination;
  existing body socket metadata is not yet a progression economy.
- Unlock prices, award timing, prerequisites, active-module limits and compatibility.
- Progression lifetime across unequip, loadout swaps, run boundaries and death.

Keep existing sword/shield dummy experiments as the immediate development slice.
This records the progression direction without adding XP, shops, new slots, mage
abilities or persistent unlocks to the runtime.

## Development Constraints

- Do not implement these additions yet.
- Do not change existing runtime contracts.
- Preserve separation between the Self, controller, game simulation and player progression.
- Keep verified events separate from agent-authored interpretations.
- Do not promise external-agent identity continuity.
- Do not make BYOA a dependency of the base game.
- Treat monetization and audience expansion as future decisions requiring validation.
- Continue prioritizing usable combat mechanics, equipment-granted abilities and training-dummy experiments.

**Immediate development objective remains unchanged: establish whether Steve can effectively use equipment-granted actions against training targets before designing a larger skill or leveling system.**
