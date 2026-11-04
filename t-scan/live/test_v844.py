"""v8.4.4: complete, exact handoff errors, goal-link errors, the stall stop, and no facing in what the model sees."""
import json,tempfile,unittest
from pathlib import Path

import agent_state_tools
import movement_tools
from agent_task_list import execute
from grid_context import coordinate_world,compact_receipt,inference_messages,xy_self
from grid_conversation import SYSTEM
from grid_world import GridWorld
from runtime_store import RuntimeStore
from world_test_support import publish


def handoff(**changes):
    args=dict(task_id='visit_blue',task_list_revision=3,reason='Next step',criterion='visit_landmark',landmark_id='target_blue',instructions='Occupy the exact cell.',intention_id=None);args.update(changes)
    return json.dumps({k:v for k,v in args.items() if v != '__omit__'})


class CompleteHandoffErrors(unittest.TestCase):
    def reason(self,raw):
        with self.assertRaises(ValueError) as caught:agent_state_tools.validate('plan_handoff',raw)
        return str(caught.exception)

    def test_manual_criterion_accepts_a_null_or_missing_landmark(self):
        for landmark in (None,'__omit__'):self.assertEqual(agent_state_tools.validate('plan_handoff',handoff(criterion='manual',landmark_id=landmark))['criterion'],'manual')

    def test_visit_landmark_without_a_landmark_says_how_to_fix_it(self):
        text=self.reason(handoff(landmark_id=None))
        self.assertIn('landmark_id: required when criterion is visit_landmark',text);self.assertIn('received null',text);self.assertIn('For a manual criterion, omit landmark_id or send null',text)
        self.assertIn('nothing was executed or saved',text);self.assertNotEqual(text,'Invalid landmark_id')

    def test_every_problem_is_reported_in_one_message(self):
        text=self.reason(json.dumps(dict(task_id='bad id!',task_list_revision=-1,criterion='someday',instructions='',surprise=1)))
        self.assertIn('(6 problems; nothing was executed or saved)',text)
        for part in ('task_id: must be 1 to 64 letters','task_list_revision: must be a nonnegative integer','criterion: must be one of visit_landmark, manual; received "someday"','instructions: must have at least 1','surprise: not a field of plan_handoff','reason: required, but missing'):self.assertIn(part,text)

    def test_long_values_are_not_echoed_whole(self):
        text=self.reason(handoff(criterion='manual',landmark_id='x'*400))
        self.assertIn('landmark_id: must have at most 100 characters; received 400',text);self.assertNotIn('x'*100,text)

    def test_non_object_arguments(self):
        with self.assertRaises(ValueError) as caught:agent_state_tools.validate('plan_handoff','[1]')
        self.assertIn('must be one JSON object',str(caught.exception))

    def test_other_tools_get_the_same_exact_errors(self):
        with self.assertRaises(ValueError) as caught:agent_state_tools.validate('intention_write',json.dumps(dict(intention_id='g',statement='s',reason='r',status='done',lifetime='run',expected_revision='0')))
        text=str(caught.exception);self.assertIn('status: must be one of active, fulfilled, abandoned; received "done"',text);self.assertIn('expected_revision: must be a nonnegative integer',text)

    def test_the_valid_call_still_passes(self):
        self.assertEqual(agent_state_tools.validate('plan_handoff',handoff())['task_id'],'visit_blue')

    def test_tool_description_says_what_manual_takes(self):
        text=next(t['function']['description'] for t in movement_tools.TOOLS if t['function']['name']=='plan_handoff')
        self.assertIn('requires landmark_id',text);self.assertIn('takes no landmark_id',text)
        required=next(t['function']['parameters']['required'] for t in movement_tools.TOOLS if t['function']['name']=='plan_handoff');self.assertNotIn('landmark_id',required)
        self.assertIn('expected_revision 0 when creating',next(t['function']['description'] for t in movement_tools.TOOLS if t['function']['name']=='intention_write'))


