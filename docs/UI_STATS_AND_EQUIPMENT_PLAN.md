# Steve HUD, character sheet and equipment UI

**Stats conversion shipped, 6 November 2026:** the engine now supplies the live
level, HP/MP, attribute breakdown and evaluated abilities. Character Forge also
receives read-only server previews for proposed effective stats and damage.
The earlier unavailable-field notes below are historical. Starter rules are
base 1, sword +2 STR, shield +2 CON, Slash=STR, Bash=max(1,floor(CON/3)).

**Implementation update, 6 November 2026:** compact corner pane, confirmed-body
portrait, native pack HP/MP controls, expandable/scrollable sheet, mount/module
details, and equipment/capability draft comparison are implemented. Character
Forge sits to the right of the HUD so both remain usable. Live RPG sheet fields
are not yet published by Python: level, HP/MP and attributes deliberately display
unavailable, and numeric draft stat comparisons remain unavailable. No stat
conversion, level progression, affect removal or combat-rule change is implied.
The remainder records the design and future binding requirements.

Design plan, 6 November 2026. Asset audit performed against the installed Moon
Tribe Fantasy RPG UI Pack, including its Quick Start, UXML templates and visual
inspection of all 49 empty board frames and the six main board backgrounds.
This document specifies the next UI pass; it does not claim a live stat sheet or
stat conversion has been implemented. Stat rules and domain ownership remain in
[STATS_AND_SCALING.md](STATS_AND_SCALING.md).

## What is actually available

Pack root: `TScanViewer/Assets/Fantasy RPG UI Pack/`.
The installed UI Toolkit templates contain 498 presentations:

| Group under `UI Toolkit/Templates/Painted/` | Count | Useful application |
| --- | ---: | --- |
| `Boards/` main compositions | 6 | Character stats, inventory, two class panels, victory and defeat |
| `Boards/Empty_panels/` | 49 | Compact HUDs, sheet sections, details, dialogs and builder panels |
| `Buttons/Default/` and `Buttons/Highlighted/` | 133 each | Consistent normal/selected controls and item frames |
| `Healthbars/RPG_linear/` | 21 | Metal/gold, red/blue/grayscale horizontal resource bars |
| `Healthbars/RPG_round/` | 16 | Round red/blue resource alternatives; too bulky for our compact HUD |
| `Healthbars/Skill Panel/` | 2 | Ability/progression presentations; reserve for later rather than inventing a skill tree |
| `Icons/Clean/` | 133 | Equipment and control imagery; semantic matches must be checked per item |
| `Name_plates/` | 4 | Compact headers and target labels |
| `Panels/` | 1 | General panel presentation |

These are art and UI controls, not implemented inventory, character progression
or equipment rules. Available resource controls already support values, maxima,
masked fills and cosmetic smoothing. Their callbacks must never cause gameplay
damage, death, rewards or resource changes.

The supplied `character_stats_panel.uxml` contains health/energy/experience
controls and sample text such as Knight/Lvl 6. Its main background
`PNG/decor/UI_elements_decor_162.png` contains a painted human knight. Therefore
use its reusable components and visual language with Steve's own portrait; do
not shrink the entire demonstration sheet into a corner or display its sample
class, XP, labels or resource values as real state.

`Inventory_panel.uxml` uses `PNG/decor/UI_elements_decor_67.png`: a coherent
two-part composition suitable for the existing expanded Character workspace.
It is distinct from the small always-visible character HUD.

## Persistent corner pane

Replace the existing upper-left Steve card with one compact character pane,
visible in Watch and World Build. Upper-left is the initial placement so the
other corners remain available for chat, builder controls and world information.
Do not add a second overlapping Steve card. In Character Build, keep this pane
showing confirmed live state while the larger editor is explicitly Draft.

Proposed normal footprint: approximately 360 × 190 logical UI units, inset
12–16 units. Use `Boards/Empty_panels/Panel_rect_30_empty.uxml`
(`PNG/boards/UI_elements_board_31.png`, authored 2048 × 1080) as the quiet,
landscape outer frame. Fit the frame uniformly. Keep the interior compact:

1. Small current-body portrait, Steve's name and level, plus a readable run-state
   indicator. The portrait depicts confirmed body/equipment, not an unapplied draft.
2. Red HP bar and blue MP bar, each with explicit current/max numbers. Candidate
   controls: `Healthbars/RPG_linear/RPG_linear_metal_red_1.uxml` and
   `RPG_linear_metal_blue_1.uxml`. Preserve their authored proportions and clipping.
3. One compact line for STR, DEX, INT, WIS and CON, showing effective values.
4. Small equipped-module icons, initially sword and shield. These open details;
   they are not player-controlled attack buttons. Support extra mounts with a
   bounded row and an overflow count instead of growing the HUD indefinitely.
5. Small position/readiness footer and an explicit expand/collapse control.

The 10/10 HP/MP and five 5s are the approved level-1 baseline, not permission to
populate a live HUD before those fields exist. Missing data displays an em dash
or unavailable state. Disconnection marks the last confirmed values stale;
zero HP must never be a substitute for an unavailable reading.

