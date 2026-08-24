#!/usr/bin/env python
"""Report rendered JSON size of each IAM policy file against the AWS 6144-byte limit."""
import glob
import json
import sys
from typing import Any

import yaml

AWS_LIMIT = 6144
THRESHOLD = 6124  # 20-byte buffer, matches test-policies.yml


def render_policy(path: str, region: str = 'us-east-1', account_id: str = '123456789012') -> str:
    """Render a policy YAML template to JSON, substituting placeholder variables."""
    with open(path) as f:
        content = f.read()
    content = content.replace('{{ aws_region }}', region)
    content = content.replace('{{ aws_account_id }}', account_id)
    policy: dict[str, Any] = yaml.safe_load(content)
    return json.dumps(policy)


def main() -> int:
    """Check all policy files and report their rendered sizes."""
    paths = glob.glob('aws/policy/*.yaml')
    if not paths:
        print('No policy files found', file=sys.stderr)
        return 1

    has_error = False
    for path in sorted(paths):
        rendered = render_policy(path)
        size = len(rendered)
        remaining = AWS_LIMIT - size
        pct = size / AWS_LIMIT * 100

        if size > THRESHOLD:
            status = 'OVER' if size > AWS_LIMIT else 'TIGHT'
            has_error |= size > AWS_LIMIT
        elif remaining < 500:
            status = 'WARN'
        else:
            status = 'OK'

        bar_len = 40
        filled = int(bar_len * size / AWS_LIMIT)
        bar = '#' * filled + '-' * (bar_len - filled)

        print(f'  {status:5s} [{bar}] {size:5d}/{AWS_LIMIT} ({remaining:+5d} remaining)  {path}')

    print()
    print(f'  Limit: {AWS_LIMIT} bytes | Threshold: {THRESHOLD} bytes')
    return 1 if has_error else 0


if __name__ == '__main__':
    sys.exit(main())
