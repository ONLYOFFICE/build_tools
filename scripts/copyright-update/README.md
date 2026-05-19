# Copyright Header Replacement

A central Gitea workflow that replaces a known **old** copyright header with
a known **new** copyright header across a list of repositories. Driven by a
small Python 3 script with no external dependencies.

---

## 1. Overview

ONLYOFFICE source files carry a long C-style `/* ... */` copyright block at
the top. When the legal text changes, those blocks need to be updated
across repositories. A simple year bump is not enough when wording, address,
URLs, or license clauses also change.

This tool is intentionally focused:

- It replaces a known old header with a known new header.
- It avoids third-party copyright blocks (holder-substring gate).
- It never writes directly to the target base branch (always pushes a
  generated branch).
- It is idempotent: files that already exactly match the new template are
  skipped.

It is not a license checker, not a generic year bumper, and not a tool
for adding missing headers.

### Where it lives

- Script and templates: [`scripts/copyright-update/`](./)
- Workflow: [`.github/workflows/copyright-header.yml`](../../.github/workflows/copyright-header.yml)
- OLD template: [`templates/old.license`](./templates/old.license)
- NEW template: [`templates/new.license`](./templates/new.license)
- Push-driven run list: [`config.json`](./config.json)

---

## 2. How To Run

### 2.1 Manual dispatch

From the Gitea Actions UI, run **Copyright header replacement** with two
inputs:

| Input          | Required | Description |
|----------------|----------|-------------|
| `repositories` | yes      | One target repository per line. Accepts `owner/repo` or bare `repo` (owner defaults to `ONLYOFFICE`). |
| `base_branch`  | no       | Branch **name** (e.g. `master`, `release/v9.4.0`). Branch names only -- tags, arbitrary refs, and commit SHAs are not supported. Empty means each repo's default branch. |

### 2.2 Push-driven runs via `config.json`

Editing [`config.json`](./config.json) and pushing to `feature/copyright`
also triggers the workflow. The configured list of repositories is read
straight from the file; the script parses it via `--emit-targets` so the
YAML stays free of config-shape logic.

`config.json` schema (both fields optional, missing means "empty"):

```json
{
  "base_branch": "release/v9.4.0",
  "repositories": [
    "sdkjs",
    "ONLYOFFICE/server"
  ]
}
```

- `repositories` -- `owner/repo` or bare `repo` names. Bare names get the
  same `ONLYOFFICE` default owner as the dispatch input. An empty or
  missing list flips the workflow's `enabled` output to `false`, and the
  per-repo step is skipped via its `if:` guard rather than running with
  an empty matrix.
- `base_branch` -- same semantics as the dispatch input.

The default committed `config.json` ships **empty** so push to
`feature/copyright` is safe and does no work until an operator populates
the list.

### 2.3 Required secrets and variables

The workflow uses a **token split**: read paths use a read-scoped PAT,
push uses bot credentials. This minimises the surface where write-scoped
credentials are passed.

| Name                 | Kind    | Used for |
|----------------------|---------|----------|
| `secrets.READ_PAT`   | secret  | Cross-repo `git clone` and Gitea REST API calls (resolving default branches). |
| `secrets.USERNAME`   | secret  | Bot account username for HTTP basic auth. |
| `secrets.TOKEN`      | secret  | Bot account PAT (write scope on target repositories). Used only for `git push`. |
| `vars.GITEA_URL`     | var     | Optional override for the Gitea instance URL. Defaults to `${{ github.server_url }}`, which Gitea auto-populates. |

---

## 3. What Happens After Run

For every target repository the workflow:

1. Resolves the base branch (input/config value, or the repo's default
   branch via Gitea API when empty).
2. Generates a disposable branch name `feature/copyright-<base-slug>-YYYY-MM-DD`.
3. **If the generated branch already exists on the target remote, the
   repo is skipped** with `reason=already_generated`. This avoids
   redoing the replacement when an operator extends `config.json` with
   new repos and re-pushes; previously processed repos keep their
   existing branch untouched. To force a fresh run, manually delete
   the remote branch in the Gitea UI.
