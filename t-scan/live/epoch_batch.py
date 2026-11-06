"""Epoch-based navigation batch: Steve runs each route until he finishes, not until a clock expires.

A trial ends when Steve calls complete(), idles with a text-only reply, the operator stops it, or a backstop trips:
the epoch cap, the grace period after all three flags were reached in order, or a generous wall-clock limit.
Grading is unchanged (ordered exact-cell arrivals from settled receipts) and is external to Steve's own task marks.
Headline measures are epochs and, offline from the run archive, decisions and tokens to the final arrival;
wall-clock time is recorded as a secondary column. No movement is chosen here.
"""
import argparse,json,time,uuid,urllib.request,urllib.error
from pathlib import Path
from atomic_json import write_json
from transit_batch import ROUTES,HumanTakeover,grade


class TrialWatcher:
    """Pure end-condition and progress tracking, fed one poll at a time."""

    def __init__(self,route,landmarks,run_id,started,max_epochs=40,grace_epochs=3,max_seconds=3600):
        self.route=route;self.landmarks=landmarks;self.run_id=run_id;self.started=started
        self.max_epochs=max_epochs;self.grace_epochs=grace_epochs;self.max_seconds=max_seconds
        self.epochs={};self.latest=None;self.index=0;self.reached=0;self.timeline=[];self.arrived_epoch=None;self.arrived_elapsed=None;self.saw_epoch=False

    def completed(self,after=0):
        """Epochs finished, counted from the latest index so polls that miss a fast epoch cannot undercount."""
        if not self.latest:return 0
        total=self.index if self.latest.get('ending') is not None else self.index-1
        return max(0,total-after)

    def update(self,now,health,events):
        """Record progress; return a backstop ending ('epoch_cap', 'grace_expired', 'wall_clock') or None."""
        epoch=health.get('epoch')
        if isinstance(epoch,dict) and epoch.get('run_id')==self.run_id:
            self.saw_epoch=True;self.index=epoch['index'];self.latest=dict(epoch);self.epochs[epoch['index']]=dict(epoch)
        result=grade(events,self.route,self.landmarks)
        if result['ordered_flags_reached']!=self.reached:
            self.reached=result['ordered_flags_reached']
            self.timeline.append(dict(elapsed_seconds=round(now-self.started,2),epoch=self.index,ordered_flags_reached=self.reached,moved_steps=result['moved_steps']))
            if self.reached==len(self.route) and self.arrived_epoch is None:
                self.arrived_epoch=self.index;self.arrived_elapsed=round(now-self.started,2)
        if self.arrived_epoch is not None and self.completed(self.arrived_epoch)>=self.grace_epochs:return 'grace_expired'
        if self.completed()>=self.max_epochs:return 'epoch_cap'
        if now-self.started>=self.max_seconds:return 'wall_clock'
        return None

    def summary(self):
        completed=self.completed()
        return dict(epochs_started=self.index,epochs_completed=completed,arrived_epoch=self.arrived_epoch,arrived_elapsed_seconds=self.arrived_elapsed,
                    epochs_after_arrival=None if self.arrived_epoch is None else self.completed(self.arrived_epoch),
                    progress_timeline=self.timeline,epochs=[self.epochs[i] for i in sorted(self.epochs)])


