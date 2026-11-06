"""Two consecutive five-run repetitions, using the normal archived epoch runner."""
import argparse,json,subprocess,sys,time,os
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'t-scan/live'))
from atomic_json import write_json
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
routes=[['red','blue'],['blue','yellow'],['yellow','purple'],['purple','red'],['red','yellow']]
write_json(out/'routes.json',routes)
status=dict(status='starting',pid=os.getpid(),batches=2,trials_per_batch=5,routes=routes,started_at_unix=time.time(),results=[])
def save():write_json(out/'status.json',status)
save()
try:
 for batch in (1,2):
  folder=out/('batch-'+str(batch));status.update(status='running',current_batch=batch,current_folder=str(folder));save()
  with (out/('batch-'+str(batch)+'.log')).open('w') as log:
   proc=subprocess.Popen([sys.executable,'-S',str(root/'t-scan/live/epoch_batch.py'),'--output',str(folder),'--data-dir',str(root/'t-scan/runtime_data'),'--routes-file',str(out/'routes.json'),'--spawn','8','8','--max-epochs','40','--max-seconds','1200'],cwd=root,stdout=log,stderr=subprocess.STDOUT)
   status['runner_pid']=proc.pid;save()
   while proc.poll() is None:
    if (out/'STOP').exists() and folder.exists():(folder/'STOP').touch()
    time.sleep(1)
  report=json.loads((folder/'status.json').read_text());status['results'].append(dict(batch=batch,status=report['status'],passed=report.get('passed'),trials=len(report['results'])));save()
  if report['status']!='complete':status.update(status=report['status'],reason=report.get('reason') or report.get('error'));break
  if (out/'STOP').exists():status.update(status='cancelled',reason='Parent STOP file');break
 else:status.update(status='complete',passed=sum(r['passed'] for r in status['results']))
except Exception as error:
 status.update(status='failed',error=str(error));raise
finally:
 status['finished_at_unix']=time.time();save()
