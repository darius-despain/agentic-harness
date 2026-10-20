#!/usr/bin/env python3
"""Read-only staged-path and AI attribution checks; no file contents in diagnostics."""
import argparse
import os
from pathlib import Path
import subprocess
import sys

from git_preflight import private_path


def check_staged(repository):
    # Disable rename detection so both endpoints appear, including private deletions.
    # Inherit GIT_INDEX_FILE: Git supplies a temporary index for scoped commits.
    try:
        result = subprocess.run(
            ["git", "-C", str(repository), "-c", "core.fsmonitor=false", "diff",
             "--cached", "--name-only", "-z", "--no-renames", "--no-ext-diff", "--"],
            env=dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_OPTIONAL_LOCKS="0"),
            capture_output=True, timeout=15)
    except (OSError, subprocess.TimeoutExpired):
        raise ValueError("staged-path inspection unavailable") from None
    if result.returncode:
        raise ValueError("staged-path inspection failed; Git diagnostics suppressed")
    paths = [os.fsdecode(value) for value in result.stdout.split(b"\0") if value]
    if any(private_path(path) for path in paths):
        raise ValueError("staged private configuration path detected; preserve the index and resolve before committing")


def surviving_commit_message(message):
    """Conservatively retain only text that survives Git comment/scissors cleanup."""
    def git(*args, input_text=None):
        try:
            result = subprocess.run(["git", *args], input=input_text, capture_output=True,
                                    text=True, timeout=15)
        except (OSError, subprocess.TimeoutExpired, UnicodeError):
            raise ValueError("commit-message cleanup inspection unavailable") from None
        return result

    # Older Git ignores commentString. Conservatively consider all configured
    # prefixes plus the default instead of guessing version-specific precedence.
    # An unset key returns 1; other failures must fail closed without diagnostics.
    prefixes = {"#"}
    for key in ("core.commentString", "core.commentChar"):
        result = git("config", "--get", key)
        if result.returncode not in (0, 1):
            raise ValueError("commit-message comment configuration unavailable")
        if result.returncode == 0:
            value = result.stdout.rstrip("\n")
            prefixes.update(list("#;@!$%^&|:") if value == "auto" else [value])
    retained = []
    for line in message.splitlines(keepends=True):
        if any(line.startswith(prefix + " ------------------------ >8 ------------------------")
               for prefix in prefixes):
            break
        retained.append(line)
    result = git("stripspace", "--strip-comments", input_text="".join(retained))
    if result.returncode:
        raise ValueError("commit-message cleanup failed; Git diagnostics suppressed")
    return result.stdout


def check_message(path, agent, commit=False):
    if not agent.strip() or agent != agent.strip() or "\n" in agent or "\r" in agent:
        raise ValueError("agent identity must be nonempty, single-line, and have no surrounding whitespace")
    if private_path(str(path)) or private_path(str(path.resolve())):
        raise ValueError("private configuration cannot be used as a message file")
    expected = f"Co-authored by: {agent} (AI)"
    message = path.read_text()
    if commit:
        message = surviving_commit_message(message)
    if expected not in message.splitlines():
        raise ValueError("message lacks the exact standalone AI attribution line for the supplied agent")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    staged = sub.add_parser("staged", help="check staged filenames only")
    staged.add_argument("--repository", type=Path, default=Path.cwd())
    message = sub.add_parser("message", help="check a commit or PR/MR body")
    message.add_argument("--file", type=Path, required=True)
    message.add_argument("--agent", required=True, help="actual current runtime identity; never inferred")
    message.add_argument("--commit", action="store_true", help="require attribution to survive Git comment/scissors cleanup")
    args = parser.parse_args(argv)
    try:
        if args.command == "staged":
            check_staged(args.repository)
        else:
            check_message(args.file, args.agent, args.commit)
    except (OSError, UnicodeError):
        print("Harness guard: message file unavailable or unreadable", file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"Harness guard: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
