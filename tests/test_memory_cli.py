import importlib.util
import tempfile
import unittest
from pathlib import Path
MODULE=Path(__file__).parents[1]/"scripts"/"memory_cli.py"
spec=importlib.util.spec_from_file_location("memory_cli",MODULE); memory_cli=importlib.util.module_from_spec(spec); spec.loader.exec_module(memory_cli)
def ns(**kw): return type("Args",(),kw)
class MemoryCliTests(unittest.TestCase):
 def test_lifecycle_backup_search_and_rollback(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/"rules.yaml"; self.assertEqual(memory_cli.cmd_add(ns(file=p,id="demo",scope="math",rule="use clear notation",evidence="focused check",owner="math-profile",examples=None)),0); self.assertEqual(memory_cli.cmd_search(ns(file=p,query="notation",scope=None,status=None)),0); self.assertEqual(memory_cli.cmd_validate(ns(file=p,id="demo",note="representative task",force=False)),0); self.assertEqual(memory_cli.cmd_apply(ns(file=p,id="demo",owner=None,change_ref="skill:1",force=False)),0); self.assertEqual(memory_cli.cmd_rollback(ns(file=p,id="demo",reason="rule changed",force=False)),0); self.assertEqual(memory_cli.load(p)["records"][0]["status"],"rolled_back"); self.assertTrue(list((p.parent/"backups").glob("*.bak")))
 def test_duplicate_and_schema_are_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/"rules.yaml"; memory_cli.cmd_add(ns(file=p,id="one",scope="math",rule="same",evidence="e",owner="o",examples=None));
   with self.assertRaisesRegex(ValueError,"duplicate"): memory_cli.cmd_add(ns(file=p,id="two",scope="MATH",rule="same",evidence="e",owner="o",examples=None))
   self.assertEqual(memory_cli.validate_data(memory_cli.load(p)),[])
 def test_invalid_transition_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/"rules.yaml"; memory_cli.cmd_add(ns(file=p,id="demo",scope="x",rule="r",evidence="e",owner="o",examples=None))
   with self.assertRaisesRegex(ValueError,"validated"): memory_cli.cmd_apply(ns(file=p,id="demo",owner=None,change_ref=None,force=False))
if __name__=="__main__": unittest.main()
