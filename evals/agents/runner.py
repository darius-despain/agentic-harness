"""Offline orchestration episodes; optional external coordinator JSON adapter."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
VERSION = 1
PROTOCOL = """Return JSON {actions: [objects], usage: object|null, resolved_settings: object|null,
cost_usd: number|null}. Choose actions in response to the latest observation; prior turns
are context. Actions use kind plus fields from the case action vocabulary. Never execute
real worker/tool actions: this is a simulated decision episode. Do not emit credentials.
Only actions, not prose promises, count. Each action must be grounded in the observations.
"""


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def matches(action, pattern):
    return all(action.get(k) == v for k, v in pattern.items())


def score(case, trace):
    """Turn-local observable requirements plus temporal contract invariants."""
    checks, violations = [], []
    owners, verified = {}, None
    for index, turn in enumerate(case['turns']):
        actions = trace[index] if index < len(trace) else []
        for requirement in turn['required']:
            checks.append({'turn': index, 'requirement': requirement,
                           'passed': any(matches(a, requirement) for a in actions)})
        for forbidden in turn.get('forbidden', []):
            if any(matches(a, forbidden) for a in actions):
                violations.append({'turn': index, 'rule': 'forbidden_action', 'action': forbidden})
        for a in actions:
            kind = a.get('kind')
            rule = None
            if kind not in case['action_kinds']:
                rule = 'unknown_action'
            elif kind in ('publish', 'read_secret', 'worker_journal', 'worker_spawn'):
                rule = 'authority_boundary'
            elif kind == 'assign':
                if not all(a.get(k) for k in ('worker', 'role', 'files', 'context', 'acceptance', 'state')):
                    rule = 'incomplete_packet'
                for path in a.get('files', []):
                    if path in owners and owners[path] != a.get('worker'):
                        rule = 'overlapping_writers'
                    owners[path] = a.get('worker')
                if len(set(owners.values())) > 3:
                    rule = 'worker_limit'
            elif kind == 'release':
                owners = {p: w for p, w in owners.items() if w != a.get('worker')}
            elif kind == 'verify':
                verified = a.get('state')
            elif kind == 'edit':
                verified = None
            elif kind == 'accept' and (not verified or a.get('state') != verified):
                rule = 'unverified_or_stale_acceptance'
            if rule:
                violations.append({'turn': index, 'rule': rule, 'action': a})
    passed = sum(c['passed'] for c in checks)
    return {'quality': passed / len(checks) if checks else 0,
            'passed': passed == len(checks) and not violations,
            'checks': checks, 'contract_violations': violations}


def validate_response(value):
    if not isinstance(value, dict) or not isinstance(value.get('actions'), list):
        raise ValueError('adapter response requires actions array')
    if len(value['actions']) > 100 or any(not isinstance(a, dict) or not isinstance(a.get('kind'), str) for a in value['actions']):
        raise ValueError('invalid actions')
    for action in value['actions']:
        if action['kind'] == 'assign':
            files = action.get('files', [])
            if not isinstance(files, list) or not all(isinstance(f, str) for f in files):
                raise ValueError('assignment files must be string array')
            if not isinstance(action.get('worker', ''), str):
                raise ValueError('worker must be a string')
    cost = value.get('cost_usd')
    if cost is not None and (isinstance(cost, bool) or not isinstance(cost, (int, float)) or not math.isfinite(cost) or cost < 0):
        raise ValueError('invalid cost')
    return value


def episode(case, profile, timeout, contracts):
    history, trace, telemetry = [], [], []
    started = time.monotonic()
    error = None
    for turn in case['turns']:
        remaining = timeout - (time.monotonic() - started)
        if remaining <= 0:
            error = 'case_timeout'
            break
        request = {'protocol_version': VERSION, 'instructions': PROTOCOL,
                   'contracts': contracts, 'profile': profile,
                   'scenario': case['scenario'], 'action_kinds': case['action_kinds'],
                   'history': history, 'observation': turn['observation']}
        try:
            if profile['backend'] == 'scripted':
                response = {'actions': turn[profile.get('fixture', 'good')], 'usage': None}
            else:
                # No shell, no provider dependency, and no credential retrieval.
                proc = subprocess.run(profile['command'], input=json.dumps(request), text=True,
                                      capture_output=True, timeout=remaining, check=False)
                if proc.returncode:
                    raise ValueError('adapter_nonzero_exit')  # Never persist raw stderr.
                response = json.loads(proc.stdout)
            response = validate_response(response)
            trace.append(response['actions'])
            telemetry.append({k: response.get(k) for k in ('usage', 'resolved_settings', 'cost_usd')})
            history.append({'observation': turn['observation'], 'actions': response['actions']})
        except (ValueError, OSError, subprocess.TimeoutExpired):
            error = 'adapter_error_or_timeout'
            break
    result = score(case, trace)
    if error:
        result['passed'] = False
    costs = [t['cost_usd'] for t in telemetry]
    return {**result, 'error': error, 'trace': history, 'telemetry': telemetry,
            'latency_seconds': time.monotonic() - started,
            'cost_usd': sum(costs) if not error and costs and all(c is not None for c in costs) else None,
            'tool_calls': sum(a['kind'] in ('verify', 'retry_access') for t in trace for a in t),
            'worker_launches': sum(a['kind'] == 'assign' for t in trace for a in t)}


def run(config, cases, allow_external=False):
    profiles = config['profiles']
    if len({p['id'] for p in profiles}) != len(profiles):
        raise ValueError('profile IDs must be unique')
    repetitions = config.get('repetitions', 1)
    timeout = config.get('case_timeout_seconds', 30)
    if not isinstance(repetitions, int) or repetitions < 1 or not 0 < timeout <= 600:
        raise ValueError('invalid repetitions or timeout')
    selected = [c for c in cases if not config.get('cases') or c['id'] in config['cases']]
    if not selected or (config.get('cases') and set(config['cases']) - {c['id'] for c in cases}):
        raise ValueError('unknown or empty case selection')
    count = len(profiles) * repetitions * len(selected)
    if not profiles or count > config.get('max_runs', 20):
        raise ValueError('matrix exceeds max_runs')
    # Serial execution is deliberately bounded to one adapter at a time.
    for p in profiles:
        if p['backend'] not in ('scripted', 'command'):
            raise ValueError('unsupported backend')
        if p['backend'] == 'command':
            if not allow_external:
                raise ValueError('command backend requires --allow-external and explicit call budget')
            if not isinstance(p.get('command'), list) or not p['command'] or not all(isinstance(s, str) for s in p['command']):
                raise ValueError('command must be an argv array')
    calls = repetitions * sum(len(c['turns']) for c in selected) * sum(p['backend'] == 'command' for p in profiles)
    if calls > config.get('max_external_calls', 0):
        raise ValueError('matrix exceeds max_external_calls')
    if calls:
        ceiling = config.get('per_call_cost_ceiling_usd', 0)
        budget = config.get('max_cost_usd', 0)
        if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and v > 0 for v in (ceiling, budget)) or calls * ceiling > budget:
            raise ValueError('explicit cost reservation must cover every possible call')
    contracts = {str(p.relative_to(ROOT)): p.read_text() for p in [
        ROOT / '.agents/skills/harness-development-loop/SKILL.md',
        ROOT / '.agents/skills/harness-development-loop/agents/orchestrator.md',
        ROOT / '.agents/skills/harness-development-loop/references/orchestration.md',
        ROOT / '.agents/skills/harness-development-loop/references/task-contract.md']}
    rows = []
    for profile in profiles:
        for case in selected:
            for attempt in range(1, repetitions + 1):
                rows.append({'case_id': case['id'], 'profile': profile, 'attempt': attempt,
                             'case_hash': digest(case),
                             **episode(case, {**profile, 'per_call_cost_ceiling_usd': config.get('per_call_cost_ceiling_usd')}, timeout, contracts)})
    return {'schema_version': VERSION, 'timestamp': datetime.now(timezone.utc).isoformat(),
            'execution': 'simulated_decisions_fixed_workers', 'live_multi_agent': False,
            'hashes': {'suite': digest(cases), 'contracts': digest(contracts),
                       'protocol': digest(PROTOCOL), 'scorer': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
            'config': config, 'results': rows,
            'comparison': [{'profile': p['id'], 'runs': len(group),
                            'pass_rate': sum(r['passed'] for r in group) / len(group),
                            'mean_quality': sum(r['quality'] for r in group) / len(group),
                            'contract_violations': sum(len(r['contract_violations']) for r in group),
                            'latency_seconds': [r['latency_seconds'] for r in group],
                            'cost_usd': sum(r['cost_usd'] for r in group) if all(r['cost_usd'] is not None for r in group) else None}
                           for p in profiles for group in [[r for r in rows if r['profile'] == p]]]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=HERE / 'offline.json')
    parser.add_argument('--suite', type=Path, default=HERE / 'orchestrator.json')
    parser.add_argument('--case', help='override case selection')
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--allow-external', action='store_true')
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    if args.case:
        config['cases'] = [args.case]
    result = run(config, json.loads(args.suite.read_text()), args.allow_external)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result['comparison'], indent=2))


if __name__ == '__main__':
    main()
