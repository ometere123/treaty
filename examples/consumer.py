# Example only: how another Intelligent Contract can gate an action on Treaty.
# This file is documentation and is not a second deployable contract.


def consumer_pattern(treaty_contract, treaty_id, expected_agreement_hash):
    """Pseudocode integration pattern for a downstream Intelligent Contract."""
    if not treaty_contract.is_treaty_active(treaty_id, expected_agreement_hash):
        raise Exception("required bilateral treaty is not active")

    terms = treaty_contract.get_treaty_terms(treaty_id)

    # The consumer decides what to do next. Treaty deliberately stops at
    # semantic compatibility plus bilateral consent.
    return terms
