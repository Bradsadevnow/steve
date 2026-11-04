"""Epoch counter and context meter: observability state only."""
import unittest

from epoch_meter import EpochMeter


class Meter(unittest.TestCase):
    def test_no_measurement_before_the_first_usage_report(self):
        meter=EpochMeter(131072);meter.begin('run-a','req-1','planner','user')
        context=meter.context();self.assertIsNone(context['percent_full']);self.assertIsNone(context['tokens_until_threshold'])

    def test_percent_and_distance_to_the_threshold(self):
        meter=EpochMeter(100000);meter.usage(dict(prompt_tokens=41000))
        context=meter.context();self.assertEqual(context['percent_full'],41.0);self.assertEqual(context['tokens_until_threshold'],29000)

    def test_distance_never_goes_negative(self):
        meter=EpochMeter(1000);meter.usage(dict(prompt_tokens=900));self.assertEqual(meter.context()['tokens_until_threshold'],0)

    def test_bad_usage_reports_are_ignored(self):
        meter=EpochMeter(1000);meter.usage(dict(prompt_tokens=300));meter.usage(dict(prompt_tokens='many'));meter.usage(None);meter.usage({});meter.usage(dict(prompt_tokens=True));meter.usage(dict(prompt_tokens=-5))
        self.assertEqual(meter.prompt_tokens,300)

    def test_epoch_index_counts_turns_and_restarts_with_each_run(self):
        meter=EpochMeter(1000)
        self.assertEqual([meter.begin('run-a','r%d'%i,'executor','tick')['epoch']['index'] for i in range(3)],[1,2,3])
        fresh=meter.begin('run-b','r9','planner','user');self.assertEqual(fresh['epoch']['index'],1);self.assertIsNone(fresh['context']['percent_full'])

    def test_calls_and_executor_summary_are_recorded(self):
        meter=EpochMeter(1000);meter.begin('run-a','r1','executor','user')
        for _ in range(3):meter.call()
        meter.finish(dict(kind='done',reason='clock_budget',epoch=dict(policy='clock_actions',calls=5,clock_spent=3,clock_limit=3)))
        epoch=meter.snapshot()['epoch'];self.assertEqual((epoch['calls'],epoch['clock_spent'],epoch['ending']),(5,3,'clock_budget'))

    def test_finish_without_a_summary_keeps_the_counted_calls(self):
        meter=EpochMeter(1000);meter.begin('run-a','r1','executor','user');meter.call();meter.finish(dict(kind='done',reason='model_finished'))
        epoch=meter.snapshot()['epoch'];self.assertEqual((epoch['calls'],epoch['ending']),(1,'model_finished'))

    def test_snapshot_is_a_copy(self):
        meter=EpochMeter(1000);snapshot=meter.begin('run-a','r1','planner','user');snapshot['epoch']['calls']=99
        self.assertEqual(meter.snapshot()['epoch']['calls'],0)


if __name__=='__main__':unittest.main()
