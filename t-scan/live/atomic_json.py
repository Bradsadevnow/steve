"""Atomic checkpoints tolerate brief Windows/OneDrive file-sharing locks."""
import json,time,uuid
from pathlib import Path
def write_json(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 temporary=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp');payload=json.dumps(value,indent=2,ensure_ascii=True)
 for attempt in range(6):
  try:
   temporary.write_text(payload,encoding='utf-8');temporary.replace(path);return
  except PermissionError:
   if attempt==5:raise
   time.sleep(.03*2**attempt)
