# Steve's hover unicorn

Original cream/teal hover body with gold accents and a softly lit underside. Steve's established head was explicitly copied from this same project's `UnicornTower/SteveUnicornTower` prefab through `HoverHeadExport.cs`, preserving the face, eyes, horn, ears and mane. No PLEASE HOLD game or shorts assets are used.

`steve_hover_unicorn.blend` contains the editable model and a four-bone authoring rig: root, head and two eye pivots. `hover_preview.png` shows the model. `head_source.json` is the local source-geometry copy; `build_hover.py` reconstructs the source, exports the hover geometry and explicitly exports the meadow's shared meshes/instances into `TScanViewer/Assets/Resources/Meadow/`.

Unity's `GridWorkbench` controls orientation, head/eye leading, lean, tile translation, settling, idle bob and the floor shadow. These transforms never write logical position. The body has no limbs, inventory or manipulation tools.

The active tool and simulation contract is `STEVE_MOVEMENT_011.md` in the workspace root. Warden integration remains optional and is not claimed by this implementation.
