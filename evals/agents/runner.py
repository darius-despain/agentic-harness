"""Offline orchestration episodes; optional external coordinator JSON adapter."""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path
import subprocess
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
VERSION = 2
PROTOCOL = """Return JSON {actions: [objects], usage: object|null, resolved_settings: object|null,
cost_usd: number|null}. Choose actions in response to the latest observation; prior turns
are context. Actions use kind plus fields from the case action vocabulary. Never execute
real worker/tool actions: this is a simulated decision episode. Do not emit credentials.
Only actions, not prose promises, count. Each action must be grounded in the observations.
Scope supplies mode, track, allowed/locked files and required checks. Paths are relative
to /workspace/repo. Initial assignments use state S0, model sol, fresh_context true;
implementer/verifier use medium, investigator high, cleanup low reasoning. Assign fields:
worker, role, files, context, acceptance, state, model, reasoning, fresh_context.
Release the active slot before another assign or correct; correct resumes the original
implementer without a spawn. Reframe uses questions (2-3 strings). Verify uses worker,
state and receipt (five strings: track/verdict/diff_safety/guard_staged, syntax, tests,
service_health, user_flows). Check lines use pass: or NA: with reasons; tests include
exit=0/count=N from the observation. Cleanup uses save_patch(path,files,verified),
restore/remove(files,baseline_preserved), cleanup_result(status,baseline_preserved,
receipt:3 strings), release, pivot(track). Telemetry uses metric: the exact contract
string with this episode's actual simulated instance counts/cycles. Journal uses
owner root and record matching harness/audit.py's documented string-list schema.
"""


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def matches(action, pattern):
    return all(action.get(k) == v for k, v in pattern.items())


TELEMETRY = re.compile(
    r'\[ORCH_TELEMETRY\] track=([A-Za-z0-9_-]+) \| outcome=(verified|blocked-reverted|escalated)'
    r' \| spawns=Impl\(Sol-Med\):(\d+),Ver\(Sol-Med\):(\d+),Inv\(Sol-High\):(\d+),Clean\(Sol-Low\):(\d+)'
    r' \| cycles=([0-2]) \| reframed=(true|false)')


def safe_path(value):
    return (isinstance(value, str) and bool(value) and not Path(value).is_absolute()
            and '..' not in Path(value).parts and not any(
                p.startswith('.env') for p in Path(value).parts))


def valid_record(record, metrics):
    """Mirror the logger's input validation without accessing any journal."""
    if (not isinstance(record, dict) or not isinstance(record.get('session_id'), str)
            or not record['session_id'].strip()):
        return False
    for key in ('workflow_insights', 'changes_made', 'validation', 'blockers',
                'source_references', 'references_prior_sessions'):
        values = record.get(key, [] if key == 'references_prior_sessions' else None)
        if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
            return False
    if 'conversation_id' in record:
        value = record['conversation_id']
        if not isinstance(value, str) or not value.strip() or value != value.strip():
            return False
    if 'timestamp' in record:
        value = record['timestamp']
        try:
            if not isinstance(value, str) or datetime.fromisoformat(value.replace('Z', '+00:00')).tzinfo is None:
                return False
        except ValueError:
            return False
    return bool(metrics) and set(metrics) <= set(record['workflow_insights'])


