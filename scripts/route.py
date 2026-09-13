#!/usr/bin/env python3
"""Read-only project preflight and skill router.

The router deliberately makes recommendations only.  It never installs a
skill, changes memory, or publishes anything; those actions require an
explicit command and user authorization.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import yaml


KEYWORDS = {
    "mathematics": ("math", "mathemat", "数学", "分数", "方程", "几何", "练习题"),
    "documents": ("word", "docx", "pdf", "文档", "排版", "论文", "表格", "幻灯片"),
    "software": ("code", "coding", "软件", "代码", "项目", "编程", "构建", "测试", "服务器"),
}


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME") or (Path.home() / ".codex"))


def load_memory(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data.get("records", []) if isinstance(data, dict) else []


def classify(task: str) -> str:
    lowered = task.casefold()
    scores = {
        scope: sum(1 for word in words if word.casefold() in lowered)
        for scope, words in KEYWORDS.items()
    }
    best, score = max(scores.items(), key=lambda item: item[1])
    return best if score else "general"


def discover_skills(home: Path, repo: Path | None) -> list[str]:
    roots = [home / "skills"]
    if repo:
        roots.append(repo / "skills")
    found: set[str] = set()
    for root in roots:
        if root.is_dir():
            found.update(p.name for p in root.iterdir() if p.is_dir() and (p / "SKILL.md").is_file())
    return sorted(found)


def route(task: str, home: Path, repo: Path | None) -> dict[str, Any]:
    scope = classify(task)
    memory = load_memory(home / "personal-agent-system" / "memory" / "rules.yaml")
    relevant = [
        r for r in memory
        if r.get("status") in {"validated", "applied"}
        and r.get("scope") in {scope, "all-projects", "global"}
    ]
    # YAML safely parses ISO dates as ``date`` objects; make the read-only
    # JSON interface deterministic and portable.
    relevant = [
        {key: (value.isoformat() if hasattr(value, "isoformat") else value)
         for key, value in record.items()}
        for record in relevant
    ]
    skills = discover_skills(home, repo)
    selected = ["personal-project-router"]
    domain_skill = {"mathematics": "math-profile", "documents": "document-fidelity", "software": "computer-development"}.get(scope)
    if domain_skill and domain_skill in skills:
        selected.append(domain_skill)
    return {"task": task, "scope": scope, "selected_skills": selected,
            "available_skills": skills, "memory_records": relevant,
            "external_search": not bool(domain_skill and domain_skill in skills)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only personal project preflight")
    parser.add_argument("task", nargs="+", help="task description")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    result = route(" ".join(args.task), codex_home(), args.repo)
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"scope: {result['scope']}")
        print("selected: " + ", ".join(result["selected_skills"]))
        print("memory: " + str(len(result["memory_records"])))
        print("external search suggested: " + ("yes" if result["external_search"] else "no"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