4. Otherwise: clones the target via `READ_PAT`, fetches the resolved
   base branch, and checks out the disposable branch off it.
5. Runs the replacement script over all tracked source files.
6. If anything changed: commits, swaps `origin`'s push URL to the
   `USERNAME:TOKEN` bot credentials, and pushes via
   `git push --force-with-lease`.
7. Prints a per-repo summary to the workflow run page, with
   `not_our_header` files highlighted as the actionable subset.

### Generated branch name

```text
feature/copyright-<base-branch-slug>-YYYY-MM-DD
```

- The slug is the base branch name with non-`[A-Za-z0-9._-]` characters
  replaced by `-` (so `release/v9.4.0` becomes `release-v9.4.0`).
- The date is the runner's date, computed once for the whole dispatch.

Examples:

- `base_branch = master` -> `feature/copyright-master-2026-05-14`
- `base_branch = release/v9.4.0` -> `feature/copyright-release-v9.4.0-2026-05-14`

The branch is **generated and disposable**. Re-running the workflow on
the same day, against the same base, overwrites the remote branch via
`git push --force-with-lease`.

### Pull requests

The workflow pushes the generated branch and stops. **It does not open
pull requests.** Operators open PRs from the pushed branch by hand when
they are ready to review and merge.

### Summary line per repository

The workflow run page lists, for each target repository:

- `base_branch` -- the branch the work is based on
- `generated_branch` -- the disposable branch that was created/updated
- `branch_created` -- `true` if changes were pushed, `false` if nothing changed
- `reason` -- `ok`, `no_changes`, `already_generated`, or an error message
- `replaced`, `not_our_header`, `no_header`, `vendor`, `already_new`,
  `errors` -- per-classification counts

If `not_our_header > 0`, a highlighted bullet flags it as the
actionable subset; the file paths themselves live in the run log
(the script echoes `not_our_header: <path>` for each).

### Repositories with no changes

If a repository has no files matching the old template (e.g. it has
already been migrated, or it has no Ascensio System SIA headers at all),
the workflow reports `branch_created=false`, `reason=no_changes`, and
that single repo exits successfully. The bash loop continues to the
next repository on any single-repo failure, but the **overall job
exits non-zero if any repo failed** so a silently-broken push never
hides as a green run.

---

## 4. Safety Model

The tool is designed to be aggressively conservative.

### Default branches are never touched

The replacement is always performed on a fresh disposable branch
(`feature/copyright-...-YYYY-MM-DD`) created from the base branch. The
workflow pushes only that branch; it does not push to the base branch
and does not delete any remote branch. A human reviewer is always in
the loop between the workflow and the protected branches.

### Third-party copyrights are skipped by holder match

Before rewriting any file the tool requires the substring
`Ascensio System SIA` (case-insensitive) to be present in the normalised
top-of-file comment block. Without this match the file is classified
`SKIP_VENDOR_UNKNOWN_HOLDER` and left alone, **regardless of where it
lives in the tree or how similar the surrounding boilerplate is**.

This is the load-bearing safety check: a fuzzy match against AGPL-style
boilerplate could otherwise score high on a third-party AGPL file (e.g.
Chromium, V8) and accidentally strip the original author's attribution.
The holder check makes that impossible.

A built-in conservative path-exclude list (`node_modules/**`,
`vendor/**`, `third_party/**`, `build/**`, `dist/**`, etc.) is applied
on top as a defence-in-depth measure, but the primary safety is the
holder match.

### Idempotency

Before classifying a file as `REPLACE`, the tool first checks similarity
against the **new** template. If that ratio crosses
`--idempotency-threshold` (default `1.0`), the file is classified
`SKIP_ALREADY_NEW` and left alone. With `1.0` the threshold means
"exact match required"; any drift from the canonical NEW template is
re-aligned on the next run.

### Force-with-lease, not force

Pushing the generated branch uses `git push --force-with-lease`. If
someone else has pushed to the same generated branch between this run's
fetch and its push, the push is rejected and the job fails loudly. The
workflow never retries with plain `--force` and never silently
overwrites.

