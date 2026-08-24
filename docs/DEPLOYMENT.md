# StudioNet deployment and lifecycle evidence

## Final source deployment

- Final source commit: `b1cfe0f`
- Contract: `0x16238CD12aae247b8E985d63C317BC6cb18c57A4`
- Network: StudioNet (`https://studio.genlayer.com/api`)
- Deployer: `0xB5EcD6dDa36B370aca4af5E2005d8E2Ae89c6db2`
- Deployment transaction: `0x352cf0f047db56393328e2da3ebe6eca06fa17df9af6c8ef8002c14bbbf2e641`
- Final status: `FINALIZED`
- Execution: `SUCCESS`
- Consensus: `MAJORITY_AGREE`

## Verified final-source lifecycle evidence

The following writes were executed against the address above with two independent StudioNet accounts:

- Domain creation: `0x2716ed8719a3ff86f149639b7813344b1c2a237af51644a5d14122eb262f80dd`
- Alice policy: `0xf8a04b31d9b3547d7adb7a2b610eeda60ccb5d82bda5bdad70eb2f879ce7479a`
- Bob policy: `0x0120298a556f01380d1943629514f5294281d7c4c0e62757af552df9556f72ec`
- Assessment open: `0x14bcaebab4201897987bb08fde60603b7361894dd410530bfd1320802ce16929`
- Compatible resolution: `0xabd96ddadc9b90182e45bac790f467a160e5f23ed3e61bee4305f6d099e3279a`
- Reverse-order cache open: `0x57fddfe83c301698db0f853834c337b4fcd7aa4c9911e5be0779fc239925d78b`

The final compatible read returned `COMPATIBLE`; reverse cache returned assessment ID `1`. The final treaty proposal was `0xca07ec3cc605b41754edd320a52d12d81455df1f87d827795a81b2808bc470f0`, and Bob’s independent ratification was `0x9d5aa0dbd68c4734a101d6c77a88eafcf45b28840634904ff24171b761d35523`. The final read returned treaty `1` as `ACTIVE`, with agreement hash `815647de95e1edee728101da9fe0957e40b968c94c15e20367ed1399a6657cb6` and `effective_active=true`.

## Evidence boundary

Earlier deployments and the earlier `MAJORITY_DISAGREE` semantic-resolution attempt are historical only. The final-source incompatible, ambiguous, supersession, and pause lifecycle cases were not completed in this run because the CLI keychain stopped exposing the existing account keys and requested an unavailable password. No substitute or fabricated evidence is claimed.
