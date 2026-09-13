#!/usr/bin/env python3
"""Local-only lifecycle manager for personal-agent-system memory records."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, os, shutil, sys, uuid
from pathlib import Path
import yaml
STATUSES={"candidate","validated","applied","rejected","superseded","rolled_back","open-question"}
REQUIRED_FIELDS={"id","scope","rule","evidence","status","owner","last_verified"}
TRANSITIONS={"candidate":{"candidate","validated","rejected","open-question"},"validated":{"validated","applied","rejected","superseded","rolled_back"},"applied":{"applied","superseded","rolled_back"},"open-question":{"open-question","candidate","validated","rejected"},"rejected":{"rejected","candidate"},"superseded":{"superseded","candidate"},"rolled_back":{"rolled_back","candidate"}}
def default_path():
    root=os.environ.get("CODEX_HOME") or (Path.home()/".codex")
    return Path(root)/"personal-agent-system"/"memory"/"rules.yaml"
def _empty(): return {"version":1,"records":[]}
def validate_data(data):
    errors=[]
    if not isinstance(data,dict): return ["memory file must be a mapping"]
    if data.get("version",1)!=1: errors.append("version must be 1")
    records=data.get("records")
    if not isinstance(records,list): return errors+["memory file must contain a records list"]
    ids=set(); keys=set()
    for i,r in enumerate(records):
        p=f"records[{i}]"
        if not isinstance(r,dict): errors.append(f"{p} must be a mapping"); continue
        missing=REQUIRED_FIELDS-set(r)
        if missing: errors.append(f"{p} missing: {', '.join(sorted(missing))}")
        rid=r.get("id")
        if not isinstance(rid,str) or not rid.strip(): errors.append(f"{p}.id must be non-empty text")
        elif rid in ids: errors.append(f"duplicate id: {rid}")
        ids.add(str(rid))
        if r.get("status") not in STATUSES: errors.append(f"{p}.status unsupported: {r.get('status')}")
        scope,rule=r.get("scope"),r.get("rule")
        if scope and rule:
            key=(str(scope).strip().lower(),str(rule).strip())
            if key in keys: errors.append(f"duplicate rule: {scope} / {rule}")
            keys.add(key)
        for field in ("scope","rule","owner"):
            if not isinstance(r.get(field),str) or not r.get(field).strip(): errors.append(f"{p}.{field} must be non-empty text")
        evidence=r.get("evidence")
        if not ((isinstance(evidence,str) and evidence.strip()) or (isinstance(evidence,dict) and evidence.get("digest"))): errors.append(f"{p}.evidence must be non-empty text or a mapping with digest")
        if "examples" in r and not isinstance(r["examples"],list): errors.append(f"{p}.examples must be a list")
        if r.get("last_verified") is not None and not isinstance(r.get("last_verified"),str): errors.append(f"{p}.last_verified must be date text or null")
        if r.get("evidence_digest") is not None and (not isinstance(r.get("evidence_digest"),str) or len(r.get("evidence_digest"))!=64): errors.append(f"{p}.evidence_digest must be a SHA-256 hex digest")
    return errors
def load(path):
    if not path.exists(): return _empty()
    data=yaml.safe_load(path.read_text(encoding="utf-8")) or _empty()
    errors=validate_data(data)
    if errors: raise ValueError("invalid memory file: "+"; ".join(errors))
    return data
def backup(path):
    if not path.exists(): return None
    stamp=dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    d=path.parent/"backups"; d.mkdir(parents=True,exist_ok=True)
    target=d/f"{path.stem}-{stamp}{path.suffix}.bak"; shutil.copy2(path,target); return target
def save(path,data,make_backup=True):
    errors=validate_data(data)
    if errors: raise ValueError("refusing to save invalid memory: "+"; ".join(errors))
    path.parent.mkdir(parents=True,exist_ok=True)
    made=backup(path) if make_backup else None
    temp=path.with_suffix(path.suffix+".tmp")
    temp.write_text(yaml.safe_dump(data,allow_unicode=True,sort_keys=False),encoding="utf-8"); temp.replace(path)
    return made
def _record(data,rid):
    for r in data["records"]:
        if r.get("id")==rid:return r
    raise ValueError(f"record not found: {rid}")
def _set_status(data,rid,new_status,force=False,**fields):
    if new_status not in STATUSES: raise ValueError(f"unsupported status: {new_status}")
    r=_record(data,rid); old=r.get("status")
    if not force and new_status not in TRANSITIONS.get(old,set()): raise ValueError(f"invalid transition: {old} -> {new_status} (use --force only for repair)")
    r["status"]=new_status; r["last_verified"]=dt.date.today().isoformat(); r.update({k:v for k,v in fields.items() if v is not None}); return r
def cmd_add(a):
    d=load(a.file); scope,rule=a.scope.strip(),a.rule.strip()
    for r in d["records"]:
        if str(r.get("scope","")).strip().lower()==scope.lower() and str(r.get("rule","")).strip()==rule: raise ValueError(f"duplicate rule already exists: {r.get('id')}")
    r={"id":a.id or f"rule-{uuid.uuid4().hex[:10]}","scope":scope,"rule":rule,"evidence":a.evidence,"status":"candidate","owner":a.owner or "unassigned","last_verified":None}
    if a.examples:r["examples"]=a.examples
    d["records"].append(r); save(a.file,d); print(r["id"]); return 0
def cmd_list(a):
    for r in load(a.file)["records"]:
        if a.scope and r.get("scope") not in {a.scope,"all-projects"}:continue
        if a.status and r.get("status")!=a.status:continue
        print(f"{r.get('id')}\t{r.get('status')}\t{r.get('scope')}\t{r.get('rule')}")
    return 0
def cmd_search(a):
    q=a.query.casefold()
    for r in load(a.file)["records"]:
        hay=" ".join(str(r.get(k,"")) for k in ("id","scope","rule","evidence","owner","examples")).casefold()
        if q in hay and (not a.scope or r.get("scope") in {a.scope,"all-projects"}) and (not a.status or r.get("status")==a.status): print(f"{r.get('id')}\t{r.get('status')}\t{r.get('scope')}\t{r.get('rule')}")
    return 0
def _sha256(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def cmd_validate(a):
    d=load(a.file)
    if a.id:
        r=_record(d,a.id); force=getattr(a,"force",False)
        if r.get("status")!="candidate" and not force: raise ValueError(f"only candidate records can be validated (current: {r.get('status')})")
        note=(a.note or "").strip()
        if not note and not force: raise ValueError("validate requires a non-empty --note describing the focused check")
        evidence_file=getattr(a,"evidence_file",None); digest=(getattr(a,"evidence_digest",None) or "").lower()
        if evidence_file:
            ep=Path(evidence_file)
            if not ep.is_file(): raise ValueError(f"evidence file not found: {ep}")
            actual=_sha256(ep)
            if digest and digest!=actual: raise ValueError("evidence digest does not match file")
            digest=actual; r["evidence_ref"]=str(ep.resolve())
        elif not digest:
            digest=(r.get("evidence_digest") or (r.get("evidence") or {}).get("digest","") if isinstance(r.get("evidence"),dict) else r.get("evidence_digest") or "").lower()
        if not force and (len(digest)!=64 or any(c not in "0123456789abcdef" for c in digest)): raise ValueError("validate requires --evidence-file or a 64-character --evidence-digest")
        _set_status(d,a.id,"validated",force=force,validation=note,evidence_digest=digest or None); save(a.file,d); print(f"{a.id}\tvalidated")
    else: print(f"valid\t{len(d['records'])} record(s)")
    return 0
def cmd_apply(a):
    d=load(a.file); r=_record(d,a.id)
    if r.get("status")!="validated" and not getattr(a,"force",False): raise ValueError(f"only validated records can be applied (current: {r.get('status')})")
    if not a.owner and r.get("owner") in (None,"","unassigned") and not getattr(a,"force",False): raise ValueError("apply requires --owner (the durable owner of this rule)")
    if not a.change_ref and not getattr(a,"force",False): raise ValueError("apply requires --change-ref identifying the durable owner change")
    r=_set_status(d,a.id,"applied",force=getattr(a,"force",False),owner=a.owner,change_ref=a.change_ref); save(a.file,d); print(f"{r['id']}\tapplied\t{r.get('owner')}"); return 0
def cmd_rollback(a):
    d=load(a.file); r=_record(d,a.id)
    if r.get("status") not in {"applied","validated"} and not getattr(a,"force",False): raise ValueError(f"cannot roll back status {r.get('status')}")
    r=_set_status(d,a.id,"rolled_back",force=getattr(a,"force",False),rollback_reason=a.reason); save(a.file,d); print(f"{r['id']}\trolled_back"); return 0
def cmd_status(a):
    if a.new_status not in {"candidate","open-question","rejected","superseded"}: raise ValueError("use validate, apply, or rollback for lifecycle status changes")
    d=load(a.file); r=_record(d,a.id); old=r.get("status")
    if a.new_status not in TRANSITIONS.get(old,set()) and not getattr(a,"force",False): raise ValueError(f"invalid transition: {old} -> {a.new_status}")
    r["status"]=a.new_status; save(a.file,d); print(f"{a.id}\t{a.new_status}"); return 0

def cmd_restore(a):
    source=Path(a.backup)
    if not source.is_file(): raise ValueError(f"backup not found: {source}")
    data=load(source); save(a.file,data); print(f"restored\t{source}"); return 0

def cmd_export(a):
    if not a.confirm_private: raise ValueError("export is opt-in and may contain private memory; pass --confirm-private")
    data=load(a.file); out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(yaml.safe_dump(data,allow_unicode=True,sort_keys=False),encoding="utf-8"); print(f"exported\t{out}"); return 0
def build_parser():
    p=argparse.ArgumentParser(description="Manage local personal-agent memory"); p.add_argument("--file",type=Path,default=default_path()); s=p.add_subparsers(dest="command",required=True)
    x=s.add_parser("add"); x.add_argument("--scope",required=True); x.add_argument("--rule",required=True); x.add_argument("--evidence",required=True); x.add_argument("--owner"); x.add_argument("--examples",nargs="*"); x.add_argument("--id"); x.set_defaults(func=cmd_add)
    x=s.add_parser("list"); x.add_argument("--scope"); x.add_argument("--status",choices=sorted(STATUSES)); x.set_defaults(func=cmd_list)
    x=s.add_parser("search"); x.add_argument("query"); x.add_argument("--scope"); x.add_argument("--status",choices=sorted(STATUSES)); x.set_defaults(func=cmd_search)
    x=s.add_parser("validate"); x.add_argument("id",nargs="?"); x.add_argument("--note"); x.add_argument("--evidence-file"); x.add_argument("--evidence-digest"); x.add_argument("--force",action="store_true"); x.set_defaults(func=cmd_validate)
    x=s.add_parser("apply"); x.add_argument("id"); x.add_argument("--owner"); x.add_argument("--change-ref"); x.add_argument("--force",action="store_true"); x.set_defaults(func=cmd_apply)
    x=s.add_parser("rollback"); x.add_argument("id"); x.add_argument("--reason",required=True); x.add_argument("--force",action="store_true"); x.set_defaults(func=cmd_rollback)
    x=s.add_parser("status"); x.add_argument("id"); x.add_argument("new_status",choices=sorted(STATUSES)); x.add_argument("--force",action="store_true"); x.set_defaults(func=cmd_status)
    x=s.add_parser("restore"); x.add_argument("backup"); x.set_defaults(func=cmd_restore)
    x=s.add_parser("export"); x.add_argument("--output",required=True); x.add_argument("--confirm-private",action="store_true"); x.set_defaults(func=cmd_export)
    return p
def main():
    a=build_parser().parse_args()
    try:return a.func(a)
    except (OSError,ValueError,yaml.YAMLError) as e: print(f"error: {e}",file=sys.stderr); return 2
if __name__=="__main__": raise SystemExit(main())
