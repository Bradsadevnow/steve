"""Read-only operator projection. Never selects tasks or authors Self content."""
import json
from agent_task_list import context as task_context
from movement_tools import TOOLS


def record_item(record):
    return dict(owner=record['owner'],id=record['id'],revision=record['revision'],
                statement=record.get('statement',''),reason=record.get('reason',''),
                dimension=record.get('dimension',''),status=record.get('status',''))


def build(runtime, world, run_id, health):
    with runtime.lock:
        observed=world.observe();store=runtime.agent;records=store.records()
        tasks=task_context(runtime)['tasks'];plan=store.get('plan','current')
        if plan and plan['run_id']!=run_id:plan=None
        selected=next((t for t in tasks if plan and t['id']==plan['task_id']),None)
        focus=None
        if selected and selected['status']!='completed':
            focus=dict(task_id=selected['id'],title=selected['title'],reason=plan.get('reason',''),status=selected['status'],goal_id=plan.get('intention_id') or '')
        def eligible(record):
            if record.get('status') in ('retired','archived','fulfilled','abandoned'):return False
            scope=record.get('scope','global')
            return scope=='global' or record.get('scope_id')==(run_id if scope=='run' else observed.get('world_manifest_hash'))
        authored=[r for r in records if r['owner'] in ('self','doctrine') and eligible(r) and r.get('origin')=='agent_authored']
        assessments=[record_item(r) for r in authored if r['owner']=='self' and r.get('dimension')!='beliefs']
        beliefs=[record_item(r) for r in authored if r['owner']=='doctrine' or r.get('dimension')=='beliefs']
        # Goals are this run's intentions in any status, so a fulfilled or abandoned goal stays visible as Steve's assessment.
        # Commitments are the persistent ones that survive New chat. Neither is chosen or edited here.
        goals=[dict(record_item(r),lifetime=r['lifetime'],linked_to_focus=bool(focus and focus['goal_id']==r['id'])) for r in records if r['owner']=='intention' and r.get('lifetime')=='run' and r.get('run_id')==run_id]
        commitments=[record_item(r) for r in records if r['owner']=='intention' and r['status']=='active' and r['lifetime']=='persistent']
        rows=store.db.execute('SELECT id,body FROM agent_evidence WHERE run_id=? ORDER BY time DESC LIMIT 12',(run_id,)).fetchall()
        recent=[];counts={};seen=set()
        for row in store.db.execute('SELECT id,body FROM agent_evidence WHERE run_id=? ORDER BY time',(run_id,)):
            receipt=json.loads(row['body'])
            if not receipt.get('action','').startswith('move_') or receipt['action_id'] in seen:continue
            # Pending presentation is not counted as a settled action.
            if receipt.get('presentation_status')=='pending':continue
            seen.add(receipt['action_id']);outcome=receipt.get('outcome','unknown');counts[outcome]=counts.get(outcome,0)+1
        for row in rows:
            receipt=json.loads(row['body']);action=receipt.get('action','');outcome=receipt.get('outcome','')
            before=receipt.get('position_before');after=receipt.get('position_after')
            if action.startswith('move_') and before and after:
                direction=action[5:]
                if outcome=='moved':summary=f'Moved {direction}: ({before[0]}, {before[1]}) → ({after[0]}, {after[1]})'
                elif outcome=='blocked_boundary':summary=f'Blocked {direction} at ({after[0]}, {after[1]})'
                else:summary=f'{direction.capitalize()} request: {outcome.replace("_"," ")}'
            elif action=='complete':summary='Ended the interaction'
            else:summary=outcome.replace('_',' ')
            recent.append(dict(id=row['id'],summary=summary,status=receipt.get('presentation_status',''),outcome=outcome))
        names={t['function']['name'] for t in TOOLS};capabilities=[]
        if {'move_north','move_south','move_east','move_west'}<=names:capabilities.append('Move one cell north, south, east or west')
        if 'task_list_write' in names:capabilities.append('Maintain tasks and choose a plan')
        if 'assertion_write' in names:capabilities.append('Record and revise beliefs and self-assessments')
        if 'intention_write' in names:capabilities.append('Keep commitments across conversations')
        running=observed['running'];activity='Idle' if not running else 'Moving' if observed.get('presentation') else 'Thinking' if health.get('status')=='generating' else 'Continuing'
        a=observed['self'];latest=store.db.execute('SELECT id,phase,status,context FROM agent_decisions ORDER BY time DESC LIMIT 1').fetchone()
        return dict(schema='steve-self-view-v1',activity=activity,
                    position=dict(x=a['col'],y=a['row'],facing=a['facing'],current=observed['world_ready']),
                    focus=focus,goals=goals,tasks=[dict(id=t['id'],title=t['title'],status=t['status'],in_focus=bool(focus and focus['task_id']==t['id'])) for t in tasks],
                    status_note='Goal and task statuses are Steve\'s own assessments, not verified by the world.',unfinished=[dict(id=t['id'],title=t['title'],status=t['status']) for t in tasks if t['status']!='completed'],
                    finished=[dict(id=t['id'],title=t['title'],status=t['status']) for t in tasks if t['status']=='completed'],
                    commitments=commitments,assessments=assessments,beliefs=beliefs,capabilities=capabilities,
                    recent=recent,attempts=dict(total=sum(counts.values()),moved=counts.get('moved',0),blocked=counts.get('blocked_boundary',0)),
                    inspection=dict(phase=store.phase()['phase'],records=[store.describe(r) for r in records if r['owner'] in ('self','doctrine','intention')],
                                    latest_decision=dict(latest) if latest else None,
                                    metadata_scope='Storage and provenance; available material differs from a decision-specific supplied context.'))
