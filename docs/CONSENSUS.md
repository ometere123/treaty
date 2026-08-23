# Consensus Design

## Scope

Treaty uses GenLayer consensus for exactly one semantic operation:

> Given two hard constraints on the same topic, is there clearly at least one behavior that satisfies both?

Everything else is deterministic.

## Why exact-topic pairing is deterministic

Policy authors provide machine topic keys such as:

```text
price.usd
data.pii
refund.failure
delivery.seconds
```

Treaty never asks a model to discover which topics match.

It sorts both policies by exact topic key and computes unilateral A topics, unilateral B topics, and overlapping topics. Only overlapping pairs enter nondeterministic execution.

## Leader output

For every overlapping topic, the leader must return exactly one of:

```text
COMPATIBLE
CONFLICT
AMBIGUOUS
```

No prose is consensus-critical.

## Validator behavior

The validator does not evaluate JSON shape alone. It independently calls the same semantic satisfiability function against the same immutable inputs.

A proposal is accepted only when:

1. proposed topics exactly match expected topics
2. order is exact
3. every proposed relation is valid
4. independent validator output is valid
5. every independent relation matches the proposed relation

This is implemented through `gl.vm.run_nondet_unsafe`.

## Failure behavior

Malformed LLM output raises inside nondeterministic execution and cannot settle into state.

Validator exceptions return disagreement.

If models cannot converge on a clearly bounded relation, the transaction should not achieve consensus rather than silently writing weaker state. At the semantic level, the prompt also provides `AMBIGUOUS` as the safe output when the policy text itself cannot be resolved.

## Deterministic aggregation

```text
any CONFLICT  -> assessment INCOMPATIBLE
else
any AMBIGUOUS -> assessment AMBIGUOUS
else
COMPATIBLE
```

No model chooses the final assessment status.

## Why unilateral constraints are compatible

The Treaty policy model defines every listed clause as a hard restriction and absence of a topic as no extra restriction from that side.

Therefore:

```text
A: delivery <= 600 seconds
B: no delivery topic
```

is not interpreted as B disagreeing with the limit. The unilateral clause remains visible and authoritative in `get_treaty_terms`.

## Consensus does not equal consent

A compatible semantic assessment is not an agreement.

`propose_treaty` creates a deterministic proposal referencing the compatible assessment. Only actual policy owners can ratify. Both owner flags must become true before the state transition to `ACTIVE`.

This separation prevents an LLM quorum from creating contractual consent.

## Cache safety

Assessments are cached by an order-independent hash containing:

- policy A ID
- policy A version
- policy A definition hash
- policy B ID
- policy B version
- policy B definition hash

Because versions are immutable, a cached assessment cannot silently drift when either owner publishes a later version. The new version creates a new pair hash and therefore needs a new semantic assessment.
