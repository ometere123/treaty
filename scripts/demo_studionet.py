#!/usr/bin/env python3
"""Run a reviewer-facing Treaty lifecycle against the active CLI account.

The script delegates signing and receipt polling to the GenLayer CLI. It never
accepts or prints keys/passwords. A second account must be selected explicitly
by the operator for bilateral ratification; the script never fabricates one.
"""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess


ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = "0x3bBC68Fb2863EF1a362298d6d6941df1506418BC"
BUYER = json.dumps([
    {"topic": "data.pii", "statement": "Customer PII must never be disclosed."},
    {"topic": "delivery.seconds", "statement": "Delivery must complete within 600 seconds."},
    {"topic": "price.usd", "statement": "Total price must not exceed 50 USD."},
])
SELLER = json.dumps([
    {"topic": "data.pii", "statement": "The service must operate without customer PII."},
    {"topic": "delivery.seconds", "statement": "Delivery completes within 300 seconds."},
    {"topic": "price.usd", "statement": "Price must be between 40 USD and 45 USD."},
])
INCOMPATIBLE = json.dumps([
    {"topic": "price.usd", "statement": "Price must be at least 60 USD."},
])


def run(*args: str) -> None:
    cli = shutil.which("genlayer")
    if cli is None:
        raise SystemExit("genlayer CLI is not on PATH")
    command = [cli, *args]
    print("+", " ".join(command), flush=True)
    completed = subprocess.run(command, cwd=ROOT, check=False)
    if completed.returncode:
        raise SystemExit(completed.returncode)


def main() -> int:
    run("network", "set", "studionet")
    run("account", "show")
    print("Create the buyer and seller policies with the CLI write command, then:")
    print("  genlayer write", CONTRACT, "open_assessment --args <buyer_id> 1 <seller_id> 1")
    print("  genlayer write", CONTRACT, "resolve_assessment --args <assessment_id>")
    print("Repeat open_assessment with reversed IDs to prove cache reuse.")
    print("A second independent unlocked account must ratify; never use one account for both owners.")
    print("Buyer JSON:", BUYER)
    print("Seller JSON:", SELLER)
    print("Incompatible JSON:", INCOMPATIBLE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
