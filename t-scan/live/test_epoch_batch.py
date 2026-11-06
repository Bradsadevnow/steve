"""Epoch runner: end conditions in isolation, then the whole runner against a scripted fake bridge."""
import json,sys,tempfile,threading,time,unittest
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

import epoch_batch
from epoch_batch import TrialWatcher

ROUTE=['blue','red','yellow']
LANDMARKS=[dict(col=8,row=7,color='blue'),dict(col=2,row=8,color='red'),dict(col=9,row=2,color='yellow')]
CELL={'blue':[8,7],'red':[2,8],'yellow':[9,2]}


def arrival(n,color):
    return [dict(action_id='a%d'%n,outcome='moved',position_after=CELL[color]),dict(kind='presentation_result',action_id='a%d'%n,status='settled')]


def health(index,ending=None,run='run-1'):
    return dict(status='generating',epoch=dict(run_id=run,index=index,calls=1,clock_spent=0,ending=ending))


class Watcher(unittest.TestCase):
    def test_settled_obstacle_bumps_are_counted_without_arrivals(self):
        events=[dict(action_id='bump',outcome='blocked_obstacle',position_after=[5,5]),dict(kind='presentation_result',action_id='bump',status='settled')]
        result=epoch_batch.grade(events,['red'],LANDMARKS)
        self.assertEqual((result['blocked_steps'],result['moved_steps'],result['ordered_flags_reached']),(1,0,0))
    def make(self,**limits):return TrialWatcher(ROUTE,LANDMARKS,'run-1',100.0,**limits)

    def test_progress_is_graded_from_settled_arrivals_and_stamped_with_the_epoch(self):
        w=self.make();events=[]
        events+=arrival(1,'blue');self.assertIsNone(w.update(110.0,health(1),events))
        events+=arrival(2,'red');w.update(130.0,health(2),events)
        self.assertEqual([(t['epoch'],t['ordered_flags_reached']) for t in w.timeline],[(1,1),(2,2)])
        self.assertIsNone(w.arrived_epoch)

    def test_unsettled_arrival_does_not_count(self):
        w=self.make();w.update(110.0,health(1),[dict(action_id='a1',outcome='moved',position_after=CELL['blue'])]);self.assertEqual(w.reached,0)

    def test_out_of_order_arrival_does_not_advance(self):
        w=self.make();w.update(110.0,health(1),arrival(1,'red'));self.assertEqual(w.reached,0)

    def test_epoch_cap_counts_completed_epochs_only(self):
        w=self.make(max_epochs=2)
        self.assertIsNone(w.update(101.0,health(1,'tool_call_limit'),[]))
        self.assertIsNone(w.update(102.0,health(2),[]))
        self.assertEqual(w.update(103.0,health(2,'tool_call_limit'),[]),'epoch_cap')

    def test_grace_runs_from_the_epoch_after_the_final_arrival(self):
        w=self.make(grace_epochs=2,max_epochs=99);events=arrival(1,'blue')+arrival(2,'red')+arrival(3,'yellow')
        self.assertIsNone(w.update(110.0,health(3),events));self.assertEqual(w.arrived_epoch,3)
        self.assertIsNone(w.update(111.0,health(3,'tool_call_limit'),events))
        self.assertIsNone(w.update(112.0,health(4,'tool_call_limit'),events))
        self.assertEqual(w.update(113.0,health(5,'tool_call_limit'),events),'grace_expired')

    def test_wall_clock_backstop(self):
        self.assertEqual(self.make(max_seconds=60).update(161.0,health(1),[]),'wall_clock')

    def test_stale_epoch_from_a_previous_run_is_ignored(self):
        w=self.make();w.update(101.0,health(7,'tool_call_limit',run='old-run'),[])
        self.assertFalse(w.saw_epoch);self.assertEqual(w.completed(),0)

    def test_summary_reports_epochs_and_timeline(self):
        w=self.make();w.update(110.0,health(1,'tool_call_limit'),arrival(1,'blue'));summary=w.summary()
        self.assertEqual((summary['epochs_started'],summary['epochs_completed']),(1,1));self.assertEqual(summary['progress_timeline'][0]['ordered_flags_reached'],1)


