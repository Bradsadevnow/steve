"""One shared chat, one inference connection, one requested step per decision."""
import copy,json,time,uuid,traceback
from lmstudio_client import LMStudio,chat_events
from grid_world import GridDispatch
from grid_conversation import VERSION
from movement_tools import registry,COUNT_ACCEPTED

# Rejected calls do not spend the turn's three calls and get one retry; a second consecutive rejection of the same
# tool ends the turn, and this many such turns in a row hand control back instead of looping.
EPOCH_POLICY=COUNT_ACCEPTED
STALL_EPOCHS=3
from context_records import envelope
from runtime_store import APPRAISAL_SYSTEM
from agent_notepad import AgentDispatch
from agent_task_list import context as task_list_context
from orchestrator import Orchestrator
from epoch_meter import EpochMeter

def appraisal_messages(runtime,job):
 """Legacy archived-context formatter only. Active inference never schedules affect appraisal."""
 history=runtime.history(6);identity=copy.deepcopy(job.get('self_model'))
 if identity:
  eligible=[m['id'] for m in runtime.history(1000000)];supplied=[m['id'] for m in history]
  identity['manifest']['historical_memory']=dict(eligible=eligible,supplied=supplied,omitted=[i for i in eligible if i not in supplied],authority='Active conversation event IDs actually supplied to affect appraisal; no retrieved memory prose is included.')
 return [dict(role='system',content=APPRAISAL_SYSTEM),dict(role='user',content=envelope('affect_appraisal_input',agent_task_list=task_list_context(runtime),self_model=identity,historical_conversation=history,current_user_message=dict(source_id=job.get('source_id'),text=job['prompt'])))]
def claim_job(b,next_tick,now):
 """Human input wins over a continuation; waking and cancellation are serialized."""
 with b.lock:
  world=b.grid_world.observe()
  if world['presentation'] or not world['world_ready']:return None
  job=b.pending;b.pending=None
  if job is None and world['running'] and now>=next_tick:job=dict(source='tick',prompt='',requestId=uuid.uuid4().hex)
  if job is None:return None
  b.active_kind='chat';b.turn_interrupt.clear()
  if job['source']!='tick':b.grid_world.wake(job['requestId'])
  return job

