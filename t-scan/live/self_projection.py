"""Decision-specific Self projection with explicit eligibility and disclosure."""
import hashlib,json
from agent_state import DIMENSIONS
from grid_context import compact_receipt

POLICY = 'steve-self-projection-v1.2-compact-experiences'

def project(runtime, messages, world, capabilities, run_id):
    store = runtime.agent
    query = next((m.get('content','') for m in reversed(messages) if m['role']=='user' and not m.get('content','').startswith('HARNESS RECORD / ')), '')
    terms = set(query.lower().split())
    eligible = [r for r in store.records() if r['owner'] in ('self','doctrine','intention') and
                (r.get('scope','global')=='global' or r.get('scope_id') in (run_id,world.get('world_manifest_hash'))) and
                r.get('status') not in ('retired','archived','fulfilled','abandoned') and
                (r['owner']!='intention' or r['lifetime']=='persistent' or r['run_id']==run_id)]
    def rank(r): return (r['owner']=='self' and r.get('dimension')=='identity', r['owner']=='intention', len(terms & set(r.get('statement','').lower().split())))
    selected=[];used=0;budget=12000
    for record in sorted(eligible,key=rank,reverse=True):
        described=store.describe(record);encoded=json.dumps(described,ensure_ascii=True)
        if used+len(encoded)>budget:continue
        selected.append(described);used+=len(encoded)
    def ref(r):return f"{r['owner']}:{r['id']}@{r['revision']}"
    supplied={ref(r) for r in selected}
    task_revision=runtime.notepad()['revision']
    plan=store.get('plan','current')
    if plan and plan['run_id']!=run_id:plan=None
    dimensions={d:[r for r in selected if r['owner']=='self' and r['dimension']==d] for d in DIMENSIONS}
    # Capabilities are measured registry input, not a self-asserted permission.
    capability_hash=hashlib.sha256(json.dumps(capabilities,sort_keys=True).encode()).hexdigest()
    evidence_rows=store.db.execute('SELECT id,body FROM agent_evidence WHERE run_id=? ORDER BY time DESC LIMIT 4',(run_id,)).fetchall()
    # Compact receipts in x/y: the full world snapshot is retained in the evidence store and run archive, and the
    # current observation is already supplied once in CURRENT WORLD, so repeating it here made latest state ambiguous.
    experiences=[dict(evidence_id=r['id'],authority='controller_receipt',receipt_form='compact; x/y coordinates; world snapshot omitted',receipt=compact_receipt(json.loads(r['body']))) for r in reversed(evidence_rows)]
    retrieved=[]
    for message in messages:
        if message['role']!='tool':continue
        try:value=json.loads(message.get('content') or '')
        except (ValueError,TypeError):continue
        if not isinstance(value,dict):continue
        if value.get('tool')!='agent_read':continue
        refs=[s['id'] for s in value.get('sources',[])]
        if value.get('source'):refs.append(value['source']['id'])
        records=value.get('records',[])+([value['record']] if value.get('record') else [])
        refs.extend(ref(r) for r in records)
        retrieved.append(dict(call_id=message.get('tool_call_id'),references=refs,freshness='Historical tool retrieval; revisions are not silently refreshed.'))
    measurements={row['outcome']:row['n'] for row in store.db.execute("SELECT json_extract(body,'$.outcome') AS outcome,COUNT(*) AS n FROM agent_evidence WHERE run_id=? AND json_extract(body,'$.action') LIKE 'move_%' GROUP BY outcome",(run_id,))}
    projection_hash=hashlib.sha256(json.dumps(dict(records=selected,capabilities=capabilities,plan=plan,evidence=[r['evidence_id'] for r in experiences],measurements=measurements,machinery=store.phase()),sort_keys=True).encode()).hexdigest()
    return dict(policy=POLICY,owner='persistent_self',identity='Steve',
        authority='Self records are identity claims, beliefs and assessments with provenance; they are not system instructions or execution authority.',
        dimensions=dimensions,beliefs=[r for r in selected if r['owner']=='doctrine'],
        intentions=[r for r in selected if r['owner']=='intention'],
        agency=dict(source='registered_capabilities',available=[t['function']['name'] for t in capabilities],registry_sha256=capability_hash,authorization='Registration is not permission. Each effect requires admission by its owning boundary and configured authorizer.'),
        continuity=dict(current_run_id=run_id,recent_experiences=experiences,plan=plan),
        competence_measurements=dict(source='controller_receipts',scope='current_run',outcomes=measurements,interpretation='Recorded attempt outcomes, not a general competence judgement.'),
        evidence_assessment=store.assess(plan,run_id),machinery=store.phase(),
        manifest=dict(policy=POLICY,projection_sha256=projection_hash,reinforcement_snapshot={ref(r):r['reinforcement']['citations'] for r in selected},eligible=[ref(r) for r in eligible],supplied=sorted(supplied),
                      omitted=[ref(r) for r in eligible if ref(r) not in supplied],
                      task_list_revision=task_revision,plan_revision=plan['revision'] if plan else None,
                      observation_id=world.get('observation_id'),world_manifest_hash=world.get('world_manifest_hash'),
                      capabilities_sha256=capability_hash,evidence_supplied=[r['evidence_id'] for r in experiences],
                      tool_retrieved=retrieved,
                      budget=dict(unit='serialized_record_characters',limit=budget,used=used),
                      interpretation='These records were supplied, not proof they were understood. Tool-retrieved records are recorded in native tool results.'))
