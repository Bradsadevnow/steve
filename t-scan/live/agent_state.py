"""Versioned Self, beliefs and intentions. Model statements never grant capabilities.

All changes, revisions and mutation receipts share the runtime SQLite transaction.
World effects remain owned by GridWorld and are referenced as evidence, not rewritten.
"""
import hashlib, json, re

DIMENSIONS = ('identity', 'agency', 'continuity', 'competence', 'beliefs', 'intentions')


class AgentState:
    def __init__(self, runtime):
        self.runtime = runtime
        self.db = runtime.db
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS agent_records(
          owner TEXT NOT NULL, id TEXT NOT NULL, revision INTEGER NOT NULL,
          body TEXT NOT NULL, PRIMARY KEY(owner,id));
        CREATE TABLE IF NOT EXISTS agent_revisions(
          owner TEXT NOT NULL, id TEXT NOT NULL, revision INTEGER NOT NULL,
          body TEXT NOT NULL, time REAL NOT NULL, call_id TEXT NOT NULL,
          PRIMARY KEY(owner,id,revision));
        CREATE TABLE IF NOT EXISTS agent_mutations(
          call_id TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, result TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS agent_evidence(
          id TEXT PRIMARY KEY, run_id TEXT NOT NULL, kind TEXT NOT NULL,
          body TEXT NOT NULL, time REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS agent_citations(
          owner TEXT NOT NULL, id TEXT NOT NULL, revision INTEGER NOT NULL,
          decision_id TEXT NOT NULL, reason TEXT NOT NULL, time REAL NOT NULL,
          UNIQUE(owner,id,revision,decision_id));
        CREATE TABLE IF NOT EXISTS agent_decisions(
          id TEXT PRIMARY KEY, run_id TEXT NOT NULL, phase TEXT NOT NULL,
          status TEXT NOT NULL, context TEXT, command TEXT, receipt TEXT,
          time REAL NOT NULL);
        ''')
        self.db.commit()
        self.import_identity()

    def records(self, owner=None):
        with self.runtime.lock:
            rows = self.db.execute('SELECT owner,id,revision,body FROM agent_records '
                                   + ('WHERE owner=? ' if owner else '') + 'ORDER BY owner,id',
                                   (owner,) if owner else ()).fetchall()
            return [dict(owner=r['owner'], id=r['id'], revision=r['revision'], **json.loads(r['body'])) for r in rows]

    def get(self, owner, record_id):
        return next((r for r in self.records(owner) if r['id'] == record_id), None)

    def history(self, owner, record_id):
        with self.runtime.lock:
            return [dict(revision=r['revision'], time=r['time'], call_id=r['call_id'], **json.loads(r['body']))
                    for r in self.db.execute('SELECT * FROM agent_revisions WHERE owner=? AND id=? ORDER BY revision', (owner, record_id))]

    def _put(self, owner, record_id, body, expected, call_id):
        current = self.get(owner, record_id)
        actual = current['revision'] if current else 0
        if expected != actual:
            return dict(outcome='rejected_stale_revision', error=f'Use expected_revision={actual}; nothing was saved.', current=current)
        revision = actual + 1
        encoded = json.dumps(body, sort_keys=True, ensure_ascii=True)
        self.db.execute('INSERT OR REPLACE INTO agent_records VALUES(?,?,?,?)', (owner, record_id, revision, encoded))
        self.db.execute('INSERT INTO agent_revisions VALUES(?,?,?,?,?,?)', (owner, record_id, revision, encoded, self.runtime.clock(), call_id))
        return dict(outcome='record_saved', record=dict(owner=owner, id=record_id, revision=revision, **body))

    def import_identity(self):
        # Preserve exact curated source statements. Never classify old prose into
        # invented agency, competence, intentions or autobiographical experiences.
        with self.runtime.lock, self.db:
            seeds = [r for r in self.runtime.seed_memories(limit=1000000, collection='conversation')
                     if r['kind'] == 'self_model' and r['status'] == 'curated_self_model']
            for seed in seeds:
                key = 'seed-' + str(seed['id'])
                if self.get('self', key):
                    continue
                self._put('self', key, dict(dimension='identity', statement=seed['summary'],
                          status='held', scope='global', scope_id='global', origin='curated_source',
                          sources=['event:' + str(seed['id'])], reason='Preserved curated identity source; not firsthand recall.'), 0, 'seed-import:' + key)

    def source(self, reference):
        if reference.startswith('event:') and reference[6:].isdigit():
            row = self.db.execute('SELECT id,kind,source_id,content FROM events WHERE id=?', (int(reference[6:]),)).fetchone()
            if row:
                return dict(id=reference, authority='historical_' + row['kind'], source_id=row['source_id'], content=row['content'])
        row = self.db.execute('SELECT * FROM agent_evidence WHERE id=?', (reference,)).fetchone()
        if row:
            return dict(id=reference, run_id=row['run_id'], authority=row['kind'], content=json.loads(row['body']))
        match = re.fullmatch(r'(self|doctrine|intention|plan):([A-Za-z0-9_-]{1,64})@(\d+)', reference)
        if match:
            owner, record_id, revision = match.groups()
            record = next((r for r in self.history(owner, record_id) if r['revision'] == int(revision)), None)
            if record:
                return dict(id=reference, authority='agent_authored_claim', content=record)
        return None

    def evidence(self, run_id, receipt):
        action_id = receipt.get('action_id')
        if not action_id:
            return
        with self.runtime.lock, self.db:
            # A pending and a settled receipt are separate immutable observations.
            key = 'receipt:' + action_id + ':' + receipt.get('presentation_status', 'not_required')
            self.db.execute('INSERT OR IGNORE INTO agent_evidence VALUES(?,?,?,?,?)',
                            (key, run_id, 'controller_receipt', json.dumps(receipt), self.runtime.clock()))

    def citations(self, owner, record_id, revision):
        return self.db.execute('SELECT COUNT(*) FROM agent_citations WHERE owner=? AND id=? AND revision=?', (owner, record_id, revision)).fetchone()[0]

    def describe(self, record):
        count = self.citations(record['owner'], record['id'], record['revision']) if record['owner'] in ('self', 'doctrine') else 0
        return dict(record, reinforcement=dict(citations=count, status='established' if count >= 3 else 'provisional' if count else 'emergent'),
                    authority='Agent-authored assessment; reinforcement is reliance, not independent verification.')

    def execute(self, name, args, call_id, decision_id, run_id, world):
        fingerprint = hashlib.sha256(json.dumps([name, args], sort_keys=True).encode()).hexdigest()
        with self.runtime.lock, self.db:
            self.db.execute('BEGIN IMMEDIATE')
            prior = self.db.execute('SELECT * FROM agent_mutations WHERE call_id=?', (call_id,)).fetchone()
            if prior:
                result=json.loads(prior['result']) if prior['fingerprint'] == fingerprint else dict(outcome='rejected_call_id_conflict', error='Call ID already belongs to different arguments.')
                return dict(result,record_type='agent_state_receipt',call_id=call_id)
            try:
                from agent_state_tools import validate
                validate(name,json.dumps(args))
                result = self._execute(name, args, call_id, decision_id, run_id, world)
            except (ValueError, KeyError, TypeError) as error:
                result = dict(outcome='rejected_schema', error=str(error))
            self.db.execute('INSERT INTO agent_mutations VALUES(?,?,?)', (call_id, fingerprint, json.dumps(result)))
            return dict(result, record_type='agent_state_receipt', call_id=call_id)

    def _execute(self, name, a, call_id, decision_id, run_id, world):
        if name == 'assertion_write':
            owner = a['owner']
            current = self.get(owner, a['claim_id'])
            refs = [s.strip() for s in a['source_refs'].split(',') if s.strip()]
            if any(self.source(s) is None for s in refs):
                raise ValueError('One or more source references do not exist. No claim was saved.')
            body = dict(dimension=a['dimension'], statement=a['statement'], status=a['status'], scope=a['scope'],
                        scope_id=run_id if a['scope'] == 'run' else world.get('world_manifest_hash', '') if a['scope'] == 'world' else 'global',
                        sources=refs, reason=a['reason'], origin='agent_authored')
            if current:
                body['supersedes'] = f"{owner}:{a['claim_id']}@{current['revision']}"
            return self._put(owner, a['claim_id'], body, a['expected_revision'], call_id)
        if name == 'assertion_cite':
            current = self.get(a['owner'], a['claim_id'])
            if not current or current['revision'] != a['expected_revision']:
                return dict(outcome='rejected_stale_revision', current=current, error='Cite an existing current revision.')
            self.db.execute('INSERT OR IGNORE INTO agent_citations VALUES(?,?,?,?,?,?)',
                            (a['owner'], a['claim_id'], current['revision'], decision_id, a['reason'], self.runtime.clock()))
            return dict(outcome='assertion_cited', record=self.describe(current))
        if name == 'assertion_link':
            current=self.get(a['owner'],a['claim_id'])
            if not current or current['revision']!=a['expected_revision']:
                return dict(outcome='rejected_stale_revision',current=current,error='Link an existing current revision.')
            if self.source(a['reference']) is None:raise ValueError('Referenced source or assertion revision does not exist.')
            body={k:v for k,v in current.items() if k not in ('owner','id','revision')}
            body['links']=body.get('links',[])+[dict(relation=a['relation'],reference=a['reference'],reason=a['reason'])]
            body['supersedes']=f"{a['owner']}:{a['claim_id']}@{current['revision']}"
            return self._put(a['owner'],a['claim_id'],body,a['expected_revision'],call_id)
        if name == 'intention_write':
            body = {k:a[k] for k in ('statement', 'reason', 'status', 'lifetime')}
            body['run_id'] = run_id
            expected = a['expected_revision']
            # A run-lifetime goal left by an earlier run is not this run's record. Its ID is free to reuse:
            # creating (expected_revision 0) continues the same ID's revision history under this run.
            earlier = self.get('intention', a['intention_id'])
            if earlier and expected == 0 and earlier.get('lifetime') == 'run' and earlier.get('run_id') != run_id: expected = earlier['revision']
            return self._put('intention', a['intention_id'], body, expected, call_id)
        if name == 'plan_handoff':
            from agent_task_list import context
            tasks = context(self.runtime)
            task = next((t for t in tasks['tasks'] if t['id'] == a['task_id']), None)
            intention = self.get('intention', a['intention_id']) if a.get('intention_id') else None
            if intention and intention.get('lifetime') == 'run' and intention.get('run_id') != run_id: intention = None
            if not task or task['status'] == 'completed' or tasks['revision'] != a['task_list_revision']:
                unfinished = [t['id'] for t in tasks['tasks'] if t['status'] != 'completed']
                reasons = []
                if not task: reasons.append('task_id ' + json.dumps(a['task_id']) + ' is not in your task list.')
                elif task['status'] == 'completed': reasons.append('task ' + json.dumps(a['task_id']) + ' is already completed.')
                if tasks['revision'] != a['task_list_revision']: reasons.append('task_list_revision ' + str(a['task_list_revision']) + ' is not the current revision.')
                error = ' '.join(reasons) + ' Current task-list revision: ' + str(tasks['revision']) + '. Unfinished task IDs: ' + (', '.join(unfinished) or 'none') + '. task_list_write adds a task with a new task_id, or reopens one by rewriting its task_id with status pending or in_progress. Nothing was saved and the phase did not change.'
                return dict(outcome='rejected_stale_plan', error=error, current_task_list_revision=tasks['revision'], unfinished_task_ids=unfinished)
            if a.get('intention_id') and (not intention or intention['status'] != 'active'):
                recorded = [r['id'] + ' (' + r['status'] + ')' for r in self.records('intention') if r.get('lifetime') == 'persistent' or r.get('run_id') == run_id]
                why = 'has no goal record' if not intention else 'is ' + intention['status'] + ', not active'
                raise ValueError('intention_id ' + json.dumps(a['intention_id']) + ' ' + why + '. Goals recorded for this run: ' + (', '.join(recorded) or 'none') + '. Record or revive it with intention_write (expected_revision 0 for a new goal), or omit intention_id. Nothing was saved and the phase did not change.')
            if a['criterion'] == 'visit_landmark' and not any(t['id'] == a.get('landmark_id') for t in world['visible_targets']):
                raise ValueError('landmark_id ' + json.dumps(a.get('landmark_id')) + ' is not a landmark in the current world. Landmark IDs: ' + ', '.join(t['id'] for t in world['visible_targets']) + '. Nothing was saved and the phase did not change.')
            body = dict(task_id=a['task_id'], task_list_revision=tasks['revision'], intention_id=a.get('intention_id'),reason=a['reason'],desired_outcome=task['title'],
                        intention_revision=intention['revision'] if intention else None, criterion=a['criterion'], landmark_id=a.get('landmark_id'),
                        instructions=a['instructions'], run_id=run_id, world_manifest_hash=world.get('world_manifest_hash'))
            current = self.get('plan', 'current')
            result = self._put('plan', 'current', body, current['revision'] if current else 0, call_id)
            self.set_phase('executor', 'agent_plan_handoff', run_id)
            return dict(result, outcome='plan_handed_off')
        if name == 'request_replan':
            self.set_phase('planner', a['reason'], run_id)
            return dict(outcome='replanning_requested', reason=a['reason'])
        raise ValueError('Unknown agent-state operation')

    def graph(self):
        records=[r for r in self.records() if r['owner'] in ('self','doctrine','intention','plan')]
        nodes=[dict(r,node_id=f"{r['owner']}:{r['id']}@{r['revision']}") for r in records]
        nodes.append(dict(node_id='self:steve',owner='self',kind='persistent_self',label='Steve'))
        edges=[dict(source='self:steve',relation='operates_through_plan' if n['owner']=='plan' else 'intends' if n['owner']=='intention' else 'holds_assessment',target=n['node_id']) for n in nodes if n['node_id']!='self:steve']
        for node in nodes:
            edges.extend(dict(source=node['node_id'],relation='cites_source',target=s) for s in node.get('sources',[]))
            edges.extend(dict(source=node['node_id'],relation=l['relation'],target=l['reference']) for l in node.get('links',[]))
            if node.get('supersedes'):edges.append(dict(source=node['node_id'],relation='supersedes',target=node['supersedes']))
        known={n['node_id'] for n in nodes}
        for reference in sorted({e['target'] for e in edges}-known):
            source=self.source(reference)
            nodes.append(dict(node_id=reference,kind='source_reference',authority=source['authority'] if source else 'unresolved',reference=reference))
        return dict(nodes=nodes,edges=edges,authority='Authored relationships; support/contradiction labels are assessments, not a truth adjudicator.')

    def phase(self):
        record = self.get('orchestration', 'current')
        return record or dict(phase='planner', reason='initial', run_id='')

    def set_phase(self, phase, reason, run_id):
        current = self.get('orchestration', 'current')
        return self._put('orchestration', 'current', dict(phase=phase, reason=reason, run_id=run_id),
                         current['revision'] if current else 0, 'orchestration:' + str(self.runtime.clock()))

    def transition(self, phase, reason, run_id):
        with self.runtime.lock, self.db:
            return self.set_phase(phase, reason, run_id)

    def recover(self):
        with self.runtime.lock, self.db:
            interrupted = self.db.execute("SELECT id FROM agent_decisions WHERE status IN ('deciding','dispatching','receipted')").fetchall()
            self.db.execute("UPDATE agent_decisions SET status='interrupted_requires_review' WHERE status IN ('deciding','dispatching','receipted')")
            if interrupted:
                self.set_phase('planner', 'Interrupted decision requires review; no automatic replay.', self.phase()['run_id'])
            return len(interrupted)

    def decision(self, decision_id, run_id, phase):
        with self.runtime.lock, self.db:
            self.db.execute('INSERT INTO agent_decisions(id,run_id,phase,status,time) VALUES(?,?,?,?,?)',
                            (decision_id, run_id, phase, 'deciding', self.runtime.clock()))

    def decision_update(self, decision_id, **fields):
        if not set(fields) <= {'status', 'context', 'command', 'receipt'}:
            raise ValueError('Invalid decision update')
        with self.runtime.lock, self.db:
            self.db.execute('UPDATE agent_decisions SET ' + ','.join(k+'=?' for k in fields) + ' WHERE id=?',
                            [json.dumps(v) if k != 'status' else v for k,v in fields.items()] + [decision_id])

    def reset_run(self, run_id):
        with self.runtime.lock, self.db:
            for intention in self.records('intention'):
                if intention['lifetime'] == 'run' and intention['status'] == 'active':
                    body = {k:v for k,v in intention.items() if k not in ('owner','id','revision')}
                    body['status'] = 'archived'
                    self._put('intention', intention['id'], body, intention['revision'], 'run-reset:' + run_id)
            self.set_phase('planner', 'new_run', run_id)

    def assess(self, plan, run_id):
        if not plan or plan['run_id'] != run_id or plan['criterion'] != 'visit_landmark':
            return dict(status='unverified', reason='No current explicit machine-checkable criterion.')
        rows = self.db.execute('SELECT id,body FROM agent_evidence WHERE run_id=? ORDER BY time', (run_id,)).fetchall()
        for row in rows:
            receipt = json.loads(row['body']); observation = receipt.get('observation', {})
            if receipt.get('presentation_status') == 'settled' and plan['landmark_id'] in observation.get('standing_on', []) and observation.get('world_manifest_hash') == plan['world_manifest_hash']:
                return dict(status='supported', evidence_id=row['id'], authority='Exact occupancy in a settled controller receipt; does not change task status or prove an unspecified ordering constraint.')
        return dict(status='insufficient_evidence', reason='No matching settled occupancy receipt in this run.')
