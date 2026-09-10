#!/usr/bin/env python3
"""Replace a known OLD copyright header with a known NEW copyright header.

Scope is intentionally narrow: this tool does not add missing headers, does
not fix invalid headers, does not handle non-C-style comments, and does not
touch third-party copyrights. See README.md for the full list of non-goals.
"""

import argparse
import difflib
import fnmatch
import json
import os
import re
import subprocess
import sys


EXTENSIONS = frozenset({
    '.js', '.ts', '.tsx', '.jsx', '.mjs', '.cjs',
    '.c', '.h', '.cpp', '.hpp',
    '.cs', '.java', '.go', '.swift',
    '.m', '.mm',
})

DEFAULT_EXCLUDES = (
    'node_modules/**',
    'vendor/**',
    'Vendor/**',
    'third_party/**',
    '3dParty/**',
    'external/**',
    'deps/**',
    'build/**',
    'dist/**',
    'out/**',
    '**/*.min.js',
)

BOM = b'\xef\xbb\xbf'
HOLDER_SUBSTRING = 'ascensio system sia'

# Defaults for the two fuzzy-match thresholds. Both are exposed on the CLI
# (--similarity-threshold, --idempotency-threshold) so they can be tuned
# per-run without editing the source.
#
# SIMILARITY_THRESHOLD: minimum difflib ratio against the OLD template
# required to classify a candidate block as REPLACE. Lower values catch
# more drifted historical variants of our header at the cost of admitting
# unrelated AGPL-style boilerplate. The holder-substring check
# (HOLDER_SUBSTRING below) is a separate gate that prevents vendor blocks
# from being rewritten regardless of similarity, so this can be set quite
# permissively.
#
# IDEMPOTENCY_THRESHOLD: minimum difflib ratio against the NEW template
# required to classify a block as SKIP_ALREADY_NEW. We write NEW byte-for-
# byte and normalize_block is deterministic, so a freshly migrated file
# reads back at ratio EXACTLY 1.0. Setting this to 1.0 means "if anything
# differs from the canonical NEW template, re-align it on the next run".
SIMILARITY_THRESHOLD = 0.75
IDEMPOTENCY_THRESHOLD = 1.0

MAX_BLOCK_BYTES = 32 * 1024

# Default owner used by --emit-targets when a config entry is a bare repo name.
# Matches the constant inlined into the workflow's dispatch fanout path.
DEFAULT_OWNER = 'ONLYOFFICE'

CLASS_REPLACE = 'REPLACE'
CLASS_SKIP_NO_HEADER = 'SKIP_NO_HEADER'
CLASS_SKIP_ALREADY_NEW = 'SKIP_ALREADY_NEW'
CLASS_SKIP_VENDOR = 'SKIP_VENDOR_UNKNOWN_HOLDER'
CLASS_SKIP_NOT_OURS = 'SKIP_NOT_OUR_HEADER'

_DECORATION_RE = re.compile(r'^[\s*=\-_/]+$')
_WHITESPACE_RE = re.compile(r'\s+')


def find_candidate_block(text):
    """Return (start, end_exclusive) of the first top-of-file /* ... */ block.

    Skips leading blank lines. The first non-blank line must start (after
    optional whitespace) with `/*`. End is the index just past the first `*/`
    after the opening. Returns None if no plausible block exists, or if the
    candidate block exceeds MAX_BLOCK_BYTES (defensive).
    """
    i = 0
    n = len(text)
    while i < n:
        # Find end of current line.
        j = text.find('\n', i)
        line_end = n if j == -1 else j
        line = text[i:line_end]
        stripped = line.strip()
        if stripped == '':
            i = line_end + 1
            continue
        # First non-blank line must begin (after optional whitespace) with /*.
        lstripped = line.lstrip()
        if not lstripped.startswith('/*'):
            return None
        start = i + (len(line) - len(lstripped))
        close = text.find('*/', start + 2)
        if close == -1:
            return None
        end = close + 2
        if end - start > MAX_BLOCK_BYTES:
            return None
        return (start, end)
    return None


def normalize_block(block):
    """Strip comment decoration and whitespace for fuzzy comparison.

    Lowercases; per line removes leading whitespace, leading `*`, and one
    space; drops pure decoration lines; collapses runs of whitespace within
    a line; rejoins with `\\n`; trims.
    """
    out_lines = []
    for raw in block.splitlines():
        line = raw.strip()
        if line.startswith('*'):
            line = line[1:]
            if line.startswith(' '):
                line = line[1:]
        line = line.strip()
        if line == '' or _DECORATION_RE.match(line):
            continue
        line = _WHITESPACE_RE.sub(' ', line)
        out_lines.append(line.lower())
    return '\n'.join(out_lines).strip()


