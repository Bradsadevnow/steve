"""Check shipped character/catalog parity, mesh keys, thumbnails and Unity GUIDs."""
import json,re,struct
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
assets=ROOT/'TScanViewer/Assets'
backend=json.loads((ROOT/'t-scan/live/character_catalog.json').read_text())
viewer=json.loads((assets/'Resources/Meadow/character/catalog.json').read_text())
if backend!=viewer:raise SystemExit('Backend and Unity equipment catalogs differ')
blob=(assets/'Resources/Meadow/character/meshes.bytes').read_bytes()
if blob[:4]!=b'SKIT':raise SystemExit('Invalid mesh blob')
offset=12;mesh_ids=set()
for _ in range(struct.unpack_from('<I',blob,8)[0]):
 length=struct.unpack_from('<H',blob,offset)[0];offset+=2
 key=blob[offset:offset+length].decode();offset+=length
 vertices,indices=struct.unpack_from('<II',blob,offset);offset+=8+vertices*20+indices*4
 if key in mesh_ids:raise SystemExit('Duplicate mesh key: '+key)
 mesh_ids.add(key)
if offset!=len(blob):raise SystemExit('Unexpected mesh blob length')
for entry in backend['bodies']+backend['modules']:
 if entry['mesh'] and entry['mesh'] not in mesh_ids:raise SystemExit('Missing mesh: '+entry['id'])
for module in backend['modules']:
 path=assets/'Resources/Meadow/character/thumbnails'/(module['id']+'.png')
 png=path.read_bytes()
 if png[:8]!=b'\x89PNG\r\n\x1a\n' or struct.unpack_from('>II',png,16)!=(256,256):raise SystemExit('Invalid thumbnail: '+module['id'])
guids={}
for path in assets.rglob('*.meta'):
 if '/Temp/' in path.as_posix():continue
 match=re.search(r'^guid: ([a-f0-9]{32})$',path.read_text(encoding='utf-8-sig'),re.M)
 if not match:continue
 guid=match[1]
 if guid in guids:raise SystemExit('Duplicate Unity GUID: '+str(path)+' and '+str(guids[guid]))
 guids[guid]=path
print(json.dumps(dict(passed=True,bodies=len(backend['bodies']),modules=len(backend['modules']),mesh_keys=len(mesh_ids),unique_unity_guids=len(guids))))
