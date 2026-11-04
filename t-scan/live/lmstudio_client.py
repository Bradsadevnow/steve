"""HTTP inference only. No local model, templates, activation hooks or text tool parser."""
import copy,json,os,urllib.request,urllib.error,uuid

def api_messages(messages):
    value=copy.deepcopy(messages)
    for message in value:
        for call in message.get('tool_calls',[]):
            arguments=call['function']['arguments']
            if not isinstance(arguments,str):call['function']['arguments']=json.dumps(arguments)
    return value

class LMStudio:
    def __init__(self,url,model,context=131072):
        self.url=url.rstrip('/').removesuffix('/v1');self.model=model;self.context=context
        self.headers={'Content-Type':'application/json'}
        if os.environ.get('LM_STUDIO_API_KEY'):self.headers['Authorization']='Bearer '+os.environ['LM_STUDIO_API_KEY']
    def request(self,path,payload=None):
        if payload is not None and getattr(self,'on_request',None):self.on_request(path,copy.deepcopy(payload))
        req=urllib.request.Request(self.url+path,data=None if payload is None else json.dumps(payload).encode(),headers=self.headers)
        try:return urllib.request.urlopen(req,timeout=120)
        except urllib.error.HTTPError as error:
            raise RuntimeError('LM Studio HTTP '+str(error.code)+': '+error.read().decode('utf-8','replace')) from error
    def connect(self):
        with self.request('/v1/models') as response:models=json.load(response)['data']
        if not any(m['id']==self.model for m in models):raise ValueError('LM Studio does not list '+self.model)
        with self.request('/api/v0/models') as response:details=json.load(response)['data']
        info=next(m for m in details if m['id']==self.model)
        self.context=info.get('loaded_context_length') or info.get('max_context_length') or self.context
        return info
    def payload(self,messages,temperature,tools=None):
        value=dict(model=self.model,messages=api_messages(messages),temperature=temperature)
        if tools:value.update(tools=tools,tool_choice='auto',parallel_tool_calls=False)
        return value
    def stream(self,messages,tools,temperature,should_stop=lambda:False):
        payload=self.payload(messages,temperature,tools)
        payload.update(stream=True,stream_options=dict(include_usage=True))
        calls={};text='';finish=None;completed=False
        with self.request('/v1/chat/completions',payload) as response:
            for line in response:
                if not line.startswith(b'data:'):continue
                raw=line[5:].strip()
                if getattr(self,'on_stream_event',None):self.on_stream_event(raw.decode('utf-8'))
                if should_stop():raise InterruptedError('Turn interrupted by operator')
                if raw==b'[DONE]':completed=True;break
                event=json.loads(raw)
                if event.get('error'):raise RuntimeError('LM Studio: '+json.dumps(event['error']))
                if event.get('usage'):yield dict(kind='usage',usage=event['usage'])
                for choice in event.get('choices',[]):
                    delta=choice.get('delta',{})
                    # Providers may use either name; prefer one alias to avoid duplication.
                    reasoning=delta.get('reasoning_content') or delta.get('reasoning')
                    if isinstance(reasoning,str) and reasoning:yield dict(kind='reasoning',piece=reasoning)
                    piece=delta.get('content') or ''
                    if piece:text+=piece;yield dict(kind='token',piece=piece,speech=True,token=None,states=None)
                    for part in delta.get('tool_calls',[]):
                        call=calls.setdefault(part['index'],dict(id='',type='function',function=dict(name='',arguments='')))
                        if part.get('id'):call['id']=part['id']
                        for key in ('name','arguments'):call['function'][key]+=part.get('function',{}).get(key,'')
                    if choice.get('finish_reason'):finish=choice['finish_reason']
        if not completed or finish is None:raise RuntimeError('LM Studio stream ended without a completion marker; no pending tools executed')
        if finish not in ('stop','tool_calls','length'):raise RuntimeError('LM Studio stopped with '+finish)
        yield dict(kind='response',text=text,calls=[calls[k] for k in sorted(calls)],finish=finish)
    def appraisal(self,messages):
        from runtime_store import EMOTIONS
        schema=dict(type='object',properties=dict(signals=dict(type='array',maxItems=3,items=dict(type='object',properties=dict(name=dict(type='string',enum=list(EMOTIONS)),delta=dict(type='integer',minimum=-2,maximum=2)),required=['name','delta'],additionalProperties=False))),required=['signals'],additionalProperties=False)
        payload=self.payload(messages,.25)
        payload.update(stream=False,max_tokens=2048,response_format=dict(type='json_schema',json_schema=dict(name='affect_appraisal',strict=True,schema=schema)))
        with self.request('/v1/chat/completions',payload) as response:value=json.load(response)['choices'][0]
        if value.get('finish_reason')=='length':raise ValueError('Affect appraisal reached its separate output allowance')
        return value['message']['content']

