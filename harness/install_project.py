#!/usr/bin/env python3
"""Preview or install a project-local logger without overwriting existing assets."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from audit import load_config


def ignore_directory(path):
    """Return an anchored gitignore rule matching this literal relative path."""
    value = path.as_posix()
    if '\n' in value or '\r' in value:
        raise ValueError('journal/report paths cannot contain line breaks in gitignore rules')
    # Git wildmatch treats these characters as pattern syntax, including backslash.
    escaped = ''.join('\\' + char if char in '\\*?[]' else char for char in value)
    return '/' + escaped + '/'


def install(root, project, apply=False):
    root = root.expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError('project root must be an existing directory')
    if not project.strip() or project == '<update-me>':
        raise ValueError('project must be a nonempty name')
    # Reject linked installation assets instead of modifying a shared checkout.
    for relative in ('harness', 'harness/audit.py', 'harness-config.json', '.gitignore'):
        path = root / relative
        if path.is_symlink():
            raise ValueError(f'refusing symlink installation target: {relative}')
        if path.exists() and (path.is_dir() if relative != 'harness' else not path.is_dir()):
            raise ValueError(f'unexpected file type: {relative}')
    config_path = root / 'harness-config.json'
    if not config_path.exists() and (root / 'harness/harness-config.json').exists():
        raise ValueError('legacy nested config found; migrate it to the project root before installing')
    defaults = {'template_version': '2.0', 'project': project,
                'session_persistence_dir': 'conversations', 'audit_output_dir': 'harness/reports',
                'max_age_days': 30, 'minimum_sessions': 2}
    if config_path.exists():
        config = load_config(config_path)
        if config['project'] != project:
            raise ValueError('existing config project does not match --project')
    else:
        config = dict(defaults)
        for key in ('session_persistence_dir', 'audit_output_dir'):
            config[key] = (root / defaults[key]).resolve()
            if not config[key].is_relative_to(root):
                raise ValueError(f'{key} escapes project through a symlink')
    for key in ('session_persistence_dir', 'audit_output_dir'):
        directory = config[key]
        for path in (directory, *directory.parents):
            if path == root:
                break
            if path.exists() and not path.is_dir():
                raise ValueError(f'{key} has a non-directory component')
    source = Path(__file__).resolve().with_name('audit.py').read_bytes()
    target = root / 'harness/audit.py'
    if target.exists() and target.read_bytes() != source:
        raise ValueError('existing harness/audit.py differs; review and update it explicitly')
    ignore_path = root / '.gitignore'
    ignore = ignore_path.read_text() if ignore_path.exists() else ''
    patterns = [ignore_directory(config[key].relative_to(root))
                for key in ('session_persistence_dir', 'audit_output_dir')]
    # Config remains local; journals and reports are never staged by this installer.
    patterns.append('/harness-config.json')
    missing = [p for p in patterns if p not in ignore.splitlines()]
    plan = []
    if not target.exists():
        plan.append('create harness/audit.py')
    if not config_path.exists():
        plan.append('create harness-config.json')
    if missing:
        plan.append('append local config/journal/report ignore rules')
    for key in ('session_persistence_dir', 'audit_output_dir'):
        if not config[key].exists():
            plan.append(f'create {config[key].relative_to(root)}/')
    if not apply:
        return {'applied': False, 'changes': plan}
    (root / 'harness').mkdir(exist_ok=True)
    if not target.exists():
        with target.open('xb') as output:
            output.write(source)
    if not config_path.exists():
        with config_path.open('x') as output:
            output.write(json.dumps(defaults, indent=2) + '\n')
    if missing:
        with ignore_path.open('a') as output:
            output.write(('\n' if ignore and not ignore.endswith('\n') else '') + '\n'.join(missing) + '\n')
    for key in ('session_persistence_dir', 'audit_output_dir'):
        config[key].mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(target), '--config', str(config_path), 'check'],
                   check=True, capture_output=True, text=True)
    return {'applied': True, 'changes': plan}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--project', required=True)
    parser.add_argument('--apply', action='store_true', help='apply the previewed installation')
    args = parser.parse_args()
    try:
        print(json.dumps(install(args.root, args.project, args.apply), indent=2))
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        print(f'Installation error: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
