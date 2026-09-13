import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(task: str, tmp_path: Path):
    env = os.environ.copy()
    env["CODEX_HOME"] = str(tmp_path)
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "route.py"), "--json", task],
        cwd=ROOT, env=env, text=True, capture_output=True, check=True,
    )


def test_unknown_domain_is_general(tmp_path):
    result = json.loads(run("设计一个摄影项目", tmp_path).stdout)
    assert result["scope"] == "general"
    assert result["selected_skills"] == ["personal-project-router"]


def test_user_skill_is_discovered_dynamically(tmp_path):
    skill = tmp_path / "skills" / "photography-helper"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("---\nname: photography-helper\ndescription: photography workflow\nkeywords: [摄影, photo]\n---\n", encoding="utf-8")
    result = json.loads(run("设计一个摄影项目", tmp_path).stdout)
    assert "photography-helper" in result["selected_skills"]


def test_memory_is_scope_isolated(tmp_path):
    memory = tmp_path / "personal-agent-system" / "memory"
    memory.mkdir(parents=True)
    (memory / "rules.yaml").write_text(
        "version: 1\nrecords:\n  - id: math-only\n    scope: mathematics\n    rule: use stacked notation\n    evidence: checked\n    status: validated\n    owner: math-skill\n    last_verified: '2026-09-13'\n",
        encoding="utf-8",
    )
    result = json.loads(run("设计一个摄影项目", tmp_path).stdout)
    assert result["memory_records"] == []