def main():
    p=argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('--output',type=Path,required=True);p.add_argument('--data-dir',type=Path,required=True)
    p.add_argument('--max-epochs',type=int,default=40);p.add_argument('--grace-epochs',type=int,default=3)
    p.add_argument('--max-seconds',type=int,default=3600);p.add_argument('--routes',type=int,default=None,help='Run only the first N routes')
    p.add_argument('--routes-file',type=Path,help='JSON array of ordered flag-color routes')
    p.add_argument('--spawn',type=int,nargs=2,default=[5,5],metavar=('X','Y'),help='Expected authored reset cell')
    p.add_argument('--endpoint',default='http://127.0.0.1:8765');args=p.parse_args()
    available=json.loads(args.routes_file.read_text()) if args.routes_file else ROUTES
    if not isinstance(available,list) or not available or any(not isinstance(route,list) or not route or any(not isinstance(color,str) for color in route) for route in available):raise SystemExit('Routes must be a nonempty JSON array of nonempty color arrays')
    count=len(available) if args.routes is None else args.routes
    if min(args.max_epochs,args.grace_epochs,args.max_seconds,count,*args.spawn)<1 or count>len(available):raise SystemExit('Epoch, grace, time, spawn and route limits must be positive; routes cannot exceed the supplied set')
    routes=available[:count]
    args.output.mkdir(parents=True,exist_ok=False)
    report=dict(status='starting',mode='epoch',spawn=args.spawn,limits=dict(max_epochs=args.max_epochs,grace_epochs=args.grace_epochs,max_seconds=args.max_seconds),total_tests=len(routes),routes=routes,results=[],started_at_unix=time.time(),pid=__import__('os').getpid())
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
    def rotate():return api('/chat/new',dict(request_id='epoch-batch-'+uuid.uuid4().hex))
    save()
    try:
        state=api('/grid/state');health=api('/health')
        if health['status'] not in ('ready','complete') or not state['world_ready'] or state['running'] or state['presentation']:raise RuntimeError('Batch requires ready inference, live Unity and an idle loop')
        colors={t['color'] for t in state['visible_targets']}
        if any(color not in colors for route in routes for color in route):raise RuntimeError('A requested flag is absent from the current Unity world; no reset or trial was started')
        report['condition']=dict(execution=health.get('execution'),model=health.get('model'),world_manifest_hash=state.get('world_manifest_hash'))
        report['prior_run_archive']=rotate();save()
        for number,route in enumerate(routes,1):
            state=api('/grid/state')
            if state['self']!={'id':'steve','col':args.spawn[0],'row':args.spawn[1],'facing':'north'}:raise RuntimeError('Reset verification failed')
            if not state['world_ready']:raise RuntimeError('Unity disconnected before trial')
            run_id=json.loads((args.data_dir/'current-run.json').read_text())['id']
            log=args.data_dir/'grid-world.receipts.jsonl';offset=log.stat().st_size if log.exists() else 0
            prompt='Please visit the '+', then the '.join(color+' flag' for color in route)+', in that order. After visiting all requested flags, call complete.'
            started=time.time();landmarks=state['visible_targets']
            request_id=api('/generate',dict(prompt=prompt))['requestId']
            report.update(status='running',current_test=number,current_route=route,current_run_id=run_id,current_request_id=request_id,current_prompt=prompt,current_started_at_unix=started);save()
            watcher=TrialWatcher(route,landmarks,run_id,started,args.max_epochs,args.grace_epochs,args.max_seconds)
            activated=False;ending=None;last_saved=0
            while ending is None:
                now=time.time();state=api('/grid/state');health=api('/health');loop=state['decision_loop']
                if (args.output/'STOP').exists():stop();report.update(status='cancelled',reason='Batch STOP file');save();return
                if not state['world_ready']:raise RuntimeError('Unity disconnected; batch halted')
                if health['status']=='error':raise RuntimeError('Inference failed: '+health.get('error',''))
                if state.get('world_manifest_hash')!=report['condition']['world_manifest_hash'] or health.get('execution')!=report['condition']['execution'] or health.get('model')!=report['condition']['model']:raise RuntimeError('Experimental conditions changed; batch halted')
                if loop['origin_request_id']==request_id:activated=True
                elif activated and loop['origin_request_id']!=request_id:raise HumanTakeover('New human request detected; batch released control without stopping the conversation')
                with log.open('rb') as source:source.seek(offset);events=[json.loads(line) for line in source if line.strip()]
                ending=watcher.update(now,health,events)
                if not watcher.saw_epoch and now-started>45:raise RuntimeError('Backend reports no epoch state; restart it on v8.4.2 or later before using the epoch runner')
                if activated and not state['running'] and ending is None:
                    ending=loop['pause_reason']
                    if ending=='operator':report.update(status='cancelled',reason='Operator Stop');save();return
                    break
                if now-last_saved>10:report.update(current_epoch=watcher.index,current_ordered_flags=watcher.reached,epochs_completed=watcher.completed());save();last_saved=now
                if ending is None:time.sleep(.25)
            if ending in ('epoch_cap','grace_expired','wall_clock'):stop()
            drain();final=api('/grid/state')
            with log.open('rb') as source:source.seek(offset);events=[json.loads(line) for line in source if line.strip()]
            watcher.update(time.time(),api('/health'),events)
            result=dict(test=number,route=route,prompt=prompt,run_id=run_id,request_id=request_id,ending=ending,elapsed_seconds=time.time()-started,final_state=final,**grade(events,route,landmarks),**watcher.summary())
            result['archive']=rotate();report['results'].append(result);save()
        report.update(status='complete',finished_at_unix=time.time(),passed=sum(r['passed'] for r in report['results']));save()
    except HumanTakeover as error:
        report.update(status='cancelled',reason=str(error),finished_at_unix=time.time());save()
    except BaseException as error:
        try:stop()
        except Exception:pass
        report.update(status='failed',error=str(error),finished_at_unix=time.time());save();raise


if __name__=='__main__':main()
