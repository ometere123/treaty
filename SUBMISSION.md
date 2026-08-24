# Treaty — Intelligent Contract Submission Notes

## Reviewer summary

Treaty is a reusable GenLayer primitive for protocol-level compatibility and bilateral consent between independent autonomous systems. A versioned domain vocabulary closes topic-key evasion; immutable policy versions are grouped into semantic units; GenLayer consensus produces a bounded compatibility receipt with a global cross-group safety result; and only the two policy owners can activate a treaty.

GenLayer matters because natural-language satisfiability cannot be fully reduced to ordinary deterministic contract logic, while neither policy owner should unilaterally interpret both sides. Treaty is not a thin LLM wrapper: the contract owns domain/version hashes, policy ownership, cache identity, source pinning, assessment state, expiry, consent, rejection, and supersession. The LLM only evaluates bounded compatibility claims.

The exact adversarial proof is in `tests/direct/test_treaty_hardening.py`: malformed, reordered, invented-group, invented-witness, prompt-injection, validator-rejection, and payload-boundary cases are covered. Local proof is 40 Direct Mode tests, 45 deterministic preflight checks, and a passing GenVM lint. Live lifecycle evidence is recorded in `docs/DEPLOYMENT.md`; only claims backed by finalized receipts belong there.

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

The final committed StudioNet instance is `0xd11310Fd37C99700075bA0F49870730cb128e0b6`. Deployment transaction `0x03dd39eee8cd53a5b8be9e60fe673e7489253b28ff34407fe25d363989295718` is explicitly `FINALIZED`, with `SUCCESS` execution and `MAJORITY_AGREE`. Full evidence and the reproducible live semantic-resolution limitation are in [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).
