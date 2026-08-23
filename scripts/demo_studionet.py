#!/usr/bin/env python3
"""Execute and record Treaty’s two-account StudioNet lifecycle.

This runner delegates signing to the installed GenLayer CLI. It never accepts,
prints, or stores keys/passwords. The two account names must already exist and
be unlocked in the CLI keychain.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys
from datetime import datetime, timezone


ROOT = pathlib.Path(__file__).resolve().parents[1]
TX_RE = re.compile(r"0x[0-9a-fA-F]{64}")
DOMAIN = {
    "topics": [
        {"topic": "commercial.price", "group": "commercial-payment"},
        {"topic": "identity.email", "group": "identity-data"},
        {"topic": "identity.pii", "group": "identity-data"},
        {"topic": "execution.delivery", "group": "execution"},
        {"topic": "refund.failure", "group": "refund"},
    ],
    "dependencies": [],
}
BUYER = [
    {"topic": "commercial.price", "statement": "Total price must not exceed 50 USD."},
    {"topic": "identity.pii", "statement": "Customer personally identifiable information must never be disclosed."},
    {"topic": "refund.failure", "statement": "A full refund is required when execution never begins."},
]
SELLER = [
    {"topic": "commercial.price", "statement": "Price must be between 40 USD and 45 USD."},
    {"topic": "identity.email", "statement": "The service must operate without receiving customer PII."},
    {"topic": "execution.delivery", "statement": "Delivery completes within 300 seconds."},
]
INCOMPATIBLE = [
    {"topic": "commercial.price", "statement": "Price must be at least 60 USD."},
]


class Demo:
    def __init__(self, contract: str, alice: str, bob: str):
        self.contract = contract
        self.alice = alice
        self.bob = bob
        self.account = None
        self.transactions = []
        self.reads = {}

    def cli(self, *args: str, account: str | None = None) -> str:
        if account is not None and account != self.account:
            self.run("account", "use", account)
            self.account = account
        command = ["genlayer", *args]
        print("+", " ".join(command), flush=True)
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
        output = (result.stdout or "") + (result.stderr or "")
        print(output, end="", flush=True)
        if result.returncode != 0:
            raise RuntimeError(f"command failed: {' '.join(command)}")
        return output

    def run(self, *args: str) -> str:
        return self.cli(*args)

    def write(self, label: str, method: str, args: list[object], account: str) -> str:
        rendered = [json.dumps(value, separators=(",", ":")) if isinstance(value, (dict, list)) else str(value) for value in args]
        output = self.cli("write", self.contract, method, "--args", *rendered, account=account)
        matches = TX_RE.findall(output)
        if not matches:
            raise RuntimeError(f"no transaction hash returned for {label}")
        tx = matches[0]
        finality = self.cli("receipt", tx, "--status", "FINALIZED", account=account)
        if "FINALIZED" not in finality.upper():
            raise RuntimeError(f"{label} did not reach explicit FINALIZED status")
        if "SUCCESS" not in finality.upper() and "FINISHED_WITH_RETURN" not in finality.upper():
            raise RuntimeError(f"{label} finalized without a verified successful execution")
        self.transactions.append({"label": label, "tx": tx, "account": account, "finality": "FINALIZED"})
        return tx

    def read(self, label: str, method: str, args: list[object], account: str) -> str:
        rendered = [str(value) for value in args]
        output = self.cli("call", self.contract, method, "--args", *rendered, account=account)
        self.reads[label] = output
        return output

    def execute(self) -> dict:
        self.run("network", "set", "studionet")
        self.run("account", "show")
        self.write("domain creation", "create_domain", ["Agent Service", DOMAIN], self.alice)
        self.write("Alice policy", "create_policy", ["Alice Buyer", 1, 1, BUYER], self.alice)
        self.write("Bob policy", "create_policy", ["Bob Seller", 1, 1, SELLER], self.bob)
        self.write("compatible assessment open", "open_assessment", [1, 1, 2, 1], self.alice)
        self.write("compatible assessment resolve", "resolve_assessment", [1], self.alice)
        self.read("compatible assessment", "get_assessment", [1], self.alice)
        self.read("reverse cache", "get_cached_assessment", [2, 1, 1, 1], self.bob)
        self.write("treaty proposal", "propose_treaty", [1, 0, 0], self.alice)
        self.read("proposed treaty", "get_treaty", [1], self.alice)
        self.write("Bob ratification", "ratify_treaty", [1], self.bob)
        active = self.read("active treaty", "get_treaty", [1], self.bob)
        self.write("incompatible policy", "create_policy", ["Bob Conflict", 1, 1, INCOMPATIBLE], self.bob)
        self.write("incompatible assessment open", "open_assessment", [1, 1, 3, 1], self.alice)
        self.write("incompatible assessment resolve", "resolve_assessment", [2], self.alice)
        self.read("incompatible assessment", "get_assessment", [2], self.alice)
        self.write("successor proposal", "propose_treaty", [1, 0, 1], self.alice)
        self.read("parent while successor proposed", "get_treaty", [1], self.alice)
        self.write("successor ratification", "ratify_treaty", [2], self.bob)
        self.read("superseded parent", "get_treaty", [1], self.bob)
        self.read("active successor", "get_treaty", [2], self.bob)
        evidence = {
            "network": "studionet",
            "contract": self.contract,
            "accounts": {"alice": self.alice, "bob": self.bob},
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "transactions": self.transactions,
            "reads": self.reads,
            "expected": {
                "compatible_assessment": "COMPATIBLE",
                "reverse_cache": 1,
                "proposal": "PROPOSED",
                "active_treaty": "ACTIVE",
                "incompatible_assessment": "INCOMPATIBLE",
                "parent_after_successor": "SUPERSEDED",
                "successor": "ACTIVE",
            },
        }
        output = ROOT / "artifacts" / "studionet_lifecycle.json"
        output.parent.mkdir(exist_ok=True)
        output.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
        print(f"Evidence written to {output}")
        return evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", required=True)
    parser.add_argument("--alice", default="termsmet-studionet-submitter")
    parser.add_argument("--bob", default="party_b")
    args = parser.parse_args()
    Demo(args.contract, args.alice, args.bob).execute()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
