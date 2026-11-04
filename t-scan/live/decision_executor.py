"""Execute one model decision through the registered action boundary.

Provider transport lives in lmstudio_client; scheduling lives in orchestrator.
"""
import copy,json,traceback

def chat_events(client,messages,dispatch,request_id,registry,temperature,live_message,on_transcript,should_stop):
    """Each complete structured call is validated, executed once, and receipted before another inference."""
    messages=copy.deepcopy(messages);display='';ordinal=0;decision_index=0
    limit=getattr(registry,'MAX_CALLS',1 if getattr(registry,'SINGLE_ACTION',False) else 3)
    if type(limit) is not int or limit<1:raise ValueError('Positive integer tool-call limit required')
    # all_calls (v8.4): every call, even a rejected one, spends the allowance.
    # clock_actions: only registered clock tools the controller admitted spend it; MAX_TOTAL_CALLS bounds the rest.
    # accepted_calls: every call counts except a rejected one, which gets a free retry; a second consecutive
    # rejection of the same tool ends the turn ('repeated_rejection') so a failing call cannot loop.
    policy=getattr(registry,'COUNT_POLICY','all_calls');spent=0;accepted=0;rejected=0;streak_tool=None;streak=0
    if policy not in ('all_calls','clock_actions','accepted_calls'):raise ValueError('Unknown epoch count policy')
    ceiling=getattr(registry,'MAX_TOTAL_CALLS',limit)
    if type(ceiling) is not int or ceiling<limit:raise ValueError('Total-call ceiling must be an integer of at least the clock budget')
    while True:
        if should_stop():raise InterruptedError('Turn interrupted by operator')
        decision_id=request_id if decision_index==0 else request_id+'-decision-'+str(decision_index)
        if hasattr(dispatch,'bind'):dispatch.bind(decision_id)
        if getattr(dispatch,'before_inference',None):dispatch.before_inference(decision_id,decision_index)
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
            call['id']=decision_id+'-tool-'+str(ordinal);ordinal+=1
        messages.append(dict(role='assistant',content=response['text'],tool_calls=calls))
        reported=None;halt=False
        for call in calls:
            name=call['function']['name'];arguments=call['function']['arguments']
            if getattr(dispatch,'before_call',None):dispatch.before_call(call)
            yield dict(kind='call',call=call)
            direct=getattr(registry,'DIRECT_ARGUMENTS',getattr(registry,'ZERO_ARGUMENT',False))
            stage='validate'
            try:
                if name not in registry.SCHEMAS:raise ValueError('Unregistered tool name')
                try:outer=json.loads(arguments)
                except ValueError as error:raise ValueError('Arguments for '+name+' were not valid JSON ('+str(error)+'). Nothing was executed. Send one JSON object; use {} for a tool that takes no arguments.') from error
                if direct:
                    target=outer;command=registry.validate(name,arguments)
                else:
                    if not isinstance(outer,dict) or set(outer)!={'target'}:raise ValueError('Expected exactly the target argument')
                    target=outer['target'];command=registry.validate(name,json.dumps(target))
                stage='execute'
                if reported or halt or should_stop():result=dispatch.reject(name,target,call['id'],'stopped') if direct else dict(outcome='interrupted',error='Earlier call ended or operator stopped this turn')
                elif direct and len(calls)!=1:result=dict(dispatch.reject(name,target,call['id'],'rejected_conflict'),error='This response contained '+str(len(calls))+' tool calls. Only one call per response is allowed, so none of them was executed or saved. Send one call, wait for its result, then send the next.')
                else:
                    key=dispatch.submit(target,call['id'],tool=name);result=dispatch.wait(key)
                result=dict(result,tool=name,command=command)
            except (ValueError,TypeError,KeyError) as error:
                if stage=='execute' and not isinstance(error,ValueError):
                    # A fault in the harness, not in the model's call: keep it out of the schema-rejection count.
                    traceback.print_exc()
                    result=dict(outcome='internal_error',error_category='internal',tool=name,error='Harness fault ('+type(error).__name__+') while executing this call. Your arguments were not found invalid, and whether the call took effect is not confirmed; read current state before relying on it.')
                else:
                    # Validation failures are schema errors; a store refusal (limits, conflicts) raised while executing is not.
                    category,reason=('schema','rejected_schema') if stage=='validate' else ('store','rejected_store')
                    result=dispatch.reject(name,{},call['id'],reason) if direct else dict(outcome='rejected',tool=name)
                    result=dict(result,error=str(error),error_category=category,tool=name)
            messages.append(dict(role='tool',tool_call_id=call['id'],content=json.dumps(result,indent=2)))
            # Keep call/result pairs durable together, including partial batches.
            yield dict(kind='receipt',call=call,result=result)
            if name in getattr(registry,'CLOCK',()) and result.get('outcome') in getattr(registry,'CLOCK_OUTCOMES',()):spent+=1
            if str(result.get('outcome','')).startswith(('rejected','denied')) or result.get('outcome')=='internal_error':
                rejected+=1;streak=streak+1 if streak_tool==name else 1;streak_tool=name
            else:
                accepted+=1;streak=0;streak_tool=None
            if result.get('outcome')=='task_reported':reported='reported_'+result['task_status']
            halt=halt or result.get('outcome') in ('stopped','offline','timeout','interrupted') or result.get('presentation_status') in ('timeout','failed')
        on_transcript(messages)
        outcome=result.get('outcome')
        boundary=outcome in ('interaction_complete','plan_handed_off','replanning_requested')
        if policy=='clock_actions':exhausted='clock_budget' if spent>=limit else 'call_ceiling' if ordinal>=ceiling else None
        elif policy=='accepted_calls':exhausted='tool_call_limit' if accepted>=limit else 'call_ceiling' if ordinal>=ceiling else None
        else:exhausted='tool_call_limit' if ordinal>=limit else None
        repeated=policy!='all_calls' and streak>=2
        if reported or halt or boundary or len(calls)!=1 or repeated or exhausted:
            reason=reported or ('interrupted' if halt else 'phase_boundary' if boundary else 'rejected_conflict' if len(calls)!=1 else 'repeated_rejection' if repeated else exhausted)
            yield dict(kind='done',text=display,reason=reason,epoch=dict(policy=policy,calls=ordinal,accepted=accepted,rejected=rejected,clock_spent=spent,clock_limit=limit));return
        decision_index+=1
        if display and not display.endswith(('\n',' ')):display+='\n'
