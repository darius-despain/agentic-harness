#!/usr/bin/env python3
"""Read-only, config-relative Git inventory. No credential or file contents output."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlsplit


def run(path, *args):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_OPTIONAL_LOCKS="0")
    try:
        result = subprocess.run(["git", "-C", str(path), *args], env=env,
                                capture_output=True, text=True, timeout=15)
        return result.returncode, result.stdout
    except (OSError, subprocess.TimeoutExpired):
        return 125, ""


def identity(url):
    """Allowlisted repository identity; discard userinfo, queries and fragments."""
    if "://" in url:
        parsed = urlsplit(url)
        host, path = parsed.hostname, parsed.path.lstrip("/")
    else:
        match = re.fullmatch(r"(?:[^/@:]+@)?([^/:]+):(.+)", url)
        if not match:
            return None
        host, path = match.groups()
    if path.endswith(".git"):
        path = path[:-4]
    if host and re.fullmatch(r"[A-Za-z0-9.-]+", host) and re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", path):
        return host.lower() + "/" + path
    return None


def load_registry(config_path):
    config_path = config_path.resolve()
    entries = json.loads(config_path.read_text()).get("git_repositories")
    if not isinstance(entries, dict) or not entries:
        raise ValueError("configure nonempty git_repositories keyed by checkout name")
    output = []
    for name, entry in entries.items():
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            raise ValueError("each checkout requires a relative path")
        relative = Path(entry["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("checkout path must be relative without parent traversal")
        path = (config_path.parent / relative).resolve()
        if not path.is_relative_to(config_path.parent):
            raise ValueError("checkout path escapes config root through a symlink")
        expected = entry.get("origin")
        if expected is not None and (not isinstance(expected, str) or
                identity("https://" + expected) != expected):
            raise ValueError("origin must be a host/owner/repository identity")
        output.append((name, path, expected))
    return output


def inspect(path, expected=None, recurse=True):
    report = {"path": str(path), "inspection": "unavailable"}
    rc, top = run(path, "rev-parse", "--show-toplevel")
    if rc or Path(top.strip()).resolve() != path.resolve():
        report["reason"] = "No exact checkout visible; do not initialize or repair metadata automatically"
        return report
    commands = {"head": ("rev-parse", "--verify", "HEAD"),
                "branch": ("branch", "--show-current"),
                "status": ("status", "--porcelain=v1", "-z", "--untracked-files=normal"),
                "index": ("ls-files", "--stage", "-z")}
    values = {}
    for key, args in commands.items():
        rc, value = run(path, *args)
        if rc:
            report["reason"] = "Required Git inspection failed; cleanliness unknown"
            return report
        values[key] = value
    report.update(inspection="complete", head=values["head"].strip(),
                  branch=values["branch"].strip() or None)
    status = []
    items = iter(values["status"].split("\0"))
    for item in items:
        if not item:
            continue
        code, filename = item[:2], item[3:]
        status.append({"code": code, "path": filename,
                       "private_configuration": any(p == ".env" or p.startswith(".env.")
                                                     for p in Path(filename).parts)})
        if "R" in code or "C" in code:
            next(items, None)  # rename source, not a second status entry
    report["changes"] = status
    report["clean"] = not status
    rc, origin = run(path, "remote", "get-url", "origin")
    report["origin"] = identity(origin.strip()) if not rc else None
    report["origin_matches_config"] = report["origin"] == expected if expected else None
    _, helpers = run(path, "config", "--get-all", "credential.helper")
    report["generic_credential_helper_present"] = bool(helpers.strip())
    report["origin_credential_helper_present"] = None
    if report["origin"] and origin.strip().startswith(("https://", "http://")):
        # Query URL-specific helpers using a credential-free identity, never raw userinfo.
        scheme = origin.strip().split(":", 1)[0]
        safe_url = scheme + "://" + report["origin"] + ".git"
        _, scoped_helpers = run(path, "config", "--get-urlmatch", "credential.helper", safe_url)
        report["origin_credential_helper_present"] = bool(scoped_helpers.strip())
    report["credential_override_names_present"] = [name for name in
        ("GH_TOKEN", "GITHUB_TOKEN", "GH_ENTERPRISE_TOKEN", "GITHUB_ENTERPRISE_TOKEN", "GH_CONFIG_DIR", "XDG_CONFIG_HOME",
         "GIT_ASKPASS", "SSH_ASKPASS", "SSH_AUTH_SOCK", "GIT_CONFIG_COUNT") if os.environ.get(name)]
    report["local_git_network_access"] = "not_probed"
    report["connector_access"] = "not_tested_by_this_tool"
    rc, upstream = run(path, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
    report["cached_upstream"] = upstream.strip() if not rc else None
    report["cached_history"] = None
    if not rc:
        rc, counts = run(path, "rev-list", "--left-right", "--count", "HEAD...@{upstream}")
        if rc:
            report["history_error"] = "Cached history comparison unavailable"
        else:
            ahead, behind = map(int, counts.split())
            report["cached_history"] = {"ahead": ahead, "behind": behind}
    report["submodules"] = []
    if recurse:
        for item in values["index"].split("\0"):
            if not item.startswith("160000 "):
                continue
            metadata, filename = item.split("\t", 1)
            _, recorded, index_stage = metadata.split()
            child = (path / filename).resolve()
            if not child.is_relative_to(path.resolve()):
                state = {"inspection": "unavailable", "reason": "Submodule path escapes checkout"}
            else:
                state = inspect(child)
            state.update(relative_path=filename, recorded_head=recorded, index_stage=index_stage,
                         matches_gitlink=state.get("head") == recorded if state.get("head") else None)
            report["submodules"].append(state)
    return report


def probe(command):
    """Capture and discard all diagnostics; expose only an allowlisted outcome."""
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1",
               GIT_ASKPASS="/bin/false", SSH_ASKPASS="/bin/false",
               GIT_SSH_COMMAND="ssh -oBatchMode=yes -oConnectTimeout=15")
    try:
        result = subprocess.run(command, env=env, capture_output=True, timeout=20)
        return {"result": "success" if result.returncode == 0 else "failed_auth_network_or_remote",
                "exit_code": result.returncode}
    except subprocess.TimeoutExpired:
        return {"result": "timeout"}
    except OSError:
        return {"result": "executable_unavailable"}


def readiness(reports):
    """Independent account API and repository Git checks; no connector/push claim."""
    accounts, repositories = {}, {}
    for report in reports:
        origin = report.get("origin")
        if report["inspection"] != "complete" or not origin or report.get("origin_matches_config") is False:
            report["readiness"] = {"result": "unavailable_or_origin_mismatch"}
            continue
        host = origin.split("/", 1)[0]
        if host not in accounts:
            accounts[host] = probe(["gh", "api", "--hostname", host, "user", "--silent"])
        if origin not in repositories:
            repositories[origin] = probe(["git", "-C", report["path"], "ls-remote",
                                          "--exit-code", "origin", "HEAD"])
        report["readiness"] = {"gh_account": accounts[host], "git_repository": repositories[origin],
                               "connector_access": "not_tested", "push_permission": "not_tested"}
    return any(any(result.get("result") != "success" for result in r["readiness"].values()
                   if isinstance(result, dict)) or "result" in r["readiness"] for r in reports)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("harness-config.json"))
    parser.add_argument("--repository", help="configured checkout name; default is all")
    parser.add_argument("--probe-remote", action="store_true", help="one noninteractive ls-remote per distinct origin")
    parser.add_argument("--readiness", action="store_true", help="explicit gh API and Git read checks; no push or connector check")
    args = parser.parse_args()
    if args.readiness and args.probe_remote:
        parser.error("choose --readiness or --probe-remote, not both")
    try:
        entries = load_registry(args.config)
        if args.repository:
            entries = [e for e in entries if e[0] == args.repository]
            if not entries:
                raise ValueError("unknown configured checkout")
        reports, probed = [], {}
        for name, path, expected in entries:
            report = inspect(path, expected)
            report["name"] = name
            if args.probe_remote and report.get("origin") and report["inspection"] == "complete":
                # Reuse a failure across worktrees; never repeat unchanged auth failures in bulk.
                origin = report["origin"]
                if origin not in probed:
                    result = probe(["git", "-C", str(path), "ls-remote", "--exit-code", "origin", "HEAD"])
                    probed[origin] = "success" if result["result"] == "success" else "failed_auth_network_or_remote"
                report["local_git_network_access"] = probed[origin]
            reports.append(report)
        readiness_failed = readiness(reports) if args.readiness else False
        print(json.dumps({"kind": "git_preflight", "remote_refs": "cached_only_no_fetch",
                          "repositories": reports}, indent=2))
        return int(readiness_failed or any(r["inspection"] != "complete" or r.get("origin_matches_config") is False
                       or r.get("local_git_network_access") == "failed_auth_network_or_remote" for r in reports))
    except (OSError, ValueError, TypeError, KeyError):
        print("Git preflight failed: invalid configuration or unavailable inspection; raw diagnostics suppressed", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