### Token split for least privilege

`READ_PAT` (read-only) is used for `git clone` and Gitea REST API
calls. The write-scoped `USERNAME` + `TOKEN` bot credentials are
plugged in only for the single `git push` step, via
`git remote set-url --push origin`. This minimises the surface where
write credentials are passed to subprocesses.

### Reports cannot land inside the target repo

The script refuses to write reports inside the target repository: if
`--report-dir` resolves (via `realpath`) to the repo or any path under
it, the script exits non-zero before doing anything. The workflow
always passes a path under `$GITHUB_WORKSPACE/reports/`, which is
outside any cloned target.

---

## 5. Limitations And Trade-Offs

v1 is intentionally narrow:

- **Top-of-file C-style `/* ... */` blocks only.** Hash (`#`),
  line (`//`), and HTML (`<!-- -->`) headers are out of scope.
- **Replacement only.** Missing headers are reported but not added.
  Unknown or invalid headers are reported but not auto-fixed.
- **No year substitution.** The new template's year text is written
  verbatim.
- **No PR creation.** The workflow pushes a branch and stops.
- **No schedule.** Runs on `workflow_dispatch` and on pushes to
  `feature/copyright` that touch `scripts/copyright-update/config.json`.
- **Branch names only.** The `base_branch` input does not accept tags,
  arbitrary refs, or commit SHAs.
- **One base_branch per dispatch.** All target repos use the same
  `base_branch` value in a single dispatch.
- **No per-dispatch template override.** Templates live at fixed paths
  in this repo; updating them is a commit.
- **Sequential, not parallel.** The bash-loop shape (a Gitea act-runner
  workaround for dynamic matrix from `needs.outputs`) processes repos
  one after another. Acceptable for the small list typical of an
  annual run.

---

## 6. Reports

Reports are produced at three levels of detail; pick the one that
suits the question you have.

### 6.1 Run page (Job Summary)

For each target repository the run page shows:

- `base_branch`, `generated_branch`, `branch_created`, `reason`
- The full counts: `replaced`, `not_our_header`, `no_header`, `vendor`,
  `already_new`, `errors`
- **A highlighted `not_our_header` bullet** -- the actionable subset:
  count + hint to review manually or lower `--similarity-threshold`.
  Paths themselves are not inlined to keep the summary compact.

### 6.2 Run log (collapsible per-repo blocks)

Every iteration is wrapped in `::group::` markers, so the run-log
renders each repository as its own collapsible block. Inside the
block the script prints:

- `not_our_header: <path>` for every actionable skip (small, always shown)
- The totals line at the end (`scanned=N replaced=N ...`)
- All git operations (clone, fetch, push) verbatim

`replaced:` paths are NOT printed by default to keep the run log
small for big repos. Pass `--verbose` locally to see them.

### 6.3 `reports` artifact (full audit trail)

The workflow uploads a single artifact named `reports`, containing
one subdirectory per target repository:

```text
reports/
  ONLYOFFICE-server/
    report.txt    -- per-file outcomes + totals (everything, plain text)
    summary.md    -- the per-repo summary block (same as in the Job Summary)
```

`report.txt` is the source of truth for "what happened":

- `replaced: <path>` for every modified file
- `not_our_header: <path>` for every actionable skip
- `vendor: <path>` for every third-party block left alone
- `error: <path> (msg)` for any per-file failures
- Final totals block (`scanned=N replaced=N ...`)

To get just one subset, grep:

```bash
grep '^replaced:'       report.txt
grep '^not_our_header:' report.txt
```

### 6.4 Commit message

The same stats land in the commit message body, with `not_our_header`
first:

```text
[copyright] Update copyright header

not_our_header=15 replaced=57 no_header=8 vendor=0 already_new=0 errors=0
```

So `git log --oneline` and PR titles also surface the actionable
signal long after the workflow run page is gone.

### Classifications

