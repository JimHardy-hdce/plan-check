# Plan Check — single authoritative master

- Master id: `plan-check-master`
- Master version: `1.0.0`
- Release destination: `JimHardy-hdce/plan-check`, `docs/plan-check/PLAN_CHECK.md`.
- Adoption staged: this is an isolated release candidate developed from an
  owner-maintained private source.
  The owner approved release intent and conditional adoption on October 9, 2026.
  This file is the sole master for the standalone release. Consumer adoption is staged
  through reviewed integration (see `ADOPTION.md`); existing repositories remain untouched.
  A consumer switches through a reviewed pointer migration in an idle checkout.
  Never resolve both historical source and this master for the same build.
  Consumers keep pointers, never edited copies of these rules.

## Operating rule

Build, verify, correct, continue, and bring you the completed result.

Internal gates, tests, review and correction are autonomous within granted authority.
Only interrupt for an unresolved outcome-changing ambiguity, missing authority or credentials,
or a destructive or irreversible action requiring the user's decision.
Never push, publish, deploy, merge or change visibility without explicit authorization.
Guardian approval is unconfirmed unless actually wired and producing evidence for this change.

## Versioned pointer resolution

Read the current canonical master from the declared repository and ref; record its semantic
version, last-changing full Git commit and SHA-256 of its exact bytes. Compare all fields
with the consumer pointer before every check. Do not use memory, a cached chat or a competing copy.
A missing master or unverifiable revision is BLOCKED. A stale pin is REVISE: review the current
master and update the pointer through normal review before starting implementation.
The verifier checks local repository identity, path, ref, version, commit and hash. Network
fetching and pointer updates are external, authorized operations; no automatic sync is claimed.

## Before build: consistency and traceability

Record the goal, scope, excluded areas, authority, constraints, validation and unknowns.
Use stable requirement IDs. Each requirement has exactly one spec statement, a matching plan
entry, tasks, implementation paths and acceptance evidence. Every task names a requirement;
plan references and task IDs must match. Requirements and tasks must not silently disappear.
Every plan entry names implementation paths that also appear in its tasks.
Spec, plan and tasks share one revision. A changed requirement invalidates prior evidence.
Use `examples/ready.json` as the machine-readable record schema. Paths are relative to the
project root. Evidence refers to a real UTF-8 report with its exact hash, observed result and
revision. A passing status is a recorded assertion, not proof of test execution by this tool.

## Implementation readiness

Run `python3 docs/plan-check/check_plan.py --record RECORD --root PROJECT --phase prebuild`.
PASS: consistent scope, complete mappings, resolved blockers and granted build authority.
REVISE: missing mappings, revision drift, incomplete acceptance or invalid records.
BLOCKED: unresolved blockers or missing build authority. Correct REVISE autonomously;
resolve BLOCKED within existing authority, otherwise report the exact dependency.
PASS authorizes only work already granted by the user; it never grants publishing authority.

## End-to-end convergence

Implement, run acceptance checks, inspect outcomes, correct failures and repeat.
Before completion, run the same checker with `--phase final`. Final PASS requires all tasks
complete, mapped implementation files present, and current passing evidence for every
requirement. Failed, missing, changed or stale evidence is REVISE. Report checks actually run,
results, remaining blockers and unconfirmed integrations. Do not equate readiness PASS with
completion PASS. No independent reviewer, CI, Guardian or cross-repo propagation is implied.
