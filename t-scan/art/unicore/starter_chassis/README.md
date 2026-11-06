# Duelist and Mantle

Authored 6 November 2026. Both are hovering unicorn chassis with exactly three
mounts and no inherent stat bonuses or change to grid footprint.

| Body | Mount IDs | Compatibility |
| --- | --- | --- |
| Duelist | `hand_L`, `hand_R`, `horn` | Two standard tool mounts; horn focus. `hand_R` may reserve `hand_L` for a supported two-mount item. |
| Mantle | `shoulder_L`, `shoulder_R`, `horn` | Two utility mounts; horn focus. No hand-tool mounts. Current orb/tome/coil/lens visual compatibility follows the trusted module catalog. |

`starter_chassis.blend` contains both source bodies and a render studio.
`body_catalog.json` records Blender-space socket transforms and types.
`starter_lineup.png`, `duelist.png` and `mantle.png` are rendered previews.
`five_chassis_comparison.blend` is a copy of the open Blender lineup after the two
new collections were appended. The previous source/variant files were not overwritten.

Rebuild from the workspace using the installed Blender:

```
blender -b t-scan/art/unicore/unicore_chassis.blend --python t-scan/art/unicore/build_starter_chassis.py
blender -b --python t-scan/art/unicore/export_character.py
```

The exporter includes these bodies in both local character catalogs and the
Unity mesh blob. They are available in Build → Character, bringing the body
selection to seven. Body changes still require resolving incompatible equipment
and a backend-confirmed Apply. A body selection alone grants no abilities.

Verification covered exact socket sets/types, valid hand and utility loadouts,
two-mount reservation, rejection of wrong mounts, body-neutral stats and Unity
module local-position/rotation checks. Duelist's equipped Unity preview was
visually inspected; both Blender renders were inspected. The operator switched
to Watch during the Mantle screen capture, so that capture is not a visual oracle
for its Unity preview.
