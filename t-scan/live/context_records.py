"""Serialize harness records without importing an environment or controller."""
import json


def envelope(kind, **data):
    payload = json.dumps(dict(kind=kind, **data), indent=2, ensure_ascii=True)
    payload = payload.replace('<', '\\u003c').replace('>', '\\u003e')
    return 'HARNESS RECORD / ' + kind + '\n' + '=' * 40 + '\n' + payload + '\n' + '=' * 40
