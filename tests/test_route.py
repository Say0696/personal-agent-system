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


def test_math_route(tmp_path):
    result = json.loads(run("生成数学分数练习题", tmp_path).stdout)
    assert result["scope"] == "mathematics"
    assert "math-profile" in result["selected_skills"]


def test_software_route(tmp_path):
    result = json.loads(run("修复代码并运行测试", tmp_path).stdout)
    assert result["scope"] == "software"
    assert "computer-development" in result["selected_skills"]
