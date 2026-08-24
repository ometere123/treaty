# StudioNet deployment and lifecycle evidence

## Final source and deployment

- Final source commit: `f3dd2c4e0d17f9f580b231eb231253c49fd979d4`
- Contract: `0xd11310Fd37C99700075bA0F49870730cb128e0b6`
- Network: StudioNet (`https://studio.genlayer.com/api`)
- Deployer: `0xB5EcD6dDa36B370aca4af5E2005d8E2Ae89c6db2` (`termsmet-studionet-submitter`)
- Deployment transaction: `0x03dd39eee8cd53a5b8be9e60fe673e7489253b28ff34407fe25d363989295718`
- Final status: `FINALIZED`
- Execution: `SUCCESS`
- Consensus: `MAJORITY_AGREE`

The deployment was performed after the final contract-source change. Prior addresses are historical only and are not canonical.

## Lifecycle attempt

The real runner is `scripts/demo_studionet.py`; it uses independent local accounts and checks `FINALIZED` receipts. On the final deployment, these writes finalized successfully before semantic resolution:

- Domain creation: `0x839a45af5d728150c3908da3f05cf68733d6142e5d515a656eaf2aaf95537cc9`
- Alice policy: `0x183d0b63ba9a2b42ecabc855956ff5bc149e375438f878d45c2e0300400615ab`
- Bob policy: `0xd56c28c0f41a8ab30add72e7b31fc7dfe4100f2d817d63683951f4b61d373fdf`
- Assessment open: `0xecbc6a8dfbbd90a580c2dc7e6a455d75bba99141e493e1153c2a52cf690f61a9`

Compatibility resolution `0xd365a7b56f553c91b4eaef1f5c9c8d21b7e217003875a3fabebd3ebbae2f26ad` reached `FINALIZED`, but StudioNet reported `UNDETERMINED` (`MAJORITY_DISAGREE`) because all non-idle validators rejected the leader proposal. No compatible assessment, treaty, or supersession proof is claimed from this run.

This was reproduced on three fresh deployments. The receipts show successful leader execution and validator-side rejection; the limitation is current StudioNet validator behavior, not a substituted local or simulated result. The machine-readable artifact records the deployment and blocked lifecycle attempt without secrets.