class FakeBridge:
    """Just enough of the bridge API; a script thread plays Steve once a request is accepted."""
    def __init__(self,folder,script):
        self.folder=Path(folder);self.script=script;self.lock=threading.Lock();self.n=0;self.stopped=False
        self.running=False;self.origin=None;self.pause='startup';self.health_status='ready';self.epoch=None
        (self.folder/'current-run.json').write_text(json.dumps(dict(id='run-1')));self.log=self.folder/'grid-world.receipts.jsonl';self.log.write_text('')
    def state(self):
        return dict(self=dict(id='steve',col=5,row=5,facing='north'),world_ready=True,running=self.running,presentation=None,visible_targets=LANDMARKS,
                    decision_loop=dict(active=self.running,origin_request_id=self.origin,pause_reason=self.pause))
    def health(self):return dict(status=self.health_status,epoch=self.epoch)
    def play(self):
        for step in self.script:
            time.sleep(.4)  # longer than the runner's .25 s poll, as real epochs are
            with self.lock:
                if not self.running:return
                index=step['epoch']
                for color in step.get('arrive',[]):
                    self.n+=1
                    with self.log.open('a') as f:
                        for event in arrival(self.n,color):f.write(json.dumps(event)+'\n')
                self.epoch=dict(run_id='run-1',index=index,calls=3,clock_spent=0,ending=step.get('ending','tool_call_limit'))
                if step.get('complete'):self.running=False;self.pause='complete';self.health_status='complete'
        # script exhausted: keep running until stopped, like an idle-looping model
    def serve(self):
        fake=self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*a):pass
            def reply(self,value,status=200):
                body=json.dumps(value).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
            def do_GET(self):
                with fake.lock:self.reply(fake.state() if self.path=='/grid/state' else fake.health())
            def do_POST(self):
                data=json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))) or b'{}')
                with fake.lock:
                    if self.path=='/chat/new':return self.reply(dict(archived_run_id='x',new_run_id='run-1'))
                    if self.path=='/generate':
                        fake.running=True;fake.origin='req-1';fake.pause=None;fake.health_status='generating'
                        threading.Thread(target=fake.play,daemon=True).start();return self.reply(dict(accepted=True,requestId='req-1'),202)
                    if self.path=='/grid/control':
                        fake.running=False;fake.pause='operator' if False else 'stopped';fake.health_status='complete';fake.stopped=True;return self.reply(dict(outcome='ok'))
                self.reply(dict(error='nope'),404)
        self.server=ThreadingHTTPServer(('127.0.0.1',0),Handler);self.port=self.server.server_address[1]
        threading.Thread(target=self.server.serve_forever,daemon=True).start()


class WholeRunner(unittest.TestCase):
    def test_custom_two_flag_route_and_course_spawn(self):
        with tempfile.TemporaryDirectory() as directory:
            routes=Path(directory)/'routes.json';routes.write_text(json.dumps([['red','blue']]))
            original=FakeBridge.state
            with patch.object(FakeBridge,'state',lambda fake:dict(original(fake),self=dict(id='steve',col=8,row=8,facing='north'))):
                report,_=self.run_runner([dict(epoch=1,arrive=['red']),dict(epoch=2,arrive=['blue'],complete=True)],'--routes-file',str(routes),'--spawn','8','8')
            self.assertEqual(report['routes'],[['red','blue']]);self.assertTrue(report['results'][0]['passed'])
            self.assertIn('After visiting all requested flags',report['results'][0]['prompt'])
    def run_runner(self,script,*flags):
        with tempfile.TemporaryDirectory() as folder:
            fake=FakeBridge(folder,script);fake.serve()
            output=Path(folder)/'out'
            argv=['epoch_batch','--output',str(output),'--data-dir',folder,'--routes','1','--max-seconds','25','--endpoint','http://127.0.0.1:%d'%fake.port,*flags]
            try:
                with patch.object(sys,'argv',argv):epoch_batch.main()
            finally:fake.server.shutdown();fake.server.server_close()
            return json.loads((output/'status.json').read_text()),fake

    def test_runs_until_steve_completes(self):
        report,_=self.run_runner([dict(epoch=1,arrive=['blue']),dict(epoch=2,arrive=['red']),dict(epoch=3,arrive=['yellow'],complete=True)])
        self.assertEqual(report['status'],'complete');result=report['results'][0]
        self.assertEqual((result['ending'],result['ordered_flags_reached'],result['passed']),('complete',3,True))
        self.assertEqual(result['arrived_epoch'],3);self.assertEqual([t['ordered_flags_reached'] for t in result['progress_timeline']],[1,2,3])

    def test_grace_expires_when_steve_never_completes(self):
        script=[dict(epoch=1,arrive=['blue','red','yellow']),dict(epoch=2),dict(epoch=3)]
        report,fake=self.run_runner(script,'--grace-epochs','2')
        result=report['results'][0];self.assertEqual((result['ending'],result['passed'],result['arrived_epoch']),('grace_expired',True,1));self.assertTrue(fake.stopped)

    def test_epoch_cap_stops_a_run_that_never_arrives(self):
        report,fake=self.run_runner([dict(epoch=i) for i in range(1,6)],'--max-epochs','3')
        result=report['results'][0];self.assertEqual((result['ending'],result['passed'],result['epochs_completed']),('epoch_cap',False,3));self.assertTrue(fake.stopped)

    def test_bad_limits_are_refused(self):
        with patch.object(sys,'argv',['epoch_batch','--output','x','--data-dir','y','--max-epochs','0']),self.assertRaises(SystemExit):epoch_batch.main()


if __name__=='__main__':unittest.main()
