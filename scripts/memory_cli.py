#!/usr/bin/env python3
"""Small local-only memory manager for the personal-agent-system template."""
from __future__ import annotations

import argparse
import datetime as dt
import os
from pathlib import Path
import sys
import uuid

import yaml


STATUSES = {"candidate", "validated", "applied", "rejected", "superseded", "rolled_back", "open-question"}


def default_path() -> Path:
    root = os.environ.get("CODEX_HOME") or (Path.home() / ".codex")
    return Path(root) / "personal-agent-system" / "memory" / "rules.yaml"


def load(path: Path) -> dict:
    if not path.exists():
        return {"version": 1, "records": []}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict) or not isinstance(data.get("records", []), list):
        raise ValueError("memory file must contain a records list")
    return data


def save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def cmd_add(args: argparse.Namespace) -> int:
    data = load(args.file)
    record = {
        "id": args.id or f"rule-{uuid.uuid4().hex[:10]}",
        "scope": args.scope,
        "rule": args.rule,
        "evidence": args.evidence,
        "status": "candidate",
        "owner": args.owner or "unassigned",
        "last_verified": dt.date.today().isoformat(),
    }
    data["records"].append(record)
    save(args.file, data)
    print(record["id"])
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    data = load(args.file)
    for r in data["records"]:
        if args.scope and r.get("scope") not in {args.scope, "all-projects"}:
            continue
        if args.status and r.get("status") != args.status:
            continue
        print(f"{r.get('id')}\t{r.get('status')}\t{r.get('scope')}\t{r.get('rule')}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    data = load(args.file)
    for r in data["records"]:
        if r.get("id") == args.id:
            if args.new_status not in STATUSES:
                raise ValueError(f"unsupported status: {args.new_status}")
            r["status"] = args.new_status
            r["last_verified"] = dt.date.today().isoformat()
            save(args.file, data)
            print(f"{args.id}\t{args.new_status}")
            return 0
    raise ValueError(f"record not found: {args.id}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage local personal-agent memory")
    parser.add_argument("--file", type=Path, default=default_path())
    sub = parser.add_subparsers(dest="command", required=True)
    add = sub.add_parser("add")
    add.add_argument("--scope", required=True)
    add.add_argument("--rule", required=True)
    add.add_argument("--evidence", required=True)
    add.add_argument("--owner")
    add.add_argument("--id")
    add.set_defaults(func=cmd_add)
    ls = sub.add_parser("list")
    ls.add_argument("--scope")
    ls.add_argument("--status")
    ls.set_defaults(func=cmd_list)
    status = sub.add_parser("status")
    status.add_argument("id")
    status.add_argument("new_status", choices=sorted(STATUSES))
    status.set_defaults(func=cmd_status)
    try:
        return args.func(args)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
