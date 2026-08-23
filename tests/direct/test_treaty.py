"""Direct-mode tests for the Treaty reusable Intelligent Contract."""

import json

CONTRACT = "contracts/treaty.py"
PROMPT = r"You are a semantic satisfiability checker for two autonomous-system policies"

A_CONSTRAINTS = json.dumps([
    {"topic": "data.pii", "statement": "Customer personally identifiable information must never be disclosed to the service provider."},
    {"topic": "price.usd", "statement": "Total price must not exceed 50 USD."},
    {"topic": "refund.failure", "statement": "A full refund is required when execution never begins."},
])

B_COMPATIBLE = json.dumps([
    {"topic": "data.pii", "statement": "The service must operate without receiving customer personally identifiable information."},
    {"topic": "price.usd", "statement": "The service price must be at least 40 USD and at most 45 USD."},
    {"topic": "delivery.seconds", "statement": "Delivery must complete within 600 seconds."},
])

B_CONFLICT = json.dumps([
    {"topic": "data.pii", "statement": "The customer email address is required before execution may begin."},
    {"topic": "price.usd", "statement": "The service price must be at least 60 USD."},
])

COMPATIBLE_LLM = json.dumps({
    "results": [
        {"topic": "data.pii", "relation": "COMPATIBLE"},
        {"topic": "price.usd", "relation": "COMPATIBLE"},
    ]
})

CONFLICT_LLM = json.dumps({
    "results": [
        {"topic": "data.pii", "relation": "CONFLICT"},
        {"topic": "price.usd", "relation": "CONFLICT"},
    ]
})


def create_pair(direct_vm, contract, alice, bob, b_constraints=B_COMPATIBLE):
    direct_vm.sender = alice
    policy_a = contract.create_policy("Buyer Guardrails", "agent-service-v1", A_CONSTRAINTS)
    with direct_vm.prank(bob):
        policy_b = contract.create_policy("Seller Guardrails", "agent-service-v1", b_constraints)
    return policy_a, policy_b


def test_create_policy_publishes_immutable_version(direct_vm, direct_deploy, direct_alice):
    direct_vm.sender = direct_alice
    contract = direct_deploy(CONTRACT)
    policy_id = contract.create_policy("Buyer", "agent-service-v1", A_CONSTRAINTS)
    policy = contract.get_policy(policy_id)
    version = contract.get_policy_version(policy_id, 1)
    expected_owner = "0x" + direct_alice.hex()
    assert policy["owner"].lower() == expected_owner.lower()
    assert policy["active_version"] == 1
    assert policy["domain_key"] == "agent-service-v1"
    assert len(version["constraints"]) == 3
    assert len(version["definition_hash"]) == 64


def test_publish_version_changes_definition_without_mutating_v1(direct_vm, direct_deploy, direct_alice):
    direct_vm.sender = direct_alice
    contract = direct_deploy(CONTRACT)
    policy_id = contract.create_policy("Buyer", "agent-service-v1", A_CONSTRAINTS)
    v1 = contract.get_policy_version(policy_id, 1)
    v2_constraints = json.dumps([
        {"topic": "price.usd", "statement": "Total price must not exceed 55 USD."},
        {"topic": "refund.failure", "statement": "A full refund is required when execution never begins."},
    ])
    version = contract.publish_version(policy_id, v2_constraints)
    assert int(version) == 2
    assert contract.get_policy_version(policy_id, 1)["definition_hash"] == v1["definition_hash"]
    assert contract.get_policy_version(policy_id, 2)["definition_hash"] != v1["definition_hash"]


def test_duplicate_topics_and_bad_keys_revert(direct_vm, direct_deploy):
    contract = direct_deploy(CONTRACT)
    with direct_vm.expect_revert("duplicate topic"):
        contract.create_policy("Bad", "agent-service-v1", json.dumps([
            {"topic": "price.usd", "statement": "Price <= 50 USD."},
            {"topic": "price.usd", "statement": "Price >= 40 USD."},
        ]))
    with direct_vm.expect_revert("domain_key"):
        contract.create_policy("Bad", "Agent Service With Spaces", A_CONSTRAINTS)


def test_only_owner_can_publish_or_pause(direct_vm, direct_deploy, direct_alice, direct_bob):
    direct_vm.sender = direct_alice
    contract = direct_deploy(CONTRACT)
    policy_id = contract.create_policy("Buyer", "agent-service-v1", A_CONSTRAINTS)
    with direct_vm.prank(direct_bob):
        with direct_vm.expect_revert("only policy owner"):
            contract.publish_version(policy_id, A_CONSTRAINTS)
        with direct_vm.expect_revert("only policy owner"):
            contract.pause_policy(policy_id, True)


