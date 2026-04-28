#!/usr/bin/env python3
"""
Copyright year bump tool for ONLYOFFICE repositories.

Finds files with Ascensio System SIA copyright headers and updates
the end year to the target year. Only modifies lines that strictly
match the expected pattern. Does not add missing headers or fix
invalid ones.

Usage:
  python copyright_year_bump.py --year 2026 --mode fix
  python copyright_year_bump.py --year 2026 --mode dry-run
  python copyright_year_bump.py --year 2026 --mode check
  python copyright_year_bump.py --year 2026 --mode fix --since 2025-01-01
"""

import argparse
import os
import re
import subprocess
import sys

# Strict regex: matches only "(c) Copyright Ascensio System SIA YYYY-YYYY"
# with any comment prefix (* // # ; <!-- etc.)
COPYRIGHT_RE = re.compile(
    r'(?P<before>.*\(c\)\s*Copyright\s+Ascensio\s+System\s+SIA\s+(?P<from>\d{4})-)(?P<year>\d{4})(?P<after>.*)'
)

# How many lines from the top of the file to check for the copyright header
HEADER_SCAN_LINES = 5

# Source file extensions to process
EXTENSIONS = frozenset({
    '.js', '.ts', '.tsx', '.jsx', '.mjs', '.cjs',
    '.h', '.c', '.hpp', '.cpp', '.hxx', '.cxx',
    '.cs', '.m', '.mm', '.swift', '.xcconfig',
    '.py', '.sh', '.java', '.go', '.license',
})

BOM = b'\xef\xbb\xbf'


def git_tracked_files():
    """Return list of tracked files via git ls-files."""
    result = subprocess.run(
        ['git', 'ls-files'],
        capture_output=True, text=True, check=True
    )
    return [f for f in result.stdout.splitlines() if f]


def git_files_since(since_date):
    """Return set of files with commits since the given date."""
    result = subprocess.run(
        ['git', 'log', f'--since={since_date}', '--name-only', '--pretty=format:'],
        capture_output=True, text=True, check=True
    )
    return set(f for f in result.stdout.splitlines() if f)


def is_binary(data, check_bytes=8192):
    """Check if data looks binary (contains null bytes)."""
    return b'\x00' in data[:check_bytes]


def process_file(filepath, target_year, dry_run=False):
    """
    Process a single file. Returns a status string:
      'updated'       - file was updated (or would be in dry-run)
      'current'       - already has the target year
      'no_match'      - no matching copyright line in header area
      'future_year'   - end year is ahead of target year (warning)
      'binary'        - binary file, skipped
      'error'         - could not read/write
    """
    try:
        with open(filepath, 'rb') as f:
            raw = f.read()
    except (OSError, IOError):
        return 'error'

    if is_binary(raw):
        return 'binary'

    has_bom = raw.startswith(BOM)
    content = raw[len(BOM):] if has_bom else raw

    # Detect line ending
    if b'\r\n' in content:
        newline = '\r\n'
        lines = content.decode('utf-8', errors='replace').split('\r\n')
    else:
        newline = '\n'
        lines = content.decode('utf-8', errors='replace').split('\n')

    modified = False
    status = 'no_match'

    scan_limit = min(HEADER_SCAN_LINES, len(lines))
    for i in range(scan_limit):
        m = COPYRIGHT_RE.match(lines[i])
        if m:
            end_year = int(m.group('year'))
            if end_year == target_year:
                return 'current'
            if end_year > target_year:
                return 'future_year'
            if end_year < target_year:
                lines[i] = m.group('before') + str(target_year) + m.group('after')
                modified = True
                status = 'updated'
            break  # only process the first copyright line found

    if not modified:
        return status

    if dry_run:
        return 'updated'

    # Write back preserving BOM and line endings
    new_content = newline.join(lines).encode('utf-8')
    if has_bom:
        new_content = BOM + new_content

    try:
        with open(filepath, 'wb') as f:
            f.write(new_content)
    except (OSError, IOError):
        return 'error'

    return 'updated'


def main():
    parser = argparse.ArgumentParser(description='Copyright year bump for Ascensio System SIA')
    parser.add_argument('--year', type=int, required=True, help='Target copyright year')
    parser.add_argument('--mode', choices=['fix', 'dry-run', 'check'], default='fix',
                        help='fix=update files, dry-run=report only, check=exit 1 if outdated')
    parser.add_argument('--since', type=str, default=None,
                        help='Only process files with commits since this date (YYYY-MM-DD)')
    args = parser.parse_args()

    target_year = args.year
    dry_run = args.mode in ('dry-run', 'check')

    # Get file list
    all_files = git_tracked_files()

    # Filter by extension
    candidates = [f for f in all_files if os.path.splitext(f)[1] in EXTENSIONS]

    # Optional: filter by git history
    if args.since:
        modified_files = git_files_since(args.since)
        candidates = [f for f in candidates if f in modified_files]

    # Process files
    stats = {'updated': 0, 'current': 0, 'no_match': 0,
             'future_year': 0, 'binary': 0, 'error': 0}
    warnings = []
    updated_files = []

    for filepath in candidates:
        result = process_file(filepath, target_year, dry_run=dry_run)
        stats[result] += 1
        if result == 'updated':
            updated_files.append(filepath)
        if result == 'future_year':
            warnings.append(f'  WARN future year: {filepath}')
        if result == 'error':
            warnings.append(f'  WARN error reading: {filepath}')

    # Report
    mode_label = {'fix': 'fix', 'dry-run': 'dry-run', 'check': 'check'}[args.mode]
    print(f'Copyright year bump → {target_year} (mode: {mode_label})')
    if args.since:
        print(f'Only files changed since: {args.since}')
    print(f'Scanned:         {len(candidates)} files')
    print(f'Updated:         {stats["updated"]} files')
    print(f'Already current: {stats["current"]} files')
    print(f'No match:        {stats["no_match"]} files')
    if stats['future_year']:
        print(f'Future year:     {stats["future_year"]} files')
    if stats['binary']:
        print(f'Binary skipped:  {stats["binary"]} files')
    if stats['error']:
        print(f'Errors:          {stats["error"]} files')
    if warnings:
        print(f'Warnings:        {len(warnings)}')
        for w in warnings:
            print(w)
    if updated_files and args.mode == 'dry-run':
        print('\nFiles that would be updated:')
        for f in updated_files:
            print(f'  {f}')

    # Exit code
    if args.mode == 'check' and stats['updated'] > 0:
        print(f'\n{stats["updated"]} files need updating.')
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
