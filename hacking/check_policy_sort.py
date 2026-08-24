#!/usr/bin/env python
"""Check that Action lists in IAM policy YAML files are sorted alphabetically (case-insensitive)."""
import glob
import sys
from typing import Any

import yaml


def check_file(path: str) -> list[str]:
    """Validate that every Action list in a policy file is sorted case-insensitively."""
    errors: list[str] = []
    with open(path) as f:
        policy: dict[str, Any] = yaml.safe_load(f)

    for statement in policy.get('Statement', []):
        sid: str = statement.get('Sid', '<no Sid>')
        actions: list[str] | str = statement.get('Action', [])
        if isinstance(actions, str):
            continue
        sorted_actions: list[str] = sorted(actions, key=str.casefold)
        if actions != sorted_actions:
            out_of_order: list[str] = []
            for actual, expected in zip(actions, sorted_actions):
                if actual != expected:
                    out_of_order.append(f'    {actual}')
            errors.append(
                f'{path}: statement "{sid}" has unsorted actions:\n'
                + '\n'.join(out_of_order)
            )
    return errors


def main() -> int:
    """Check all policy files and report any unsorted action lists."""
    paths: list[str] = glob.glob('aws/policy/*.yaml')
    if not paths:
        print('No policy files found', file=sys.stderr)
        return 1

    all_errors: list[str] = []
    for path in sorted(paths):
        all_errors.extend(check_file(path))

    if all_errors:
        print('Policy action sort errors:\n', file=sys.stderr)
        for error in all_errors:
            print(error, file=sys.stderr)
        print(f'\nFound {len(all_errors)} unsorted action list(s).', file=sys.stderr)
        return 1

    print(f'All action lists in {len(paths)} policy files are sorted.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