class ExecutionErrors(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();root=Path(self.tmp.name)
        self.r=RuntimeStore(root/'memory.db');self.w=GridWorld(root/'world.json');publish(self.w);self.n=0
        execute(self.r,'task_list_write',dict(task_id='visit_blue',title='Visit blue',status='pending',expected_revision=0),'t1')
    def tearDown(self):self.r.close();self.tmp.cleanup()
    def agent(self,name,**args):
        self.n+=1;return self.r.agent.execute(name,args,'call-%d'%self.n,'decision-%d'%self.n,'run-a',self.w.observe())
    def handoff(self,**changes):
        args=dict(task_id='visit_blue',task_list_revision=1,reason='Next step',criterion='visit_landmark',landmark_id='target_blue',instructions='Occupy the exact cell.',intention_id=None);args.update(changes)
        return self.agent('plan_handoff',**args)

    def test_unrecorded_goal_link_names_the_goals_that_exist_and_how_to_record_one(self):
        self.agent('intention_write',intention_id='real_goal',statement='Visit blue.',reason='Human request',status='active',lifetime='run',expected_revision=0)
        result=self.handoff(intention_id='visit-flags-sequence');text=result['error']
        for part in ('intention_id "visit-flags-sequence" has no goal record','Goals recorded for this run: real_goal (active)','intention_write (expected_revision 0 for a new goal)','omit intention_id','Nothing was saved'):self.assertIn(part,text)

    def test_goal_link_with_no_goals_says_none(self):
        self.assertIn('Goals recorded for this run: none',self.handoff(intention_id='anything')['error'])

    def test_inactive_goal_is_named_as_such(self):
        self.agent('intention_write',intention_id='old',statement='Old.',reason='r',status='abandoned',lifetime='run',expected_revision=0)
        self.assertIn('is abandoned, not active',self.handoff(intention_id='old')['error'])

    def test_unknown_landmark_lists_the_real_ones(self):
        text=self.handoff(landmark_id='target_green')['error']
        self.assertIn('"target_green" is not a landmark in the current world',text);self.assertIn('target_blue',text);self.assertIn('target_yellow',text)

    def test_manual_handoff_without_a_landmark_succeeds(self):
        self.assertEqual(self.handoff(criterion='manual',landmark_id=None)['outcome'],'plan_handed_off')
        self.assertIsNone(self.r.agent.get('plan','current')['landmark_id'])


class Stall(unittest.TestCase):
    def test_stall_hands_control_back_with_its_own_reason(self):
        with tempfile.TemporaryDirectory() as folder:
            world=GridWorld(Path(folder)/'w.json');world.wake('req-1');world.stall(3)
            observed=world.observe();self.assertFalse(observed['running']);self.assertEqual(observed['decision_loop']['pause_reason'],'stalled')
            log=[json.loads(l) for l in (Path(folder)/'w.receipts.jsonl').read_text().splitlines()]
            self.assertEqual(log[-1]['kind'],'decision_loop_stalled');self.assertEqual(log[-1]['epochs'],3)

    def test_stall_does_nothing_when_the_loop_is_not_running(self):
        with tempfile.TemporaryDirectory() as folder:
            world=GridWorld(Path(folder)/'w.json');world.stall(3);self.assertNotEqual(world.observe()['decision_loop']['pause_reason'],'stalled')


class NoFacingForTheModel(unittest.TestCase):
    def world(self):
        with tempfile.TemporaryDirectory() as folder:
            world=GridWorld(Path(folder)/'w.json');publish(world);return world.observe()

    def test_current_world_text_has_no_facing(self):
        text=coordinate_world(self.world());self.assertNotIn('facing',text);self.assertIn('STEVE / measured now',text)

    def test_receipts_have_no_facing(self):
        compact=compact_receipt(dict(action_id='a',action='move_north',outcome='moved',position_before=[5,5],position_after=[5,6],facing_before='north',facing_after='north'))
        self.assertNotIn('facing_before',compact);self.assertNotIn('facing_after',compact);self.assertEqual(compact['position_after'],dict(x=5,y=6))

    def test_historical_positions_have_no_facing(self):
        self.assertEqual(xy_self(dict(id='steve',col=2,row=3,facing='east')),dict(id='steve',x=2,y=3))

    def test_prompt_and_movement_tools_do_not_mention_facing(self):
        self.assertNotIn('facing',SYSTEM.lower())
        for tool in movement_tools.TOOLS:self.assertNotIn('facing',tool['function']['description'].lower())

    def test_authoritative_state_and_the_operator_view_keep_facing(self):
        observed=self.world();self.assertEqual(observed['self']['facing'],'north')


if __name__=='__main__':unittest.main()
