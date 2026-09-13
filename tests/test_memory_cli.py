from pathlib import Path
import importlib.util
MODULE = Path(__file__).parents[1] / "scripts" / "memory_cli.py"
spec = importlib.util.spec_from_file_location("memory_cli", MODULE)
memory_cli = importlib.util.module_from_spec(spec); spec.loader.exec_module(memory_cli)

def ns(**kw): return type("Args", (), kw)

def test_lifecycle_backup_search_and_rollback(tmp_path):
    path=tmp_path/"rules.yaml"
    assert memory_cli.cmd_add(ns(file=path,id="demo",scope="math",rule="use clear notation",evidence="focused check",owner="math-profile",examples=None))==0
    assert memory_cli.cmd_search(ns(file=path,query="notation",scope=None,status=None))==0
    assert memory_cli.cmd_validate(ns(file=path,id="demo",note="representative task",force=False))==0
    assert memory_cli.cmd_apply(ns(file=path,id="demo",owner=None,change_ref="skill:1",force=False))==0
    assert memory_cli.cmd_rollback(ns(file=path,id="demo",reason="rule changed",force=False))==0
    assert memory_cli.load(path)["records"][0]["status"]=="rolled_back"
    assert list((tmp_path/"backups").glob("*.bak")), "every mutation should leave a backup"

def test_duplicate_and_schema_are_rejected(tmp_path):
    path=tmp_path/"rules.yaml"
    a=ns(file=path,id="one",scope="math",rule="same",evidence="e",owner="o",examples=None)
    memory_cli.cmd_add(a)
    try: memory_cli.cmd_add(ns(file=path,id="two",scope="MATH",rule="same",evidence="e",owner="o",examples=None))
    except ValueError as e: assert "duplicate" in str(e)
    else: raise AssertionError("duplicate should be rejected")
    assert memory_cli.validate_data(memory_cli.load(path))==[]

def test_invalid_transition_is_rejected(tmp_path):
    path=tmp_path/"rules.yaml"
    memory_cli.cmd_add(ns(file=path,id="demo",scope="x",rule="r",evidence="e",owner="o",examples=None))
    try: memory_cli.cmd_apply(ns(file=path,id="demo",owner=None,change_ref=None,force=False))
    except ValueError as e: assert "validated" in str(e)
    else: raise AssertionError("candidate cannot be applied")

def test_cli_help_starts():
    assert memory_cli.main.__name__ == "main"