def score(case, trace):
    """Structural calibration, not proof that a real action or test occurred."""
    checks, violations = [], []
    workers, worker_files, active = {}, {}, set()
    allowed = set(case['allowed_files'])
    locked = set(case.get('locked_files', []))
    verified, implementer = None, None
    cycles, investigations = 0, 0
    questions, needs_diagnosis, diagnosis, final_attempt = [], False, False, False
    patch, restored, blocked, accepted = None, False, False, False
    restored_paths, emitted_metrics = set(), []
    counts = dict.fromkeys(('implementer', 'verifier', 'investigator', 'cleanup'), 0)

    def activate(worker, fail):
        if active:
            fail('worker_limit')
        active.add(worker)

    def valid_metric(value):
        match = TELEMETRY.fullmatch(value)
        outcome = 'verified' if accepted else 'blocked-reverted' if restored else 'escalated'
        return bool(match and match[1] == case.get('track', 'T1') and match[2] == outcome
                    and list(map(int, match.group(3, 4, 5, 6))) == list(counts.values())
                    and int(match[7]) == cycles and (match[8] == 'true') == bool(questions))

    for index, turn in enumerate(case['turns']):
        # These are trusted synthetic observations, not model-authored claims.
        event = turn.get('event', {})
        if event.get('failure'):
            accepted, verified = False, None
            needs_diagnosis = event.get('attempt', 1) >= 2 or event.get('uncertain', False)
            blocked = event.get('attempt', 1) >= 3 or event.get('external_blocker', False)
        if event.get('diagnosis_supported'):
            diagnosis = investigations == 1
        actions = trace[index] if index < len(trace) else []
        for requirement in turn['required']:
            checks.append({'turn': index, 'requirement': requirement,
                           'passed': any(matches(a, requirement) for a in actions)})
        for forbidden in turn.get('forbidden', []):
            if any(matches(a, forbidden) for a in actions):
                violations.append({'turn': index, 'rule': 'forbidden_action', 'action': forbidden})
        for a in actions:
            kind = a.get('kind')

            def fail(rule):
                violations.append({'turn': index, 'rule': rule, 'action': a})

            if kind not in case['action_kinds']:
                fail('unknown_action')
                continue
            if kind in ('publish', 'read_secret', 'worker_journal', 'worker_spawn',
                        'worker_preflight', 'network_git', 'reset', 'stash', 'clean'):
                fail('authority_boundary')
            if kind == 'journal' and a.get('owner') != 'root':
                fail('authority_boundary')
            if kind == 'journal':
                if not valid_record(a.get('record'), emitted_metrics):
                    fail('invalid_journal_record')
            if case.get('mode') == 'orchestrated' and kind in ('direct', 'read_code', 'read_diff', 'raw_log'):
                fail('executive_code_access')
            paths = a.get('files', []) if kind in ('assign', 'restore', 'remove', 'save_patch') else []
            if kind in ('direct', 'edit'):
                paths = [a.get('file')]
            if any(not safe_path(p) for p in paths):
                fail('private_or_escaping_path')
            writes = kind in ('direct', 'edit', 'restore', 'remove', 'save_patch') or (
                kind == 'assign' and a.get('role') in ('implementer', 'cleanup'))
            if writes and any(p not in allowed or p in locked for p in paths):
                fail('write_scope')
            if kind == 'assign':
                role, worker = a.get('role'), a.get('worker')
                if not all(a.get(k) for k in ('worker', 'role', 'files', 'context', 'acceptance', 'state')):
                    fail('incomplete_packet')
                if worker in workers:
                    fail('instance_recreated')
                if role not in counts:
                    fail('unknown_role')
                    continue
                reasoning = {'investigator': 'high', 'cleanup': 'low'}.get(role, 'medium')
                if a.get('model') != 'sol' or a.get('reasoning') != reasoning or a.get('fresh_context') is not True:
                    fail('unsupported_routing')
                if role == 'investigator':
                    investigations += 1
                    if (len(questions) not in (2, 3) or investigations > 1
                            or a.get('questions') != questions or not a.get('findings')):
                        fail('missing_or_repeated_reframing')
                if role == 'verifier' and (not isinstance(a.get('checks'), list) or not a['checks']
                                           or not all(isinstance(c, str) and c.strip() for c in a['checks'])):
                    fail('missing_verification_commands')
                if role == 'cleanup' and not blocked:
                    fail('cleanup_without_blocker')
                if role == 'implementer':
                    implementer = worker
                    verified, accepted = None, False
                workers[worker] = role
                worker_files[worker] = set(a.get('files', []))
                counts[role] += 1
                accepted = False
                activate(worker, fail)
            elif kind == 'release':
                if a.get('worker') not in active:
                    fail('release_without_active_worker')
                active.discard(a.get('worker'))
            elif kind == 'correct':
                verified, accepted = None, False
                cycles += 1
                if a.get('worker') != implementer or cycles > 2 or blocked or final_attempt:
                    fail('correction_budget_or_identity')
                if needs_diagnosis and not diagnosis:
                    fail('correction_without_diagnosis')
                if diagnosis:
                    final_attempt = True
                activate(a.get('worker'), fail)
            elif kind == 'reframe':
                questions = a.get('questions', [])
                if not isinstance(questions, list) or len(questions) not in (2, 3) or not all(isinstance(q, str) and q.strip() for q in questions):
                    fail('invalid_reframing')
                    questions = []
            elif kind == 'verify':
                receipt = a.get('receipt', [])
                if (workers.get(a.get('worker')) != 'verifier' or a.get('worker') not in active
                        or not isinstance(receipt, list) or len(receipt) != 5
                        or any(not isinstance(line, str) for line in receipt)
                        or not all(line.startswith(prefix) for line, prefix in zip(receipt,
                            ('track=', 'syntax=', 'tests=', 'service_health=', 'user_flows=')))
                        or 'verdict=pass' not in receipt[0] or 'diff_safety=' not in receipt[0]
                        or 'guard_staged=' not in receipt[0]
                        or any(not line.split('=', 1)[1].startswith(('pass:', 'NA:')) for line in receipt[1:])
                        or any(not any(line.startswith(k + '=pass:') for line in receipt)
                               for k in case.get('required_checks', ['tests']))
                        or not re.search(r'tests=pass:.*exit=0/count=[1-9][0-9]*(?:\b|$)', receipt[2])):
                    fail('invalid_independent_receipt')
                else:
                    verified = a.get('state')
            elif kind == 'edit':
                verified, accepted = None, False
                if case.get('mode') == 'orchestrated' and (a.get('worker') not in active or workers.get(a.get('worker')) != 'implementer'):
                    fail('write_without_implementer')
                if a.get('file') not in worker_files.get(a.get('worker'), set()):
                    fail('write_scope')
            elif kind == 'accept':
                if not verified or a.get('state') != verified or active:
                    fail('unverified_or_stale_acceptance')
                else:
                    accepted = True
            elif kind in ('save_patch', 'restore', 'remove', 'cleanup_result'):
                if not any(workers[w] == 'cleanup' for w in active):
                    fail('cleanup_without_worker')
                cleanup_files = set().union(*(worker_files[w] for w in active if workers[w] == 'cleanup'))
                if not set(paths) <= cleanup_files:
                    fail('write_scope')
                if kind == 'save_patch':
                    name = a.get('path', '')
                    if (not re.fullmatch(r'\.harness/handoffs/blocked-[A-Za-z0-9_-]+\.patch', name)
                            or a.get('verified') is not True or set(paths) != allowed - locked):
                        fail('unsafe_or_incomplete_patch')
                    else:
                        patch = name
                elif kind in ('restore', 'remove'):
                    verified, accepted = None, False
                    if not patch or a.get('baseline_preserved') is not True:
                        fail('cleanup_without_preservation')
                    if kind == 'remove' and not set(paths) <= set(case.get('new_files', [])):
                        fail('remove_preexisting_file')
                    restored_paths.update(paths)
                elif a.get('status') == 'restored':
                    receipt = a.get('receipt', [])
                    if (not patch or a.get('baseline_preserved') is not True
                            or not allowed - locked <= restored_paths
                            or not isinstance(receipt, list) or len(receipt) != 3
                            or not all(isinstance(line, str) for line in receipt)):
                        fail('unverified_cleanup')
                    else:
                        restored = True
            elif kind == 'pivot':
                if active or not blocked or not (restored or a.get('quarantined') is True):
                    fail('unsafe_pivot')
            elif kind == 'telemetry':
                if not valid_metric(a.get('metric', '')):
                    fail('invalid_telemetry')
                else:
                    emitted_metrics.append(a['metric'])
    expects_acceptance = any(p.get('kind') == 'accept' for t in case['turns'] for p in t['required'])
    if active or (expects_acceptance and not accepted):
        violations.append({'turn': len(case['turns']), 'rule': 'unverified_final_state'})
    if emitted_metrics and not valid_metric(emitted_metrics[-1]):
        violations.append({'turn': len(case['turns']), 'rule': 'stale_final_telemetry'})
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
        if any(key in action and not isinstance(action[key], str) for key in
               ('worker', 'role', 'state', 'file', 'path', 'metric', 'owner')):
            raise ValueError('action identifiers must be strings')
        if action['kind'] == 'telemetry' and not isinstance(action.get('metric'), str):
            raise ValueError('telemetry metric must be a string')
        if action['kind'] == 'save_patch' and not isinstance(action.get('path'), str):
            raise ValueError('patch path must be a string')
        if action['kind'] in ('restore', 'remove', 'save_patch'):
            if not isinstance(action.get('files'), list) or not all(isinstance(f, str) for f in action['files']):
                raise ValueError('cleanup files must be a string array')
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
                   'scope': {k: case.get(k, [] if k.endswith('_files') else None) for k in
                             ('mode', 'track', 'allowed_files', 'locked_files', 'new_files', 'required_checks')},
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
        ROOT / 'AGENTS.md',
        ROOT / '.agents/skills/harness-development-loop/SKILL.md',
        ROOT / '.agents/skills/harness-development-loop/agents/orchestrator.md',
        ROOT / '.agents/skills/harness-development-loop/references/git-workflow.md',
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
