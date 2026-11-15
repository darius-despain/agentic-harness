#!/usr/bin/env python3
"""Select one harness tool profile; no agent launch, network, or history scan."""
import argparse
import json
from pathlib import Path
import sys


TOOLS = ('codex', 'antigravity', 'claude-code', 'generic')
HERE = Path(__file__).resolve().parent


def settings_path(root):
    """Keep machine preferences in the target project, refusing linked settings."""
    directory = root / '.harness'
    path = directory / 'local.json'
    if directory.is_symlink() or path.is_symlink():
        raise ValueError('refusing symlinked .harness/local.json settings')
    return path


def read_settings(path):
    if not path.exists():
        return {}
    if not path.is_file():
        raise ValueError('.harness/local.json must be a regular file')
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError('.harness/local.json must be a JSON object')
    return value


def write_settings(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Preserve unrelated local keys. This file must never contain credentials.
    path.write_text(json.dumps(value, indent=2) + '\n')


def select(root, tool=None, remember=False, forget=False):
    root = root.expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError('--root must be an existing project directory')
    path = settings_path(root)
    if forget:
        settings = read_settings(path)
        if 'tool' in settings:
            del settings['tool']
            write_settings(path, settings)
        return {'selection': 'cleared'}
    source = 'explicit'
    if tool is None:
        settings = read_settings(path)
        tool = settings.get('tool')
        source = 'local'
        if 'tool' not in settings:
            if not sys.stdin.isatty():
                raise ValueError('no tool selected; pass --tool ' + '|'.join(TOOLS) +
                                 ' or run in a terminal to choose')
            source = 'prompt'
            while tool not in TOOLS:
                print('Choose harness tool profile (' + ', '.join(TOOLS) + '): ',
                      end='', file=sys.stderr, flush=True)
                tool = input().strip().lower()
                if tool not in TOOLS:
                    print('Enter one of the listed profile names.', file=sys.stderr)
    if tool not in TOOLS:
        raise ValueError('invalid tool preference; use --tool with one of: ' + ', '.join(TOOLS))
    shared = [HERE / 'CORE.md', HERE / 'profiles' / (tool + '.md')]
    for file in shared:
        if not file.is_file():
            raise ValueError('incomplete harness installation; missing ' + file.name)
    local = root / 'AGENTS.local.md'
    # Never follow a private preference file outside its owning project.
    if local.is_symlink():
        raise ValueError('refusing symlinked AGENTS.local.md')
    if local.exists() and not local.is_file():
        raise ValueError('AGENTS.local.md must be a regular file')
    if remember:
        settings = read_settings(path)
        settings['tool'] = tool
        write_settings(path, settings)
    return {'tool': tool, 'source': source, 'remembered': remember,
            'load': [str(file) for file in shared] + ([str(local)] if local.is_file() else [])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd(), help='target project, default: current directory')
    parser.add_argument('--tool', choices=TOOLS, help='override the saved choice for this session')
    parser.add_argument('--remember', action='store_true', help='save the selected profile locally')
    parser.add_argument('--forget', action='store_true', help='clear only the saved tool preference and exit')
    args = parser.parse_args()
    if args.forget and (args.tool or args.remember):
        parser.error('--forget cannot be combined with --tool or --remember')
    try:
        result = select(args.root, args.tool, args.remember, args.forget)
    except (OSError, ValueError, EOFError, RuntimeError) as error:
        print(f'Harness session error: {error}', file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
