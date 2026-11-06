"""Rejections must say what was wrong, that nothing ran, and what to do instead (v8.4.1)."""
import json,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace

import movement_tools
from agent_task_list import execute
from decision_executor import chat_events
from grid_conversation import SYSTEM,VERSION
from grid_world import GridWorld
from runtime_store import RuntimeStore
from world_test_support import publish


class ZeroArgumentValidation(unittest.TestCase):
    def reason(self,name,text):
        with self.assertRaises(ValueError) as caught:movement_tools.validate(name,text)
        return str(caught.exception)

    def test_complete_with_arguments_points_to_task_mark_complete(self):
        message=self.reason('complete',json.dumps(dict(description='the yellow task is done')))
        self.assertIn('takes no arguments',message);self.assertIn('description',message)
        self.assertIn('Nothing was executed',message);self.assertIn('task_mark_complete',message)

    def test_movement_with_arguments_has_no_completion_hint(self):
        message=self.reason('move_north',json.dumps(dict(steps=3)))
        self.assertIn('move_north() takes no arguments',message);self.assertIn('steps',message);self.assertNotIn('task_mark_complete',message)

    def test_hint_matches_the_phase_the_caller_is_in(self):
        args=json.dumps(dict(description='done'))
        with self.assertRaises(ValueError) as executor:movement_tools.registry(phase='executor').validate('complete',args)
        text=str(executor.exception);self.assertIn('not available in this phase',text);self.assertIn('request_replan',text)
        self.assertNotIn('call task_mark_complete',text)
        with self.assertRaises(ValueError) as planner:movement_tools.registry(phase='planner').validate('complete',args)
        self.assertIn('call task_mark_complete',str(planner.exception));self.assertNotIn('request_replan',str(planner.exception))

    def test_non_object_arguments_are_described(self):
        self.assertIn('list value',self.reason('complete','[1]'))

    def test_valid_zero_argument_calls_still_pass(self):
        self.assertEqual(movement_tools.validate('complete','{}'),dict(tool='complete'))
        self.assertEqual(movement_tools.validate('move_east','{}'),dict(tool='move_east'))

    def test_unknown_name_is_distinct_from_bad_arguments(self):
        self.assertEqual(self.reason('move_up','{}'),'Unregistered tool name')


class Client:
    def __init__(self,responses):self.responses=list(responses)
    def stream(self,messages,tools,temperature,should_stop):
        calls=[dict(id='',type='function',function=dict(name=n,arguments=a)) for n,a in self.responses.pop(0)] if self.responses else []
        yield dict(kind='response',text='',calls=calls,finish='tool_calls' if calls else 'stop')


class Dispatch:
    def bind(self,turn):pass
    def submit(self,*args,**kwargs):raise AssertionError('nothing should execute')
    def wait(self,key):raise AssertionError('nothing should execute')
    def reject(self,tool,args,call_id,reason):return dict(outcome=reason,record_type='task_list_receipt')


def receipts(responses,phase='planner'):
    registry=movement_tools.registry(phase=phase)
    events=list(chat_events(Client(responses),[],Dispatch(),'r',registry,1.,lambda:'live',lambda m:None,lambda:False))
    return [e['result'] for e in events if e['kind']=='receipt'],events[-1]


class ExecutorMessages(unittest.TestCase):
    def test_parallel_calls_say_none_executed_and_how_to_proceed(self):
        write=lambda t:('task_list_write',json.dumps(dict(task_id=t,title='Visit '+t,status='pending',expected_revision=3)))
        results,done=receipts([[write('a'),write('b'),write('c')]])
        self.assertEqual(len(results),3);self.assertEqual(done['reason'],'rejected_conflict')
        for result in results:
            self.assertEqual(result['outcome'],'rejected_conflict')
            self.assertIn('3 tool calls',result['error']);self.assertIn('none of them was executed or saved',result['error'])
            self.assertIn('one call',result['error'])

    def test_invalid_json_arguments_are_explained(self):
        results,_=receipts([[('complete','{"description": ')]],phase='executor')
        self.assertIn('not valid JSON',results[0]['error']);self.assertIn('{}',results[0]['error'])
        self.assertEqual(results[0]['error_category'],'schema')


class RejectedReceiptLabel(unittest.TestCase):
    def label(self,outcome):
        from grid_context import inference_messages
        content=json.dumps(dict(record_type='task_list_receipt',call_id='c',outcome=outcome,task_list_revision=4,tool='task_list_write'))
        return json.loads(inference_messages([dict(role='tool',tool_call_id='c',content=content)])[0]['content'])['freshness']

    def test_rejected_call_is_not_labelled_an_edit(self):
        for outcome in ('rejected_conflict','rejected_stale_task_list','denied_governance'):
            text=self.label(outcome);self.assertIn('rejected',text);self.assertIn('nothing was saved',text);self.assertNotIn('edit',text)

    def test_saved_call_keeps_its_label(self):
        self.assertIn('Historical agent-authored task-list edit',self.label('task_list_saved'))


