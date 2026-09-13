import importlib.util
from pathlib import Path


MODULE = Path(__file__).parents[1] / "scripts" / "memory_cli.py"
spec = importlib.util.spec_from_file_location("memory_cli", MODULE)
memory_cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(memory_cli)


def test_add_and_status_are_local(tmp_path):
    path = tmp_path / "rules.yaml"
    args = type("Args", (), {"file": path, "id": "demo", "scope": "math", "rule": "use clear notation", "evidence": "focused check", "owner": "math-profile"})
    assert memory_cli.cmd_add(args) == 0
    data = memory_cli.load(path)
    assert data["records"][0]["status"] == "candidate"
    status_args = type("Args", (), {"file": path, "id": "demo", "new_status": "validated"})
    assert memory_cli.cmd_status(status_args) == 0
    assert memory_cli.load(path)["records"][0]["status"] == "validated"
