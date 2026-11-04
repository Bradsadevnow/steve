"""One shared chat, one inference connection, one requested step per decision."""
import json,time,uuid,traceback
from lmstudio_client import LMStudio,chat_events
from grid_world import GridDispatch
from grid_conversation import VERSION
from movement_tools import registry
from context_records import envelope
from runtime_store import APPRAISAL_SYSTEM
from agent_notepad import AgentDispatch
from agent_task_list import context as task_list_context

def appraisal_messages(runtime,job):
 return [dict(role='system',content=APPRAISAL_SYSTEM),dict(role='user',content=envelope('affect_appraisal_input',agent_task_list=task_list_context(runtime),historical_conversation=runtime.history(6),current_user_message=dict(source_id=job.get('source_id'),text=job['prompt'])))]
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
  client=LMStudio(args.lm_url,args.model,args.ctx);info=client.connect();dispatch=AgentDispatch(GridDispatch(b.grid_world),b.runtime);next_tick=0
  if getattr(b,'run_archive',None):
   client.on_request=lambda path,payload:b.run_archive.request(path,payload,b.state.get('requestId'))
   client.on_stream_event=lambda data:b.run_archive.stream_event(b.state.get('requestId'),data)
  b.update(status='ready',source='LM Studio / '+args.model,inferenceProvider='lm-studio',model=args.model,contextTokens=client.context,execution=VERSION,scanMode='disabled',activationTelemetry=False,modelInfo=info)
  while True:
   if getattr(b,'shutdown',None) is not None and b.shutdown.is_set():return
   b.request.wait(.1);b.request.clear()
   job=claim_job(b,next_tick,time.monotonic())
   if job is None:continue
   text='';reasoning='';began=time.monotonic();chunks=0;generated=0;had_tool=False
   b.update(status='generating',text='',token='',reasoningText='',reasoningToken='',reasoningTokens=0,reasoningActive=False,index=0,lastTools=[],usage=None,generatedTokens=0,error='',requestId=job['requestId'])
   try:
    if job['source']=='tick':b.conversation.tick(b.grid_world.loop_origin)
    else:
     b.conversation.user(job['prompt'])
     try:
      value=client.appraisal(appraisal_messages(b.runtime,job))
      b.runtime.apply_appraisal(value,job.get('source_id'),job['requestId'])
     except Exception as e:b.runtime.event('appraisal_error',str(e),job['requestId'])
    dispatch.bind(job['requestId']);b.turn_start=len(b.conversation.messages)
    events=chat_events(client,b.conversation.messages,dispatch,job['requestId'],registry(),args.temperature,lambda:b.conversation.context(dispatch),b.conversation.checkpoint,b.turn_interrupt.is_set)
    try:
     for event in events:
      kind=event['kind']
      if kind!='token' and getattr(b,'run_archive',None):b.run_archive.event(job['requestId'],event)
      if kind=='token':
       text+=event['piece'];chunks+=1;b.update(status='generating',text=text,token=event['piece'],reasoningActive=False,reasoningToken='',index=chunks)
      elif kind=='reasoning':
       reasoning+=event['piece'];b.update(reasoningText=reasoning,reasoningToken=event['piece'],reasoningActive=True)
      elif kind=='usage':
       generated+=event['usage'].get('completion_tokens',0);b.update(usage=event['usage'],generatedTokens=generated,reasoningTokens=event['usage'].get('completion_tokens_details',{}).get('reasoning_tokens',0))
      elif kind=='call':had_tool=True;b.update(status='using_tool',token='',reasoningActive=False,reasoningToken='');b.runtime.event('chat_tool_call',json.dumps(event['call']),event['call']['id'])
      elif kind=='receipt':
       value=dict(call=event['call'],result=event['result']);b.runtime.event('chat_tool_result',json.dumps(value),event['call']['id']);b.update(lastTools=b.state.get('lastTools',[])+[value])
      elif kind=='done':text=event['text']
    finally:events.close()
    if text:b.runtime.event('assistant',text,job['requestId'],job.get('source_id'))
    if not had_tool:b.grid_world.idle()
    b.update(status='complete',text=text,token='',reasoningActive=False,reasoningToken='',elapsedSeconds=time.monotonic()-began,tokensPerSecond=generated/max(.001,time.monotonic()-began))
   except InterruptedError:b.update(status='complete',text=text,token='',reasoningActive=False,reasoningToken='')
   except Exception as e:traceback.print_exc();b.grid_world.control('stop');b.update(status='error',error=str(e),text=text,token='',reasoningActive=False,reasoningToken='')
   finally:
    b.turn_start=None;next_tick=time.monotonic()+.25
    with b.lock:b.active_kind=None
 except Exception as e:traceback.print_exc();b.update(status='error',error=str(e))
