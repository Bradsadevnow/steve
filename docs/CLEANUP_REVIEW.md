# Character builder and combat cleanup — 6 November 2026

This pass reviews the uncommitted Steve character/UI/stat slice. It preserves
authored identity, memory, goals, task ordering and independent project boundaries.

Fixed concrete issues:

- Combat admission/effects are pure calculations in `combat_rules.py`; only the
  grid writer commits target HP, position, receipts and world ticks.
- Combat save failures restore HP, position, tick, pending presentation, receipt
  state and turn admission. Failed world saves no longer leave partial relocation
  or a misleading relocation journal entry.
- `training_targets.py` owns passive target initialization/reconciliation. An
  unrelated world edit preserves damage/death on unchanged target instances.
- Registries admit equipment actions only in executor phase, reject unavailable
  actions explicitly, and discard unknown capability names.
- Character, portrait and item studios share resource cleanup. Owner traversal
  includes temporary `DontSave` roots, preventing old swords/other geometry from
  appearing in new item previews. Old objects deactivate before deferred deletion.
- Visual cache keys depend on body/equipment, so HP/stat changes do not rebuild
  meshes. Missing mesh lookups no longer destroy meshes used by live characters.
- Builder workspace and draft survive reload; context/resources stay authoritative.
- Removed obsolete forge styles and the exporter's magic AST constant replacement.
  Character export now requests precision through an explicit bake parameter.
- Optional PSD sources (~780 MB) and temporary screenshots remain local and ignored.
  Imported runtime/gallery assets, local UI copies, source art and Unity metadata
  remain available. Moon Tribe artwork/font attribution is in `CREDITS.md`.

Watch keeps the existing records flyout, not a second Goals monitor. Its single
header row contains Goals/Self/Log/Debug/camera/menu icons. The minimap sits at the
top; expanded records fill the space below it. Collapsing leaves the icon row.
Task provenance is available on hover instead of repeated visible notes.

Verification: 290 backend tests, boundary checks, character asset parity/GUID
checks, Unity compilation, and live UI checks. Two isolated Gemma executor probes
passed with actual assembled provider messages/native call IDs captured separately
from reasoning. UI checks preserve drafts and exercise both builders, the existing
Goals flyout, clear center input and single-model rotating item previews.

After preserving earlier diagnostics and resetting the console baseline, the final
live check passed with 0 new Unity errors and 0 warnings. Unity 6.6's occasional
GC-handle assertion during script reload was observed earlier; this pass does not
claim to repair engine internals. Earlier failed diagnostics remain captured.

Evidence stays in ignored `t-scan/runtime_data/verification/`: `ui-cleanup.json`,
`stats-provider-a5166cf2/`, and `cleanup-reload-4ccb2efb/`. Reload preserved the
live session, position, character, targets, game tick, goals, tasks and focus.

Remaining design/implementation work is explicit: dummies have fixed 10 HP and no
level/attribute sheet, enemy scaling or enemy AI. At 0 HP they are defeated and
cannot be attacked, but their authored geometry/collision remains. XP, persistent
Tokens, death/despawn presentation and enemy progression are not implemented by
this cleanup. Synthetic presentation ACK probes do not establish autonomous Unity
combat or agent navigation success.
