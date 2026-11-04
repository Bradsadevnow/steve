"""Observable epoch and context-meter state for the viewer and batch runner.

Read-only: nothing here changes what the model is sent or what the world does. The prompt-token figure is the
provider's own count for the previous request, so it excludes the next decision's new messages (hence "approximate").
"""
import copy

DEFAULT_THRESHOLD = .70


class EpochMeter:
    def __init__(self, window, call_limit=3, threshold=DEFAULT_THRESHOLD):
        self.window = window; self.call_limit = call_limit; self.threshold = threshold
        self.run_id = None; self.index = 0; self.epoch = None; self.prompt_tokens = None

    def begin(self, run_id, request_id, phase, source):
        """Start an epoch: one scheduled turn. The index restarts with each run."""
        if run_id != self.run_id:
            self.run_id = run_id; self.index = 0; self.prompt_tokens = None
        self.index += 1
        self.epoch = dict(run_id=run_id, index=self.index, request_id=request_id, phase=phase, source=source,
                          call_limit=self.call_limit, calls=0, accepted=0, rejected=0, clock_spent=0, ending=None)
        return self.snapshot()

    def call(self):
        if self.epoch: self.epoch['calls'] += 1

    def usage(self, usage):
        tokens = usage.get('prompt_tokens') if isinstance(usage, dict) else None
        if type(tokens) is int and tokens >= 0: self.prompt_tokens = tokens

    def finish(self, done):
        if not self.epoch: return
        self.epoch['ending'] = done.get('reason')
        counted = done.get('epoch')
        if isinstance(counted, dict):
            self.epoch['calls'] = counted.get('calls', self.epoch['calls'])
            self.epoch['accepted'] = counted.get('accepted', self.epoch['accepted'])
            self.epoch['rejected'] = counted.get('rejected', self.epoch['rejected'])
            self.epoch['clock_spent'] = counted.get('clock_spent', self.epoch['clock_spent'])

    def context(self):
        if self.prompt_tokens is None or not self.window:
            return dict(prompt_tokens=None, window=self.window, percent_full=None, compaction_threshold=self.threshold, tokens_until_threshold=None)
        limit = int(self.window * self.threshold)
        return dict(prompt_tokens=self.prompt_tokens, window=self.window, percent_full=round(100 * self.prompt_tokens / self.window, 1),
                    compaction_threshold=self.threshold, tokens_until_threshold=max(0, limit - self.prompt_tokens))

    def snapshot(self):
        return dict(epoch=copy.deepcopy(self.epoch), context=self.context())
