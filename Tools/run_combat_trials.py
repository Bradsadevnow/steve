"""Bounded planner/executor combat trials on SQLite/world snapshots, never main Steve.

Uses production context, tools, orchestration and engine. A headless manifest
presenter acknowledges effects synthetically; this does not test Unity animation.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import threading
import time
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 't-scan/live'))
from agent_notepad import AgentDispatch
from atomic_json import write_json
import character_rules
from decision_executor import chat_events
from grid_conversation import GridConversation, VERSION
from grid_context import coordinate_world, inference_messages
from grid_world import GridWorld, GridDispatch
from lmstudio_client import LMStudio
from movement_tools import registry, COUNT_ACCEPTED
from orchestrator import Orchestrator
from run_archive import RunArchive
from runtime_store import RuntimeStore

CASES = ('adjacent', 'clear_charge', 'blocked_lane', 'stronger_equipment', 'no_weapons')
PRESENTER = 'isolated-combat-presenter'


def get(route):
    with urllib.request.urlopen('http://127.0.0.1:8765/' + route, timeout=5) as response:
        return json.load(response)


def append(path, value):
    with path.open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(value, ensure_ascii=True) + '\n')


class HeadlessGrid(GridDispatch):
    def wait(self, key):
        action_id = self.local.get(key)
        if self.world.pending and self.world.pending['action_id'] == action_id:
            self.world.acknowledge(PRESENTER, action_id, self.world.state['session_id'])
        return super().wait(key)


def build_fixture(folder, saved, case):
    state = copy.deepcopy(saved)
    target = state['training_targets'][0]
    tx, ty = target['col'], target['row']
    if not (2 <= tx <= 14 and 5 <= ty <= 14):
        raise ValueError('This fixture requires a target away from the board edge; no trial started')
    manifest = state['world_definition']
    manifest['revision'] += 1
    manifest['spawn'] = dict(col=tx, row=ty - (3 if case in ('clear_charge', 'blocked_lane') else 1))
    if case == 'blocked_lane':
        prototype = next(o['prototype'] for o in manifest['obstacles'] if o['prototype'] not in ('bosses_dummy_unarmed', 'bosses_dummy_melee', 'bosses_dummy_ranged'))
        manifest['obstacles'].append(dict(id='trial_lane_blocker', prototype=prototype, col=tx, row=ty - 2, yaw=0))
    # Explicit fixture authoring, not an agent action, route, or edit of the live world.
    state['avatar'].update(manifest['spawn'])
    write_json(folder / 'world.json', state)
    world = GridWorld(folder / 'world.json')
    world.register_world(PRESENTER, manifest)
    equipment = []
    body = 'duelist'
    if case == 'stronger_equipment':
        body = 'bulwark'
        equipment = [dict(socket_id=s, module_id='warrior_blade') for s in ('left_upper', 'right_upper')]
        equipment += [dict(socket_id=s, module_id='warrior_shield') for s in ('left_lower', 'right_lower')]
    elif case != 'no_weapons':
        equipment = [dict(socket_id='hand_R', module_id='warrior_blade'), dict(socket_id='hand_L', module_id='warrior_shield')]
    world.apply_character(dict(request_id=uuid.uuid4().hex, character_id='steve', expected_revision=world.state['character']['revision'], catalog_version=character_rules.CATALOG['version'], body_id=body, equipment=equipment))
    return world, target['id']


def run_trial(parent, index, case, snapshot, saved, args, client):
    folder = parent / ('trial-' + str(index) + '-' + case)
    folder.mkdir()
    with sqlite3.connect(snapshot.as_uri() + '?mode=ro', uri=True) as source, sqlite3.connect(folder / 'steve.sqlite3') as destination:
        source.backup(destination)
    runtime = RuntimeStore(folder / 'steve.sqlite3')
    world, target_id = build_fixture(folder, saved, case)
    conversation = GridConversation(folder / 'conversation.json', runtime)
    archive = RunArchive(folder, conversation, runtime, world, dict(condition=VERSION, model=args.model, temperature=args.temperature, synthetic_presentation=True))
    archive.new_chat(conversation, runtime, world, 'isolated-new-chat-' + uuid.uuid4().hex)
    run_id = archive.current['id']
    dispatch = AgentDispatch(HeadlessGrid(world), runtime)
    dispatch.run_id = run_id
    orchestrator = Orchestrator(runtime, world, conversation)
    stop_presenter = threading.Event()
    faults = []

    def keepalive():
        while not stop_presenter.wait(.2):
            try:
                world.poll(PRESENTER, world.observe()['world_manifest_hash'])
            except Exception as error:
                faults.append(str(error))
                return

    presenter = threading.Thread(target=keepalive, daemon=True)
    presenter.start()
    began = time.monotonic()
    counts = dict(decisions=0, epochs=0, moved=0, blocked=0, rejections=0, attacks=0, repeated_bumps=0)
    false_completions = []
    claim_candidates = []
    last_bump = None
    kill = None
    finish = 'budget'
    source_id = None
    trial_status = dict(status='running', case=case, index=index, pid=os.getpid(), condition=VERSION)

    def target():
        return next(t for t in world.state['training_targets'] if t['id'] == target_id)

    def stopped():
        return (parent / 'STOP').exists() or time.monotonic() - began > args.wall_seconds or counts['decisions'] >= args.max_decisions or world.state['game_tick'] >= 24 or bool(faults)

    def before_inference(decision_id, decision_index):
        counts['decisions'] += 1
        if decision_index:
            orchestrator.store.decision(decision_id, run_id, runtime.agent.phase()['phase'])
        trial_status.update(counts, elapsed_seconds=round(time.monotonic() - began, 2), target_hp=target()['hp'], phase=runtime.agent.phase()['phase'])
        write_json(folder / 'status.json', trial_status)
        write_json(parent / 'status.json', dict(status='running', pid=os.getpid(), condition=VERSION, completed=index - 1, total=5*args.batches, current=dict(trial=index, case=case, **counts)))

    dispatch.before_inference = before_inference
    dispatch.before_call = lambda call: orchestrator.before_call(dispatch.body.turn, call)
    client.on_request = lambda path, payload: archive.request(path, payload, dispatch.body.turn)
    client.on_stream_event = lambda data: archive.stream_event(dispatch.body.turn, data)
    write_json(folder / 'fixture.json', dict(case=case, target_id=target_id, prompt='Defeat the training dummy, then stop.', world=world.observe(), scope='Copied Self/memory; fresh archived run; fixture placement/loadout; synthetic presenter ACKs'))
    try:
        for epoch in range(1, 13):
            if stopped():
                finish = 'cancelled' if (parent / 'STOP').exists() else 'budget'
                break
            counts['epochs'] = epoch
            request_id = uuid.uuid4().hex
            prompt = 'Defeat the training dummy, then stop.'
            job = dict(source='user' if epoch == 1 else 'tick', requestId=request_id, prompt=prompt if epoch == 1 else '')
            if epoch == 1:
                world.wake(request_id)
                source_id = runtime.accept_user(prompt, request_id)
            phase = orchestrator.prepare(job, run_id)
            if epoch == 1:
                conversation.user(prompt)
            else:
                conversation.tick(world.loop_origin)
            reg = registry(phase=phase, count_policy=COUNT_ACCEPTED, capabilities=world.state['character']['capabilities'])
            ending = None
            events = chat_events(client, conversation.messages, dispatch, request_id, reg, args.temperature, lambda: orchestrator.context(dispatch), conversation.checkpoint, stopped)
            try:
                for event in events:
                    if event['kind'] not in ('token', 'reasoning'):
                        archive.event(request_id, dict(event, decision_id=dispatch.body.turn))
                    if event['kind'] == 'receipt':
                        receipt = event['result']
                        call = event['call']
                        name = call['function']['name']
                        outcome = receipt.get('outcome', '')
                        orchestrator.receipt(dispatch.body.turn, run_id, receipt)
                        append(folder / 'receipts.jsonl', dict(time=time.time(), call=call, receipt=receipt, measured_target_hp=target()['hp']))
                        counts['moved'] += outcome == 'moved'
                        counts['blocked'] += outcome in ('blocked_boundary', 'blocked_obstacle')
                        counts['rejections'] += outcome.startswith(('rejected', 'denied'))
                        counts['attacks'] += outcome == 'target_hit'
                        bump = (name, tuple(receipt.get('position_before', [])), outcome) if outcome.startswith('blocked') else None
                        counts['repeated_bumps'] += bump is not None and bump == last_bump
                        last_bump = bump
                        if receipt.get('target_defeated') and kill is None:
                            kill = dict(seconds=round(time.monotonic() - began, 3), decisions=counts['decisions'], epochs=epoch, game_tick=world.state['game_tick'])
                        arguments = json.loads(call['function']['arguments'])
                        claims_done = name == 'task_mark_complete' or name == 'task_list_write' and arguments.get('status') == 'completed' or name == 'intention_write' and arguments.get('status') == 'fulfilled'
                        if claims_done and target()['hp'] > 0 and not outcome.startswith(('rejected', 'denied')):
                            false_completions.append(dict(call=call, target_hp=target()['hp']))
                    elif event['kind'] == 'done':
                        ending = event['reason']
                        if target()['hp'] > 0 and re.search(r'\b(defeated|destroyed|killed|eliminated)\b', event.get('text', ''), re.I):
                            claim_candidates.append(event['text'])
                        if event.get('text'):
                            runtime.event('assistant', event['text'], request_id, source_id)
            finally:
                events.close()
            orchestrator.finish(dispatch.body.turn)
            if ending in ('model_finished', 'provider_output_limit'):
                world.idle()
            if ending == 'repeated_rejection':
                streak = trial_status.get('rejection_epochs', 0) + 1
                trial_status['rejection_epochs'] = streak
                if streak >= 3:
                    world.stall(streak)
            else:
                trial_status['rejection_epochs'] = 0
            if not world.running:
                finish = ending or world.pause_reason
                break
    except InterruptedError:
        finish = 'cancelled' if (parent / 'STOP').exists() else 'budget'
    except Exception as error:
        finish = 'failure'
        faults.append(repr(error))
    finally:
        stop_presenter.set()
        presenter.join(timeout=2)
        world.control('stop')
        archive.finish(conversation, runtime, world)
        result = dict(case=case, index=index, condition=VERSION, **counts, elapsed_seconds=round(time.monotonic() - began, 3), target_hp=target()['hp'], verified_kill=target()['hp'] == 0, kill=kill, ending=finish, false_completions=false_completions, completion_claims_needing_review=claim_candidates, faults=faults, final_tasks=runtime.notepad(), scope='Model + production planner/executor/engine; synthetic ACKs, not Unity animation')
        write_json(folder / 'result.json', result)
        write_json(folder / 'status.json', dict(result, status='failed' if faults else 'cancelled' if finish == 'cancelled' else 'complete'))
        runtime.close()
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lm-url', default='http://192.168.1.128:1234')
    parser.add_argument('--model', default='google/gemma-4-e4b')
    parser.add_argument('--temperature', type=float, default=1.)
    parser.add_argument('--wall-seconds', type=float, default=300)
    parser.add_argument('--max-decisions', type=int, default=30)
    parser.add_argument('--batches', type=int, choices=(1,2), default=2)
    parser.add_argument('--source-dir', type=Path, help='Reuse a prior batch SQLite snapshot and fixture layout, with a fresh archived reset')
    args = parser.parse_args()
    parent = ROOT / 't-scan/runtime_data' / ('combat-trials-' + time.strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:6])
    parent.mkdir()
    before = get('grid/state')
    source_world = args.source_dir / 'trial-1-adjacent/world.json' if args.source_dir else ROOT / 't-scan/runtime_data/grid-world.json'
    saved = json.loads(source_world.read_text())
    write_json(parent / 'source-world.json', saved)
    snapshot = parent / 'main-snapshot.sqlite3'
    source_database = args.source_dir / 'main-snapshot.sqlite3' if args.source_dir else ROOT / 't-scan/runtime_data/steve.sqlite3'
    with sqlite3.connect(source_database.resolve().as_uri() + '?mode=ro', uri=True) as source, sqlite3.connect(snapshot) as destination:
        source.backup(destination)
    write_json(parent / 'live.before.json', before)
    write_json(parent / 'design.json', dict(condition=VERSION, cases=list(CASES), batches=args.batches, trials=5*args.batches, temperature=args.temperature, maximum_decisions=args.max_decisions, wall_seconds=args.wall_seconds, main_state_owner='untouched; no prompts, resets or writes', snapshot_sha256=hashlib.sha256(snapshot.read_bytes()).hexdigest(), source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), source_modified=True, synthetic_presentation=True, grading='Settled engine receipts; task marks are claims. Complete() alone is not success.'))
    client = LMStudio(args.lm_url, args.model)
    client.connect()
    results = []
    print(str(parent), flush=True)
    try:
        for index, case in enumerate(CASES * args.batches, 1):
            if (parent / 'STOP').exists():
                break
            result = run_trial(parent, index, case, snapshot, saved, args, client)
            results.append(result)
            write_json(parent / 'results.json', results)
            print(json.dumps(dict(index=index, case=case, killed=result['verified_kill'], hp=result['target_hp'], ending=result['ending'], decisions=result['decisions'], seconds=result['elapsed_seconds'])), flush=True)
            if result['ending'] in ('failure', 'cancelled'):
                break
        after = get('grid/state')
        write_json(parent / 'live.after.json', after)
        comparisons = {key: before[key] == after[key] for key in ('session_id', 'self', 'game_tick', 'character', 'training_targets')}
        write_json(parent / 'summary.json', dict(condition=VERSION, completed=len(results), total=5*args.batches, verified_kills=sum(r['verified_kill'] for r in results), armed_trials=sum(r['case'] != 'no_weapons' for r in results), false_completions=sum(len(r['false_completions']) for r in results), live_comparison=comparisons, note='Differences may be operator edits during the run; this runner has no live mutation endpoints.'))
        write_json(parent / 'status.json', dict(status='cancelled' if (parent / 'STOP').exists() else 'failed' if any(r['faults'] for r in results) else 'complete', completed=len(results), total=5*args.batches, pid=os.getpid(), condition=VERSION))
    except Exception as error:
        write_json(parent / 'status.json', dict(status='failed', error=repr(error), pid=os.getpid(), completed=len(results), total=5*args.batches))
        raise


if __name__ == '__main__':
    main()
