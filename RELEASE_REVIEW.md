# Release review

## Origin and scope

Plan Check was developed from an owner-maintained private source. Complete original
provenance, hashes and earlier release histories are preserved privately outside
this repository. PROVENANCE.json contains the public summary. The owner approved
MIT licensing, the private-repository push and subsequent history sanitization.
Public release and visibility changes require separate explicit authorization.

The protocol checks pointer drift, requirement traceability, prebuild consistency,
PASS/REVISE/BLOCKED readiness and final convergence. Evidence pins report and declared
implementation bytes. Evidence remains self-reported; tools do not execute project
tests, grant authority or certify independent review.

## Privacy and history

The release history is rebuilt from the sanitized tracked tree without linking to
the earlier private-source history. Original repository names, originating commit
identifiers and original file hashes are omitted from public provenance. Private
backups are excluded. Replacement history changes canonical commit pins; consumers
must review and refresh them even if the master version remains unchanged.

Tracked files, all reachable blobs and commit metadata are scanned for known private
identifiers, private paths and common credential patterns before replacement. These
heuristic scans do not guarantee absence of every possible secret. GitHub may retain
old objects, cached views or copies after branch replacement; local history scanning
does not establish server-side deletion.

## Canonical adoption

The canonical repository is `JimHardy-hdce/plan-check`; master path is
`docs/plan-check/PLAN_CHECK.md`, ref `main`, version `1.0.0`. Full commit and exact-byte
SHA-256 pins remain required. ADOPTION.md describes reviewed consumer integration.
Authority Engine, Guardian and existing consumer working trees remain untouched.

## Verification and limits

Run the 29-test suite, pointer verification, prebuild and final checks documented in
README.md. RELEASE_VALIDATION.json records actual validation and its scope. The
example record is a demonstration fixture, not independent acceptance evidence.
Repository identity is a configured expectation, not remote authentication. Offline
checks cannot detect unseen remote updates. Evidence can omit undeclared dependencies.
No automatic synchronization, independent review or Guardian integration is claimed.
