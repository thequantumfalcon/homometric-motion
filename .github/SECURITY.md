# Security

Only the current `main` revision is supported during the experimental 0.x
development period. There are no supported production deployments.

Report security vulnerabilities using
[GitHub private vulnerability reporting](https://github.com/thequantumfalcon/homometric-motion/security/advisories/new).
Do not disclose credentials or exploitable vulnerabilities in public issues.
Provide the affected commit, a minimal reproducer, impact and verification
steps. Reports must be reproducible and verified by the submitter.

The scientific runtime uses the standard library and reads packaged mathematical
inputs. It does not fetch data or contact a service. The `verify` command writes
only the requested new certificate file and refuses an existing output.
Development tooling downloads pinned dependencies; run it only for trusted code.

Checksums detect accidental changes relative to a manifest. They do not make
an untrusted manifest authentic. Check the repository identity, signed commit
and artifact provenance when deciding what to trust.

Report mathematical errors publicly with the relevant assumptions and failing
inequality. A scientific claim being incorrect is distinct from a software
security vulnerability.
