"""Update locally copied catalog mechanics without rerendering or changing mesh/socket art."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
mechanics=json.loads((ROOT/'t-scan/live/character_mechanics.json').read_text())
for path in (ROOT/'t-scan/live/character_catalog.json',ROOT/'TScanViewer/Assets/Resources/Meadow/character/catalog.json'):
 catalog=json.loads(path.read_text());catalog['version']=mechanics['version']
 for module in catalog['modules']:
  module.update(stat_modifiers=[],abilities=[])
  module.update(mechanics['modules'].get(module['id'],{}))
 path.write_text(json.dumps(catalog,indent=1)+'\n',encoding='utf-8')
print('Updated local character mechanics catalogs; meshes unchanged.')
