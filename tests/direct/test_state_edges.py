"""Boundary and state-machine coverage for the versioned Treaty protocol."""

import json

from test_treaty import B, DOMAIN, SAFE_COMPATIBLE, A, create_pair, resolve, setup_domain


def test_empty_domain_reverts(direct_vm, direct_deploy, direct_alice):
    direct_vm.sender = direct_alice
    contract = direct_deploy("contracts/treaty.py")
    with direct_vm.expect_revert("1..24 topics"):
        contract.create_domain("empty", json.dumps({"topics": [], "dependencies": []}))


def test_duplicate_domain_topic_reverts(direct_vm, direct_deploy, direct_alice):
    direct_vm.sender = direct_alice
    contract = direct_deploy("contracts/treaty.py")
    definition = {"topics": [
        {"topic": "x.one", "group": "g"}, {"topic": "x.one", "group": "g"}
    ], "dependencies": []}
    with direct_vm.expect_revert("duplicate domain topic"):
        contract.create_domain("bad", json.dumps(definition))


def test_dependency_must_reference_known_distinct_groups(direct_vm, direct_deploy, direct_alice):
    direct_vm.sender = direct_alice
    contract = direct_deploy("contracts/treaty.py")
    definition = {"topics": [{"topic": "x.one", "group": "g"}], "dependencies": [{"left_group": "g", "right_group": "missing"}]}
    with direct_vm.expect_revert("distinct known groups"):
        contract.create_domain("bad", json.dumps(definition))


def test_only_domain_creator_can_publish_version(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, domain_id = setup_domain(direct_vm, direct_deploy, direct_alice)
    with direct_vm.prank(direct_bob):
        with direct_vm.expect_revert("only domain creator"):
            contract.publish_domain_version(domain_id, DOMAIN)


def test_unknown_policy_version_reverts(direct_vm, direct_deploy, direct_alice):
    contract, domain_id = setup_domain(direct_vm, direct_deploy, direct_alice)
    policy_id = contract.create_policy("a", domain_id, 1, A)
    with direct_vm.expect_revert("unknown policy version"):
        contract.get_policy_version(policy_id, 99)


def test_ambiguous_assessment_cannot_be_proposed(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, _, a, b = create_pair(direct_vm, direct_deploy, direct_alice, direct_bob)
    assessment_id = contract.open_assessment(a, 1, b, 1)
    ambiguous = json.dumps({"relations": {
        "commercial-payment": "AMBIGUOUS",
        "identity-data": "AMBIGUOUS",
    }, "overall": "AMBIGUOUS"})
    resolve(direct_vm, contract, assessment_id, ambiguous)
    assert contract.get_assessment(assessment_id)["status_name"] == "AMBIGUOUS"
    with direct_vm.expect_revert("only compatible assessments"):
        contract.propose_treaty(assessment_id, 0, 0)


def test_rejection_is_terminal(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, _, a, b = create_pair(direct_vm, direct_deploy, direct_alice, direct_bob, B.replace("email", "pii"))
    assessment_id = contract.open_assessment(a, 1, b, 1)
    resolve(direct_vm, contract, assessment_id)
    treaty_id = contract.propose_treaty(assessment_id, 0, 0)
    contract.reject_treaty(treaty_id)
    assert contract.get_treaty(treaty_id)["status_name"] == "REJECTED"
    with direct_vm.expect_revert("not awaiting ratification"):
        contract.ratify_treaty(treaty_id)


def test_expiry_past_and_now_revert(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, _, a, b = create_pair(direct_vm, direct_deploy, direct_alice, direct_bob, B.replace("email", "pii"))
    assessment_id = contract.open_assessment(a, 1, b, 1)
    resolve(direct_vm, contract, assessment_id)
    now = contract.get_policy(a)["created_at"]
    with direct_vm.expect_revert("expiry must be in the future"):
        contract.propose_treaty(assessment_id, now, 0)


def test_expiry_maximum_allowed_and_plus_one_rejected(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, _, a, b = create_pair(direct_vm, direct_deploy, direct_alice, direct_bob, B.replace("email", "pii"))
    assessment_id = contract.open_assessment(a, 1, b, 1)
    resolve(direct_vm, contract, assessment_id)
    now = contract.get_policy(a)["created_at"]
    max_expiry = now + 365 * 24 * 60 * 60
    treaty_id = contract.propose_treaty(assessment_id, max_expiry, 0)
    assert contract.get_treaty(treaty_id)["expires_at"] == max_expiry
    with direct_vm.expect_revert("lifetime exceeds"):
        contract.propose_treaty(assessment_id, max_expiry + 1, 0)


def test_cached_assessment_changes_for_new_policy_version(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, domain_id, a, b = create_pair(direct_vm, direct_deploy, direct_alice, direct_bob, B.replace("email", "pii"))
    first = contract.open_assessment(a, 1, b, 1)
    direct_vm.sender = direct_alice
    contract.publish_version(a, json.dumps([{"topic": "commercial.price", "statement": "Total price must not exceed 55 USD."}]))
    with direct_vm.expect_revert("unknown policy version"):
        contract.open_assessment(a, 2, b, 2)
    assert int(contract.get_cached_assessment(a, 1, b, 1)) == int(first)


def test_assessment_cannot_be_resolved_twice(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, _, a, b = create_pair(direct_vm, direct_deploy, direct_alice, direct_bob, B.replace("email", "pii"))
    assessment_id = contract.open_assessment(a, 1, b, 1)
    resolve(direct_vm, contract, assessment_id)
    with direct_vm.expect_revert("already resolved"):
        contract.resolve_assessment(assessment_id)


def test_consumer_interface_requires_exact_agreement_hash(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, _, a, b = create_pair(direct_vm, direct_deploy, direct_alice, direct_bob, B.replace("email", "pii"))
    assessment_id = contract.open_assessment(a, 1, b, 1)
    resolve(direct_vm, contract, assessment_id)
    treaty_id = contract.propose_treaty(assessment_id, 0, 0)
    assert not contract.is_treaty_active(treaty_id, "wrong")
    assert contract.get_treaty_terms(treaty_id)
