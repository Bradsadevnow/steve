"""Inspect actual captured provider payloads; no inference or main-state writes."""
import ast
import copy
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
folder = Path(sys.argv[1]).resolve()
requests = [json.loads(line) for path in sorted(folder.rglob('inference-requests.jsonl')) for line in path.read_text().splitlines() if line]
if not requests:
    raise SystemExit('No provider capture present yet')
first = requests[0]['payload']
current = next(m['content'] for m in reversed(first['messages']) if m.get('content', '').startswith('CURRENT WORLD /'))
card = current.split('CURRENT CHARACTER /', 1)[1].split('HARNESS RECORD / decision_context', 1)[0]
fixture = json.loads(next(folder.glob('trial-1-*/fixture.json')).read_text())
world = fixture['world']
old_character = copy.deepcopy(world['character'])
for ability in old_character.get('sheet', {}).get('abilities', []):
    ability.pop('targeting', None)  # This presentation-only field did not exist in the committed old schema.
names = {o['id']:o['name'] for o in world.get('visible_obstacles', []) if o.get('name')}
old_targets = []
for target in world['training_targets']:
    value = {('x' if k == 'col' else 'y' if k == 'row' else k):v for k,v in target.items() if k != 'prototype'}
    if target['id'] in names:
        value['name'] = names[target['id']]
    old_targets.append(value)
old_card = '\n'.join(['CURRENT CHARACTER / authoritative equipment and stats, not memory', json.dumps(old_character, sort_keys=True, ensure_ascii=True), 'Game tick: ' + str(world['game_tick']), 'TRAINING TARGETS / measured HP; stationary and do not retaliate', json.dumps(old_targets, sort_keys=True, ensure_ascii=True)])
old_source = subprocess.check_output(['git', 'show', 'a809a60:t-scan/live/grid_conversation.py'], cwd=ROOT, text=True)
old_system = next(ast.literal_eval(node.value) for node in ast.parse(old_source).body if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == 'SYSTEM' for target in node.targets))
bad = []
for request in requests:
    payload = request['payload']
    messages = payload['messages']
    count = sum(m.get('content', '').count('CURRENT CHARACTER /') for m in messages)
    if count != 1:
        bad.append(dict(request_id=request.get('request_id'), current_character_count=count))
    pending = set()
    for message in messages:
        if message['role'] == 'assistant':
            pending.update(call['id'] for call in message.get('tool_calls', []))
        if message['role'] == 'tool' and message.get('tool_call_id') not in pending:
            bad.append(dict(request_id=request.get('request_id'), orphan_tool_result=message.get('tool_call_id')))
        if message['role'] == 'tool':
            pending.discard(message.get('tool_call_id'))
    if not messages or messages[0]['role'] != 'system':
        bad.append(dict(request_id=request.get('request_id'), missing_initial_system=True))
    condition = json.loads((folder / 'design.json').read_text())['condition']
    if condition == 'shared-chat-v8.9.1-combat-card-identity' and ('You are Steve.\n' not in messages[0]['content'] or 'You are Steve, represented' in messages[0]['content']):
        bad.append(dict(request_id=request.get('request_id'), identity_sentence_mismatch=True))
report = dict(captured_requests_checked=len(requests), character_card_characters=dict(previous=len(old_card), current=len('CURRENT CHARACTER /' + card), reduction_percent=round((1 - len('CURRENT CHARACTER /' + card) / len(old_card)) * 100, 1)), system_characters=dict(previous=len(old_system), current=len(first['messages'][0]['content'])), first_request_characters=sum(len(m.get('content', '')) for m in first['messages']), first_message_roles=[m['role'] for m in first['messages']], issues=bad, interpretation='Counts are serialized characters, not tokens or proof of lower cognitive effort. Previous combat card is reconstructed from the identical fixture using the committed old format; actual new requests are captured.')
(folder / 'context-audit.json').write_text(json.dumps(report, indent=2))
(folder / 'combat-card-example.txt').write_text('CURRENT CHARACTER /' + card)
print(json.dumps(report, indent=2))
