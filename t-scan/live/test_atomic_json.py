import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from atomic_json import write_json
class AtomicCheckpointTests(unittest.TestCase):
 def test_transient_lock_retries_same_checkpoint(self):
  with tempfile.TemporaryDirectory() as root:
   path=Path(root)/'conversation.json';real_replace=Path.replace;attempts=[]
   def replace(p,target):
    attempts.append(p)
    if len(attempts)==1:raise PermissionError('transient sharing lock')
    return real_replace(p,target)
   with patch.object(Path,'replace',replace),patch('atomic_json.time.sleep'):
    write_json(path,dict(messages=['preserved']))
   self.assertEqual(json.loads(path.read_text()),dict(messages=['preserved']));self.assertEqual(len(attempts),2)
 def test_persistent_lock_raises_and_preserves_previous_checkpoint(self):
  with tempfile.TemporaryDirectory() as root:
   path=Path(root)/'world.json';path.write_text('{"revision":1}')
   with patch.object(Path,'replace',side_effect=PermissionError('locked')),patch('atomic_json.time.sleep'):
    with self.assertRaises(PermissionError):write_json(path,dict(revision=2))
   self.assertEqual(json.loads(path.read_text()),dict(revision=1))
