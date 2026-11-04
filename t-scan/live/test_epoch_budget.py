"""Epoch clock registration and the two budget-counting policies."""
import unittest
from types import SimpleNamespace

import movement_tools
from decision_executor import chat_events


class ScriptedClient:
    """Each inference emits exactly one call from the script, then a text-only reply when the script ends."""
    def __init__(self,names):self.names=list(names)
    def stream(self,messages,tools,temperature,should_stop):
        if not self.names:yield dict(kind='response',text='done',calls=[],finish='stop');return
        call=dict(id='',type='function',function=dict(name=self.names.pop(0),arguments='{}'))
        yield dict(kind='response',text='',calls=[call],finish='tool_calls')


class Dispatch:
    """moves succeed unless listed in refused; everything else is a free non-clock call."""
    def __init__(self,refused=()):self.refused=set(refused);self.n=0
    def bind(self,turn):pass
    def submit(self,target,call_id=None,tool=None):self.n+=1;return (call_id,tool)
    def wait(self,key):
        call_id,tool=key
        if tool.startswith('move_'):return dict(outcome='rejected_stale' if call_id in self.refused else 'moved')
        return dict(outcome='task_list_saved')
    def reject(self,tool,args,call_id,reason):return dict(outcome=reason)


def run(names,**options):
    registry=movement_tools.registry(**options)
    registry.validate=lambda name,text:dict(tool=name)
    registry.INFERENCE_MESSAGES=lambda value:value
    events=list(chat_events(ScriptedClient(names),[],Dispatch(),'r',registry,1.,lambda:'live',lambda m:None,lambda:False))
    calls=[e for e in events if e['kind']=='call'];done=events[-1]
    return len(calls),done


class Registration(unittest.TestCase):
    def test_clock_bundle_is_the_four_moves(self):
        self.assertEqual(movement_tools.CLOCK_TOOLS,frozenset({'move_north','move_south','move_east','move_west'}))

    def test_registry_exposes_only_the_phase_visible_clock_tools(self):
        self.assertEqual(movement_tools.registry(phase='executor').CLOCK,movement_tools.CLOCK_TOOLS)
        self.assertEqual(movement_tools.registry(phase='planner').CLOCK,frozenset())

    def test_default_policy_is_the_v84_behavior(self):
        self.assertEqual(movement_tools.registry().COUNT_POLICY,'all_calls')

    def test_unknown_policy_is_refused(self):
        with self.assertRaises(ValueError):movement_tools.registry(count_policy='bogus')


class Policies(unittest.TestCase):
    SCRIPT=['task_list_write','task_list_write','move_north','move_east','move_north','move_south']

    def test_all_calls_policy_stops_after_three_calls_whatever_they_are(self):
        calls,done=run(self.SCRIPT,phase=None)
        self.assertEqual((calls,done['reason']),(3,'tool_call_limit'))
        self.assertEqual(done['epoch']['policy'],'all_calls')

    def test_clock_policy_counts_only_moves_the_controller_admitted(self):
        calls,done=run(['task_list_write','task_list_write','move_north','task_list_write','move_east','move_north','move_south'],phase=None,count_policy='clock_actions')
        self.assertEqual((calls,done['reason']),(6,'clock_budget'))
        self.assertEqual((done['epoch']['clock_spent'],done['epoch']['clock_limit']),(3,3))

    def test_free_calls_cannot_loop_forever(self):
        calls,done=run(['task_list_write']*20,phase=None,count_policy='clock_actions',max_total_calls=5)
        self.assertEqual((calls,done['reason']),(5,'call_ceiling'));self.assertEqual(done['epoch']['clock_spent'],0)

    def test_refused_moves_do_not_spend_the_clock(self):
        registry=movement_tools.registry(phase=None,count_policy='clock_actions');registry.validate=lambda n,t:dict(tool=n)
        dispatch=Dispatch(refused={'r-tool-0','r-decision-3-tool-3'})
        events=list(chat_events(ScriptedClient(['move_north','move_north','move_north','move_north','move_north']),[],dispatch,'r',registry,1.,lambda:'live',lambda m:None,lambda:False))
        done=events[-1];self.assertEqual(done['epoch']['clock_spent'],3);self.assertEqual(done['epoch']['calls'],5)

    def test_ceiling_below_budget_is_refused(self):
        with self.assertRaises(ValueError):run(['move_north'],phase=None,count_policy='clock_actions',max_total_calls=2)



class AcceptedCalls(unittest.TestCase):
    """Rejected calls are free and get one retry; a second consecutive rejection of the same tool ends the turn."""
    def play(self,script,refused=(),**options):
        registry=movement_tools.registry(count_policy='accepted_calls',**options);registry.validate=lambda n,t:dict(tool=n)
        dispatch=Dispatch(refused=refused)
        events=list(chat_events(ScriptedClient(script),[],dispatch,'r',registry,1.,lambda:'live',lambda m:None,lambda:False))
        return len([e for e in events if e['kind']=='call']),events[-1]

    def test_a_rejected_call_with_a_successful_retry_costs_one_call(self):
        calls,done=self.play(['move_north','move_north','move_east','move_east'],refused={'r-tool-0'})
        self.assertEqual((calls,done['reason']),(4,'tool_call_limit'));self.assertEqual((done['epoch']['accepted'],done['epoch']['rejected']),(3,1))

    def test_second_consecutive_rejection_of_the_same_tool_ends_the_turn(self):
        calls,done=self.play(['move_north','move_north','move_east'],refused={'r-tool-0','r-decision-1-tool-1'})
        self.assertEqual((calls,done['reason']),(2,'repeated_rejection'));self.assertEqual(done['epoch']['accepted'],0)

    def test_rejections_of_different_tools_do_not_form_a_streak(self):
        calls,done=self.play(['move_north','task_list_write','move_east','move_west'],refused={'r-tool-0','r-decision-1-tool-1'})
        self.assertNotEqual(done['reason'],'repeated_rejection')

    def test_an_accepted_call_resets_the_streak(self):
        calls,done=self.play(['move_north','move_east','move_north','move_east','move_south'],refused={'r-tool-0','r-decision-2-tool-2'})
        self.assertEqual(done['reason'],'tool_call_limit');self.assertEqual(done['epoch']['rejected'],2)

    def test_total_call_ceiling_still_bounds_alternating_rejections(self):
        refused={'r-tool-0'}|{'r-decision-%d-tool-%d'%(i,i) for i in range(1,12)}
        calls,done=self.play(['move_north','move_east']*10,refused=refused,max_total_calls=6)
        self.assertEqual((calls,done['reason'],done['epoch']['accepted']),(6,'call_ceiling',0))

    def test_all_calls_policy_never_reports_a_repeated_rejection(self):
        registry=movement_tools.registry();registry.validate=lambda n,t:dict(tool=n)
        events=list(chat_events(ScriptedClient(['move_north','move_north','move_east']),[],Dispatch(refused={'r-tool-0','r-decision-1-tool-1'}),'r',registry,1.,lambda:'live',lambda m:None,lambda:False))
        self.assertEqual(events[-1]['reason'],'tool_call_limit')


if __name__=='__main__':unittest.main()