def run(b,args):
 try:
  client=LMStudio(args.lm_url,args.model,args.ctx);info=client.connect();dispatch=AgentDispatch(GridDispatch(b.grid_world),b.runtime);next_tick=0;stall=dict(run=None,epochs=0)
  orchestrator=Orchestrator(b.runtime,b.grid_world,b.conversation);meter=EpochMeter(client.context)
  if getattr(b,'run_archive',None):
   client.on_request=lambda path,payload:b.run_archive.request(path,payload,b.state.get('decisionId') or b.state.get('requestId'))
   client.on_stream_event=lambda data:b.run_archive.stream_event(b.state.get('decisionId') or b.state.get('requestId'),data)
  b.update(status='ready',source='LM Studio / '+args.model,inferenceProvider='lm-studio',model=args.model,contextTokens=client.context,execution=VERSION,toolCallsPerTurn=3,scanMode='disabled',activationTelemetry=False,modelInfo=info)
  while True:
   if getattr(b,'shutdown',None) is not None and b.shutdown.is_set():return
   b.request.wait(.1);b.request.clear()
   job=claim_job(b,next_tick,time.monotonic())
   if job is None:continue
   run_id=b.run_archive.current['id'] if getattr(b,'run_archive',None) else b.grid_world.state['session_id']
   phase=orchestrator.prepare(job,run_id);dispatch.run_id=run_id;b.update(**meter.begin(run_id,job['requestId'],phase,job['source']))
   dispatch.before_call=lambda call:orchestrator.before_call(dispatch.body.turn,call)
   text='';reasoning='';began=time.monotonic();chunks=0;generated=0;had_tool=False;ending=None
   def before_inference(decision_id,index):
    nonlocal reasoning
    if index:
     prior=job['requestId'] if index==1 else job['requestId']+'-decision-'+str(index-1)
     orchestrator.finish(prior)
     orchestrator.store.decision(decision_id,run_id,phase)
    reasoning='';b.update(status='generating',decisionId=decision_id,reasoningText='',reasoningToken='',reasoningTokens=0,reasoningActive=False)
   dispatch.before_inference=before_inference
   b.update(status='generating',text='',token='',reasoningText='',reasoningToken='',reasoningTokens=0,reasoningActive=False,index=0,lastTools=[],usage=None,generatedTokens=0,error='',requestId=job['requestId'],decisionId=job['requestId'],toolCallsPerTurn=3)
   try:
    if job['source']=='tick':b.conversation.tick(b.grid_world.loop_origin)
    else:
     b.conversation.user(job['prompt'])
     # Affect appraisal is retired. Identity and memory are projected independently in conversation.context.
    dispatch.bind(job['requestId']);b.turn_start=len(b.conversation.messages)
    events=chat_events(client,b.conversation.messages,dispatch,job['requestId'],registry(phase=phase,count_policy=EPOCH_POLICY,capabilities=b.grid_world.observe()['character']['capabilities']),args.temperature,lambda:orchestrator.context(dispatch),b.conversation.checkpoint,b.turn_interrupt.is_set)
    try:
     for event in events:
      kind=event['kind']
      if kind!='token' and getattr(b,'run_archive',None):b.run_archive.event(job['requestId'],dict(event,decision_id=dispatch.body.turn))
      if kind=='token':
       text+=event['piece'];chunks+=1;b.update(status='generating',text=text,token=event['piece'],reasoningActive=False,reasoningToken='',index=chunks)
      elif kind=='reasoning':
       reasoning+=event['piece'];b.update(reasoningText=reasoning,reasoningToken=event['piece'],reasoningActive=True)
      elif kind=='usage':
       meter.usage(event['usage']);b.update(context=meter.context())
       generated+=event['usage'].get('completion_tokens',0);b.update(usage=event['usage'],generatedTokens=generated,reasoningTokens=event['usage'].get('completion_tokens_details',{}).get('reasoning_tokens',0))
      elif kind=='call':had_tool=True;meter.call();b.update(epoch=meter.snapshot()['epoch'],status='using_tool',token='',reasoningActive=False,reasoningToken='');b.runtime.event('chat_tool_call',json.dumps(event['call']),event['call']['id'])
      elif kind=='receipt':
       orchestrator.receipt(dispatch.body.turn,run_id,event['result'])
       value=dict(call=event['call'],result=event['result']);b.runtime.event('chat_tool_result',json.dumps(value),event['call']['id']);b.update(lastTools=b.state.get('lastTools',[])+[value])
      elif kind=='done':text=event['text'];ending=event.get('reason');meter.finish(event);b.update(epoch=meter.snapshot()['epoch'])
    finally:events.close()
    if text:b.runtime.event('assistant',text,job['requestId'],job.get('source_id'))
    if not had_tool or ending in ('model_finished','provider_output_limit'):b.grid_world.idle()
    if stall['run']!=run_id:stall.update(run=run_id,epochs=0)
    stall['epochs']=stall['epochs']+1 if ending=='repeated_rejection' else 0
    if stall['epochs']>=STALL_EPOCHS:b.grid_world.stall(stall['epochs'])
    orchestrator.finish(dispatch.body.turn)
    b.update(status='complete',text=text,token='',reasoningActive=False,reasoningToken='',turnEnding=ending,elapsedSeconds=time.monotonic()-began,tokensPerSecond=generated/max(.001,time.monotonic()-began))
   except InterruptedError:
    orchestrator.finish(dispatch.body.turn,'interrupted_requires_review');b.update(status='complete',text=text,token='',reasoningActive=False,reasoningToken='')
   except Exception as e:
    orchestrator.finish(dispatch.body.turn,'failed');traceback.print_exc();b.grid_world.control('stop');b.update(status='error',error=str(e),text=text,token='',reasoningActive=False,reasoningToken='')
   finally:
    b.turn_start=None;next_tick=time.monotonic()+.25
    with b.lock:b.active_kind=None
 except Exception as e:
  traceback.print_exc();b.grid_world.control('stop');b.update(status='error',error=str(e))
