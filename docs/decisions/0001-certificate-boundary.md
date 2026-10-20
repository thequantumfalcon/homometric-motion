# 1. Publish a bounded, portable mathematical certificate

Date: 2026-10-20

Status: accepted

## Context

The underlying research explored several parameter families and negative
results. A public repository must let a reader reproduce a specific assertion
without access to a private workspace, historical logs or a tool bundle.

## Decision

Publish one fixed chain of results as a standard-library Python package.
Recompute geometry, rational moments, outward bounds and the finite-count
certificate from small exact inputs. Keep a source manifest and run the installed
wheel in an isolated directory. Treat this port as a new source revision.

Keep mathematical assumptions, parameter selection, failure regimes and physical
validation gaps visible. Publication establishes an accessible dated record,
not priority, novelty, peer review or experimental confirmation.

## Consequences

The repository is smaller than the research archive and does not claim to
reproduce every historical grid. Future extensions require their own proof,
fresh computation and manifest update. The initial schema and API are experimental.
