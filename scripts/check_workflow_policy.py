#!/usr/bin/env python3
"""YAML-aware workflow policy check. Exits 1 on a real violation.

Usage: python3 scripts/check_workflow_policy.py [allowlist_file] [--strict-pins]

Allowlist format: `<workflow> <rule> expires YYYY-MM-DD`
Rules: trigger, permissions, writes:<scope>, pins
Each exception applies ONLY to its named rule — never to all rules.
"""
from __future__ import annotations
import sys, re, datetime
from pathlib import Path

try:
    from ruamel.yaml import YAML
except ImportError:
    print('ERROR: ruamel.yaml required', file=sys.stderr)
    raise SystemExit(2)

WF = sorted(Path('.github/workflows').glob('*.yml')) + sorted(Path('.github/workflows').glob('*.yaml'))
allow_path = Path(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else Path('.github/policy-allowlist.txt')
strict_pins = '--strict-pins' in sys.argv
allow: dict[tuple[str, str], str] = {}
if allow_path.exists():
    for line in allow_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        m = re.match(r'^(\S+)\s+(\S+)\s+expires\s+(\d{4}-\d{2}-\d{2})$', line)
        if m:
            allow[(m.group(1), m.group(2))] = m.group(3)

today = datetime.date.today().isoformat()
def excepted(base: str, rule: str) -> bool:
    exp = allow.get((base, rule))
    return exp is not None and exp >= today

yam = YAML(typ='safe')
violations = []
for f in WF:
    base = f.name
    try:
        d = yam.load(f.read_text())
    except Exception as e:
        violations.append(f'{base}: YAML parse failed: {str(e)[:100]}')
        continue
    if not isinstance(d, dict):
        violations.append(f'{base}: top level is not a mapping')
        continue
    trig = d.get(True, d.get('on', {}))
    keys = list(trig.keys()) if isinstance(trig, dict) else [trig]
    if 'pull_request_target' in keys and not excepted(base, 'trigger'):
        violations.append(f'{base}: pull_request_target trigger blocked')
    perms = d.get('permissions')
    if perms is None and not excepted(base, 'permissions'):
        violations.append(f'{base}: missing top-level permissions')
    if isinstance(perms, dict):
        if str(perms.get('write-all', '')).lower() == 'true':
            violations.append(f'{base}: permissions write-all blocked')
        for k, v in perms.items():
            if str(v).lower() == 'write' and not excepted(base, f'writes:{k}'):
                violations.append(f'{base}: write scope {k} needs a dated exception')
    for job in (d.get('jobs') or {}).values():
        for step in (job or {}).get('steps', []) or []:
            uses = step.get('uses')
            if not uses:
                continue
            ref = str(uses).split('@')[-1].split(' ')[0]
            if not re.fullmatch(r'[0-9a-f]{40}', ref):
                if strict_pins:
                    violations.append(f'{base}: action not SHA-pinned: {uses}')
                else:
                    print(f'PIN-ADVISORY {base}: {uses}')

if violations:
    print('POLICY FAILED:')
    for v in violations:
        print(' -', v)
    raise SystemExit(1)
print(f'POLICY OK: {len(WF)} workflows checked')
