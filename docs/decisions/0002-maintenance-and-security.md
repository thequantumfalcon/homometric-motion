# 2. Apply a research-appropriate T2 maintenance policy

Date: 2026-10-20

Status: accepted

## Context

This is a single-maintainer scientific repository. Controls should verify real
properties without claiming approvals or services that do not exist.

## Decision

Use signed local commits, public source review, least-privilege SHA-pinned
workflows, secret scans, dependency review and a stable CI gate. Keep a
separate no-bypass rule against deleting or force-pushing the default branch.
Allow the administrator to bypass the PR requirement for locally created
commits after running the same checks. Do not use automatic or web/API merges.

Use a local coverage threshold in CI, without an external coverage service or
upload token. Require DCO sign-off through a repository check instead of
installing an account-wide app. Do not publish to a package registry or deploy
a service; cloud credentials and deployment workflows would serve no purpose.
A future binary release must add and verify build attestations before release.

The maintainer explicitly chooses GitHub-only contact. Conduct reporting offers
a public route to the maintainer and a separate private GitHub abuse-reporting
route; it does not promise a confidential maintainer inbox.

## Consequences

Coverage percentages, dependency scans and scores do not validate a theorem.
No second-person approval is claimed. Account-level two-factor authentication
and vigilant mode require separate account verification; repository settings
cannot establish them. Public results describe observed checks and any
unavailable platform features rather than claiming perfect security.
