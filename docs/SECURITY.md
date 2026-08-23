# Security Model

## Trust boundary

All policy statements are adversarial input.

Treaty never treats a policy clause as an instruction to the validator model. The prompt explicitly marks policy JSON as untrusted data and forbids browsing, tool calls, hidden-context disclosure, or obeying embedded commands.

## No compromise generation

The most important application-level safety choice is what Treaty refuses to generate.

The model cannot return a negotiated term. It only returns a finite relation code. Original clauses remain the terms exposed by `get_treaty_terms`.

## Version pinning

Every published version is immutable and receives a canonical definition hash.

An assessment stores both hashes and rechecks them before semantic resolution. A later policy publication cannot retroactively change a previous assessment or active treaty.

## Identity and authorization

- only the policy owner may publish a new version
- only the policy owner may pause or unpause
- only one of the two policy owners may open an assessment
- policies in one assessment must have different owners
- only either treaty party may propose
- only either treaty party may ratify or reject

## Bilateral activation

Treaty proposals start with the proposer side ratified.

The second side remains false until the other owner explicitly calls `ratify_treaty`.

No semantic consensus output can write either owner consent flag.

## Supersession

A successor may identify an active parent.

The parent is not touched when the successor is proposed. It becomes `SUPERSEDED` only in the same deterministic transition that activates the fully ratified successor.

## Expiry

`expires_at = 0` means no explicit expiry.

Non-zero expiry must be in the future and no more than one year from proposal time.

`is_treaty_active` checks expiry at read time. `refresh_expiry` lets anyone materialize expiration into stored status.

## Cache collision domain

The assessment cache key includes both immutable definition hashes, IDs, and versions. It is not based on names, owners, or model output.

## Deliberate non-features

Treaty does not:

- transfer assets
- custody funds
- slash either party
- call arbitrary downstream contracts
- execute an agent action
- auto-renegotiate a conflict
- infer identity from web content

These omissions keep the primitive's trust boundary narrow.