| Classification               | Meaning |
|------------------------------|---------|
| `REPLACE`                    | File matched the OLD template strongly enough to rewrite. |
| `SKIP_ALREADY_NEW`           | File already exactly matches the NEW template (idempotency). |
| `SKIP_NO_HEADER`             | File has no top-of-file `/* ... */` block. |
| `SKIP_VENDOR_UNKNOWN_HOLDER` | Block lacks `Ascensio System SIA`. Treated as third-party regardless of path. |
| `SKIP_NOT_OUR_HEADER`        | Block has our holder but does not fuzzy-match the OLD template above the threshold. |
| `ERROR`                      | Per-file read/write error. Counted in `errors=` but does not by itself fail the script. |

#### Per-repo `reason` values (workflow level, not script)

| Reason                | Meaning |
|-----------------------|---------|
| `ok`                  | Replacement applied and pushed to the disposable branch. |
| `no_changes`          | Script ran but produced zero diffs (e.g. all files already migrated). |
| `already_generated`   | The disposable branch for today's date already exists on the remote; repo skipped. Delete the remote branch to re-run. |

---

## 7. Technical Design

### 7.1 Repository layout

```text
build_tools/
├── .github/workflows/
│   └── copyright-header.yml          # workflow_dispatch + push to feature/copyright on config.json
└── scripts/
    └── copyright-update/
        ├── replace_header.py         # CLI, Python 3 stdlib only
        ├── config.json               # push-trigger run list
        ├── templates/
        │   ├── old.license           # seeded from scripts/license_checker/header.license
        │   └── new.license           # the canonical new header
        ├── tests/
        │   ├── test_replace_header.py
        │   └── fixtures/             # exact_old.js, drifted_*, already_new.js, vendor_chromium.js, no_header.js, bom.js, crlf.h
        └── README.md                 # this document
```

The script has zero external dependencies: `argparse`, `os`, `re`,
`subprocess`, `difflib`, `fnmatch`, `json`, `sys`. `scripts/license_checker/`
is **not** a runtime dependency -- it is only the historical source of
the OLD template.

### 7.2 Python CLI

```text
python3 replace_header.py
  --repo-path PATH                # target repository (default: .)
  --old PATH                      # OLD template (default: <script_dir>/templates/old.license)
  --new PATH                      # NEW template (default: <script_dir>/templates/new.license)
  --report-dir PATH               # required; must be outside --repo-path
  --dry-run                       # local debugging only; do not write files
  --verbose                       # also print one line per `replaced` file (off by default)
  --similarity-threshold RATIO    # default 0.75, see Tuning below
  --idempotency-threshold RATIO   # default 1.0, see Tuning below
  --emit-targets CONFIG_PATH      # push-mode helper; print fanout lines from config.json
```

#### Exit codes

- `0` -- successful run, including `replaced=0`. Zero replacements is a
  normal outcome.
- non-zero -- unexpected runtime/tool error: missing repo path, missing
  templates, failed `git ls-files`, failed `os.makedirs(--report-dir)`,
  or `--report-dir` inside `--repo-path`.

Per-file decode/write errors are counted in the `errors=` total and
reported, but do not by themselves fail the script.

#### File enumeration

Files are discovered via `git -C <repo-path> ls-files`. Filesystem
walking is intentionally avoided so build artifacts and untracked
scratch files cannot leak into the scope.

The extension whitelist is hard-coded:

```text
.js .ts .tsx .jsx .mjs .cjs
.c  .h  .cpp .hpp
.cs .java .go .swift
.m  .mm
```

The built-in default excludes (applied via `fnmatch`):

```text
node_modules/**  vendor/**  Vendor/**  third_party/**  3dParty/**
external/**      deps/**    build/**   dist/**         out/**
**/*.min.js
```

### 7.3 Matching algorithm

