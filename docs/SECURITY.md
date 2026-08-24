# Security Model

## Domain trust model

A domain creator publishes an immutable vocabulary and semantic grouping. The contract validates duplicate topics, missing groups, malformed dependencies, and unknown references, then hashes the canonical definition. A later version cannot rewrite an old policy or assessment.

The registry does not magically make semantic modeling truthful. Policy parties must trust that the selected domain creator mapped related concepts into appropriate groups. The benefit is that this trust is explicit, versioned, inspectable, and shared rather than hidden in arbitrary caller-selected topic strings. A malicious domain author can still design a poor vocabulary; parties should select reputable domains and pin the exact domain hash.

## Namespace and cross-topic semantics

Policies may use only topics in their pinned domain version. Clauses are grouped by the domain’s canonical semantic group, so different keys in one group are compared together. Every declared dependency whose groups contain clauses becomes a separate bounded cross-group semantic unit, allowing relevant contradictions to produce `CONFLICT` or `AMBIGUOUS` without a giant all-policy prompt.

## LLM trust boundary

The leader proposes only a finite relation for one deterministic semantic unit. The validator independently reruns that unit over the same source and the contract compares the material relation. Group identity, unilateral classification, witness ranges, and final status are deterministic. Neither model can write state, invent an agreement, add an exception, choose owners, ratify, reject, expire, or supersede. No free-form explanation is consensus-critical.

Policy text is adversarial input. Prompts explicitly mark it as data and forbid following embedded instructions, browsing, tool use, or hidden-context disclosure. Unsupported or unresolved meaning is fail-safe ambiguity; conflict dominates ambiguity.

## Consent and pause semantics

Semantic compatibility is not consent. Only the two policy owners can ratify, and a proposal remains `PROPOSED` after one side. Pausing a policy blocks new proposals and pending ratification but does not retroactively revoke an already active treaty. This preserves completed bilateral consent; revocation is deliberately not part of the current primitive.

## Expiry and supersession races

Expiry must be future and no more than one year from proposal. Read methods enforce effective expiry; `refresh_expiry` materializes `EXPIRED`. A successor requires an active, non-expired parent with matching parties. The parent changes to `SUPERSEDED` only in the same deterministic transition that activates the fully ratified successor. If two children race, the first successful activation wins and the later child fails because its parent is no longer active.

## Resource bounds

Names, domain topics, groups, dependencies, constraints, statements, and semantic groups have explicit finite limits. Each complete semantic unit is measured before consensus and rejected above the prompt budget. Complete units may be evaluated separately; there is no source slicing or silent truncation.

## Other invariants

- Policy versions, domain versions, assessments, and agreement hashes are immutable once published.
- Assessment cache identity includes exact policy versions and definition hashes.
- A single owner cannot create both sides of an assessment.
- Wrong agreement hashes fail downstream active-state checks.
- Treaty never moves value, holds funds, or calls arbitrary downstream contracts.
