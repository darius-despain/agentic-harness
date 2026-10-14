#!/usr/bin/env python3
"""Link shared harness assets into a user's Codex installation without deleting files."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import shutil

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--home', type=Path, default=Path.home())
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
home = args.home.expanduser().resolve()
stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
backup_root = home / '.codex' / 'harness-link-backups' / stamp

def link(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.is_symlink() and destination.resolve() == source.resolve():
        print('Already linked:', destination)
        return
    if destination.exists() or destination.is_symlink():
        backup = backup_root / destination.relative_to(home)
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(destination), str(backup))
        print('Preserved previous file:', backup)
    destination.symlink_to(source, target_is_directory=source.is_dir())
    print('Linked:', destination)

config = home / '.codex' / 'config.toml'
local_config = root / 'codex' / 'config.local.toml'
if not local_config.exists():
    if config.exists():
        shutil.copyfile(config, local_config)
    else:
        local_config.write_text('# Personal machine configuration; ignored by Git.\n')
    local_config.chmod(0o600)
link(root / 'AGENTS.md', home / '.codex' / 'AGENTS.md')
link(local_config, config)
for skill in sorted((root / '.agents' / 'skills').iterdir()):
    if skill.is_dir() and (skill / 'SKILL.md').is_file():
        link(skill, home / '.agents' / 'skills' / skill.name)
link(root / 'harness', home / '.local' / 'share' / 'agentic-harness' / 'harness')
print('Restart Codex to load instructions, skills, and configuration.')
