"""Ten finite chat/persistence probes against an isolated snapshot of Steve.

Uses ordinary chat, New chat and read-only inspection APIs. Expected observations
are kept in the report, never injected as system instructions or authored records.
No production state writes, provider switching, automatic memory repair or scoring.
"""
import argparse,json,os,sqlite3,subprocess,sys,threading,time,urllib.request,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'t-scan/live'))
from atomic_json import write_json

PROBES=[
 dict(id='01-immediate',question='Can he retain a fact across ordinary chat turns?',steps=[
  'For this synthetic conversation test only, the preferred notebook color is copper. Acknowledge briefly. Do not move or make a persistent commitment.',
  'What notebook color did I just specify for this synthetic test? Answer briefly.']),
 dict(id='02-correction',question='Does a correction replace the earlier value?',steps=[
  'Synthetic chat test: the meeting label is ORCHID-14. This is only a test fact; do not move.',
  'Correction: the meeting label is ORCHID-27, replacing the earlier label. Please acknowledge briefly.',
  'What is the current meeting label, and which earlier label did it replace?']),
 dict(id='03-intervening-chat',question='Can he recall a fact after unrelated turns?',steps=[
  'Synthetic short-term recall test: the parcel code is KESTREL-482. Keep this in this chat only. Do not move.',
  'Briefly describe the difference between a circle and a square.',
  'Give one sentence about a cloudy afternoon.',
  'What parcel code did I give earlier in this chat?']),
 dict(id='04-unfinished-work',question='Can he preserve one unfinished step after another is reported done?',steps=[
  'Synthetic checklist test, no world movement: record two separate pending tasks, inspect the mock invoice and inspect the mock stamp. Do not claim either inspection happened. Stop after recording them.',
  'For this synthetic test, I report that the mock invoice inspection is finished. The mock stamp has not been inspected. Update your checklist accordingly and stop.',
  'Which inspection remains unfinished, and what evidence do you have for the other one? Do not perform either inspection.']),
 dict(id='05-plan-versus-evidence',question='Does he distinguish a hypothetical plan from a verified event?',steps=[
  'Synthetic evidence test: this is a hypothetical plan, not an event: "I delivered the silver envelope." No envelope has actually been delivered. Do not move or mark delivery complete.',
  'Has the silver envelope actually been delivered? Distinguish the plan from available evidence.']),
 dict(id='06-saved-note-reset',question='Does the explicit remember mechanism survive New chat?',steps=[
  'remember: Synthetic persistence probe only: the test lighthouse password is MARIGOLD-731. This is fabricated test data, not a real credential or enduring personal trait. Do not move.',
  {'op':'new_chat'},
  'What test lighthouse password, if any, is available in your saved notes? Identify whether it comes from a saved note or this active conversation.']),
 dict(id='07-saved-note-correction',question='Can he resolve corrected durable notes without treating old text as current?',steps=[
  'remember: Synthetic saved-note correction test: the sample delivery window is Tuesday. This is fabricated test data. Do not move.',
  'remember: Correction to the synthetic sample delivery window: Thursday replaces Tuesday. The Tuesday value is obsolete test data. Do not move.',
  {'op':'new_chat'},
  'What is the current sample delivery window in the synthetic saved-note test? Explain which note supersedes which.']),
 dict(id='08-persistent-commitment',question='Can he author and retrieve a persistent intention across New chat?',steps=[
  'Synthetic persistence test: record a persistent commitment to keep synthetic probe summaries concise. This is an experimental commitment, not an identity change. Choose your own record ID. Do not move. Stop after recording it.',
  {'op':'new_chat'},
  'Which active persistent commitment, if any, concerns synthetic probe summaries? Identify what is actually stored rather than assuming the request succeeded.']),
 dict(id='09-run-local-clear',question='Does New chat clear working conversation/tasks without leaking archived text?',steps=[
  'Synthetic run-local test: the temporary session token is WREN-908. Keep it only in this conversation, not saved notes, persistent intentions or Self claims. Add one pending run-local task to inspect a mock badge, but do not perform it or move. Stop after recording the pending task.',
  {'op':'new_chat'},
  'Without retrieving past-run records, can you state any temporary session token from before this New chat? Also report whether any working checklist tasks are currently present. Say when the available context does not contain something.']),
 dict(id='10-backend-restart',question='Does a backend restart retain current chat and authored pending work?',steps=[
  'Synthetic restart test: the active-chat ticket code is FINCH-563. Add one pending task to inspect a mock seal; do not perform it or move. Do not store the ticket code in persistent notes or identity. Stop after recording the pending task.',
  {'op':'restart'},
  'What ticket code did I give in this active chat, and which mock inspection remains pending? Distinguish the restart from New chat.'])]

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--port',type=int,default=8877);p.add_argument('--turn-seconds',type=int,default=240);a=p.parse_args()
 out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);data=out/'isolated_data';data.mkdir()
 endpoint='http://127.0.0.1:'+str(a.port);proc=None;shutdown=threading.Event();logs=[]
 status=dict(status='starting',pid=os.getpid(),total_probes=len(PROBES),results=[],endpoint=endpoint,started_at_unix=time.time(),isolation='SQLite backup; no production mutations; headless observation keepalive, not a visual or movement test')
 def save():write_json(out/'status.json',status)
 def api(route,body=None,base=endpoint):
  req=urllib.request.Request(base+route,data=None if body is None else json.dumps(body).encode(),headers={'Content-Type':'application/json'})
  with urllib.request.urlopen(req,timeout=8) as response:return json.load(response)
 def idle(timeout=45):
  deadline=time.monotonic()+timeout
  while time.monotonic()<deadline:
   try:
    h=api('/health');w=api('/grid/state')
    if h['status']=='error':raise RuntimeError('Isolated backend error: '+h.get('error',''))
    if h['status'] in ('ready','complete') and not w['running'] and not w['presentation'] and w['world_ready']:return
   except (OSError,ValueError):pass
   time.sleep(.3)
  raise TimeoutError('Isolated backend did not become idle and ready')
 def start():
  nonlocal proc
  stdout=(out/'backend.stdout.log').open('a');stderr=(out/'backend.stderr.log').open('a');logs.extend([stdout,stderr])
  proc=subprocess.Popen([sys.executable,'-S',str(ROOT/'t-scan/live/bridge.py'),'--port',str(a.port),'--data-dir',str(data),'--lm-url',config['lm_url'],'--model',config['model'],'--ctx',str(config['context_capacity']),'--temperature',str(config['temperature'])],cwd=ROOT/'t-scan',stdout=stdout,stderr=stderr,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
  status['backend_pid']=proc.pid;save();idle()
 def publisher():
  while not shutdown.is_set():
   try:
    state=api('/grid/world',dict(client_id='isolated-chat-probe',manifest=manifest))
    if state.get('presentation'):status['unexpected_presentation']=state['presentation']
   except Exception:pass
   shutdown.wait(.3)
 def snapshot():
  return {name:api(route) for name,route in [('agent','/agent-state'),('tasks','/task-list'),('notepad','/notepad'),('history','/history'),('world','/grid/state')]}
 def rotate():
  idle();return api('/chat/new',dict(request_id='chat-probe-'+uuid.uuid4().hex))
 def check_stop():
  if (out/'STOP').exists():raise InterruptedError('Probe STOP file')
  live=api('/health',base='http://127.0.0.1:8765')
  if live['status'] in ('queued','generating','using_tool'):raise InterruptedError('Main Steve is active; isolated probes released model access')
 def turn(prompt,folder,index):
  check_stop();idle();before=api('/history')['messages'];accepted=api('/generate',dict(prompt=prompt));req=accepted['requestId'];began=time.time();seen=False
  while True:
   check_stop();h=api('/health');w=api('/grid/state')
   if w['presentation'] or w['self']['col']!=8 or w['self']['row']!=8:raise RuntimeError('Unexpected movement in a no-movement probe; presentation will not be fabricated')
   if w['decision_loop'].get('origin_request_id')==req:seen=True
   if h['status']=='error':raise RuntimeError(h.get('error','Inference error'))
   if time.time()-began>a.turn_seconds or ((h.get('epoch') or {}).get('index',0)-epoch_start)>12:
    api('/grid/control',dict(action='stop',expected_origin_request_id=req));raise TimeoutError('Probe turn exceeded its time/epoch backstop')
   if seen and not w['running'] and h['status'] in ('ready','complete'):break
   time.sleep(.5)
  snap=snapshot();run=json.loads((data/'current-run.json').read_text())['id']
  result=dict(prompt=prompt,request_id=req,run_id=run,elapsed_seconds=time.time()-began,ending=w['decision_loop']['pause_reason'],new_chat_messages=snap['history']['messages'][len(before):],snapshot=snap)
  write_json(folder/('turn-'+str(index)+'.json'),result);return result
 try:
  import socket
  with socket.socket() as s:
   if s.connect_ex(('127.0.0.1',a.port))==0:raise RuntimeError('Isolated port already in use')
  check_stop()
  current=json.loads((ROOT/'t-scan/runtime_data/current-run.json').read_text())['id']
  config=json.loads((ROOT/'t-scan/runtime_data/runs'/current/'active-config.json').read_text())['config']
  manifest=json.loads((ROOT/'t-scan/runtime_data/grid-world.json').read_text())['world_definition']
  source=ROOT/'t-scan/runtime_data/steve.sqlite3'
  with sqlite3.connect(source.as_uri()+'?mode=ro',uri=True) as src,sqlite3.connect(data/'steve.sqlite3') as dst:src.backup(dst)
  write_json(out/'design.json',dict(probes=PROBES,source_run=current,config=config,manifest=manifest,grading='Review raw replies against snapshots and actual provider disclosure; no automatic semantic pass claims'))
  save();threading.Thread(target=publisher,daemon=True).start();start();rotate()
  for number,probe in enumerate(PROBES,1):
   check_stop();rotate();folder=out/probe['id'];folder.mkdir();status.update(status='running',current_probe=number,current_id=probe['id'],current_question=probe['question']);save()
   result=dict(id=probe['id'],question=probe['question'],steps=[],assessment='pending evidence review')
   for index,step in enumerate(probe['steps'],1):
    status['current_step']=index;save()
    if isinstance(step,dict):
     before=snapshot();run_before=json.loads((data/'current-run.json').read_text())['id']
     if step['op']=='new_chat':operation=rotate()
     else:
      idle();proc.terminate();proc.wait(timeout=15);start();operation=dict(restarted=True)
     after=snapshot();record=dict(op=step['op'],before=before,after=after,run_before=run_before,run_after=json.loads((data/'current-run.json').read_text())['id'],result=operation)
     write_json(folder/('boundary-'+str(index)+'.json'),record);result['steps'].append(record)
    else:
     epoch_start=(api('/health').get('epoch') or {}).get('index',0)
     result['steps'].append(turn(step,folder,index))
   result['archive']=rotate();write_json(folder/'result.json',result);status['results'].append(dict(id=probe['id'],status='captured',turns=sum(isinstance(s,str) for s in probe['steps']),folder=str(folder)));save()
  status.update(status='complete',finished_at_unix=time.time());save()
 except BaseException as error:
  status.update(status='cancelled' if isinstance(error,InterruptedError) else 'failed',error=str(error),finished_at_unix=time.time());save();raise
 finally:
  shutdown.set()
  if proc and proc.poll() is None:
   try:api('/grid/control',dict(action='stop'))
   except Exception:pass
   proc.terminate()
   try:proc.wait(timeout=15)
   except subprocess.TimeoutExpired:proc.kill()
  for log in logs:log.close()

if __name__=='__main__':main()
