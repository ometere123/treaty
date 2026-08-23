# Security Model

## Domain trust model

A domain creator publishes an immutable vocabulary and semantic grouping. The contract validates duplicate topics, missing groups, malformed dependencies, and unknown references, then hashes the canonical definition. A later version cannot rewrite an old policy or assessment.

The registry does not magically make semantic modeling truthful. Policy parties must trust that the selected domain creator mapped related concepts into appropriate groups. The benefit is that this trust is explicit, versioned, inspectable, and shared rather than hidden in arbitrary caller-selected topic strings. A malicious domain author can still design a poor vocabulary; parties should select reputable domains and pin the exact domain hash.

## Namespace and cross-topic semantics

Policies may use only topics in their pinned domain version. Clauses are grouped by the domain’s canonical semantic group, so different keys in one group are compared together. A global bounded consistency pass sees the complete pinned policy sets and dependencies, allowing contradictions that span groups to produce `CONFLICT` or `AMBIGUOUS` rather than silently becoming unilateral.

## LLM trust boundary

The leader proposes only finite relation codes, global status, and source-clause index witnesses. The validator checks structure and independently source-grounds that exact proposal. Neither model can write state, invent an agreement, add an exception, choose owners, ratify, reject, expire, or supersede. No free-form explanation is consensus-critical.

Policy text is adversarial input. Prompts explicitly mark it as data and forbid following embedded instructions, browsing, tool use, or hidden-context disclosure. Unsupported or unresolved meaning is fail-safe ambiguity; conflict dominates ambiguity.

## Consent and pause semantics

Semantic compatibility is not consent. Only the two policy owners can ratify, and a proposal remains `PROPOSED` after one side. Pausing a policy blocks new proposals and pending ratification but does not retroactively revoke an already active treaty. This preserves completed bilateral consent; revocation is deliberately not part of the current primitive.

## Expiry and supersession races

Expiry must be future and no more than one year from proposal. Read methods enforce effective expiry; `refresh_expiry` materializes `EXPIRED`. A successor requires an active, non-expired parent with matching parties. The parent changes to `SUPERSEDED` only in the same deterministic transition that activates the fully ratified successor. If two children race, the first successful activation wins and the later child fails because its parent is no longer active.

## Resource bounds

Names, domain topics, groups, dependencies, constraints, statements, and semantic groups have explicit finite limits. The complete source payload is measured before consensus and rejected above the prompt budget. There is no source slicing or silent truncation.

## Other invariants

- Policy versions, domain versions, assessments, and agreement hashes are immutable once published.
- Assessment cache identity includes exact policy versions and definition hashes.
- A single owner cannot create both sides of an assessment.
- Wrong agreement hashes fail downstream active-state checks.
- Treaty never moves value, holds funds, or calls arbitrary downstream contracts.