def test_domain_mismatch_cannot_be_assessed(direct_vm, direct_deploy, direct_alice, direct_bob):
    direct_vm.sender = direct_alice
    contract = direct_deploy(CONTRACT)
    a = contract.create_policy("A", "agent-service-v1", A_CONSTRAINTS)
    with direct_vm.prank(direct_bob):
        b = contract.create_policy("B", "different-domain", B_COMPATIBLE)
    with direct_vm.expect_revert("domains must match"):
        contract.open_assessment(a, 1, b, 1)


def test_compatible_assessment_uses_consensus_and_preserves_unilateral_terms(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy(CONTRACT)
    a, b = create_pair(direct_vm, contract, direct_alice, direct_bob)
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(PROMPT, COMPATIBLE_LLM)
    assessment_id = contract.open_assessment(a, 1, b, 1)
    contract.resolve_assessment(assessment_id)
    assessment = contract.get_assessment(assessment_id)
    assert assessment["status_name"] == "COMPATIBLE"
    relations = {row["topic"]: row["relation_name"] for row in assessment["results"]}
    assert relations["data.pii"] == "COMPATIBLE"
    assert relations["price.usd"] == "COMPATIBLE"
    assert relations["refund.failure"] == "UNILATERAL_A"
    assert relations["delivery.seconds"] == "UNILATERAL_B"
    assert direct_vm.run_validator() is True


def test_incompatible_assessment_cannot_become_treaty(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy(CONTRACT)
    a, b = create_pair(direct_vm, contract, direct_alice, direct_bob, B_CONFLICT)
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(PROMPT, CONFLICT_LLM)
    assessment_id = contract.open_assessment(a, 1, b, 1)
    contract.resolve_assessment(assessment_id)
    assert contract.get_assessment(assessment_id)["status_name"] == "INCOMPATIBLE"
    with direct_vm.expect_revert("only compatible assessments"):
        contract.propose_treaty(assessment_id, 0, 0)


def test_assessment_cache_is_order_independent(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy(CONTRACT)
    a, b = create_pair(direct_vm, contract, direct_alice, direct_bob)
    direct_vm.sender = direct_alice
    first = contract.open_assessment(a, 1, b, 1)
    with direct_vm.prank(direct_bob):
        second = contract.open_assessment(b, 1, a, 1)
    assert int(first) == int(second)
    assert int(contract.get_cached_assessment(a, 1, b, 1)) == int(first)
    assert int(contract.get_cached_assessment(b, 1, a, 1)) == int(first)


def test_bilateral_ratification_activates_treaty(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy(CONTRACT)
    a, b = create_pair(direct_vm, contract, direct_alice, direct_bob)
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(PROMPT, COMPATIBLE_LLM)
    assessment_id = contract.open_assessment(a, 1, b, 1)
    contract.resolve_assessment(assessment_id)
    treaty_id = contract.propose_treaty(assessment_id, 0, 0)
    proposed = contract.get_treaty(treaty_id)
    assert proposed["status_name"] == "PROPOSED"
    assert proposed["ratified_a"] is True
    assert proposed["ratified_b"] is False
    with direct_vm.prank(direct_bob):
        contract.ratify_treaty(treaty_id)
    active = contract.get_treaty(treaty_id)
    assert active["status_name"] == "ACTIVE"
    assert active["ratified_a"] is True
    assert active["ratified_b"] is True
    assert contract.is_treaty_active(treaty_id, active["agreement_hash"]) is True
    assert contract.is_treaty_active(treaty_id, "00" * 32) is False


def test_party_can_reject_before_activation(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy(CONTRACT)
    a, b = create_pair(direct_vm, contract, direct_alice, direct_bob)
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(PROMPT, COMPATIBLE_LLM)
    assessment_id = contract.open_assessment(a, 1, b, 1)
    contract.resolve_assessment(assessment_id)
    treaty_id = contract.propose_treaty(assessment_id, 0, 0)
    with direct_vm.prank(direct_bob):
        contract.reject_treaty(treaty_id)
    assert contract.get_treaty(treaty_id)["status_name"] == "REJECTED"


def test_treaty_terms_are_source_clauses_not_ai_invented_text(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = direct_deploy(CONTRACT)
    a, b = create_pair(direct_vm, contract, direct_alice, direct_bob)
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(PROMPT, COMPATIBLE_LLM)
    assessment_id = contract.open_assessment(a, 1, b, 1)
    contract.resolve_assessment(assessment_id)
    treaty_id = contract.propose_treaty(assessment_id, 0, 0)
    terms = contract.get_treaty_terms(treaty_id)
    by_topic = {row["topic"]: row for row in terms}
    assert by_topic["price.usd"]["party_a_constraint"] == "Total price must not exceed 50 USD."
    assert by_topic["price.usd"]["party_b_constraint"] == "The service price must be at least 40 USD and at most 45 USD."
    assert by_topic["delivery.seconds"]["party_a_constraint"] == ""
    assert "agreement" not in by_topic["price.usd"]
