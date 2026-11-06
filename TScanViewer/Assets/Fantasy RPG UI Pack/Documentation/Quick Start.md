# Fantasy RPG UI â€” Unity 6.3 update

## Artistic constraint

The painted shapes are deliberately not designed for 9-slice. Keep the original proportions. Resize a whole composition uniformly, or rearrange independent components. Never stretch the frame to fit arbitrary aspect ratios.

## uGUI health and resource bars

Drag a prefab from `Prefabs/Painted/Healthbars` beneath a Canvas. Linear and round RPG prefabs contain a `HealthBarUGUI` component. Round resources use a vertical liquid level; linear resources fill horizontally.

```csharp
using MoonTribe.UI;
using UnityEngine;

public class ResourceExample : MonoBehaviour
{
    [SerializeField] HealthBarUGUI health;
    void Start()
    {
        health.SetMax(150);
        health.SetValueInstant(150);
    }
    public void TakeDamage(float amount) => health.Damage(amount);
    public void Heal(float amount) => health.Heal(amount);
}
```

`SetValue` animates; `SetValueInstant` snaps. `SetMax(value, true)` keeps the current ratio. A maximum at/below zero is clamped to a small positive value. NaN and infinite inputs are rejected. API calls initialize the model lazily, including before Awake. Disable/enable preserves the value.

`OnEmptied` and `OnFilled` refer to the logical value and fire before smoothing completes. `OnNormalizedChanged` reports the displayed fraction. Initialization does not fire empty/full gameplay events. Default animation uses unscaled time; change `useUnscaledTime` in the Inspector when the UI should pause with gameplay.

Fill layers share the main fill's physical boundary, including differently sized VFX textures. The optional edge follows the main fill rectangle and is hidden at 0%/100%. Keep fill layers aligned with the authored geometry. The original scene-only prototype is supported, but the updated reusable prefabs are the recommended starting point.

The demo tester uses Left/Right to drain/fill, Up/Down for full/empty, and R for a random value. Space remains reserved for demo navigation. `holdRate` is percentage of maximum per second.

## UI Toolkit

Open `Scenes/UI Toolkit Gallery.unity`. The gallery lists all 498 prefab presentations, includes search, and provides a resource slider. `UI Toolkit/FantasyUICatalog.asset` maps each original prefab identifier to a UXML template.

For your own screen:

1. Create a UIDocument and assign Panel Settings, using the included FantasyPanelSettings as an example.
2. Add one of the templates from `UI Toolkit/Templates` in UI Builder, or instantiate its VisualTreeAsset from C#.
3. Give its container a real width and height. PaintedFrame fits the whole composition inside that area while preserving aspect ratio. Extra space remains empty.
4. Query a HealthBarElement within the instantiated template and connect it to your game's values.

```csharp
var instance = template.Instantiate();
instance.style.flexGrow = 1;
document.rootVisualElement.Add(instance);
var health = instance.Q<MoonTribe.UI.HealthBarElement>();
health.SetMax(150);
health.SetValue(90, instant: true);
```

`HealthBarElement` owns its model and animation tick. Do not also Tick its Model externally. It stops its scheduled animation when detached and rebuilds its layer list when attached. If you change its children after attachment, call `RefreshLayers()`.

`PaintedImage` clips the original texture/UVs to fill a bar; it does not compress the artwork. Horizontal and vertical fill are supported. This renderer is intended for the included standalone sprites. Do not repack them into a tight/rotated Sprite Atlas without adapting and testing the renderer.

`PaintedFrame` uses a fixed authored coordinate system. Responsive screens should arrange several frames rather than distort one large frame. The UXML preserves authored decorative positioning and scale. Buttons expose native UI Toolkit click/focus/disabled behavior. Default and Highlighted presentations remain separate templates.

`PaintedScrollbar` moves the original painted thumb. It supports pointer dragging, track clicks, arrow keys, Home/End, `value`, `SetValueWithoutNotify` and `RegisterValueChangedCallback`. Its normalized value is an integration point; connect it to your own scrollable content. Source prefabs do not include a complete inventory scrolling system. Do not change the authored track/handle names without updating the corresponding attributes.

The Character Stats panel contains independent health, energy and experience controls in both UI systems. Its three sprite masks are baked into generated copies under `UI Toolkit/Support`. The supplied masks match the included geometry and textures. Custom geometry requires matching masks. Runtime movement of masked child geometry requires a different masking implementation.

## Scope

These are UI presentations and resource controls, not a complete inventory, equipment, skill progression, or save-game system. Connect your own data and actions. The gallery's click feedback is a demonstration.

UI Toolkit code targets Unity 6000.3.9f1. Keep uGUI available for existing customers. Do not claim support for earlier editors, URP/HDRP, mobile platforms or new Input System configurations until independently tested. Original experimental Shader Graph files are not required by the new PaintedImage renderer.

## Gallery and artwork corrections (revision 2)

The sidebar follows the source folders, with collapsible groups, item counts, natural numeric sorting and search across all folders. Empty panels and icons have their own groups. Search temporarily expands matching groups.

Preview defaults to Natural size (up to 100%). Small artwork stays at its authored size; large compositions shrink uniformly to fit. Use Up to 200% or Fit available area explicitly when needed. PaintedFrame.MaxScale is 1 by default, 2 permits double size, and 0 removes the upper limit; call Fit() after changing it from C#.

Standalone sprites use their full Sprite.rect including transparent padding. Tight sprite bounds must not be stretched over the original rectangle. Icons preserve their aspect ratio.

Resource bars now clip fills and moving edge effects against the authored background silhouette. uGUI uses a Resource Clip sprite Mask; UI Toolkit uses generated PaintedClipShape assets. The contour representation assumes one solid horizontal interval per row, as in the included bar backgrounds. Custom background geometry requires corresponding clip data. VFX edges follow the physical fill boundary and remain hidden at empty/full values. No source artwork or 9-slice borders are changed.

PaintedScrollbar.travel-length explicitly describes the usable thumb travel in track coordinates, matching the authored top and bottom insets. If you change track geometry, update this value.
