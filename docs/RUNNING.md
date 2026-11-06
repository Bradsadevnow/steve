# Running Steve

Watch records use a single icon row inside the existing flyout: Goals, Self, Log,
Debug, camera and menu. The row stays available when its content is collapsed.
No additional Goals monitor is present. The minimap is above the flyout.

Release checks: run `Tools/verify_project_boundaries.py`,
`Tools/verify_character_assets.py`, and `python -m unittest discover -p 'test_*.py'`
from `t-scan/live`. Unity CLI `script eval_file` can run
`Tools/verify_live_viewer.cs` against the playing Steve project; it restores the
current workspace and preserves drafts. Results stay under ignored runtime data.

World Build uses left-hand options and a right-hand asset browser, with selection
details across the bottom. Steve's corner HUD appears in Watch, not Build.
World/Character tabs are inside the builder. The center remains open for placement.
Hover equipment tiles or occupied mounts to inspect bonuses, abilities and a
rotating asset view; selecting a tile edits only the draft until Apply.

Watch has a top-right world-state minimap: mint is Steve, red markers are targets,
gray cells are blocked, orange cells are hazards, and corner flags retain their
colors. North stays up. It shows the published simulation; an unapplied-draft
notice means Build still has edits waiting for **Apply to world**. Leaving Build
preserves those edits and returns the view to the published layout.

Build → Character also offers **Duelist** (two hands plus horn) and **Mantle**
(two shoulders plus horn). Shoulder sockets accept utility modules; hand sockets
accept tool modules. Incompatible existing equipment must be resolved before Apply.

The upper-left character pane shows Steve's confirmed portrait, equipment and
position, level, HP/MP and effective stats. **Sheet +** opens the bounded character sheet; module icons open item
details, and **Edit loadout** opens the forge. **Changes from equipped** compares
equipment, effective stats and gained/lost abilities before Apply using a read-only
engine preview. Base stats are 1; sword +2 STR and shield +2 CON give the starter
pair STR/CON 3. Slash deals STR; Bash deals floor(CON/3), minimum 1. Stale connection
state is labeled. Maximum HP is 10 + (CON − 1): the starter shield gives 12 max HP.
Gear swaps never heal; removing CON gear clamps excess current HP. Inspecting these
views never issues a combat action or ticks time.

Build → **Character** opens the character forge. Choose a body, select a mount,
then choose a compatible module. **Starter pair** creates a Uni-Core sword/shield
draft. Stop Steve and wait for any action to settle, then **Apply loadout**. Only
the backend-confirmed revision is live. Body swaps retain unresolved modules for
explicit removal/remapping. The enlarged editor has a compact right-hand build
sheet showing engine-preview HP/MP, attributes, changes and granted abilities.
Chassis choices collapse; detailed stat breakdowns and ability rules are on hover.
Preset controls are deferred; existing saved preset files are untouched.

The sword grants Slash (3 adjacent damage); the shield grants Bash (1 damage,
clear cardinal lane, target within 3 squares, stops adjacent). Other modules are
labeled visual prototypes. Place the authored Crash-test dummy assets using the
world builder's actor/enemy palette and Apply the world; the backend initializes
stationary 10 HP training targets and Unity shows their measured HP. Dummies do
not retaliate. Defeated dummies remain blocking scenery. No Steve leveling,
resource bars or autonomous enemy combat is implemented by this equipment pass.

Quick click places one item. Hold left for half a second, then drag to rotate the
world camera; right/middle drag pans and scroll zooms. Drag inside the Character
preview rotates that preview without editing the world. World and Character Apply
wait for backend confirmation; rejected drafts remain editable.

The active [15×15 course](MEADOW_COURSE.md) uses x/y 1..15, resets to (8,8), and reports `blocked_obstacle` when movement attempts enter occupied obstacle cells. Historical ten-route batches are not configured for this world.

The app/product name is Steve. The existing `t-scan` and `TScanViewer` folder names and internal code identifiers are retained; they do not select a separate TScan runtime.

