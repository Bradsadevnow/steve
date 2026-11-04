"""Verify active source boundaries without reading private runtime data."""
from pathlib import Path
import ast,json,re
root=Path(__file__).resolve().parents[1]
game=root/'PleaseHold';steve=root/'TScanViewer';shorts=root/'PleaseHoldShorts'
game_code='\n'.join(p.read_text(encoding='utf-8-sig') for p in (game/'Assets').rglob('*.cs'))
steve_code='\n'.join(p.read_text(encoding='utf-8-sig') for p in (steve/'Assets/TScan').rglob('*.cs'))
live=root/'t-scan/live'
modules={p.stem:p for p in live.glob('*.py')}
dependencies={}
for name,path in modules.items():
 tree=ast.parse(path.read_text(encoding='utf-8-sig'))
 dependencies[name]={dependency for node in ast.walk(tree) for dependency in (
  [node.module.split('.')[0]] if isinstance(node,ast.ImportFrom) and node.module else
  [alias.name.split('.')[0] for alias in node.names] if isinstance(node,ast.Import) else [])}
active=set();pending=['bridge']
while pending:
 name=pending.pop()
 if name in active:continue
 active.add(name);pending.extend(dependencies.get(name,set())&modules.keys())
backend='\n'.join(modules[name].read_text(encoding='utf-8-sig') for name in sorted(active))
retired={'avatar_dispatch','avatar_protocol','bench_tools','body_tools','body_protocol','chat_tools','cylinder_protocol','embodied_world','experiments','hex_tools','hex_world','llama_native','shared_conversation','shared_worker'}
checks={
 'game_has_no_inference_or_research_imports':not re.search(r'UnityWebRequest|HttpClient|SteveBridge|TScanViewer|t-scan|localhost|127\.0\.0\.1|namespace Steve\.',game_code),
 'game_sources_import_locally':'../../avatars/' not in game_code and '../../environments/' not in game_code,
 'steve_resources_are_meadow_only':{p.name for p in (steve/'Assets/Resources').iterdir() if p.is_dir()}=={'Meadow'},
 'steve_has_no_navigation_or_game_code':not re.search(r'DungeonWorld|DungeonActor|ExplorationObservation|Office/|Apartment/|Trenchcoat/|HomeRaccoons/|Hugh Mann|PollCampaignMap',steve_code),
 'backend_has_no_retired_tools_or_campaign_imports':not re.search(r'world_step|world_observe|world_interact|map_recall|campaign_memory|world_tools|Please Hold|Hugh Mann',backend),
 'active_backend_has_no_retired_or_native_dependencies':not any(dependencies[name] & (retired|{'numpy','jinja2','sklearn','torch','transformers'}) for name in active),
 'retired_backend_modules_removed':not (retired&modules.keys()),
 'hover_avatar_present':(steve/'Assets/Resources/Meadow/hover.json').exists(),
 'viewer_has_no_retired_workbench_or_activation_code':not re.search(r'HexWorkbench|RobotWorkbench|TowerWorkbench|RaccoonMotion|PollExperiments|NodeKey|IBodyWorkbench',steve_code),
 'meadow_definition_authored_in_unity':(steve/'Assets/Resources/Meadow/World.asset').exists() and 'm_Name: Meadow Environment' in (steve/'Assets/TScan/Observatory.unity').read_text(),
 'backend_has_no_authored_flag_layout':'FLAGS=' not in (root/'t-scan/live/grid_world.py').read_text() and 'from world_manifest import validate_manifest' in (root/'t-scan/live/grid_world.py').read_text(),
 'agent_visual_does_not_build_environment':'flags.Refresh' not in (steve/'Assets/TScan/GridWorkbench.cs').read_text() and 'Meadow/field' not in (steve/'Assets/TScan/GridWorkbench.cs').read_text(),
 'no_asset_symlinks':not any(p.is_symlink() for f in [game/'Assets',steve/'Assets',shorts] for p in f.rglob('*')),
}
if game.exists():checks['shorts_outside_game']=not (game/'Production').exists()
if shorts.exists():
 checks['shorts_private_rebuild_sources_present']=all((shorts/'SourceArt/avatars/trenchcoat'/p).exists() for p in ['hugh_mann_v2.blend','build_hugh_mann_v2.py'])
 checks['shorts_blend_files_present']=all((shorts/'Production/Episode_001'/p).exists() for p in ['episode_001_filming_set.blend','hugh_mann_seated.blend'])
out=root/'t-scan/runtime_data/verification/project-boundaries.json'
out.parent.mkdir(parents=True,exist_ok=True)
prior=json.loads(out.read_text()) if out.exists() else {}
result=dict(prior,passed=all(checks.values()),checks=checks,active_backend_modules=sorted(active),independent_projects_present=dict(PleaseHold=game.exists(),PleaseHoldShorts=shorts.exists()),scope='Active Steve source and folder dependencies; independent projects checked only when present locally. Runtime checks recorded separately.')
out.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
raise SystemExit(0 if result['passed'] else 1)