def similarity(a_norm, b_norm):
    return difflib.SequenceMatcher(None, a_norm, b_norm, autojunk=False).ratio()


def classify(file_text, old_norm, new_norm,
             similarity_threshold=SIMILARITY_THRESHOLD,
             idempotency_threshold=IDEMPOTENCY_THRESHOLD):
    span = find_candidate_block(file_text)
    if span is None:
        return CLASS_SKIP_NO_HEADER, None
    block_text = file_text[span[0]:span[1]]
    block_norm = normalize_block(block_text)
    # Idempotency check first: a file already containing NEW is left alone.
    if similarity(block_norm, new_norm) >= idempotency_threshold:
        return CLASS_SKIP_ALREADY_NEW, span
    # Legal safety gate: we must see our holder substring to rewrite.
    if HOLDER_SUBSTRING not in block_norm:
        return CLASS_SKIP_VENDOR, span
    if similarity(block_norm, old_norm) >= similarity_threshold:
        return CLASS_REPLACE, span
    return CLASS_SKIP_NOT_OURS, span


def detect_bom(raw):
    if raw.startswith(BOM):
        return True, raw[len(BOM):]
    return False, raw


def detect_newline(raw_bytes, head=8192):
    return '\r\n' if b'\r\n' in raw_bytes[:head] else '\n'


def render_new_block(new_template_text, newline):
    """Return the new block normalised to the target newline.

    The template on disk uses LF; output must match the destination file's
    line endings to avoid mixed endings.
    """
    body = new_template_text
    # Strip trailing newline from the template so we control what follows.
    if body.endswith('\n'):
        body = body[:-1]
    if body.endswith('\r'):
        body = body[:-1]
    lines = body.split('\n')
    return newline.join(lines)


def replace_block(file_text, span, new_block):
    start, end = span
    return file_text[:start] + new_block + file_text[end:]


def list_target_files(repo_path, extra_excludes=()):
    """Return source files tracked by git, filtered by extension and excludes."""
    try:
        proc = subprocess.run(
            ['git', '-C', repo_path, 'ls-files'],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError('git executable not found on PATH') from exc
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or '').strip()
        raise RuntimeError(
            'git ls-files failed in {!r}: {}'.format(repo_path, stderr)
        ) from exc

    excludes = tuple(DEFAULT_EXCLUDES) + tuple(extra_excludes)
    out = []
    for rel in proc.stdout.splitlines():
        rel = rel.strip()
        if not rel:
            continue
        _, ext = os.path.splitext(rel)
        if ext not in EXTENSIONS:
            continue
        # Normalise to forward slashes for fnmatch.
        rel_norm = rel.replace('\\', '/')
        if any(fnmatch.fnmatch(rel_norm, pat) for pat in excludes):
            continue
        out.append(rel)
    out.sort()
    return out


def process_file(abs_path, old_norm, new_norm, new_template_text, dry_run,
                 similarity_threshold=SIMILARITY_THRESHOLD,
                 idempotency_threshold=IDEMPOTENCY_THRESHOLD):
    """Process a single file. Returns (classification, changed_bool, error_msg)."""
    try:
        with open(abs_path, 'rb') as fh:
            raw = fh.read()
    except OSError as exc:
        return ('ERROR', False, 'read failed: {}'.format(exc))

    has_bom, content = detect_bom(raw)
    newline = detect_newline(content)
    try:
        text = content.decode('utf-8', errors='replace')
    except Exception as exc:  # pragma: no cover - decode with replace shouldn't raise
        return ('ERROR', False, 'decode failed: {}'.format(exc))

    cls, span = classify(text, old_norm, new_norm,
                        similarity_threshold=similarity_threshold,
                        idempotency_threshold=idempotency_threshold)
    if cls != CLASS_REPLACE:
        return (cls, False, None)

    new_block = render_new_block(new_template_text, newline)
    new_text = replace_block(text, span, new_block)
    if new_text == text:
        return (CLASS_SKIP_ALREADY_NEW, False, None)

    if dry_run:
        return (cls, True, None)

    try:
        encoded = new_text.encode('utf-8')
        with open(abs_path, 'wb') as fh:
            if has_bom:
                fh.write(BOM)
            fh.write(encoded)
    except OSError as exc:
        return ('ERROR', False, 'write failed: {}'.format(exc))

    return (cls, True, None)


def load_template(path):
    with open(path, 'rb') as fh:
        raw = fh.read()
    _, body = detect_bom(raw)
    return body.decode('utf-8', errors='replace')


