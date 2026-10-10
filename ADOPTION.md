# Canonical master adoption

The owner approved the five improvements and MIT licensing on October 9, 2026.
This sanitized standalone repository contains the canonical release master at
`docs/plan-check/PLAN_CHECK.md` in `JimHardy-hdce/plan-check` on `main`.
After history replacement, consumers must review and refresh their commit pins
against the published master even when its bytes and semantic version are unchanged.

No other repository, active job, Authority Engine integration or Guardian file has
been changed. Historical source retains its immutable commit provenance; it is not
an alternative master for new consumers that adopt this release.

For each existing consumer, schedule migration in an idle checkout: identify its
current master resolution, replace the legacy rule body with the pointer template,
pin the published master's version, last-changing commit and hash, run the verifier,
and test the consumer's integration. Review before any separately authorized push.
If that consumer requires older rule text, retain its explicit old pin and report
that it has not adopted the standalone master. Do not claim migration or automatic
synchronization until the consumer's pointer and integration have been verified.

The original private-source consumer is deliberately unmigrated while work may
be active. Do not modify its working tree to make a release status appear complete.
