# Steve's modular meadow

Original Blender art owned by Steve's harness. It has no dependency on PLEASE HOLD or PLEASE HOLD shorts. No movement engine, inference prompt, action tool or governance rule is changed by this asset kit.

## Open

Open `steve_meadow_001.blend` in Blender. Select either scene:

- **Meadow_OpenField:** flat 10×10-cell field, two meters per cell. All ground-module vertices are at Z=0. Low grass and flowers are decorative. The initial field has no trees, bushes, rocks or logical obstacles on its walkable surface.
- **Meadow_Kit:** a catalog of reusable ground, grass, flowers, bushes, trees and rocks. Assets are marked for Blender's Asset Browser. Their positions in this scene are display positions; exported files use a grounded local origin.

The cell size is an internal art convention, not a coordinate interface for Steve. Future gameplay can expose local surroundings and four one-step movement actions independently of these meshes.

## Kit

- Four seamless, flat 2×2-meter ground variants with identical border colors and positions.
- Five bent, tapered grass tufts with shaded roots and lighter tips.
- Four flower patches: cream daisy, golden buttercup, lilac wildflower and pink clover.
- Three shrubs: round, low spreading and flowering.
- Three trees: soft oak, tall aspen and golden-green maple. Curved tapering trunks, branch forks, spreading roots, layered canopies and shaped leaf sprays.
- Three moss-colored rocks.

All 22 assets have independent `.glb` files in `exports/`. Materials use mesh vertex colors and ordinary Principled BSDF shading, with no external textures, purchased assets or engine-specific foliage shader. Mesh instances share data in Blender. Grass is modeled geometry rather than transparent rectangles.

Trees, shrubs and rocks are *obstruction candidates*, not automatically colliders or movement restrictions. Later integration must assign their logical footprint explicitly. Decorative plants must not silently block steps.

## Research and application

The approach draws on artists' own published workflows:

1. [Antonin Pardon's Hidden Pathway breakdown](https://80.lv/articles/breakdown-how-to-create-a-peaceful-fantasy-nature-environment): reusable asset categories; asymmetrical foliage; several grass forms; root-to-ground color blending; distribution in blended patches. Applied here through mixed curved tufts, species clusters, variable density and a quiet central area. The full shader/card workflow in that article is not implemented here.
2. [Ghislain Girardot's stylized tree breakdown](https://cremuss.artstation.com/projects/Vyz12R): layered canopy volumes, edge leaves, height-dependent color and controlled foliage shading. Applied here with overlapping lobed volumes, explicit folded leaves and baked vertex-color gradients. We do not copy its meshes, textures, shell masks or Unreal shader.
3. [Blender glTF export documentation](https://docs.blender.org/manual/en/4.2/addons/import_export/scene_gltf2.html): standard material/export constraints. Applied through independent mesh assets, portable color attributes and explicit meter-scale origins.

The resulting visual design is original. It deliberately favors readable silhouettes and an open field over dense forest dressing.

## Rebuild and inspect

Run `build_meadow.py` with Blender's Python, not the harness Python environment. It creates fresh scenes in its Blender process and writes this kit's files only. It must not be run in an unsaved unrelated live scene. The saved `.blend` includes editable geometry and presentation lighting.

`manifest.json` records asset roles and geometry counts. `validation.json` records the flat surface, module count, export count and shared mesh use. `export_validation.json` confirms that all 22 GLB assets reopen in Blender with preserved vertex colors and grounded bounds, and that ground borders match. `meadow_open_field.png` and `meadow_asset_kit.png` are rendered previews. The meadow is now explicitly exported into Steve's Unity project by `../hover/build_hover.py`; movement is implemented separately under `STEVE_MOVEMENT_011.md`.
