#!/usr/bin/env python3
"""Read-only audit of this repository's effective GitHub ruleset.

Requires an authenticated GitHub CLI with permission to see bypass actors.
This script cannot install, relax, or bypass rules. API errors and incomplete
visibility are failures, not evidence that a gate exists. A configuration audit
is not a negative merge experiment or a proof of document semantics.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / ".github/rulesets/main.json"


def validate_ruleset(actual: dict, expected: dict) -> list[str]:
    """Compare all authored constraints; ignore server-owned metadata/defaults."""
    errors: list[str] = []

    def check(value, requirement, path):
        if type(value) is not type(requirement):
            errors.append(f"{path}: missing or wrong type")
        elif isinstance(requirement, dict):
            for key, item in requirement.items():
                check(value.get(key), item, f"{path}.{key}")
        elif isinstance(requirement, list):
            if path == "ruleset.rules":
                found = {r.get("type"): r for r in value if isinstance(r, dict)}
                if len(found) != len(value):
                    errors.append(f"{path}: invalid or duplicate rule types")
                for item in requirement:
                    check(found.get(item["type"]), item, f"{path}.{item['type']}")
            elif sorted(map(lambda x: json.dumps(x, sort_keys=True), value)) != sorted(
                map(lambda x: json.dumps(x, sort_keys=True), requirement)
            ):
                errors.append(f"{path}: differs from committed policy")
        elif value != requirement:
            errors.append(f"{path}: differs from committed policy")

    check(actual, expected, "ruleset")
    return errors


def api(endpoint: str, *, paginate: bool = False):
    args = ["gh", "api", endpoint]
    if paginate:
        args += ["--paginate", "--slurp"]
    result = subprocess.run(args, capture_output=True, text=True, timeout=45)
    if result.returncode:
        raise RuntimeError(f"GitHub read failed for {endpoint}; verify CLI access")
    return json.loads(result.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default="yooyea/rsi-base")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repository):
        parser.error("repository must be owner/name")
    try:
        expected = json.loads(POLICY.read_text(encoding="utf-8"))
        prefix = f"repos/{args.repository}"
        pages = api(f"{prefix}/rulesets?includes_parents=true&per_page=100", paginate=True)
        matches = [r for page in pages for r in page if r.get("name") == expected["name"]]
        if len(matches) != 1:
            raise RuntimeError("Expected exactly one matching ruleset; configuration not verified")
        actual = api(f"{prefix}/rulesets/{matches[0]['id']}")
        errors = validate_ruleset(actual, expected)
        repository = api(prefix)
        branch = repository["default_branch"]
        active_pages = api(f"{prefix}/rules/branches/{branch}?per_page=100", paginate=True)
        active_types = {r["type"] for page in active_pages for r in page
                        if r.get("ruleset_id") == actual["id"]}
        if not {r["type"] for r in expected["rules"]} <= active_types:
            errors.append("ruleset is not fully effective on the default branch")
        if errors:
            print("\n".join(errors))
            return 1
        print(f"Verified active ruleset {actual['id']} on {args.repository}:{branch}; "
              "no bypass actors, required PR and expected status provider/configuration.")
        print("Scope: configuration only; merge rejection requires a separate isolated probe.")
        return 0
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"Repository rules NOT verified: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
