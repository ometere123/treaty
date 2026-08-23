# Consensus Design

Treaty uses GenLayer consensus for one bounded semantic operation: deciding whether two immutable policy versions can coexist across a versioned domain vocabulary.

## Immutable source boundary

Each policy pins a `domain_id`, `domain_version`, and `domain_definition_hash`. The domain version defines canonical topics, exactly one semantic group per topic, and bounded group dependencies. Policy statements are untrusted data. A later domain or policy version cannot mutate an earlier assessment.

Before consensus, deterministic code groups all clauses by their canonical semantic group. This prevents topic-key evasion: `identity.pii` and `identity.email` enter the same semantic unit when the domain says both belong to `identity-data`. The complete policy sets and dependency list also enter a bounded global consistency check, so contradictions that span groups cannot silently become unilateral clauses.

## Leader proposal

The leader receives the complete source and returns only bounded JSON:

```json
{"groups":[{"group":"identity-data","relation":"CONFLICT","a_indices":[0],"b_indices":[0]}],"overall":"INCOMPATIBLE"}
```

Allowed group relations are `UNILATERAL_A`, `UNILATERAL_B`, `COMPATIBLE`, `CONFLICT`, and `AMBIGUOUS`. The global result is only `COMPATIBLE`, `CONFLICT`, or `AMBIGUOUS`. Witnesses are source clause indices, never generated terms or prose.

## Validator behavior

Treaty uses `gl.vm.run_nondet_unsafe`, which is the appropriate custom boundary for non-deterministic semantic work. The validator first checks the proposal’s bounded shape, canonical group order, finite enums, and witness index bounds. It then receives the immutable source and the leader proposal and asks a source-grounded validation prompt whether that exact proposal is conservative and supported by the source.

This follows current GenLayer guidance: validators must independently verify substance, not only formatting. A source-grounded validator is appropriate here because the leader’s bounded output is a claim about fixed source clauses; the validator does not need to generate a competing classification. The validator rejects invented groups, missing groups, invalid witnesses, unsupported labels, compromise terms, and proposals that make a conflict/ambiguity claim without source-grounded witnesses.

## Deterministic final state

The model cannot choose state transitions directly. Deterministic code applies:

```text
any group CONFLICT or global CONFLICT  -> INCOMPATIBLE
else any group AMBIGUOUS or global AMBIGUOUS -> AMBIGUOUS
else                                     -> COMPATIBLE
```

Conflict dominates ambiguity. Only `COMPATIBLE` assessments can be proposed as treaties. No model output can create negotiated terms; treaty terms are always the original clauses from the pinned policy versions.

## Failure behavior and bounds

Malformed leader output, validator exceptions, invalid witnesses, or validator disagreement cannot settle state. Source size is checked before nondeterministic execution and is rejected when it exceeds the bounded prompt budget. Treaty never slices or silently truncates semantic source material.

## Cache safety

The assessment cache key includes both policy IDs, versions, and immutable policy definition hashes. The assessment additionally stores both domain references and the domain hash. Reversed policy input returns the same receipt; any new policy or domain version produces a new identity.

## Consent is separate

Consensus establishes compatibility only. A compatible assessment becomes `PROPOSED`; the two independent policy owners must ratify separately before deterministic code creates an `ACTIVE` treaty.