```
span = find_candidate_block(file_text)
if span is None:
    return SKIP_NO_HEADER

block_norm = normalize_block(file_text[span.start:span.end])

# Idempotency FIRST. A file already matching NEW is left alone
# regardless of holder presence. Default threshold is 1.0 (exact match).
if similarity(block_norm, new_norm) >= idempotency_threshold:
    return SKIP_ALREADY_NEW

# Legal safety gate. Vendor headers structurally similar to ours are
# filtered here even when the OLD-similarity ratio is high.
if 'ascensio system sia' not in block_norm:
    return SKIP_VENDOR_UNKNOWN_HOLDER

if similarity(block_norm, old_norm) >= similarity_threshold:
    return REPLACE

return SKIP_NOT_OUR_HEADER
```

### 7.4 Tuning thresholds

The two thresholds are documented CLI parameters; defaults are also
top-of-file constants in [replace_header.py](./replace_header.py).

| Constant                | CLI flag                    | Default | Role |
|-------------------------|-----------------------------|---------|------|
| `SIMILARITY_THRESHOLD`  | `--similarity-threshold`    | `0.75`  | Minimum ratio against OLD to classify as `REPLACE`. |
| `IDEMPOTENCY_THRESHOLD` | `--idempotency-threshold`   | `1.0`   | Minimum ratio against NEW to classify as `SKIP_ALREADY_NEW`. |

#### When to lower `--similarity-threshold`

Look at the highlighted `not_our_header` section of the job summary
(or the `report.txt` content inside the runner workspace) for files
classified `SKIP_NOT_OUR_HEADER` -- they
have our holder but did not score above the threshold against OLD.

- If those files are historical variants of OUR header (refactored
  paragraphs, removed clauses) and you want to migrate them too, lower
  the threshold (try `0.65`-`0.70`).
- The holder-substring check is the actual safety gate, so this can
  be set quite permissively without admitting third-party blocks.

#### When to raise `--similarity-threshold`

Only if you spot a file that was rewritten but should not have been.
The holder check makes this rare in practice.

#### When `--idempotency-threshold` matters

`1.0` (default) means "exact match against NEW". Re-running on
already-migrated files yields `replaced=0 already_new=N`. Any drift
(e.g. someone hand-edits the canonical NEW template after a migration)
re-aligns the targets on the next run.

If you want migrated files to be left alone even when the canonical
template drifts, lower this to e.g. `0.99`.

### 7.5 BOM and line-ending preservation

- BOM (`\xef\xbb\xbf`) is detected on read, stripped before decoding,
  and re-prepended on write byte-for-byte.
- Line endings are detected by the presence of `\r\n` in the first
  8 KB of the raw bytes. The new block is rendered with the same
  newline as the surrounding file, so output never mixes LF and CRLF.
- Files are decoded as UTF-8 with `errors='replace'`. The original
  byte sequence is preserved everywhere except inside the replaced
  block.

### 7.6 Replacement

`text[:start] + new_block + text[end:]`, where `(start, end)` come
from `find_candidate_block`. The new block has its trailing newline
stripped and its line endings normalised to the file's detected
newline before substitution; this preserves whatever followed the
closing `*/` in the original file (typically a blank line and then
code).

### 7.7 Workflow flow per repository

1. Checkout `build_tools` into `./action`.
2. Resolve targets and `base_branch` (parse dispatch inputs OR
   `--emit-targets` from `config.json`).
3. For each target repo (sequential bash loop):
   1. Compute `<owner>-<repo>` slug and create
      `$GITHUB_WORKSPACE/reports/<slug>/`.
   2. Resolve `effective_base` (input value or `default_branch` via
      Gitea API with `READ_PAT`).
   3. Build `gen_branch = feature/copyright-<base-slug>-<date>`.
   4. `git clone` target via `READ_PAT`.
   5. `git fetch origin <effective_base>`.
   6. Probe remote `gen_branch` with
      `git ls-remote --exit-code --heads`. Exit 2 = branch missing
      (ok); exit 0 = present (fetch it for the lease); other =
      fail loudly.
   7. `git checkout -B gen_branch origin/effective_base`.
   8. Run `replace_header.py --repo-path target --report-dir <slug-dir>`.
   9. If `git diff --quiet`: `branch_created=false`, `reason=no_changes`.
   10. Otherwise: commit, swap `origin`'s push URL to
       `https://USERNAME:TOKEN@host/repo.git`, and
       `git push --force-with-lease origin HEAD:gen_branch`.
   11. Write per-repo summary to file; concatenate into job summary.
