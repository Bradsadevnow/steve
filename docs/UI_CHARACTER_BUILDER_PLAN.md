# Fantasy UI and character builder

**Current UI design extension, 6 November 2026:**
[UI_STATS_AND_EQUIPMENT_PLAN.md](UI_STATS_AND_EQUIPMENT_PLAN.md) inventories the
installed pack and specifies the compact corner stats pane, expandable sheet,
module details, draft comparison and their ownership boundaries. It supersedes
older presentation proposals below where they differ.

**Implementation update, 6 November 2026:** the fantasy UI theme, Character
workspace, five bodies, twelve module visuals, compatibility/conflict handling,
presets, acknowledged loadouts, dynamic sword/shield tools, game ticks and
stationary dummy damage are implemented. Other module actions, leveling and
autonomous enemy combat remain outside this pass. See `ARCHITECTURE.md` for the
implemented contract. Original planning text below is retained for design context.

Design and implementation plan, 5 November 2026. UI/equipment/combat changes are
planned, not implemented. The three alternate bodies are rendered Blender art
prototypes. Existing runtime rules remain in place until their replacement is
implemented and verified.

## Full UI replacement

Use Moon Tribe's Fantasy RPG UI Pack across the whole current UI: dark painted
panels, steel borders, crimson primary actions, and consistent selection states.
Preserve compact layouts and painted artwork proportions. Decorative elements
ignore mouse events. Decorative fonts serve headings; chat/evidence stay readable.

| Current element | Replacement |
|---|---|
| Steve card | Character portrait frame, live state, coordinates |
| Watch/Build | Compact fantasy mode tabs |
| Chat drawer/input | Framed conversation and controls |
| Goals/Self/Log/Debug | Matching journal panels |
| Memory constellation | Arcane-map frame, existing graph, source-linked detail |
| Builder palette | Item cards, category tabs, selection frames |
| Flags/Delete/Undo/Apply | Consistent selected/disabled/pending/error treatments |
| Tooltips/notices | Compact information panels |
| Thought/speech bubbles | Matching style with their meanings kept distinct |

Preserve quick-click placement, half-second hold-to-rotate, right/middle pan,
scroll zoom and UI/world hit-test separation. Never invent HP/MP for decoration.

## World and Character workspaces

World retains map editing and publishing. Character adds a rotatable body preview,
body selector, named sockets, compatible module library, module details, resulting
capabilities, validation errors, Save preset, Revert and Apply. Class presets fill
ordinary slots instead of imposing permanent class restrictions.

World saves and character presets remain separate. Draft visual previews are
distinct from backend-confirmed live equipment.

## Baseline plus three alternate bodies

Keep the original Uni-Core and add the following configurations. All retain the
authored unicorn head and hover identity. Brass collars show mounting sites.

| Body | Configuration | Mounts | What it tests |
|---|---|---|---|
| Original Uni-Core | Existing hover chassis | Existing left/right tool, shoulder, back and horn sockets | Baseline sword/shield and cross-class builds |
| Skimmer | Compact scout shell with side thrusters | `ventral_tool`, `dorsal_utility`, `horn` — 3 | One light tool, utility and focus; constrained loadouts |
| Bulwark | Broad carrier, four tool couplings | `left_upper`, `right_upper`, `left_lower`, `right_lower`, `left_back`, `right_back`, `horn` — 7 | Independent tool pairs, shared occupancy and conflicts |
| Wisp | Orb shell with three floating satellite couplings | `orbit_1`, `orbit_2`, `orbit_3`, `horn` — 4 | Radial arcane equipment; no native hand-tool mounts |

These are proposed configurations, not balance decisions. Extra mounts do not
grant extra turns. No inherent HP, damage or speed bonuses are implied. Keep
logical movement on the existing grid; model size does not silently change
collision footprint.

Body definitions specify stable IDs, socket transforms/types, compatible module
types and visual footprint limits. Modules specify occupied mounts and attachment
transforms. Two-mount items reserve both sites; adapters are explicit.

Body switching proposes a remapping. Preserve only equipment with an explicitly
valid mapping, list unresolved items and require resolution before Apply. Never
silently drop or relocate equipment. Presets record body ID and catalog version.
Preview socket states: free, occupied, incompatible. Mount markers grant no actions.

