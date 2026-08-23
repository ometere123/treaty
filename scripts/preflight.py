#!/usr/bin/env python3
"""Deterministic repository preflight for Treaty."""

from __future__ import annotations

import ast
import pathlib
import py_compile
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "treaty.py"

REQUIRED_FILES = [
    ROOT / "README.md",
    ROOT / "SUBMISSION.md",
    ROOT / "contracts" / "treaty.py",
    ROOT / "docs" / "CONSENSUS.md",
    ROOT / "docs" / "SECURITY.md",
    ROOT / "examples" / "consumer.py",
    ROOT / "tests" / "direct" / "test_treaty.py",
    ROOT / "tests" / "direct" / "test_treaty_hardening.py",
]

REQUIRED_SOURCE_MARKERS = [
    "class Treaty(gl.Contract)",
    "class ITreaty",
    "gl.vm.run_nondet_unsafe",
    "assess_semantics_once",
    "build_validation_prompt",
    "class DomainVersion",
    "create_domain",
    "semantic_units",
    "assessment_cache",
    "canonical_pair",
    "policy_hash",
    "canonical_agreement_hash",
    "ratify_treaty",
    "TREATY_SUPERSEDED",
    "expected_agreement_hash",
]

FORBIDDEN_REPO_DIRS = ["frontend", "backend", "server", "api"]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    checks = 0
    for path in REQUIRED_FILES:
        checks += 1
        if not path.is_file():
            fail(f"missing required file: {path.relative_to(ROOT)}")

    for name in FORBIDDEN_REPO_DIRS:
        checks += 1
        if (ROOT / name).exists():
            fail(f"contract-only submission must not contain /{name}")

    try:
        py_compile.compile(str(CONTRACT), doraise=True)
    except Exception as exc:
        fail(f"contract does not compile as Python syntax: {exc}")
    checks += 1

    source = CONTRACT.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        fail(f"AST parse failed: {exc}")
    checks += 1

    for marker in REQUIRED_SOURCE_MARKERS:
        checks += 1
        if marker not in source:
            fail(f"missing source invariant marker: {marker}")

    for bad in ("TODO", "FIXME", "pass  # placeholder", "mock compatibility"):
        checks += 1
        if bad.lower() in source.lower():
            fail(f"unfinished source marker found: {bad}")

    for forbidden in ("@gl.public.write.payable", "gl.message.value", ".emit().transfer"):
        checks += 1
        if forbidden in source:
            fail(f"unexpected money-moving surface: {forbidden}")

    checks += 1
    if source.count("gl.nondet.exec_prompt") != 2:
        fail("expected exactly two bounded semantic LLM call sites (leader and source-grounded validator)")

    checks += 1
    if source.count("gl.vm.run_nondet_unsafe") != 1:
        fail("expected exactly one custom consensus block")

    checks += 1
    if "payload[:" in source or "source[:" in source:
        fail("semantic source must never be silently truncated")

    class_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}
    checks += 1
    if "Treaty" not in class_names:
        fail("Treaty contract class missing")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for phrase in ("no invented compromise", "bilateral ratification", "no frontend", "run_nondet_unsafe", "immutable policy versions"):
        checks += 1
        if phrase.lower() not in readme.lower():
            fail(f"README missing reviewer-facing concept: {phrase}")

    print(f"PASS: Treaty preflight ({checks} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