def chat_events(client,messages,dispatch,request_id,registry,temperature,live_message,on_transcript,should_stop):
    """Each complete structured call is validated, executed once, and receipted before another inference."""
    messages=copy.deepcopy(messages);display='';ordinal=0
    while True:
        if should_stop():raise InterruptedError('Turn interrupted by operator')
        messages.append(dict(role='user',content=live_message()));on_transcript(messages)
        response=None;partial=''
        try:
            outgoing=getattr(registry,'INFERENCE_MESSAGES',lambda value:value)(messages)
            for event in client.stream(outgoing,registry.TOOLS,temperature,should_stop):
                if event['kind']=='response':response=event
                else:
                    if event['kind']=='token':partial+=event['piece']
                    yield event
        except BaseException:
            if partial:messages.append(dict(role='assistant',content=partial));on_transcript(messages)
            raise
        display+=response['text']
        if response['finish']=='length':
            messages.append(dict(role='assistant',content=response['text']));on_transcript(messages)
            yield dict(kind='done',text=display,reason='provider_output_limit');return
        calls=response['calls']
        if not calls:
            messages.append(dict(role='assistant',content=response['text']));on_transcript(messages)
            yield dict(kind='done',text=display,reason='model_finished');return
        for call in calls:
            call['id']=request_id+'-tool-'+str(ordinal);ordinal+=1
        messages.append(dict(role='assistant',content=response['text'],tool_calls=calls))
        reported=None;halt=False
        for call in calls:
            name=call['function']['name'];arguments=call['function']['arguments']
            yield dict(kind='call',call=call)
            try:
                if name not in registry.SCHEMAS:raise ValueError('Unregistered tool name')
                outer=json.loads(arguments)
                direct=getattr(registry,'DIRECT_ARGUMENTS',getattr(registry,'ZERO_ARGUMENT',False))
                if direct:
                    target=outer;command=registry.validate(name,arguments)
                else:
                    if not isinstance(outer,dict) or set(outer)!={'target'}:raise ValueError('Expected exactly the target argument')
                    target=outer['target'];command=registry.validate(name,json.dumps(target))
                if reported or halt or should_stop():result=dispatch.reject(name,target,call['id'],'stopped') if direct else dict(outcome='interrupted',error='Earlier call ended or operator stopped this turn')
                elif direct and len(calls)!=1:result=dispatch.reject(name,target,call['id'],'rejected_conflict')
                else:
                    key=dispatch.submit(target,call['id'],tool=name);result=dispatch.wait(key)
                result=dict(result,tool=name,command=command)
            except (ValueError,TypeError,KeyError) as error:
                result=dispatch.reject(name,{},call['id'],'rejected_schema') if getattr(registry,'DIRECT_ARGUMENTS',getattr(registry,'ZERO_ARGUMENT',False)) else dict(outcome='rejected',error=str(error),error_category='schema',tool=name)
                result=dict(result,error=str(error),error_category='schema',tool=name)
            messages.append(dict(role='tool',tool_call_id=call['id'],content=json.dumps(result,indent=2)))
            # Keep call/result pairs durable together, including partial batches.
            yield dict(kind='receipt',call=call,result=result)
            if result.get('outcome')=='task_reported':reported='reported_'+result['task_status']
            halt=halt or result.get('outcome') in ('stopped','offline','timeout','interrupted')
        on_transcript(messages)
        if reported or halt or getattr(registry,'SINGLE_ACTION',False):
            yield dict(kind='done',text=display,reason=reported or ('interrupted' if halt else 'action_resolved'));return
        if display and not display.endswith(('\n',' ')):display+='\n'
