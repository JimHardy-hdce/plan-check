"""Validate recorded readiness and convergence; never execute project code."""
import argparse
import hashlib
import json
from pathlib import Path

def assess(record, root, phase="prebuild"):
    issues, blockers = [], []
    root = Path(root).resolve()
    if phase not in ("prebuild", "final"):
        return {"status":"REVISE", "issues":["invalid phase"]}
    try:
        if not isinstance(record, dict):
            raise ValueError("record must be an object")
        if type(record["schema_version"]) is not int or record["schema_version"] != 1:
            issues.append("unsupported schema_version")
        revision = record["revision"]
        if not isinstance(revision,str) or not revision:
            issues.append("revision must be nonempty text")
        if record["authority"].get("build") is not True:
            blockers.append("build authority not granted")
        if not isinstance(record["blockers"], list):
            raise ValueError("blockers must be a list")
        for item in record["blockers"]:
            if not isinstance(item,str) or not item.strip():
                issues.append("blockers must be nonempty text")
            else:
                blockers.append(item)
        for field in ("goal","scope","exclusions","constraints","validation","unknowns"):
            if not isinstance(record[field],str) or not record[field].strip():
                issues.append("missing context: " + field)
        sections = {}
        for name in ("spec","plan","tasks"):
            section = record[name]
            if section["revision"] != revision:
                issues.append(name + " revision drift")
            items = section["items"]
            if not isinstance(items,list) or not items:
                issues.append(name + " has no items")
            ids = [item["id"] for item in items]
            if any(not isinstance(i,str) or not i.strip() for i in ids) or len(set(ids)) != len(ids):
                issues.append(name + " invalid or duplicate IDs")
            sections[name] = {item["id"]:item for item in items}
        def text_list(value, field):
            if not isinstance(value, list) or not value or any(not isinstance(v, str) or not v.strip() for v in value) or len(set(value)) != len(value):
                raise ValueError(field + " must be a nonempty list of unique strings")
        for plan in sections["plan"].values():
            text_list(plan["task_ids"], "task_ids")
            text_list(plan["implementation"], "plan implementation")
        for task in sections["tasks"].values():
            text_list(task["implementation"], "task implementation")
        spec, plans, tasks = (sections[n] for n in ("spec","plan","tasks"))
        if set(spec) != set(plans):
            issues.append("spec/plan requirement mismatch")
        def local_path(value):
            if not isinstance(value,str) or not value or Path(value).is_absolute() or "\\" in value or ":" in value:
                raise ValueError("paths must be portable relative paths")
            path = (root / value).resolve()
            if not path.is_relative_to(root):
                raise ValueError("path escapes project root")
            return path
        for rid, requirement in spec.items():
            if not requirement["statement"].strip() or not requirement["acceptance"].strip():
                issues.append(rid + " lacks statement/acceptance")
        referenced = []
        for rid, plan in plans.items():
            tids = plan["task_ids"]
            paths = plan["implementation"]
            if not isinstance(tids,list) or not tids or len(set(tids)) != len(tids) or not isinstance(paths,list) or not paths:
                issues.append(rid + " incomplete plan")
            linked_paths = set()
            for tid in tids:
                referenced.append(tid)
                if tid not in tasks or tasks[tid]["requirement_id"] != rid:
                    issues.append(rid + " task mapping mismatch")
                else:
                    linked_paths.update(tasks[tid]["implementation"])
            if set(paths) != linked_paths:
                issues.append(rid + " implementation mapping mismatch")
            for path in paths:
                resolved = local_path(path)
                if phase == "final" and not resolved.is_file():
                    issues.append(rid + " implementation missing: " + path)
        if set(referenced) != set(tasks) or len(referenced) != len(set(referenced)):
            issues.append("orphaned or multiply mapped tasks")
        for tid, task in tasks.items():
            if task["requirement_id"] not in spec or not task["description"].strip() or not task["implementation"]:
                issues.append(tid + " incomplete task")
            if task["status"] not in ("pending","complete"):
                issues.append(tid + " invalid task status")
            for path in task["implementation"]:
                local_path(path)
            if phase == "final" and task["status"] != "complete":
                issues.append(tid + " unfinished")
        evidence = record["evidence"]
        if not isinstance(evidence,list):
            raise ValueError("evidence must be a list")
        covered = set()
        for item in evidence:
            rid = item["requirement_id"]
            if rid not in spec:
                issues.append("unknown evidence requirement")
            path = local_path(item["path"])
            if item["revision"] != revision or item["result"] != "PASS":
                issues.append(rid + " stale or failed evidence")
            elif not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
                issues.append(rid + " missing/changed evidence")
            elif not path.read_text(encoding="utf-8").strip():
                issues.append(rid + " empty evidence")
            else:
                snapshots = item["implementation_sha256"]
                expected_paths = set(plans[rid]["implementation"]) if rid in plans else set()
                if not isinstance(snapshots,dict) or set(snapshots) != expected_paths:
                    issues.append(rid + " evidence implementation mapping incomplete")
                elif any(not local_path(p).is_file() or hashlib.sha256(local_path(p).read_bytes()).hexdigest() != sha for p,sha in snapshots.items()):
                    issues.append(rid + " implementation changed since evidence")
                else:
                    covered.add(rid)
        if phase == "final" and set(spec) != covered:
            issues.append("acceptance evidence incomplete")
    except (KeyError, TypeError, ValueError, AttributeError, OSError, UnicodeError) as exc:
        issues.append("invalid record: " + str(exc))
    return {"status":"BLOCKED" if blockers else "REVISE" if issues else "PASS", "phase":phase,"issues":blockers + issues}

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--record",required=True)
    ap.add_argument("--root",required=True)
    ap.add_argument("--phase",choices=("prebuild","final"),default="prebuild")
    args = ap.parse_args(argv)
    try:
        result = assess(json.loads(Path(args.record).read_text(encoding="utf-8")),args.root,args.phase)
    except (OSError,UnicodeError,ValueError) as exc:
        result = {"status":"REVISE","issues":[str(exc)]}
    print(json.dumps(result,indent=2))
    return {"PASS":0,"REVISE":1,"BLOCKED":2}[result["status"]]

if __name__ == "__main__":
    raise SystemExit(main())
