"""Direct-mode protocol tests for Treaty."""

import json
import re

CONTRACT = "contracts/treaty.py"
LEADER_PROMPT = r"LEADER PASS"
VALIDATOR_PROMPT = r"INDEPENDENT VALIDATOR PASS"
DOMAIN = json.dumps({"topics": [
    {"topic": "commercial.price", "group": "commercial-payment"},
    {"topic": "identity.email", "group": "identity-data"},
    {"topic": "identity.pii", "group": "identity-data"},
    {"topic": "execution.delivery", "group": "execution"},
    {"topic": "refund.failure", "group": "refund"},
], "dependencies": []})
A = json.dumps([
    {"topic": "identity.pii", "statement": "Customer personally identifiable information must never be disclosed."},
    {"topic": "commercial.price", "statement": "Total price must not exceed 50 USD."},
    {"topic": "refund.failure", "statement": "A full refund is required when execution never begins."},
])
B = json.dumps([
    {"topic": "identity.email", "statement": "The service must operate without receiving customer email or other PII."},
    {"topic": "commercial.price", "statement": "Price must be between 40 USD and 45 USD."},
    {"topic": "execution.delivery", "statement": "Delivery completes within 300 seconds."},
])
B_CONFLICT = json.dumps([
    {"topic": "identity.email", "statement": "Customer email is required before execution begins."},
    {"topic": "commercial.price", "statement": "Price must be at least 60 USD."},
])


def semantic(groups, overall="COMPATIBLE"):
    return json.dumps({
        "relations": {
            str(row["group"]): str(row["relation"])
            for row in groups
            if str(row["relation"]) not in ("UNILATERAL_A", "UNILATERAL_B")
        },
        "overall": overall,
    })


SAFE_COMPATIBLE = semantic([
    {"group": "commercial-payment", "relation": "COMPATIBLE", "a_indices": [0], "b_indices": [0]},
    {"group": "execution", "relation": "UNILATERAL_B", "a_indices": [], "b_indices": []},
    {"group": "identity-data", "relation": "COMPATIBLE", "a_indices": [0], "b_indices": [0]},
    {"group": "refund", "relation": "UNILATERAL_A", "a_indices": [], "b_indices": []},
])
GROUP_CONFLICT = semantic([
    {"group": "commercial-payment", "relation": "CONFLICT", "a_indices": [0], "b_indices": [0]},
    {"group": "execution", "relation": "UNILATERAL_B", "a_indices": [], "b_indices": []},
    {"group": "identity-data", "relation": "CONFLICT", "a_indices": [0], "b_indices": [0]},
    {"group": "refund", "relation": "UNILATERAL_A", "a_indices": [], "b_indices": []},
], "CONFLICT")
CONFLICT_SMALL = semantic([
    {"group": "commercial-payment", "relation": "CONFLICT", "a_indices": [0], "b_indices": [0]},
    {"group": "identity-data", "relation": "CONFLICT", "a_indices": [0], "b_indices": [0]},
    {"group": "refund", "relation": "UNILATERAL_A", "a_indices": [], "b_indices": []},
], "CONFLICT")


def mock_consensus(vm, leader=SAFE_COMPATIBLE, validator=None):
    def register(pass_prompt, value):
        try:
            spec = json.loads(value)
        except Exception:
            vm.mock_llm(pass_prompt, value)
            return
        relations = spec.get("relations") if isinstance(spec, dict) else None
        if not isinstance(relations, dict):
            vm.mock_llm(pass_prompt, value)
            return
        for identity, relation in relations.items():
            if str(identity).startswith("self:"):
                identity_pattern = '"kind":"self"'
            elif str(identity).startswith("dependency:"):
                identity_pattern = '"kind":"dependency"'
            else:
                identity_pattern = re.escape(str(identity).split("<->")[0]).replace(r'\-', '-')
            vm.mock_llm(
                rf'(?s){pass_prompt}.*{identity_pattern}',
                json.dumps({"relation": relation}),
            )
    register(LEADER_PROMPT, leader)
    register(VALIDATOR_PROMPT, leader if validator is None else validator)


def setup_domain(vm, deploy, owner):
    vm.sender = owner
    contract = deploy(CONTRACT)
    return contract, contract.create_domain("Agent Service", DOMAIN)


def create_pair(vm, deploy, alice, bob, right=B):
    contract, domain_id = setup_domain(vm, deploy, alice)
    vm.sender = alice
    a = contract.create_policy("Buyer", domain_id, 1, A)
    with vm.prank(bob):
        b = contract.create_policy("Seller", domain_id, 1, right)
    vm.sender = alice
    return contract, domain_id, a, b


def resolve(vm, contract, assessment_id, leader=SAFE_COMPATIBLE, validator=None):
    mock_consensus(vm, leader, validator)
    contract.resolve_assessment(assessment_id)


def test_domain_and_policy_pin_immutable_version(direct_vm, direct_deploy, direct_alice):
    contract, domain_id = setup_domain(direct_vm, direct_deploy, direct_alice)
    policy_id = contract.create_policy("Buyer", domain_id, 1, A)
    domain = contract.get_domain_version(domain_id, 1)
    policy = contract.get_policy(policy_id)
    assert policy["domain_id"] == int(domain_id)
    assert policy["domain_definition_hash"] == domain["definition_hash"]


