#!/usr/bin/env python3
"""Deploy Treaty to GenLayer Studionet using the active CLI account.

This helper never accepts, reads, stores, or prints a private key/password.
Configure and unlock the desired GenLayer CLI account before running it.
"""

from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "treaty.py"
PREFLIGHT = ROOT / "scripts" / "preflight.py"
STUDIONET_RPC = "https://studio.genlayer.com/api"


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    completed = subprocess.run(command, cwd=ROOT, check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> int:
    cli = shutil.which("genlayer")
    if cli is None:
        print("ERROR: genlayer CLI is not installed or is not on PATH.", file=sys.stderr)
        return 2

    run([sys.executable, str(PREFLIGHT)])
    run([cli, "account", "show"])
    run([cli, "deploy", "--contract", str(CONTRACT), "--rpc", STUDIONET_RPC])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