Source and previews, relative to the workspace:

- Existing source, unchanged: `t-scan/art/unicore/unicore_chassis.blend`.
- Reproducible build: `t-scan/art/unicore/build_body_variants.py`.
- Alternate bodies: `t-scan/art/unicore/body_variants/unicore_body_variants.blend`.
- Mount metadata: `t-scan/art/unicore/body_variants/body_catalog.concept.json`.
- Comparison: `t-scan/art/unicore/body_variants/chassis_lineup.png`.
- Individual previews: `skimmer.png`, `bulwark.png`, `wisp.png` in that directory.

These still need export, scale/attachment QA and Unity integration. Renders do
not establish rigging, action compatibility or gameplay readiness.

## Frontend additions

Export chassis, separate modules, sockets and thumbnails into local Steve Unity
resources. Use stable IDs and shared versioned equipment definitions; Unity also
maps IDs to visual assets. Add independent character drafts/presets, compatibility
filtering, build summaries and body-change conflict resolution.

Submit character ID, expected revision, catalog version, body ID and module-to-mount
assignments. Show Draft → Validating → Awaiting confirmation → Applied, or Rejected.
Keep rejected drafts with actionable errors. Upgrade world Apply to this explicit
acknowledgment flow too; it currently marks the local draft clean before backend
confirmation.

## Backend additions

Python loads trusted versioned body/module/action definitions. The client sends
equipment choices, not arbitrary damage values or executable tool definitions.
Validate known IDs, revisions, body sockets, mount types, multi-socket occupancy,
adapters and complete-build conflicts.

Proposed initial Apply rule: loop stopped, no inference dispatch or pending world
action/presentation. Enforce this in the backend as well as the UI. Persist accepted
configuration/revisions and issue receipts. Make retries idempotent.

Derive capabilities from confirmed equipment, register only available execution
actions, and revalidate equipment/resources/targets when called. Stale calls from
before a loadout change cannot bypass validation. Removing a shield removes Bash.
Current observations and receipts include equipment/loadout revision and available
capabilities. Historical memory remains separate from current physical capability.

Keep native tool boundaries, provenance and actual supplied/omitted context clear;
inspect assembled provider messages after integration. Archive equipment/catalog
versions with runs. Define New chat/restart semantics explicitly rather than
silently resetting equipment.

Keep position writes in `grid_world.py`. Its JSON state, receipt journal and SQLite
stores are not currently one transaction. Choose and test a coherent commit boundary
for equipment and subsequent combat effects; do not claim cross-store atomicity.

Integration points: Unity `WorldBuilder.cs`, `WorldBuilderPanel.cs`,
`WorldBuilderUI.cs`, `ShellUI.cs`, `GridWorkbench.cs`; Python `t-scan/live/bridge.py`,
`grid_world.py`, `world_manifest.py`, `movement_tools.py`, `decision_executor.py`,
`grid_context.py` and run archival. Use explicit state owners, not UI-owned combat.

## Functional starter and order

Starter sword: adjacent Slash, 3 damage. Shield: Shield Bash, up to three squares
through a clear lane, stopping adjacent to the target, 1 damage. A charge's movement
and damage are one authoritative action, not cosmetic teleportation. Other module
skills stay undesigned until needed.

Only executed world actions advance game time. Chat, thought, memory, task edits,
operator editing and previews do not. Inference epochs are not combat turns.

1. Restyle all current screens; verify layout, text, selection, input and camera.
2. Export the baseline and three alternate bodies; verify sockets and representative
   compatible/incompatible module attachments, orientations and scale.
3. Build Character drafts, body switching, conflict handling, previews and presets.
4. Add backend validation, persistence, acknowledged Apply and stale-revision handling.
5. Register and execute starter actions from accepted equipment.
6. Run training-dummy experiments before leveling, progression or broad skills.

Verify invalid multi-mount builds, stale revisions, body swaps, duplicate/rejected
Apply requests, disconnected backend, restart, actual supplied model tools, removal
of unequipped actions and measured movement/damage. Preserve Stop; check project
boundaries, Unity compilation and actual runtime input.

Acceptance: equip sword/shield → confirmation → Steve receives both actions →
controller records dummy effects. Remove shield → Bash disappears. Switch to Wisp
→ incompatible hand tools are identified before the build can be applied.