def test_domain_and_policy_versions_are_immutable(direct_vm, direct_deploy, direct_alice):
    contract, domain_id = setup_domain(direct_vm, direct_deploy, direct_alice)
    policy_id = contract.create_policy("Buyer", domain_id, 1, A)
    old_domain = contract.get_domain_version(domain_id, 1)
    old_policy = contract.get_policy_version(policy_id, 1)
    contract.publish_domain_version(domain_id, json.dumps({"topics": [{"topic": "commercial.price", "group": "commercial-payment"}], "dependencies": []}))
    contract.publish_version(policy_id, json.dumps([{"topic": "commercial.price", "statement": "Price <= 55 USD."}]))
    assert contract.get_domain_version(domain_id, 1)["definition_hash"] == old_domain["definition_hash"]
    assert contract.get_policy_version(policy_id, 1)["definition_hash"] == old_policy["definition_hash"]


def test_unknown_topic_reverts(direct_vm, direct_deploy, direct_alice):
    contract, domain_id = setup_domain(direct_vm, direct_deploy, direct_alice)
    with direct_vm.expect_revert("not in pinned domain vocabulary"):
        contract.create_policy("Bad", domain_id, 1, json.dumps([{ "topic": "unknown.topic", "statement": "No." }]))


def test_domain_mismatch_reverts(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, domain_a = setup_domain(direct_vm, direct_deploy, direct_alice)
    with direct_vm.prank(direct_bob):
        domain_b = contract.create_domain("Other", DOMAIN)
    a = contract.create_policy("A", domain_a, 1, A)
    with direct_vm.prank(direct_bob):
        b = contract.create_policy("B", domain_b, 1, B)
    with direct_vm.expect_revert("same domain version"):
        contract.open_assessment(a, 1, b, 1)


def test_owner_access_and_policy_pause(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, domain_id = setup_domain(direct_vm, direct_deploy, direct_alice)
    policy_id = contract.create_policy("A", domain_id, 1, A)
    with direct_vm.prank(direct_bob):
        with direct_vm.expect_revert("only policy owner"):
            contract.publish_version(policy_id, A)
        with direct_vm.expect_revert("only policy owner"):
            contract.pause_policy(policy_id, True)


def test_semantic_group_closes_topic_key_evasion(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, _, a, b = create_pair(direct_vm, direct_deploy, direct_alice, direct_bob)
    assessment_id = contract.open_assessment(a, 1, b, 1)
    resolve(direct_vm, contract, assessment_id, GROUP_CONFLICT)
    result = contract.get_assessment(assessment_id)
    assert result["status_name"] == "INCOMPATIBLE"
    assert any(row["group"] == "identity-data" and row["relation_name"] == "CONFLICT" for row in result["results"])


def test_compatible_assessment_and_reverse_cache(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, _, a, b = create_pair(direct_vm, direct_deploy, direct_alice, direct_bob, B.replace("email", "pii"))
    first = contract.open_assessment(a, 1, b, 1)
    with direct_vm.prank(direct_bob):
        second = contract.open_assessment(b, 1, a, 1)
    assert int(first) == int(second)
    resolve(direct_vm, contract, first)
    assert contract.get_assessment(first)["status_name"] == "COMPATIBLE"


def test_conflict_dominates_ambiguity(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, _, a, b = create_pair(direct_vm, direct_deploy, direct_alice, direct_bob)
    assessment_id = contract.open_assessment(a, 1, b, 1)
    mixed = semantic([
        {"group": "commercial-payment", "relation": "CONFLICT", "a_indices": [0], "b_indices": [0]},
        {"group": "execution", "relation": "UNILATERAL_B", "a_indices": [], "b_indices": []},
        {"group": "identity-data", "relation": "AMBIGUOUS", "a_indices": [0], "b_indices": [0]},
        {"group": "refund", "relation": "UNILATERAL_A", "a_indices": [], "b_indices": []},
    ], "AMBIGUOUS")
    resolve(direct_vm, contract, assessment_id, mixed)
    assert contract.get_assessment(assessment_id)["status_name"] == "INCOMPATIBLE"


def test_bilateral_activation_and_hash_pinning(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, _, a, b = create_pair(direct_vm, direct_deploy, direct_alice, direct_bob, B.replace("email", "pii"))
    assessment_id = contract.open_assessment(a, 1, b, 1)
    resolve(direct_vm, contract, assessment_id)
    treaty_id = contract.propose_treaty(assessment_id, 0, 0)
    assert contract.get_treaty(treaty_id)["status_name"] == "PROPOSED"
    with direct_vm.prank(direct_bob):
        contract.ratify_treaty(treaty_id)
    treaty = contract.get_treaty(treaty_id)
    assert treaty["status_name"] == "ACTIVE"
    assert contract.is_treaty_active(treaty_id, treaty["agreement_hash"])
    assert not contract.is_treaty_active(treaty_id, "00" * 32)


def test_incompatible_cannot_be_proposed(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, _, a, b = create_pair(direct_vm, direct_deploy, direct_alice, direct_bob, B_CONFLICT)
    assessment_id = contract.open_assessment(a, 1, b, 1)
    resolve(direct_vm, contract, assessment_id, CONFLICT_SMALL)
    with direct_vm.expect_revert("only compatible assessments"):
        contract.propose_treaty(assessment_id, 0, 0)


def test_terms_are_original_source_clauses(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, _, a, b = create_pair(direct_vm, direct_deploy, direct_alice, direct_bob, B.replace("email", "pii"))
    assessment_id = contract.open_assessment(a, 1, b, 1)
    resolve(direct_vm, contract, assessment_id)
    treaty_id = contract.propose_treaty(assessment_id, 0, 0)
    terms = contract.get_treaty_terms(treaty_id)
    assert all("agreement" not in item for item in terms)
    assert any(item["group"] == "commercial-payment" for item in terms)
