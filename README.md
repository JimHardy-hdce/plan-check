# Plan Check

A small, local governance protocol for AI-assisted builds. It checks pointer drift,
requirement traceability, pre-build consistency, readiness and final convergence.
Developed from an owner-maintained private source; see `PROVENANCE.json`.

**Standalone release.** One canonical master lives at
[`docs/plan-check/PLAN_CHECK.md`](docs/plan-check/PLAN_CHECK.md). Read its adoption rule
before integrating. See `ADOPTION.md` for the reviewed consumer transition.
No automatic cross-repo synchronization is installed.

## Quick start

Requires Python 3.10+ and Git. No dependencies or package installation are needed.
Copy or clone the standalone repository, then from its root:

```sh
python3 -m unittest discover -s tests -v
python3 docs/plan-check/check_plan.py --record examples/ready.json --root examples/project --phase prebuild
python3 docs/plan-check/check_plan.py --record examples/ready.json --root examples/project --phase final
python3 docs/plan-check/verify_pointer.py --pointer examples/PLAN_CHECK_POINTER.md
```

On Windows, use `py -3` in place of `python3`. Files must retain their exact byte content;
`.gitattributes` enforces LF for tracked text. The example record is a demonstration fixture.

## Consumer integration

Keep only a pointer in the consuming project. Copy `POINTER_TEMPLATE.md`, set the master's
version, last-changing full commit (`git log -1 --format=%H main -- docs/plan-check/PLAN_CHECK.md`)
and SHA-256 of its bytes. Run the verifier from a trusted master checkout before each build.
It resolves the declared local ref and fails if the working master differs. Repository identity
is a declared expected value, not authentication of a remote. Fetching current refs is the
integrator's responsibility; a stale local checkout cannot detect unseen remote updates.

Create a JSON record using `examples/ready.json`. Every requirement maps to plan tasks,
implementation files and current evidence. Each evidence item includes an
`implementation_sha256` map covering every implementation path for its requirement;
changed implementation bytes invalidate that evidence. Run prebuild before implementing, then final after
executing acceptance checks. Exit codes: 0 PASS, 1 REVISE, 2 BLOCKED. Pointer failures use the
same codes. Fix REVISE and rerun; report unresolved BLOCKED dependencies.

The tools validate records and report hashes; they do not execute tests, establish evidence
truth, grant new authority or certify independent review. Evidence should include actual
commands, outcomes and the tested implementation revision. Publish only sanitized examples.

## Release and licensing

Licensed under MIT; see [`LICENSE`](LICENSE). Copyright (c) 2026 Jim Hardy.
The owner approved licensing and the release intent on October 9, 2026.
See `SECURITY.md` and `RELEASE_REVIEW.md` for limitations, validation and remaining release gates.
The owner authorized the private-repository push and history sanitization.
Public release or visibility changes require separate explicit authorization.
