"""Read-only local version, provenance and hash drift verifier. No network or writes."""
import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

DEFAULT_MASTER = Path(__file__).resolve().parent / "PLAN_CHECK.md"
FIELDS = ("master_repo", "master_path", "master_ref", "master_version", "pinned_commit", "sha256")

def master_sha256(master):
    return hashlib.sha256(Path(master).read_bytes()).hexdigest()

def check(pointer, master=DEFAULT_MASTER, *, repo="JimHardy-hdce/plan-check", ref="main", commit=None, master_path="docs/plan-check/PLAN_CHECK.md"):
    problems = []
    try:
        text = Path(pointer).read_text(encoding="utf-8")
        body = Path(master).read_text(encoding="utf-8")
        actual = master_sha256(master)
    except (OSError, UnicodeError) as exc:
        return ["BLOCKED: cannot read pointer/master: " + str(exc)]
    found = {}
    allowed = re.compile(r"^- ([a-z_0-9]+): (\S+)\s*$")
    for line in text.splitlines():
        match = allowed.fullmatch(line)
        if not match or match[1] not in FIELDS:
            if line.strip():
                problems.append("invalid pointer content (competing copy or unknown field)")
            continue
        name, value = match.groups()
        if name in found:
            problems.append("duplicate field: " + name)
        found[name] = value
    for name in FIELDS:
        if name not in found:
            problems.append("missing field: " + name)
    version = re.search(r"^- Master version: `([0-9]+\.[0-9]+\.[0-9]+)`$", body, re.M)
    if not version:
        problems.append("BLOCKED: master version missing or invalid")
    if commit is None:
        try:
            root = subprocess.check_output(["git", "-C", str(Path(master).parent), "rev-parse", "--show-toplevel"], text=True, stderr=subprocess.DEVNULL).strip()
            relative = Path(master).resolve().relative_to(Path(root).resolve()).as_posix()
            commit = subprocess.check_output(["git", "-C", root, "log", "-1", "--format=%H", ref, "--", relative], text=True, stderr=subprocess.DEVNULL).strip()
            committed = subprocess.check_output(["git", "-C", root, "show", ref + ":" + relative], stderr=subprocess.DEVNULL)
            if hashlib.sha256(committed).hexdigest() != actual:
                problems.append("DRIFT: working master differs from declared ref")
        except (OSError, ValueError, subprocess.CalledProcessError):
            problems.append("BLOCKED: cannot resolve master revision")
    if not commit or not re.fullmatch(r"[0-9a-f]{40}", commit):
        problems.append("BLOCKED: expected commit must be a full Git SHA")
    expected = dict(master_repo=repo, master_path=master_path, master_ref=ref, master_version=version[1] if version else None, pinned_commit=commit, sha256=actual)
    for key,value in expected.items():
        if key in found and value is not None and found[key] != value:
            problems.append("DRIFT: " + key + " differs from master")
    return problems

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pointer", required=True)
    ap.add_argument("--master", default=str(DEFAULT_MASTER))
    ap.add_argument("--repo", default="JimHardy-hdce/plan-check")
    ap.add_argument("--ref", default="main")
    args = ap.parse_args(argv)
    problems = check(args.pointer,args.master,repo=args.repo,ref=args.ref)
    for problem in problems:
        print(problem,file=sys.stderr)
    print("BLOCKED" if any(p.startswith("BLOCKED") for p in problems) else "REVISE" if problems else "PASS")
    return 2 if any(p.startswith("BLOCKED") for p in problems) else 1 if problems else 0

if __name__ == "__main__":
    sys.exit(main())
