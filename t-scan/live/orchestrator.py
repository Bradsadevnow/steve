"""Schedules machinery phases. Never invents goals, routes or completion claims."""
import json
from agent_task_list import context as task_context
from context_records import decode_envelope

class Orchestrator:
    def __init__(self, runtime, world, conversation):
        self.runtime=runtime;self.world=world;self.conversation=conversation
        self.store=runtime.agent;self.store.recover()

    def prepare(self, job, run_id):
        if job['source']!='tick':self.store.transition('planner','human_message',run_id)
        phase=self.store.phase()['phase']
        if phase=='executor':
            plan=self.store.get('plan','current');world=self.world.observe();tasks=task_context(self.runtime)
            intention=self.store.get('intention',plan['intention_id']) if plan and plan.get('intention_id') else None
            if not plan or plan['run_id']!=run_id or plan['world_manifest_hash']!=world.get('world_manifest_hash') or plan['task_list_revision']!=tasks['revision'] or (plan.get('intention_id') and (not intention or intention['revision']!=plan['intention_revision'] or intention['status']!='active')):
                self.store.transition('planner','Plan references changed; agent review required.',run_id);phase='planner'
        self.conversation.run_id=run_id
        self.store.decision(job['requestId'],run_id,phase)
        return phase

    def before_call(self, decision_id, call):
        self.store.decision_update(decision_id,status='dispatching',command=call)

    def receipt(self, decision_id, run_id, value):
        self.store.evidence(run_id,value)
        self.store.decision_update(decision_id,status='receipted',receipt=value)

    def finish(self, decision_id, status='complete'):
        self.store.decision_update(decision_id,status=status)

    def context(self, dispatch):
        value=self.conversation.context(dispatch)
        record=decode_envelope(value)[1]
        self.store.decision_update(dispatch.body.turn,context=record['self_model']['manifest'])
        return value
