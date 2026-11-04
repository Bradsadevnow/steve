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


def chat_events(*args, **kwargs):
    # Stable import for existing integrations; execution belongs to its own boundary.
    from decision_executor import chat_events as execute_decision
    return execute_decision(*args, **kwargs)