From `t-scan/` in PowerShell:

```powershell
./Start-Steve.ps1
```

The launcher uses `t-scan/.venv/Scripts/python.exe`. The active backend requires Python 3.12 and only its standard library. If the environment is missing, create it with `py -3.12 -m venv .venv` from `t-scan/`.

LM Studio must serve the configured model. Defaults are `http://192.168.1.128:1234`, model `google/gemma-4-e4b`, temperature 1, and context capacity 131072. Override the host/model through `Start-Steve.ps1 -LMStudioUrl <url> -Model <id>`. The loaded model's reported context capacity is recorded at connection time.

Open `TScanViewer` in Unity, open `Assets/TScan/Observatory.unity`, and press Play. The scene-owned meadow and flags render independently of inference. The backend listens on `127.0.0.1:8765`; `/health` reports inference status and `/grid/state` reports world/loop state.

Human chat wakes Steve. Settled actions offer another decision. `complete()` or a text-only response idles. Stop interrupts the loop. New chat archives the current run, clears working chat/task state, resets Steve to (8,8) facing north, and preserves long-term authored memory. Provider reasoning fills the bottom Thinking panel, with Stop in its header. The right panel has Activity, Self and View tabs. Self shows position, selected focus, unfinished and agent-marked finished goals, commitments, authored assessments and beliefs, recent experience and capabilities. Operator Notes and the separate Current run area are retired from the viewer.

The v8.4 runtime allows up to three sequential tool calls per scheduled turn. Every call is a separate model decision with fresh feedback; multiple calls in one response are rejected. Handoffs and `complete()` end the turn early. Exhausting the three-call allowance yields to scheduling without marking tasks complete. The boundary does not automatically appraise affect or write memory. See [sequential turns](SEQUENTIAL_TOOLS.md).

The epoch runner (`live/epoch_batch.py`) runs each fixed route until Steve completes it instead of until a clock expires. It needs a backend on v8.4.2 or later. See [EXPERIMENTS.md](EXPERIMENTS.md) for its end conditions and a smoke-test command. Besides `complete`, `no_action`, the epoch cap, grace and wall-clock endings, a trial ends `stalled` when the backend hands control back after three turns in a row ending `repeated_rejection`.

From the workspace root, verify changes with:

```powershell
./t-scan/.venv/Scripts/python.exe -m unittest discover -s t-scan/live -p 'test_*.py'
./t-scan/.venv/Scripts/python.exe Tools/verify_project_boundaries.py
```

Boundary output is written to `t-scan/runtime_data/verification/project-boundaries.json`. Neither command wakes Steve or starts a navigation trial.

In the world builder, **Start · P** selects the start tool. Click a valid cell,
then **Apply to world** to move Steve there and save that start for future resets.
Draft clicks alone do not move him. Applying a changed start preserves the current
chat/run and does not advance the game clock; stop Steve and settle presentation
before applying.

## Re-exporting the kit and building worlds

Kit art lives in Blender files under `t-scan/art/` (`dungeon/`, `swapmeet/`, `highschool/`). After changing a piece, re-export from the workspace root with Blender's headless Python (not the harness Python):

```powershell
& 'C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe' -b t-scan/art/dungeon/dungeon_kit.blend --python t-scan/art/export_kit.py -- TScanViewer/Assets/Resources/Meadow/kit dungeon "Dungeon"
```

Packs used so far: `dungeon` (Dungeon), `dungeon_foes` (Dungeon foes), `swap` (Cursed swap meet), `school` (Cursed high school). Roles and display names are set in `export_kit.py`.

In play mode, **Build** in the world panel opens the builder: pick a piece, click or drag on the grid, Q/E rotate, right or middle drag pans. **Apply to world** publishes a new revision (stop Steve's loop first). **Revert** discards the draft; **Save** and **Load** use `Worlds/` under Unity's `persistentDataPath`. The backend must be v8.5.0 or newer to accept a v3 world; restart it with `Start-Steve.ps1` only when the loop is idle.