class CompactExperiences(unittest.TestCase):
    def test_recent_experiences_are_compact_x_y_without_a_world_snapshot(self):
        from self_projection import project
        with tempfile.TemporaryDirectory() as folder:
            runtime=RuntimeStore(Path(folder)/'m.db');world=GridWorld(Path(folder)/'w.json');publish(world)
            snapshot=world.observe();receipt=dict(action_id='act-1',call_id='c',turn_id='t',session_id='s',observation_id='s:obs-1',action='move_north',decision='ACCEPT',decision_basis='moved',outcome='moved',position_before=[5,5],position_after=[5,6],facing_before='north',facing_after='north',world_revision=1,observation_seq=1,presentation_status='settled',observation=snapshot,tool='move_north')
            runtime.agent.evidence('run-a',receipt)
            self_model=project(runtime,[dict(role='user',content='go')],snapshot,movement_tools.registry(phase='executor').TOOLS,'run-a')
            experience=self_model['continuity']['recent_experiences'][0];compact=experience['receipt']
            self.assertNotIn('observation',compact);self.assertEqual((compact['position_before'],compact['position_after']),(dict(x=5,y=5),dict(x=5,y=6)))
            self.assertIn('x/y',experience['receipt_form']);self.assertLess(len(json.dumps(experience)),len(json.dumps(receipt))/2)
            runtime.close()


