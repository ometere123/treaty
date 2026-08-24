# Treaty — Intelligent Contract Submission Notes

## Reviewer summary

Treaty is a reusable GenLayer primitive for protocol-level compatibility and bilateral consent between independent autonomous systems. A versioned domain vocabulary closes topic-key evasion; immutable policy versions are evaluated through bounded group, dependency, and same-policy consistency units; GenLayer consensus produces a bounded compatibility receipt; and only the two policy owners can activate a treaty.

GenLayer matters because natural-language satisfiability cannot be fully reduced to ordinary deterministic contract logic, while neither policy owner should unilaterally interpret both sides. Treaty is not a thin LLM wrapper: the contract owns domain/version hashes, policy ownership, cache identity, source pinning, assessment state, expiry, consent, rejection, and supersession. The LLM only evaluates bounded compatibility claims.

The exact adversarial proof is in `tests/direct/`: malformed relation, bilateral unilateral-enum, prompt-injection, validator-rejection, self-policy contradiction, and payload-boundary cases are covered. Local proof is 45 Direct Mode tests, 45 deterministic preflight checks, and a passing GenVM lint. Live lifecycle evidence is recorded in `docs/DEPLOYMENT.md`; only claims backed by finalized receipts belong there.

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

Only bilateral semantic units and declared interacting groups require nondeterministic reasoning.

The leader classifies each overlap into one bounded relation:

```text
COMPATIBLE
CONFLICT
AMBIGUOUS
```

Validators independently rerun the same classification from the immutable source clauses.

The validator checks:

1. every model response is exactly relation-only JSON
2. bilateral/self responses use only the three semantic relations
3. unilateral results arise only from deterministic source cardinality
4. validator independently executes the same semantic task
5. every validator relation equals the proposed relation

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

The final committed StudioNet instance is `0x16238CD12aae247b8E985d63C317BC6cb18c57A4`. Deployment transaction `0x352cf0f047db56393328e2da3ebe6eca06fa17df9af6c8ef8002c14bbbf2e641` is explicitly `FINALIZED`, with `SUCCESS` execution and `MAJORITY_AGREE`. Full evidence and the exact remaining lifecycle boundary are in [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).
