# Active meadow course

Current model view: `shared-chat-v8.4.6-x-map` draws a north-up x/y grid with `X` for obstacles, `@` for Steve, dots for open cells and flag initials. The separate obstacle ID/type/coordinate list and adjacent-cell enumeration are omitted from the current model observation. Collision mechanics are unchanged. This presentation was requested by the owner after the initial course installation.

Installed 5 November 2026 at the owner's request, using the approved Blender layout.

The active environment has 15×15 cells, two metres per cell, and an authored spawn/reset at (8,8), north. Corner flags are blue (1,15), red (15,15), yellow (15,1) and purple (1,1). There are 24 static obstacle cells: seven stone walls, seven hedges, six boulder clusters and four wooden hurdles. Hurdles are barriers to navigate around.

Unity's `Resources/Meadow/World.asset` owns placements, bounds and spawn under `meadow-world-v2`. `MeadowEnvironment` renders offline from that asset and locally copied Blender geometry in `course.json`. `Tools/AuthorMeadowCourse.cs` is an explicit Editor authoring operation, not a startup script. It increments the world revision when invoked. `Tools/export_course_art.py` exports geometry only from the Steve-owned Blender file. No sibling project dependencies were added.

Python accepts v1 for historical 10×10 state and v2 for the new 15×15 course. It validates obstacle IDs, bounds, prototypes and collisions with spawn/landmark cells. GridWorld alone writes logical position. A blocked attempt returns `blocked_obstacle`, preserves position, and waits for Unity's settled acknowledgement. Movement remains exactly four zero-argument cardinal tools; no route selection is added.

On a changed world, a previous position that is now blocked or out of bounds is moved by GridWorld to the authored spawn, with a `world_change_relocation` audit event. Valid positions are retained. New chat uses the authored spawn and retains the existing archive/Self/memory lifecycle.

Condition `shared-chat-v8.4.5-meadow-course` records changed bounds, obstacle observations and errors, tool descriptions and prompt wording. Historical coordinates remain historical x/y values; the latest CURRENT WORLD supplies current bounds and manifest provenance. This is a new environment condition; the old ten-route results and routes, including the removed orange flag, are not a baseline for this course.

Verification: 239 backend tests passed; project boundary checks passed; Unity compiled without errors, frames advanced, and the live viewer registered 15×15, four flags and 24 obstacles at (8,8). The isolated `Tools/verify_meadow_course.py` fixture got eight real settled Unity acknowledgements, including hedge and boulder collisions. This is mechanical verification, not a model navigation trial. Evidence: `t-scan/runtime_data/verification/course-presentation.json` and `course-live.png`. The viewer was restored to port 8765 afterward; no model request was sent during verification.