class PlanHandoffRejection(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();root=Path(self.tmp.name)
        self.r=RuntimeStore(root/'memory.db');self.w=GridWorld(root/'world.json');publish(self.w);self.n=0
        execute(self.r,'task_list_write',dict(task_id='red',title='Visit red',status='pending',expected_revision=0),'t1')
        execute(self.r,'task_list_write',dict(task_id='orange',title='Visit orange',status='pending',expected_revision=1),'t2')
        execute(self.r,'task_mark_complete',dict(task_id='red',expected_revision=2),'t3')
    def tearDown(self):self.r.close();self.tmp.cleanup()
    def handoff(self,**changes):
        args=dict(task_id='orange',task_list_revision=3,reason='Next visit',criterion='visit_landmark',landmark_id='target_orange',instructions='Occupy the exact cell.',intention_id=None);args.update(changes)
        self.n+=1;return self.r.agent.execute('plan_handoff',args,'call-'+str(self.n),'decision-'+str(self.n),'run-a',self.w.observe())

    def test_unknown_task_and_stale_revision_are_named_with_current_facts(self):
        result=self.handoff(task_id='purple',task_list_revision=2)
        self.assertEqual(result['outcome'],'rejected_stale_plan')
        for text in ('"purple" is not in your task list','task_list_revision 2 is not the current revision','Current task-list revision: 3','Unfinished task IDs: orange','Nothing was saved'):
            self.assertIn(text,result['error'])
        self.assertEqual((result['current_task_list_revision'],result['unfinished_task_ids']),(3,['orange']))

    def test_completed_task_is_named(self):
        result=self.handoff(task_id='red')
        self.assertIn('"red" is already completed',result['error']);self.assertNotIn('revision 3 is not',result['error'])

    def test_valid_handoff_still_succeeds(self):
        self.assertEqual(self.handoff()['outcome'],'plan_handed_off')


class UmbrellaTaskRecovery(unittest.TestCase):
    """The route that failed in the epoch smoke test: one task covering every flag, marked complete after the second.

    It is not a mechanical dead end: the planner phase still has task_list_write, which adds or reopens a task.
    """
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();root=Path(self.tmp.name)
        self.r=RuntimeStore(root/'memory.db');self.w=GridWorld(root/'world.json');publish(self.w);self.n=0
        execute(self.r,'task_list_write',dict(task_id='visit_flags',title='Visit blue, then red, then yellow in order.',status='in_progress',expected_revision=0),'u1')
        execute(self.r,'task_mark_complete',dict(task_id='visit_flags',expected_revision=1),'u2')   # revision 2, nothing left unfinished
    def tearDown(self):self.r.close();self.tmp.cleanup()
    def agent(self,name,**args):
        self.n+=1;return self.r.agent.execute(name,args,'call-%d'%self.n,'decision-%d'%self.n,'run-a',self.w.observe())
    def handoff(self,task_id,**more):
        return self.agent('plan_handoff',task_id=task_id,task_list_revision=more.pop('revision'),reason='Next step',criterion='visit_landmark',landmark_id='target_yellow',instructions='Occupy the exact cell.',intention_id=more.pop('intention_id',None))

    def test_the_handoff_error_names_both_ways_forward(self):
        result=self.handoff('visit_flags',revision=2)
        self.assertEqual((result['outcome'],result['unfinished_task_ids']),('rejected_stale_plan',[]))
        self.assertIn('Unfinished task IDs: none',result['error']);self.assertIn('task_list_write adds a task with a new task_id',result['error']);self.assertIn('reopens one',result['error'])

    def test_adding_a_task_gets_past_it(self):
        self.assertEqual(execute(self.r,'task_list_write',dict(task_id='visit_yellow',title='Visit the yellow flag.',status='pending',expected_revision=2),'u3')['outcome'],'task_list_saved')
        self.assertEqual(self.handoff('visit_yellow',revision=3)['outcome'],'plan_handed_off')

    def test_reopening_the_task_gets_past_it(self):
        self.assertEqual(execute(self.r,'task_list_write',dict(task_id='visit_flags',title='Visit blue, then red, then yellow in order.',status='in_progress',expected_revision=2),'u3')['outcome'],'task_list_saved')
        self.assertEqual(self.handoff('visit_flags',revision=3)['outcome'],'plan_handed_off')

    def test_a_recorded_goal_can_be_linked_and_stays_active_until_assessed(self):
        goal=self.agent('intention_write',intention_id='visit_in_order',statement='Visit blue, red, then yellow, then complete.',reason='Human request',status='active',lifetime='run',expected_revision=0)
        self.assertIn('revision',goal['record'] if 'record' in goal else goal)
        execute(self.r,'task_list_write',dict(task_id='visit_yellow',title='Visit the yellow flag.',status='pending',expected_revision=2),'u3')
        self.assertEqual(self.handoff('visit_yellow',revision=3,intention_id='visit_in_order')['outcome'],'plan_handed_off')
        self.assertEqual(self.r.agent.get('intention','visit_in_order')['status'],'active')


class PromptWording(unittest.TestCase):
    def test_version_changed_with_the_prompt(self):self.assertEqual(VERSION,'shared-chat-v8.5.0-built-worlds')

    def test_goal_section_sits_between_tasks_and_rejections_in_the_prompt_style(self):
        self.assertIn('\n\nYOUR GOAL\n---------\n',SYSTEM)
        self.assertLess(SYSTEM.index('YOUR TASK LIST\n'),SYSTEM.index('\n\nYOUR GOAL\n'));self.assertLess(SYSTEM.index('\n\nYOUR GOAL\n'),SYSTEM.index('\n\nREJECTED CALLS\n'))
        block=SYSTEM.split('YOUR GOAL\n---------\n',1)[1].split('\n\nREJECTED CALLS',1)[0]
        self.assertEqual(len(block.split('\n')),3)
        for text in ('record your goal with intention_write','its own task','do not mark it complete after the first','intention_id','both your assessments','add or reopen a task with task_list_write'):self.assertIn(text,block)

    def test_planner_line_no_longer_calls_the_goal_optional(self):
        self.assertNotIn('is optional for durable commitments',SYSTEM);self.assertNotIn('Do not send intention_id unless',SYSTEM)
        self.assertIn('record your goal, author your task list',SYSTEM);self.assertIn('linking your goal with intention_id',SYSTEM)

    def test_tool_descriptions_describe_the_goal_flow(self):
        text={t['function']['name']:t['function']['description'] for t in movement_tools.TOOLS}
        self.assertIn('record or revise your goal',text['intention_write']);self.assertIn('links your active goal',text['plan_handoff'])

    def test_prompt_does_not_send_the_executor_to_a_tool_it_lacks(self):
        block=SYSTEM.split('REJECTED CALLS\n--------------\n',1)[1].split('\n\nCONTEXT AUTHORITY',1)[0]
        self.assertIn('planner phase with task_mark_complete',block);self.assertIn('from the executor phase, request_replan',block)

    def test_section_uses_the_prompt_heading_style(self):
        block=SYSTEM.split('REJECTED CALLS\n--------------\n',1)[1].split('\n\nCONTEXT AUTHORITY',1)[0]
        self.assertEqual(len(block.split('\n')),3)
        for text in ('executes nothing and saves nothing','One response carries one call','task_mark_complete'):self.assertIn(text,block)
        self.assertIn('\n\nREJECTED CALLS\n--------------\n',SYSTEM);self.assertIn('\n\nCONTEXT AUTHORITY\n-----------------\n',SYSTEM)

    def test_complete_description_says_no_arguments_and_not_a_task_mark(self):
        description=next(t['function']['description'] for t in movement_tools.TOOLS if t['function']['name']=='complete')
        self.assertIn('Takes no arguments',description);self.assertIn('task_mark_complete',description)


if __name__=='__main__':unittest.main()
