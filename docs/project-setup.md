# Install the logger in a project

Global instruction/skill links do not install `harness/audit.py` or a project config.
Use the project installer from this template checkout (Python 3.9+, no dependencies):

```bash
python3 harness/install_project.py /absolute/path/to/project --project project-name
python3 harness/install_project.py /absolute/path/to/project --project project-name --apply
```

The first command previews changes without writing. The second creates missing
logger/config files and configured journal/report directories, appends ignore rules,
and runs the installed logger's config check. It works from another working directory
when invoked using an absolute script path. The project directory must already exist.
It need not be a Git checkout; installation does not initialize Git or commit anything.

Existing config, journal records, instructions, skills, and unrelated files are
preserved. Reruns with matching assets make no changes. A differing CLI, mismatched
project name, linked installation target, invalid config, or legacy nested config
causes an error before installation writes. Review and migrate those cases explicitly;
this installer does not guess how to replace customized files. Filesystem failures
during application can leave a partial installation; correct the failure and rerun.

For a legacy nested config, preserve it first, put a valid config at the project root,
and resolve data paths relative to that root. Keep reports separate from the journal.
A compatibility symlink from the old nested path to the root config can preserve old
callers; the CLI resolves the config symlink before resolving data paths.

From the installed project root:

```bash
python3 harness/audit.py --config harness-config.json check
python3 harness/audit.py --config harness-config.json log --record /absolute/path/to/sanitized-record.json
python3 harness/audit.py --config harness-config.json audit
python3 harness/audit.py --config harness-config.json audit --write
```

Use the session-record format in the main README and include `source_references`.
Check the written journal record before claiming persistence. No automatic capture,
scheduler, global configuration change, legacy-record rewrite, or shared-project
update is performed. Audit results still require human/agent source review: old test
records without explicit fixture metadata can look like ordinary sessions. Do not
use those as evidence of recurring real work.