4. Upload the `reports` artifact with per-repo `report.txt` and `summary.md`
   files for the full audit trail.

#### Why a single bash loop instead of `matrix`

Gitea's act runner does not iterate
`matrix.<key>: ${{ fromJSON(needs.X.outputs.Y) }}` correctly -- matrix
values arrive as empty strings whether `matrix.<key>:` or
`matrix.include:` is used. The bash loop is a portable workaround;
plain GitHub Actions would handle the matrix form fine.

#### Why the bash uses `set +e` at the top + subshell with `set -euo pipefail`

The act runner invokes `bash -e -o pipefail`. With parent `set -e`
on, a failed `(...)` subshell aborts the entire step before
`rc=$?` can be captured. We turn parent errexit off and run each
per-repo block in a subshell with its own strict mode. This pattern
gives reliable per-iteration error isolation.

### 7.8 Tests

`python3 -m unittest discover scripts/copyright-update/tests` -- no
external dependencies, runs in well under two seconds.

Coverage groups:

- `FindCandidateBlockTests` -- block extraction edge cases.
- `HolderCheckTests` -- holder presence in OLD; absence in vendor.
- `ClassifyTests` -- exact, drifted-year, drifted-address, already-new,
  vendor, no-header.
- `ProcessFileTests` -- byte-for-byte replacement, idempotency, vendor
  not touched, no-header not touched, BOM preserved, CRLF preserved,
  dry-run never writes.
- `ReportDirGuardUnitTests` -- outside repo ok; equal/nested rejected;
  siblings with similar prefix ok.
- `CLITests` -- reports written outside repo; zero replacements exit 0;
  missing template / repo / report-dir-inside-repo exit non-zero;
  vendor path excludes.
- `EmitTargetsTests` -- `--emit-targets` parses `config.json` and
  prints `repos=`/`base_branch=`/`enabled=` lines correctly; bad
  inputs exit non-zero.

### 7.9 Verification (end-to-end, manual)

1. **Local dry run on one cloned repo**:

   ```text
   git clone <one-target> /tmp/t
   mkdir -p /tmp/reports/t
   python3 scripts/copyright-update/replace_header.py \
     --repo-path /tmp/t --report-dir /tmp/reports/t --dry-run
   ```

   Inspect `/tmp/reports/t/report.txt` and confirm `/tmp/t` is
   unchanged.

2. **Local wet run**: drop `--dry-run`; `git -C /tmp/t diff` should
   show only header-block changes; spot-check three files (one `.js`,
   one `.cpp`, one `.cs`).

3. **Idempotency**: re-run wet on the now-migrated tree; expect
   `replaced=0`, large `already_new=N`, exit 0.

4. **Vendor safety**:
   `git -C /tmp/t diff -- '*third_party*' '*vendor*'` must be empty.
   Manually inspect one known vendor file.

5. **Threshold tuning experiment**: re-run with
   `--similarity-threshold 0.65` and compare the file counts in
   `report.txt` -- this shows how many additional drifted variants
   would be migrated by lowering the threshold.

6. **Unit tests**:
   `python3 -m unittest discover scripts/copyright-update/tests` --
   all green.

7. **Workflow dispatch** against one small repository: a
   `feature/copyright-<slug>-YYYY-MM-DD` branch is pushed; the job
   summary lists `branch_created=true` and the per-repo stats with
   `not_our_header` highlighted; the commit message body carries the
   same stats.

8. **Same-day re-run**: dispatch the same set again; remote branch
   is overwritten via `--force-with-lease`; no leftover commits from
   the previous run remain.

9. **`base_branch` end-to-end**: dispatch with
   `base_branch = release/v9.4.0` against a repo that has that branch;
   verify the pushed branch is
   `feature/copyright-release-v9.4.0-YYYY-MM-DD` and is based on the
   release branch, not the default branch.
