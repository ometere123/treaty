# Treaty — Intelligent Contract Submission Notes

## Category

Standalone GenLayer Intelligent Contract.

Treaty is intentionally contract-only. It has no frontend and no hosted backend.

## One-line purpose

Treaty provides reusable consensus-backed semantic compatibility receipts for two immutable natural-language policy versions, then requires bilateral owner ratification before an agreement becomes active.

## Why this is a primitive

The contract stops before any product-specific action. It does not transfer funds, execute an agent task, route an API call, settle a purchase, or provide a user interface. Downstream contracts consume its assessment and treaty state.

## What is novel in the state design

Treaty deliberately separates two different trust problems.

### Compatibility truth

An immutable `CompatibilityAssessment` answers whether two exact policy versions are jointly satisfiable.

Assessments are cached by an order-independent pair hash, so the semantic result can be reused.

### Consent

A `TreatyRecord` references a compatible assessment but does not become active until both independent policy owners ratify.

AI consensus cannot manufacture consent.

This separation lets one expensive semantic assessment support multiple downstream agreements while preserving explicit bilateral authorization.

## Consensus logic

Only exact-topic overlaps require nondeterministic reasoning.

The leader classifies each overlap into one bounded relation:

```text
COMPATIBLE
CONFLICT
AMBIGUOUS
```

Validators independently rerun the same classification from the immutable source clauses.

The validator checks:

1. leader result is the expected list shape
2. result count is exact
3. every topic is exact and in deterministic order
4. every relation is one of the finite allowed codes
5. validator independently executes the same semantic task
6. every validator relation equals the proposed relation

The final assessment status is deterministic:

```text
if any CONFLICT -> INCOMPATIBLE
else if any AMBIGUOUS -> AMBIGUOUS
else -> COMPATIBLE
```

Unilateral topics do not use an LLM.

## Why the LLM cannot invent terms

The model never returns agreement prose.

Treaty stores the original clauses from both pinned policy versions. Consensus only determines whether overlapping clauses can coexist.

This makes compromise invention impossible at the storage layer.

## Important reviewer-facing invariants

- policy versions are immutable and definition-hashed
- assessments pin both definition hashes
- reversed policy order reuses one cache entry
- same owner cannot manufacture both sides
- only policy owners can open assessments
- only compatible assessments can be proposed
- paused underlying policies block new proposals and ratification
- proposer auto-ratifies only their own side
- second owner must ratify independently
- either owner may reject before activation
- supersession happens only when the successor becomes fully ratified
- policy text is untrusted prompt data
- validator disagreement rejects the leader proposal
- no funds move anywhere in the contract

## Main source

`contracts/treaty.py`

## Tests

`tests/direct/test_treaty.py`

`tests/direct/test_treaty_hardening.py`

## Documentation

`docs/CONSENSUS.md`

`docs/SECURITY.md`

## Reusable interface

`ITreaty` is declared in the contract.

A consumer can pin both treaty ID and agreement hash:

```python
treaty.is_treaty_active(treaty_id, expected_agreement_hash)
```

## Suggested review demo

1. Alice publishes buyer policy v1.
2. Bob publishes seller policy v1.
3. Open and resolve a compatible assessment.
4. Show the cached assessment when the same pair is requested in reverse order.
5. Propose a treaty.
6. Show it remains `PROPOSED` after only Alice's ratification.
7. Bob ratifies and the treaty becomes `ACTIVE`.
8. Create a successor proposal referencing the active treaty.
9. Show the parent remains active while successor has only one ratification.
10. Bob ratifies successor.
11. Show parent becomes `SUPERSEDED` and successor becomes `ACTIVE`.
12. Run the validator-disagreement direct test to prove the validator is not a format check.
13. Pause one policy and show that historical compatibility remains queryable while fresh proposal/ratification is blocked.

## Deployment

The repository includes `scripts/deploy_studionet.py`, which uses the active GenLayer CLI account and does not handle private keys or passwords itself.
