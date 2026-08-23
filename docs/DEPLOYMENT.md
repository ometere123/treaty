# StudioNet Deployment

This evidence records only operations actually verified against StudioNet.

Network: GenLayer Studio Network (`studionet`)

RPC: `https://studio.genlayer.com/api`

Contract address: `0x3bBC68Fb2863EF1a362298d6d6941df1506418BC`

Deployer: `0xB5EcD6dDa36B370aca4af5E2005d8E2Ae89c6db2`

Deployment transaction: `0xfed2b8183d687bd9c1bc5de10f480b921f693c396e1ee58fac86e82f4f046a1f`

Deployment status: StudioNet receipt status `0x1`; GenLayer execution result `SUCCESS`; consensus result `MAJORITY_AGREE`; one round; five votes revealed.

Source commit used: `af65483` plus the local test-harness assertion and deployment-tooling changes in the final commit.

The transaction receipt also returned the deployed contract address and no execution error. The address above is the canonical address for this repository’s deployed instance.

## Live lifecycle

No policy, assessment, treaty, or successor transaction is claimed here yet. The active CLI account was verified, but the CLI wrapper did not remain callable across the desktop shell boundary after deployment. `scripts/demo_studionet.py` provides the reproducible, credential-free command sequence for the lifecycle; receipts must be appended here only after those writes are actually finalized and inspected.

## Local proof

- `python scripts/preflight.py`: 40 checks passed.
- `python -m pytest tests/direct/ -v`: 21 tests passed.
- `genvm-lint check contracts/treaty.py --json`: `ok: true`, 17 methods.