def emit_targets(config_path):
    """Push-mode fanout: read config.json, print GITHUB_OUTPUT-style lines.

    Output (stdout):
        repos=<json array of "owner/repo" strings>
        base_branch=<string>

    Used only by the workflow's push trigger. workflow_dispatch keeps its own
    inline parser in YAML. The script never performs replacements in this mode.
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as fh:
            config = json.load(fh)
    except FileNotFoundError:
        print('error: --emit-targets config not found: {}'.format(config_path), file=sys.stderr)
        return 2
    except (OSError, ValueError) as exc:
        print('error: cannot read --emit-targets config {}: {}'.format(config_path, exc), file=sys.stderr)
        return 2

    if not isinstance(config, dict):
        print('error: config root must be a JSON object', file=sys.stderr)
        return 2

    raw_repos = config.get('repositories', [])
    if not isinstance(raw_repos, list):
        print('error: config "repositories" must be an array', file=sys.stderr)
        return 2

    repos = []
    for entry in raw_repos:
        if not isinstance(entry, str):
            print('error: config "repositories" entries must be strings', file=sys.stderr)
            return 2
        name = entry.strip()
        if not name:
            continue
        if '/' not in name:
            name = '{}/{}'.format(DEFAULT_OWNER, name)
        repos.append(name)

    base_branch = config.get('base_branch', '')
    if base_branch is None:
        base_branch = ''
    if not isinstance(base_branch, str):
        print('error: config "base_branch" must be a string', file=sys.stderr)
        return 2

    print('repos=' + json.dumps(repos))
    print('base_branch=' + base_branch.strip())
    print('enabled=' + ('true' if repos else 'false'))
    return 0


def report_dir_inside_repo(repo_path, report_dir):
    """Return True if report_dir resolves to the repo or to a path inside it.

    Uses realpath to follow symlinks, then commonpath to compare. Different
    drives on Windows raise ValueError from commonpath, which means the paths
    cannot share a common ancestor -- the report dir is therefore safely
    outside the repo.
    """
    repo_abs = os.path.realpath(repo_path)
    report_abs = os.path.realpath(report_dir)
    if repo_abs == report_abs:
        return True
    try:
        common = os.path.commonpath([repo_abs, report_abs])
    except ValueError:
        return False
    return common == repo_abs


def write_reports(report_dir, totals, per_file, dry_run):
    os.makedirs(report_dir, exist_ok=True)
    txt_path = os.path.join(report_dir, 'report.txt')
    verb = 'would_replace' if dry_run else 'replaced'

    lines = []
    for entry in per_file:
        if entry['classification'] == CLASS_REPLACE:
            lines.append('{}: {}'.format(verb, entry['path']))
        elif entry['classification'] == 'ERROR':
            lines.append('error: {} ({})'.format(entry['path'], entry.get('error', '')))
        elif entry['classification'] == CLASS_SKIP_VENDOR:
            lines.append('vendor: {}'.format(entry['path']))
        elif entry['classification'] == CLASS_SKIP_NOT_OURS:
            lines.append('not_our_header: {}'.format(entry['path']))
    lines.append('')
    lines.append('scanned={}'.format(totals['scanned']))
    lines.append('replaced={}'.format(totals['replaced']))
    lines.append('already_new={}'.format(totals['already_new']))
    lines.append('no_header={}'.format(totals['no_header']))
    lines.append('vendor={}'.format(totals['vendor']))
    lines.append('not_our_header={}'.format(totals['not_our_header']))
    lines.append('errors={}'.format(totals['errors']))

    with open(txt_path, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + '\n')


def parse_args(argv):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(
        description='Replace OLD copyright header with NEW across a repository.',
    )
    parser.add_argument('--repo-path', default='.', help='Path to target repository.')
    parser.add_argument(
        '--old',
        default=os.path.join(script_dir, 'templates', 'old.license'),
        help='Path to OLD template file.',
    )
    parser.add_argument(
        '--new',
        default=os.path.join(script_dir, 'templates', 'new.license'),
        help='Path to NEW template file.',
    )
    parser.add_argument(
        '--report-dir',
        required=False,
        help='Directory for report.txt (must be outside the target repo). '
             'Required for the default replacement mode; ignored when --emit-targets is set.',
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Do not write files; report what would change. Local debugging only.',
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print one line per `replaced` file to stdout. Off by default to keep the '
             'workflow run log small for repos with thousands of files; the totals '
             'line is always printed. `not_our_header` and error files are always '
             'printed because they are actionable.',
    )
    parser.add_argument(
        '--similarity-threshold',
        type=float,
        default=SIMILARITY_THRESHOLD,
        metavar='RATIO',
        help='Minimum difflib ratio against the OLD template to classify a candidate '
             'block as REPLACE. Holder-substring check (Ascensio System SIA) is the '
             'primary safety gate; this threshold can be set permissively. '
             'Default: %(default)s.',
    )
    parser.add_argument(
        '--idempotency-threshold',
        type=float,
        default=IDEMPOTENCY_THRESHOLD,
        metavar='RATIO',
        help='Minimum difflib ratio against the NEW template to classify a block as '
             'SKIP_ALREADY_NEW. Files written by this script read back at ratio 1.0, '
             'so a value of 1.0 (default) means "re-align on every drift". '
             'Default: %(default)s.',
    )
    parser.add_argument(
        '--emit-targets',
        metavar='CONFIG_PATH',
        help='Push-mode helper for the workflow: parse the config.json at this path and '
             'print GITHUB_OUTPUT-style "repos=..." and "base_branch=..." lines. '
             'When set, the script does not perform replacements and other flags are ignored.',
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    # Push-mode helper: parse config.json and emit fanout lines. Does not
    # touch any repository and ignores the replacement-mode flags.
    if args.emit_targets:
        return emit_targets(args.emit_targets)

    if not args.report_dir:
        print('error: --report-dir is required (unless --emit-targets is used).', file=sys.stderr)
        return 2
    if not os.path.isdir(args.repo_path):
        print('error: --repo-path does not exist or is not a directory: {}'.format(args.repo_path), file=sys.stderr)
        return 2
    if not os.path.isfile(args.old):
        print('error: --old template not found: {}'.format(args.old), file=sys.stderr)
        return 2
    if not os.path.isfile(args.new):
        print('error: --new template not found: {}'.format(args.new), file=sys.stderr)
        return 2
    if report_dir_inside_repo(args.repo_path, args.report_dir):
        print(
            'error: --report-dir ({}) must be outside --repo-path ({}) to keep '
            'report files out of the target repository.'.format(
                args.report_dir, args.repo_path
            ),
            file=sys.stderr,
        )
        return 2
    try:
        os.makedirs(args.report_dir, exist_ok=True)
    except OSError as exc:
        print('error: cannot create --report-dir {}: {}'.format(args.report_dir, exc), file=sys.stderr)
        return 2

    old_text = load_template(args.old)
    new_text = load_template(args.new)
    old_norm = normalize_block(old_text)
    new_norm = normalize_block(new_text)

    try:
        files = list_target_files(args.repo_path)
    except RuntimeError as exc:
        print('error: {}'.format(exc), file=sys.stderr)
        return 2

    totals = {
        'scanned': 0,
        'replaced': 0,
        'already_new': 0,
        'no_header': 0,
        'vendor': 0,
        'not_our_header': 0,
        'errors': 0,
    }
    per_file = []
    for rel in files:
        abs_path = os.path.join(args.repo_path, rel)
        cls, changed, err = process_file(
            abs_path, old_norm, new_norm, new_text, args.dry_run,
            similarity_threshold=args.similarity_threshold,
            idempotency_threshold=args.idempotency_threshold,
        )
        totals['scanned'] += 1
        entry = {'path': rel, 'classification': cls, 'changed': bool(changed)}
        if cls == CLASS_REPLACE:
            totals['replaced'] += 1
        elif cls == CLASS_SKIP_ALREADY_NEW:
            totals['already_new'] += 1
        elif cls == CLASS_SKIP_NO_HEADER:
            totals['no_header'] += 1
        elif cls == CLASS_SKIP_VENDOR:
            totals['vendor'] += 1
        elif cls == CLASS_SKIP_NOT_OURS:
            totals['not_our_header'] += 1
        elif cls == 'ERROR':
            totals['errors'] += 1
            entry['error'] = err
        per_file.append(entry)
        if cls == CLASS_REPLACE and args.verbose:
            verb = 'would replace' if args.dry_run else 'replaced'
            print('{}: {}'.format(verb, rel))
        elif cls == CLASS_SKIP_NOT_OURS:
            # Echo to stdout so the workflow run log carries the full list
            # of files that need manual review or threshold tuning.
            # `not_our_header` is typically a small subset (a few percent of
            # scanned files) so stdout volume stays bounded.
            print('not_our_header: {}'.format(rel))
        elif cls == 'ERROR':
            print('error: {}: {}'.format(rel, err), file=sys.stderr)

    write_reports(args.report_dir, totals, per_file, args.dry_run)

    summary = (
        'scanned={scanned} replaced={replaced} already_new={already_new} '
        'no_header={no_header} vendor={vendor} not_our_header={not_our_header} '
        'errors={errors}'
    ).format(**totals)
    print(summary)
    return 0


if __name__ == '__main__':
    sys.exit(main())
