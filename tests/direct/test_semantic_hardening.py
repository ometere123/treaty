"""Final semantic-surface hardening tests."""

import json

from test_treaty import CONTRACT, LEADER_PROMPT, VALIDATOR_PROMPT, mock_consensus


DOMAIN = json.dumps({
    "topics": [
        {"topic": "auth.credential", "group": "authentication"},
        {"topic": "onboarding.identity", "group": "onboarding"},
    ],
    "dependencies": [{"left_group": "authentication", "right_group": "onboarding"}],
})


def deploy_policies(vm, deploy, alice, bob, a_constraints, b_constraints):
    vm.sender = alice
    contract = deploy(CONTRACT)
    domain = contract.create_domain("self-check", DOMAIN)
    a = contract.create_policy("A", domain, 1, json.dumps(a_constraints))
    with vm.prank(bob):
        b = contract.create_policy("B", domain, 1, json.dumps(b_constraints))
    vm.sender = alice
    assessment = contract.open_assessment(a, 1, b, 1)
    return contract, assessment


def test_internal_policy_conflict_is_incompatible(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, assessment = deploy_policies(
        direct_vm, direct_deploy, direct_alice, direct_bob,
        [{"topic": "auth.credential", "statement": "Only anonymous credentials may be used."},
         {"topic": "onboarding.identity", "statement": "Government identity verification is mandatory."}],
        [{"topic": "auth.credential", "statement": "Credentials are accepted."}],
    )
    mock_consensus(direct_vm, json.dumps({"relations": {
        "self:A:authentication<->onboarding": "CONFLICT",
        "authentication": "COMPATIBLE",
        "dependency:authentication<->onboarding": "COMPATIBLE",
    }}))
    contract.resolve_assessment(assessment)
    assert contract.get_assessment(assessment)["status_name"] == "INCOMPATIBLE"


def test_internal_policy_ambiguity_is_ambiguous(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, assessment = deploy_policies(
        direct_vm, direct_deploy, direct_alice, direct_bob,
        [{"topic": "auth.credential", "statement": "Credentials use an amount with no conversion rule."},
         {"topic": "onboarding.identity", "statement": "Identity checks apply."}],
        [{"topic": "auth.credential", "statement": "Credentials are accepted."}],
    )
    contract.resolve_assessment(assessment)
    assert contract.get_assessment(assessment)["status_name"] == "AMBIGUOUS"


def test_internal_policy_compatible_continues(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, assessment = deploy_policies(
        direct_vm, direct_deploy, direct_alice, direct_bob,
        [{"topic": "auth.credential", "statement": "Credentials must be authenticated."},
         {"topic": "onboarding.identity", "statement": "Identity checks are permitted."}],
        [{"topic": "auth.credential", "statement": "Credentials are accepted."}],
    )
    mock_consensus(direct_vm, json.dumps({"relations": {
        "self:A:authentication<->onboarding": "COMPATIBLE",
        "authentication": "COMPATIBLE",
        "dependency:authentication<->onboarding": "COMPATIBLE",
    }}))
    contract.resolve_assessment(assessment)
    assert contract.get_assessment(assessment)["status_name"] == "COMPATIBLE"


def test_no_self_check_for_unrelated_group(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, assessment = deploy_policies(
        direct_vm, direct_deploy, direct_alice, direct_bob,
        [{"topic": "auth.credential", "statement": "Only anonymous credentials may be used."}],
        [{"topic": "auth.credential", "statement": "Credentials are accepted."}],
    )
    mock_consensus(direct_vm, json.dumps({"relations": {"authentication": "COMPATIBLE"}}))
    contract.resolve_assessment(assessment)
    assert contract.get_assessment(assessment)["status_name"] == "COMPATIBLE"


def test_bilateral_unilateral_validator_result_is_rejected(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, assessment = deploy_policies(
        direct_vm, direct_deploy, direct_alice, direct_bob,
        [{"topic": "auth.credential", "statement": "Credentials are required."}],
        [{"topic": "auth.credential", "statement": "Credentials are accepted."}],
    )
    mock_consensus(direct_vm, json.dumps({"relation": "COMPATIBLE"}), json.dumps({"relation": "UNILATERAL_A"}))
    contract.resolve_assessment(assessment)
    assert direct_vm.run_validator() is False


def test_bilateral_unilateral_b_validator_result_is_rejected(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, assessment = deploy_policies(
        direct_vm, direct_deploy, direct_alice, direct_bob,
        [{"topic": "auth.credential", "statement": "Credentials are required."}],
        [{"topic": "auth.credential", "statement": "Credentials are accepted."}],
    )
    mock_consensus(direct_vm, json.dumps({"relation": "COMPATIBLE"}), json.dumps({"relation": "UNILATERAL_B"}))
    contract.resolve_assessment(assessment)
    assert direct_vm.run_validator() is False


def test_legacy_multi_group_model_response_is_rejected(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract, assessment = deploy_policies(
        direct_vm, direct_deploy, direct_alice, direct_bob,
        [{"topic": "auth.credential", "statement": "Credentials are required."}],
        [{"topic": "auth.credential", "statement": "Credentials are accepted."}],
    )
    mock_consensus(direct_vm, json.dumps({"groups": [], "overall": "COMPATIBLE"}))
    with direct_vm.expect_revert():
        contract.resolve_assessment(assessment)