At smaller Game views, reflow to roughly 300 logical units wide and move optional
position/module detail into expansion before reducing text below readable size.
All five attributes and HP/MP remain available in the compact presentation.
An optional minimized header may hide detail only by explicit user choice.
Final sizes require actual 1280×720 and 1920×1080 runtime inspection; these are
layout targets, not verified pixel-perfect measurements.

## Expanded compact sheet

Click the expand control to open a neighboring or downward section anchored to
the same pane. Keep it bounded, with internal scrolling when needed; do not
replace the game view with a full-screen sheet. Use independent matching empty
frames (the simpler `Panel_rect_26_empty`/`Panel_rect_30_empty` family), rather
than stretching one painted frame to arbitrary dimensions.

- Character identity/body, level and current/max HP/MP.
- Attribute rows with Base, Level, Equipment, Temporary and Effective columns.
  This decomposition explains exactly why a displayed value changed.
- Named mounts and their equipped modules, including empty or reserved sockets.
  Use the same item-frame styling as the Character builder.
- Granted abilities and their current evaluated damage, stat used, range and lane
  requirements. Begin with Slash and Shield Bash only. Do not suggest that a
  visual prototype module grants an unimplemented spell.
- Temporary effects only when the engine actually reports them. No XP gauge or
  progression allocation controls until those systems are designed and present.

Hover/focus on a module shows its definition and confirmed contribution. The
human can inspect Steve's options; Steve still chooses his own combat actions.
An Edit loadout button opens Build → Character using the existing stopped/settled
Apply rules. Opening or inspecting any sheet spends no world tick.

## Character builder and world UI integration

Keep the large inventory-style Character workspace for loadout editing:
Steve preview and named mounts on the left, compatible module library on the
right. Reuse the existing item frame (`PNG/decor/UI_elements_decor_47.png`) and
consistent selected, reserved, incompatible and empty states. A thumbnail should
depict the module where available; a generic icon remains visibly a placeholder.

Add an explicit draft sheet beside or within a dedicated section of the editor.
Show current → proposed effective values and list which actions will be gained
or lost. Proposed derived values must come from a read-only engine preview
interface using the same trusted evaluator as Apply. Unity sends choices, not
authoritative stat totals. Until preview evaluation exists, show choices and
unevaluated modifiers without claiming final confirmed numbers.

Keep the sword/shield details specific: Slash uses STR with a 3-damage stat-5
anchor; Bash uses CON with a 1-damage stat-5 anchor and a clear cardinal lane up
to 3 squares, ending adjacent. Sliding coefficients remain undecided. Cards use
the live trusted rule revision rather than separately hardcoded formulas.

World builder palette, Start/Flags/Delete, Apply/Revert and notices use the same
steel/dark panel family and readable typography. Crimson is reserved for strong
actions, gold for selection/headings, red/blue for HP/MP. Decorative flourishes
ignore input. Keep ornate victory/defeat boards for a later results/death design;
do not introduce a victory condition, reward economy or respawn UI in this pass.

## Frontend/backend ownership

- Character domain publishes the confirmed sheet, resources, equipment, available
  capabilities and revisions. Equipment modules supply their own icon/thumbnail
  references, modifiers and ability definitions through the trusted catalog.
- The game engine evaluates stats/abilities and any proposed loadout preview.
  World/enemy domains own enemy state; target UI uses an approved observable
  projection rather than exposing enemy internals to Steve.
- Steve's perception supplies current measured world information. Agent context
  receives structured relevant sheet/perception data independently of whether
  the human expanded or collapsed a UI panel. UI labels and tooltip prose never
  become behavioral instructions or a substitute for native tool definitions.
- UI owns layout, selection, expansion, drafts and cosmetic bar interpolation.
  Numeric labels show committed values immediately; animated fills may catch up.
  Rendering, inspecting and opening panels cannot tick the simulation.
- Reuse an independent character presentation component/view model for the HUD,
  expanded sheet and builder comparison. Keep this out of the agent prompt
  assembler and avoid adding all of it to the large shell controller.

## Implementation order and acceptance

1. Establish the character/module/perception/engine boundaries and versioned sheet
   contract from the stats plan. Keep UI design independent of balance choices.
2. Assemble the compact pane from actual pack components with a clearly labeled
   preview fixture. Replace the old Steve card and verify sizing/input in Unity.
3. Bind confirmed sheet/resources and explicit stale/missing states after the
   authoritative stats slice exists. Connect the expanded stat breakdown.
4. Bind module details and engine-evaluated draft comparison in Character Build.
5. Verify real mouse/focus input, preview rotation/zoom, expansion and scrolling;
   clicks on the pane must not place pieces or rotate the world beneath it.

Acceptance includes a small readable corner pane at both target resolutions;
real confirmed values after equipment changes; accurate base/bonus totals;
no false XP/classes/spells; preserved body preview and mount alignment; no
overlap with mode controls/chat/builder; stale state clearly shown on disconnect;
no simulation tick from inspection; and no runtime behavior changes caused by
bar animation or decorative input handling.
