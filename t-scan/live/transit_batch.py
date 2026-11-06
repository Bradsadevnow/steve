"""Operator-requested finite navigation batch using the ordinary chat/run APIs.

No movement is selected here. Only the model requests movement tools. Each trial
is archived/reset through New chat and externally graded from settled receipts.
"""
import argparse,json,time,uuid,urllib.request,urllib.error
from pathlib import Path
from atomic_json import write_json

ROUTES=[['blue','red','yellow'],['purple','orange','blue'],['yellow','blue','red'],['red','purple','orange'],['orange','yellow','purple'],['blue','orange','red'],['purple','yellow','blue'],['red','blue','orange'],['yellow','purple','red'],['orange','red','yellow']]

class HumanTakeover(Exception):pass

def grade(events,route,landmarks):
 settled={e['action_id'] for e in events if e.get('kind')=='presentation_result' and e.get('status')=='settled'}
 locations={(v['col'],v['row']):v['color'] for v in landmarks};visits=[];progress=0;steps=0;blocked=0
 for e in events:
  if e.get('action_id') not in settled:continue
  if e.get('outcome') in ('blocked_boundary','blocked_obstacle'):blocked+=1
  if e.get('outcome')!='moved':continue
  steps+=1;color=locations.get(tuple(e['position_after']))
  if color:
   visits.append(color)
   if progress<len(route) and color==route[progress]:progress+=1
 return dict(passed=progress==len(route),ordered_flags_reached=progress,required_flags=route,flag_visits=visits,moved_steps=steps,blocked_steps=blocked)

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--data-dir',type=Path,required=True);p.add_argument('--seconds',type=int,default=300);p.add_argument('--endpoint',default='http://127.0.0.1:8765');args=p.parse_args()
 args.output.mkdir(parents=True,exist_ok=False)
 report=dict(status='starting',seconds_per_test=args.seconds,total_tests=len(ROUTES),routes=ROUTES,results=[],started_at_unix=time.time(),pid=__import__('os').getpid())
 def save():write_json(args.output/'status.json',report)
 def api(route,data=None):
  req=urllib.request.Request(args.endpoint+route,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'})
  with urllib.request.urlopen(req,timeout=8) as r:return json.load(r)
 def stop():
  if not report.get('current_request_id'):return
  try:api('/grid/control',dict(action='stop',expected_origin_request_id=report['current_request_id']))
  except urllib.error.HTTPError as error:
   if error.code!=409:raise
   raise HumanTakeover('Human conversation took over; batch released control') from error
 def drain():
  deadline=time.monotonic()+150
  while time.monotonic()<deadline:
   state=api('/grid/state');health=api('/health')
   if not state['presentation'] and health['status'] in ('ready','complete','error'):return
   time.sleep(.3)
  raise TimeoutError('Stopped run did not settle; batch halted without resetting it')
 def rotate():
  return api('/chat/new',dict(request_id='transit-batch-'+uuid.uuid4().hex))
 save()
 try:
  if args.seconds<1:raise ValueError('Positive test duration required')
  state=api('/grid/state');health=api('/health')
  if health['status'] not in ('ready','complete') or not state['world_ready'] or state['running'] or state['presentation']:raise RuntimeError('Batch requires ready inference, live Unity and an idle loop')
  rotation=rotate();report['prior_run_archive']=rotation;save()
  for number,route in enumerate(ROUTES,1):
   state=api('/grid/state')
   if state['self']!={'id':'steve','col':5,'row':5,'facing':'north'}:raise RuntimeError('Reset verification failed')
   if not state['world_ready']:raise RuntimeError('Unity disconnected before trial')
   run_id=json.loads((args.data_dir/'current-run.json').read_text())['id']
   log=args.data_dir/'grid-world.receipts.jsonl';offset=log.stat().st_size if log.exists() else 0
   prompt='Please visit the '+', then the '.join(color+' flag' for color in route)+', in that order. After visiting all three, call complete.'
   started=time.time();deadline=time.monotonic()+args.seconds
   accepted=api('/generate',dict(prompt=prompt));request_id=accepted['requestId']
   report.update(status='running',current_test=number,current_route=route,current_run_id=run_id,current_request_id=request_id,current_prompt=prompt,current_started_at_unix=started,current_deadline_unix=started+args.seconds);save()
   activated=False;ending='timeout'
   while time.monotonic()<deadline:
    state=api('/grid/state');health=api('/health');loop=state['decision_loop']
    if (args.output/'STOP').exists():stop();report.update(status='cancelled',reason='Batch STOP file');save();return
    if not state['world_ready']:raise RuntimeError('Unity disconnected; batch halted')
    if health['status']=='error':raise RuntimeError('Inference failed: '+health.get('error',''))
    if loop['origin_request_id']==request_id:activated=True
    elif activated and loop['origin_request_id']!=request_id:raise HumanTakeover('New human request detected; batch released control without stopping the conversation')
    if activated and not state['running']:
     ending=loop['pause_reason']
     if ending=='operator':report.update(status='cancelled',reason='Operator Stop');save();return
     break
    time.sleep(.25)
   if ending=='timeout':stop()
   drain();final=api('/grid/state')
   with log.open('rb') as source:source.seek(offset);events=[json.loads(line) for line in source if line.strip()]
   result=dict(test=number,route=route,prompt=prompt,run_id=run_id,request_id=request_id,ending=ending,elapsed_seconds=time.time()-started,final_state=final,**grade(events,route,state['visible_targets']))
   rotation=rotate();result['archive']=rotation;report['results'].append(result);save()
  report.update(status='complete',finished_at_unix=time.time(),passed=sum(r['passed'] for r in report['results']));save()
 except HumanTakeover as error:
  report.update(status='cancelled',reason=str(error),finished_at_unix=time.time());save()
 except BaseException as error:
  try:stop()
  except Exception:pass
  report.update(status='failed',error=str(error),finished_at_unix=time.time());save();raise

if __name__=='__main__':main()
