"""Steve's local state/tool bridge, with inference supplied by LM Studio."""
import argparse, json, threading, uuid, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
from runtime_store import RuntimeStore
ROOT=Path(__file__).resolve().parents[1]
runtime=None
lock=threading.Lock()
state=dict(schema=3,indexBase=0,identity='text_stream',source='LM Studio',status='starting',token='',text='',index=0,
           nodes=[],edges=[],layers=0,width=0,nodeCount=0,scanMode='disabled',sampleCount=0,error='',
           purpose='steve-harness-observability',researchInterventionsEnabled=False)
request=threading.Event(); pending=None
active_kind=None
conversation=None
grid_world=None
run_archive=None
turn_interrupt=threading.Event()
turn_start=None

def update(**kw):
    with lock: state.update(kw)

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def send_json(self,data,status=200):
        body=json.dumps(data,ensure_ascii=False,allow_nan=False).encode()
        self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(body))); self.end_headers()
        try: self.wfile.write(body)
        except (ConnectionError,OSError): pass
    def do_GET(self):
        if not self.allowed():return self.send_json(dict(error='Forbidden request origin'),403)
        route=urlsplit(self.path);query=parse_qs(route.query)
        if route.path=='/self-view':
            from self_view import build
            with lock:health=dict(state)
            return self.send_json(build(runtime,grid_world,run_archive.current['id'] if run_archive else grid_world.state['session_id'],health))
        if route.path=='/agent-state':
            from movement_tools import registry
            with runtime.lock:
                phase=runtime.agent.phase();rows=runtime.db.execute('SELECT * FROM agent_decisions ORDER BY time DESC LIMIT 8').fetchall()
                decisions=[dict(row) for row in rows]
                for decision in decisions:
                    for field in ('context','command','receipt'):
                        if decision[field]:decision[field]=json.loads(decision[field])
                run_id=run_archive.current['id'] if run_archive else grid_world.state['session_id']
                plan=runtime.agent.get('plan','current')
                if plan and plan['run_id']!=run_id:plan=None
                payload=dict(identity='Steve',records=[runtime.agent.describe(r) for r in runtime.agent.records() if r['owner'] in ('self','doctrine','intention')],phase=phase,plan=plan,evidence_assessment=runtime.agent.assess(plan,run_id),continuation_running=grid_world.running,capabilities=[t['function']['name'] for t in registry(phase=phase['phase']).TOOLS],decisions=decisions,authority='Stored claims and records; decision context manifests identify actual supplied material.')
            return self.send_json(payload)
        if route.path=='/agent-state/graph':return self.send_json(runtime.agent.graph())
        if route.path=='/agent-state/history':
            owner=query.get('owner',['self'])[0];record_id=query.get('id',[''])[0]
            if owner not in ('self','doctrine','intention','plan','orchestration'):return self.send_json(dict(error='Invalid owner'),400)
            return self.send_json(dict(owner=owner,id=record_id,revisions=runtime.agent.history(owner,record_id)))
        if self.path=='/operator-notes':return self.send_json(run_archive.operator_notes())
        if self.path=='/grid/state':return self.send_json(grid_world.observe())
        if self.path=='/notepad':
            from agent_notepad import context
            return self.send_json(context(runtime))
        if self.path=='/task-list':
            from agent_task_list import context
            return self.send_json(context(runtime))
        if self.path.startswith(('/hex/','/avatar/','/experiment/','/body/')):return self.send_json(dict(error='Workbench interface is retired; use /grid/state'),410)
        if self.path=="/memory_graphs":return self.send_json(runtime.graphs())
        if self.path=="/development":return self.send_json(dict(records=runtime.seed_memories(limit=1000,collection="development")))
        if self.path=="/seed_memories":return self.send_json(dict(memories=runtime.seed_memories(limit=100)))
        if self.path=="/runtime":return self.send_json(runtime.snapshot())
        if self.path=="/history":
            with lock:live_start=turn_start if active_kind is not None else None;live_text=state.get('text','');live_id=state.get('requestId','');live_token=state.get('token','')
            return self.send_json(dict(messages=conversation.history(live_start,live_text,live_id,live_token)))
        if self.path not in ('/frame','/health'): return self.send_json({'error':'not found'},404)
        with lock: snapshot=dict(state)
        if self.path=='/health':
            snapshot['nodeSamples']=len(snapshot.pop('nodes',[]))
            snapshot['displayLinks']=len(snapshot.pop('edges',[]))
        self.send_json(snapshot)
    def allowed(self,post=False):
        """Loopback-only API. Reject browser cross-origin requests and DNS-rebinding Host values.

        Browsers always attach Origin to cross-origin writes and cannot send application/json cross-origin
        without a preflight this server never answers. The Unity viewer and batch runner send neither Origin
        nor a foreign Host, and already send Content-Type: application/json.
        """
        port=str(self.server.server_address[1])
        if (self.headers.get('Host') or '').lower() not in ('127.0.0.1:'+port,'localhost:'+port):return False
        if self.headers.get('Origin') is not None:return False
        return not post or (self.headers.get('Content-Type') or '').lower().startswith('application/json')
    def do_POST(self):
        global pending
        if not self.allowed(True):return self.send_json(dict(error='Forbidden request origin or content type'),403)
        if self.path=='/operator-notes':
            from run_archive import OperatorNotesConflict
            try:
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<=524288:raise ValueError('Invalid notes size')
                data=json.loads(self.rfile.read(length))
                with lock:value=run_archive.save_operator_notes(data['run_id'],data['expected_revision'],data['content'])
                return self.send_json(value)
            except OperatorNotesConflict as error:return self.send_json(dict(error=str(error),current=error.current),409)
            except (ValueError,KeyError) as error:return self.send_json(dict(error=str(error)),400)
            except OSError as error:return self.send_json(dict(error='Could not save notes: '+str(error)),500)
        if self.path=='/chat/new':
            try:
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<=4096:raise ValueError('Invalid request size')
                data=json.loads(self.rfile.read(length));key=data.get('request_id')
                if not isinstance(key,str) or not key or len(key)>100:raise ValueError('request_id required')
                with lock:
                    if pending is not None or active_kind is not None or grid_world.pending:return self.send_json(dict(error='Stop or wait for the current turn and presentation before starting a new chat'),409)
                    result=run_archive.new_chat(conversation,runtime,grid_world,key)
                    state.update(status='ready',text='',token='',reasoningText='',reasoningToken='',reasoningTokens=0,reasoningActive=False,error='',lastTools=[],usage=None,generatedTokens=0,requestId='',index=0,epoch=None,context=None)
                return self.send_json(result)
            except (ValueError,KeyError) as error:return self.send_json(dict(error=str(error)),400)
            except Exception as error:return self.send_json(dict(error='Archive/new chat failed: '+str(error)),500)
        if self.path in ('/grid/world','/grid/poll','/grid/ack','/grid/control'):
            try:
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<=65536:raise ValueError('Invalid grid request size')
                data=json.loads(self.rfile.read(length))
                if not isinstance(data,dict):raise ValueError('Expected a grid request object')
                if self.path=='/grid/world':
                    with lock:
                        if active_kind is not None:return self.send_json(dict(error='Wait for the current turn before registering the world'),409)
                        value=grid_world.register_world(data['client_id'],data['manifest'])
                    return self.send_json(value)
                if self.path=='/grid/poll':return self.send_json(grid_world.poll(data['client_id'],data.get('manifest_hash')))
                if self.path=='/grid/ack':return self.send_json(dict(accepted=grid_world.acknowledge(data['client_id'],data['action_id'],data['session_id'])))
                action=data['action']
                with lock:
                    expected=data.get('expected_origin_request_id')
                    if expected is not None:
                        if action!='stop' or not isinstance(expected,str) or not expected:raise ValueError('An origin guard requires stop and a nonempty request ID')
                        if grid_world.loop_origin!=expected or (pending is not None and pending['requestId']!=expected):
                            return self.send_json(dict(outcome='control_skipped',reason='Conversation ownership changed'),409)
                    if action in ('run','reset') and (pending is not None or active_kind is not None):return self.send_json(dict(error='Wait for the current turn to finish'),409)
                    value=grid_world.control(action)
                    runtime.event('operator_grid_control',json.dumps(dict(action=action,state=value)))
                    if run_archive:run_archive.event(None,dict(kind='operator_grid_control',action=action,state=value))
                    if action in ('stop','reset'):
                        if pending:
                            state['cancelledRequests']=(state.get('cancelledRequests',[])+[pending['requestId']])[-32:]
                            runtime.event('request_cancelled','Operator stopped the queued turn',pending['requestId'])
                        pending=None;turn_interrupt.set();conversation.pause('stopped')
                        if active_kind is None:state.update(status='complete',token='')
                request.set();return self.send_json(value)
            except (ValueError,KeyError) as e:return self.send_json(dict(error=str(e)),400)
        if self.path.startswith(('/hex/','/experiment/','/avatar/','/body/')):return self.send_json(dict(error='The workbench interface is retired; use the grid interface'),410)
        if self.path!='/generate':return self.send_json({'error':'not found'},404)
        try:
            length=int(self.headers.get('Content-Length','0'))
            if length<1 or length>131072: raise ValueError('Invalid request size')
            data=json.loads(self.rfile.read(length))
            prompt=data['prompt']
            if not isinstance(prompt,str) or not prompt.strip() or len(prompt)>40000:raise ValueError('Nonempty prompt up to 40000 characters required')
            if data.get('diagnostic'):raise ValueError('Isolated diagnostic conversations are retired')
            request_id=uuid.uuid4().hex
            with lock:
                if pending is not None:return self.send_json(dict(error='A human turn is already queued'),409)
                source_id=runtime.accept_user(prompt,request_id)
                pending=dict(kind='chat',source='user',prompt=prompt,requestId=request_id,source_id=source_id)
                if active_kind is not None:turn_interrupt.set()
                else:state.update(status='queued',requestId=request_id,requestKind='chat',text='',token='',index=0,error='')
            request.set();return self.send_json(dict(accepted=True,requestId=request_id),202)
        except (ValueError,KeyError) as exc: self.send_json({'error':str(exc)},400)

def worker(args):
    from grid_worker import run
    return run(sys.modules[__name__],args)

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--model',default='google/gemma-4-e4b')
    parser.add_argument('--lm-url',default='http://192.168.1.128:1234')
    parser.add_argument('--ctx',type=int,default=131072)
    parser.add_argument('--temperature',type=float,default=1.)
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--data-dir',type=Path,default=ROOT/'runtime_data')
    parser.add_argument('--database',default=None)
    args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    runtime=RuntimeStore(args.database or args.data_dir/'steve.sqlite3')
    from grid_conversation import GridConversation
    conversation=GridConversation(args.data_dir/'conversation.json',runtime)
    from grid_world import GridWorld
    grid_world=GridWorld(args.data_dir/'grid-world.json')
    from run_archive import RunArchive
    run_archive=RunArchive(args.data_dir,conversation,runtime,grid_world,dict(model=args.model,lm_url=args.lm_url,temperature=args.temperature,context_capacity=args.ctx))
    threading.Thread(target=worker,args=(args,),daemon=True).start()
    print(f'Steve bridge http://127.0.0.1:{args.port} -> LM Studio {args.lm_url} / {args.model}',flush=True)
    server.serve_forever()

