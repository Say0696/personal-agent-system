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
import re

import yaml


KEYWORDS = {
    "general": ("task", "任务", "项目", "工作"),
}


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME") or (Path.home() / ".codex"))


def load_memory(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data.get("records", []) if isinstance(data, dict) else []


def classify(task: str, known_scopes: set[str] | None = None) -> str:
    lowered = task.casefold()
    for scope in sorted(known_scopes or set(), key=len, reverse=True):
        if scope and scope.casefold() in lowered:
            return scope
    for scope, words in KEYWORDS.items():
        if any(word.casefold() in lowered for word in words):
            return scope
    return "general"


def _skill_metadata(path: Path) -> dict[str, Any]:
    text = (path / "SKILL.md").read_text(encoding="utf-8", errors="ignore")
    if not text.startswith("---"):
        return {"name": path.name, "description": "", "keywords": []}
    end = text.find("\n---", 3)
    if end < 0:
        return {"name": path.name, "description": "", "keywords": []}
    data = yaml.safe_load(text[3:end]) or {}
    return {"name": data.get("name", path.name), "description": data.get("description", ""), "keywords": data.get("keywords", []) or [], "scope": data.get("scope")}


def discover_skills(home: Path, repo: Path | None) -> list[dict[str, Any]]:
    roots = [home / "skills"]
    if repo:
        roots.append(repo / "skills")
    found: dict[str, dict[str, Any]] = {}
    for root in roots:
        if root.is_dir():
            for p in root.iterdir():
                if p.is_dir() and (p / "SKILL.md").is_file():
                    found[p.name] = _skill_metadata(p)
    return [found[name] for name in sorted(found)]


def _matches(task: str, metadata: dict[str, Any]) -> bool:
    lowered = task.casefold()
    terms = [str(x) for x in metadata.get("keywords", [])]
    terms += [str(metadata.get("scope") or ""), str(metadata.get("name") or "")]
    if any(term and term.casefold() in lowered for term in terms):
        return True
    words = re.findall(r"[a-z0-9]{3,}", str(metadata.get("description", "")).casefold())
    return any(word in lowered for word in words)


def route(task: str, home: Path, repo: Path | None) -> dict[str, Any]:
    memory = load_memory(home / "personal-agent-system" / "memory" / "rules.yaml")
    known_scopes = {str(r.get("scope")) for r in memory if r.get("scope") and r.get("scope") not in {"all-projects", "global"}}
    scope = classify(task, known_scopes)
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
    skill_meta = discover_skills(home, repo)
    skills = [item["name"] for item in skill_meta]
    selected = ["personal-project-router"]
    # User-created skills advertise their own scope in SKILL.md. The core
    # router does not maintain a hard-coded domain list.
    candidates = [item["name"] for item in skill_meta if item["name"] not in {"personal-project-router", "personal-memory"} and _matches(task, item)]
    selected.extend(candidates)
    return {"task": task, "scope": scope, "selected_skills": selected,
            "available_skills": skills, "memory_records": relevant,
            "external_search": not bool(candidates)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only personal project preflight")
    parser.add_argument("task", nargs="+", help="task description")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="project to inspect (default: current directory)")
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
