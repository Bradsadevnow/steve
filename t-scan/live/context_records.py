"""Serialize harness records without importing an environment or controller."""
import json

HEADER = 'HARNESS RECORD / '
RULE = '=' * 40


def envelope(kind, **data):
    payload = json.dumps(dict(kind=kind, **data), indent=2, ensure_ascii=True)
    payload = payload.replace('<', '\\u003c').replace('>', '\\u003e')
    return HEADER + kind + '\n' + RULE + '\n' + payload + '\n' + RULE


def decode_envelope(text):
    """Inverse of envelope(): return (kind, payload). Raises ValueError if text is not one.

    The payload is JSON with every string quoted, so no payload line can equal the rule line.
    """
    lines = text.split('\n') if isinstance(text, str) else []
    if len(lines) < 4 or not lines[0].startswith(HEADER) or lines[1] != RULE or lines[-1] != RULE:
        raise ValueError('Not a harness record envelope')
    return lines[0][len(HEADER):], json.loads('\n'.join(lines[2:-1]))
