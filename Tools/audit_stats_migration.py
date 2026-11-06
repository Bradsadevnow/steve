"""Local read-only continuity audit and pre-migration backups. No agent record edits."""
import hashlib,json,sqlite3,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];data=ROOT/'t-scan/runtime_data';out=data/'verification/stats-migration';out.mkdir(exist_ok=True)
def get(route):
 with urllib.request.urlopen('http://127.0.0.1:8765/'+route,timeout=5) as response:return json.load(response)
world=get('grid/state');health=get('health')
if world['running'] or world['presentation'] or health['status'] not in ('ready','complete','idle'):raise RuntimeError('Main Steve is busy; no migration backup or restart should proceed')
db=sqlite3.connect((data/'steve.sqlite3').as_uri()+'?mode=ro',uri=True)
def digest(query):return hashlib.sha256(json.dumps(db.execute(query).fetchall(),ensure_ascii=True).encode()).hexdigest()
record=dict(session_id=world['session_id'],position=world['self'],game_tick=world['game_tick'],equipment=world['character']['equipment'],body=world['character']['body_id'],memory_sha=digest("SELECT id,time,kind,content,request_id,source_id FROM events WHERE kind IN ('seed_source','seed_memory','user_note') ORDER BY id"),self_sha=digest("SELECT owner,id,revision,body FROM agent_records WHERE owner IN ('self','doctrine') ORDER BY owner,id"),affect_sha=digest("SELECT value FROM state WHERE key='affect'"))
if '--after' in sys.argv:
 before=json.loads((out/'before.json').read_text());checks={key:before[key]==value for key,value in record.items()}
 (out/'after.json').write_text(json.dumps(dict(record=record,checks=checks),indent=2));print(json.dumps(dict(preserved=all(checks.values()),checks=checks),indent=2))
 if not all(checks.values()):raise SystemExit(1)
else:
 if (out/'before.json').exists():raise RuntimeError('Existing migration audit preserved; do not overwrite its backup')
 for name in ('grid-world.json','conversation.json'):(out/(name+'.before')).write_bytes((data/name).read_bytes())
 target=sqlite3.connect(out/'steve.before.sqlite3');db.backup(target);target.close()
 (out/'before.json').write_text(json.dumps(record,indent=2));print(json.dumps(dict(backup=str(out),session_id=record['session_id'],position=record['position'],game_tick=record['game_tick']),indent=2))
db.close()
