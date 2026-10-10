# Security and privacy review

Both tools are local and read-only. They make no network requests and execute no project
commands. The pointer verifier invokes Git only to read the local master revision and blob.
Use trusted Git/Python installations and a trusted master checkout. Repository names and refs
are assertions; hashes detect drift, not authenticity. They are not a supply-chain signature.

The record checker rejects absolute paths, traversal, Windows drive paths and symlink escapes
from the supplied root. It reads implementation existence and evidence bytes. Do not process
untrusted huge files or repositories: no resource sandbox is provided. Concurrent changes can
invalidate a check; use an immutable checkout when recording release evidence.

Evidence PASS is self-reported. The tool binds evidence to the declared implementation file hashes but does not prove
tests ran or discover undeclared dependencies. Use trusted reports tied to the tested revision and rerun after changes.
Avoid secrets, client names, credentials, customer documents and personal paths in records.
PROVENANCE.json retains the source repository name, original commit and hashes;
office usernames and absolute source paths have been removed from release files and history. Report security concerns privately to the owner; no public
contact address or vulnerability intake has been configured.
