# Consensus Design

Treaty uses GenLayer consensus for one bounded semantic operation: deciding whether two immutable policy versions can coexist across a versioned domain vocabulary.

## Immutable source boundary

Each policy pins a `domain_id`, `domain_version`, and `domain_definition_hash`. The domain version defines canonical topics, exactly one semantic group per topic, and bounded group dependencies. Policy statements are untrusted data. A later domain or policy version cannot mutate an earlier assessment.

Before consensus, deterministic code groups all clauses by their canonical semantic group. This prevents topic-key evasion: `identity.pii` and `identity.email` enter the same semantic unit when the domain says both belong to `identity-data`. Declared dependency pairs are converted mechanically into additional bounded cross-group units; no giant global prompt is used.

## Leader proposal

For each bilateral group or relevant dependency unit, the leader receives only that unit’s immutable source and returns one bounded relation:

```json
{"relation":"CONFLICT"}
```

Unilateral groups never enter consensus: deterministic source cardinality produces `UNILATERAL_A` or `UNILATERAL_B`. Nondeterministic units allow only `COMPATIBLE`, `CONFLICT`, or `AMBIGUOUS`. Stored group identities and witness ranges are reconstructed deterministically from the immutable source, never generated as prose.

## Validator behavior

Treaty uses `gl.vm.run_nondet_unsafe`, which is the appropriate custom boundary for non-deterministic semantic work. The validator first checks the bounded result shape and then independently reruns the same narrow unit judgments over the same immutable source. Consensus compares the material relation for every canonical unit; the validator is not a `{valid:true}` rubber stamp.

This follows current GenLayer guidance: validators must independently verify substance, not only formatting. Deterministic unit identity prevents invented or omitted groups/dependencies; malformed JSON, unsupported labels, validator errors, and material disagreement fail safely. The model never controls witnesses, negotiated terms, or state transitions.

## Deterministic final state

The model cannot choose state transitions directly. Deterministic code applies:

```text
any group/dependency CONFLICT  -> INCOMPATIBLE
else any group/dependency AMBIGUOUS -> AMBIGUOUS
else                                     -> COMPATIBLE
```

Conflict dominates ambiguity. Only `COMPATIBLE` assessments can be proposed as treaties. No model output can create negotiated terms; treaty terms are always the original clauses from the pinned policy versions.

## Failure behavior and bounds

Malformed leader output, validator exceptions, invalid witnesses, or validator disagreement cannot settle state. Source size is checked before nondeterministic execution and is rejected when it exceeds the bounded prompt budget. Treaty never slices or silently truncates semantic source material.

## Cache safety

The assessment cache key includes both policy IDs, versions, and immutable policy definition hashes. The assessment additionally stores both domain references and the domain hash. Reversed policy input returns the same receipt; any new policy or domain version produces a new identity.

## Consent is separate

Consensus establishes compatibility only. A compatible assessment becomes `PROPOSED`; the two independent policy owners must ratify separately before deterministic code creates an `ACTIVE` treaty.
