# Final StudioNet Deployment Evidence

- Final repository commit: `87b679dffea13640e75d23b52a6392b817724504`
- Deployed source commit: `87b679dffea13640e75d23b52a6392b817724504`
- Network: StudioNet
- Contract: `0x4f3710ea791458aBe1Fe1cE5D0bbBCc0CBdf098A`
- Deployer: `0xB5EcD6dDa36B370aca4af5E2005d8E2Ae89c6db2`
- Deployment tx: `0xa3ca4b5b7fbd0570dd028a2b702f61e46524af986a2acf8953926cb36409b47c`
- Deployment status: `FINALIZED / SUCCESS / MAJORITY_AGREE`

## Lifecycle receipts

The two policy owners were independent accounts: Alice `0xB5EcD6dDa36B370aca4af5E2005d8E2Ae89c6db2` and Bob `0xA7EeAE0E93793e3146Cb14b0700251B8b0ebadfb`.

- Domain creation: `0x6e7391fae167633f19986242a54932ffdeea5911eebc2469ff96faac7267081c`
- Alice policy: `0x2eae104554b8683d4c6c7eadbdf8d7e099ef1e5b98215b3e12169afecb606df8`
- Bob policy: `0xb43ce8b22599c281b41330ad0f940aefb80b8f26fa72f1b34fc95b14cc7f802c`

Compatible assessment 1:

- Open: `0x0b2f68f04bf5603fbe21fc2930dfcd8dca305a891d3e3f6e71d9d746be8b6b23`
- Resolve: `0xbffcecef7e0e4e0180a59dde2a47ca12c2b0e6ff48ec6001b72644e3ea00f0ae`
- Result: `FINALIZED / SUCCESS / MAJORITY_AGREE`, `COMPATIBLE`
- Reverse `get_cached_assessment(2,1,1,1)` returned assessment `1`.

Incompatible assessment 2:

- Open: `0x48219711ef5b7494322ef1b4caed2e89a3bc7df48685e963ff4d08127d6955a9`
- Resolve: `0xe1e2f3849754053745cccc1cd9dc8186b3c3b1626d7b4b4d0281e18e275154a7`
- Result: `FINALIZED / SUCCESS / MAJORITY_AGREE`, `INCOMPATIBLE`

Ambiguous assessment 3:

- Open: `0x4f45555a1fba88727732f4c4680fbf26ab83821df0efc47e10ef31f47da761a6`
- Resolve: `0x22d8d687cf73c1c7449e98feee11da9a37b08e47d26dcbc3c679c8bc0a3cae88`
- Result: `FINALIZED / SUCCESS / MAJORITY_AGREE`, `AMBIGUOUS`

Treaty 1:

- Proposal: `0xfa5f6ce42e9a08ab79231ac0fce3b211daef45717a92b905da75a1570c6d180f`; read showed `PROPOSED`, Alice ratified, Bob not ratified.
- Bob ratification: `0xd72bf944b7e454cf97f5037174abebce56f874e1dffc04361feba3575bd856db`
- Final state: `ACTIVE`; agreement hash `57d1ff4125370b18c6483746e716636f578f71d2810d80f366b94e58501d6764`.
- `is_treaty_active(1, wrong-agreement-hash)` returned `false`.

Supersession:

- Successor proposal: `0x303ff394325f266e445bed65d839de3b7da428a6fad16dd840f51fc3d03e4ccd`
- Bob ratification: `0x12615a264e548a6daf86cede271790cd29a914394d45e24904ccccb237b60e02`
- Parent `1` was `ACTIVE` after proposal and became `SUPERSEDED` only after the second ratification.
- Successor `2` became `ACTIVE`.
- Competing child attempt: `0xa36d90b0a95c3c989328d556cf21ead1351365fcde0254c04af513bc55a7dafd`; finalized with execution error `EXPECTED: parent treaty must be active`.

Machine-readable evidence is in [`artifacts/studionet_lifecycle.json`](../artifacts/studionet_lifecycle.json).
