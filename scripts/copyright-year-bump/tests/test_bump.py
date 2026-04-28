#!/usr/bin/env python3
"""Unit tests for copyright_year_bump.py"""

import os
import shutil
import sys
import tempfile
import unittest

# Add parent directory to path so we can import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from copyright_year_bump import process_file, COPYRIGHT_RE, BOM

FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')


class TestRegex(unittest.TestCase):
    """Test the copyright regex pattern."""

    def test_block_comment(self):
        m = COPYRIGHT_RE.match(' * (c) Copyright Ascensio System SIA 2010-2024')
        self.assertIsNotNone(m)
        self.assertEqual(m.group('year'), '2024')

    def test_line_comment(self):
        m = COPYRIGHT_RE.match('// (c) Copyright Ascensio System SIA 2010-2025')
        self.assertIsNotNone(m)
        self.assertEqual(m.group('year'), '2025')

    def test_hash_comment(self):
        m = COPYRIGHT_RE.match('# (c) Copyright Ascensio System SIA 2010-2023')
        self.assertIsNotNone(m)
        self.assertEqual(m.group('year'), '2023')

    def test_no_match_vendor(self):
        m = COPYRIGHT_RE.match(' * Copyright The Chromium Authors 2010-2024')
        self.assertIsNone(m)

    def test_no_match_without_c_marker(self):
        m = COPYRIGHT_RE.match(' * Copyright Ascensio System SIA 2010-2024')
        self.assertIsNone(m)

    def test_no_match_plain_text(self):
        m = COPYRIGHT_RE.match('This is just regular code')
        self.assertIsNone(m)

    def test_replacement(self):
        line = ' * (c) Copyright Ascensio System SIA 2010-2024'
        m = COPYRIGHT_RE.match(line)
        result = m.group('before') + '2026' + m.group('after')
        self.assertEqual(result, ' * (c) Copyright Ascensio System SIA 2010-2026')

    def test_preserves_suffix(self):
        line = ' * (c) Copyright Ascensio System SIA 2010-2024  '
        m = COPYRIGHT_RE.match(line)
        result = m.group('before') + '2026' + m.group('after')
        self.assertEqual(result, ' * (c) Copyright Ascensio System SIA 2010-2026  ')


class TestProcessFile(unittest.TestCase):
    """Test process_file on fixture files."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def _copy_fixture(self, name):
        """Copy a fixture file to tmpdir and return its path."""
        src = os.path.join(FIXTURES_DIR, name)
        dst = os.path.join(self.tmpdir, name)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        return dst

    def test_outdated_2024_updated(self):
        path = self._copy_fixture('outdated_2024.js')
        result = process_file(path, 2026)
        self.assertEqual(result, 'updated')
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('2010-2026', content)
        self.assertNotIn('2010-2024', content)

    def test_outdated_2025_updated(self):
        path = self._copy_fixture('outdated_2025.js')
        result = process_file(path, 2026)
        self.assertEqual(result, 'updated')
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('2010-2026', content)

    def test_already_current(self):
        path = self._copy_fixture('already_current.js')
        result = process_file(path, 2026)
        self.assertEqual(result, 'current')

    def test_future_year(self):
        path = self._copy_fixture('future_year.js')
        result = process_file(path, 2026)
        self.assertEqual(result, 'future_year')

    def test_no_copyright(self):
        path = self._copy_fixture('no_copyright.js')
        result = process_file(path, 2026)
        self.assertEqual(result, 'no_match')

    def test_vendor_not_touched(self):
        path = self._copy_fixture('vendor_copyright.js')
        with open(path, 'rb') as f:
            before = f.read()
        result = process_file(path, 2026)
        self.assertEqual(result, 'no_match')
        with open(path, 'rb') as f:
            after = f.read()
        self.assertEqual(before, after)

    def test_cpp_header(self):
        path = self._copy_fixture('outdated_cpp.h')
        result = process_file(path, 2026)
        self.assertEqual(result, 'updated')
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('2010-2026', content)
        self.assertIn('#pragma once', content)

    def test_shell_comment(self):
        path = self._copy_fixture('outdated_shell.sh')
        result = process_file(path, 2026)
        self.assertEqual(result, 'updated')
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('2010-2026', content)
        self.assertIn('#!/bin/bash', content)

    def test_line_comment(self):
        path = self._copy_fixture('outdated_line_comment.js')
        result = process_file(path, 2026)
        self.assertEqual(result, 'updated')
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('2010-2026', content)

    def test_bom_preserved(self):
        path = self._copy_fixture('bom_utf8.js')
        result = process_file(path, 2026)
        self.assertEqual(result, 'updated')
        with open(path, 'rb') as f:
            raw = f.read()
        self.assertTrue(raw.startswith(BOM), 'BOM was not preserved')
        self.assertIn(b'2010-2026', raw)

    def test_crlf_preserved(self):
        path = self._copy_fixture('crlf.js')
        result = process_file(path, 2026)
        self.assertEqual(result, 'updated')
        with open(path, 'rb') as f:
            raw = f.read()
        self.assertIn(b'2010-2026', raw)
        self.assertIn(b'\r\n', raw)
        # Ensure no bare \n (all newlines should be \r\n)
        content_without_crlf = raw.replace(b'\r\n', b'<CRLF>')
        self.assertNotIn(b'\n', content_without_crlf, 'Found bare \\n — CRLF was not preserved')

    def test_dry_run_does_not_write(self):
        path = self._copy_fixture('outdated_2024.js')
        with open(path, 'rb') as f:
            before = f.read()
        result = process_file(path, 2026, dry_run=True)
        self.assertEqual(result, 'updated')
        with open(path, 'rb') as f:
            after = f.read()
        self.assertEqual(before, after, 'dry-run should not modify the file')

    def test_idempotent(self):
        path = self._copy_fixture('outdated_2024.js')
        process_file(path, 2026)
        with open(path, 'rb') as f:
            first_pass = f.read()
        result = process_file(path, 2026)
        self.assertEqual(result, 'current')
        with open(path, 'rb') as f:
            second_pass = f.read()
        self.assertEqual(first_pass, second_pass, 'Second run should not change file')

    def test_only_year_changes(self):
        """Verify that ONLY the year digits change, nothing else."""
        path = self._copy_fixture('outdated_2024.js')
        with open(path, 'r', encoding='utf-8') as f:
            before_lines = f.readlines()
        process_file(path, 2026)
        with open(path, 'r', encoding='utf-8') as f:
            after_lines = f.readlines()
        self.assertEqual(len(before_lines), len(after_lines))
        diffs = 0
        for b, a in zip(before_lines, after_lines):
            if b != a:
                diffs += 1
                # The only difference should be 2024 -> 2026
                self.assertEqual(b.replace('2024', '2026'), a)
        self.assertEqual(diffs, 1, 'Exactly one line should differ')

    def test_agpl_body_not_changed(self):
        """The AGPL version 3, Section 7(a), etc. numbers must not change."""
        path = self._copy_fixture('outdated_2024.js')
        with open(path, 'r', encoding='utf-8') as f:
            before = f.read()
        process_file(path, 2026)
        with open(path, 'r', encoding='utf-8') as f:
            after = f.read()
        # All lines except the copyright line must be identical
        before_body = before.split('\n')[2:]  # skip first 2 lines (/* and copyright)
        after_body = after.split('\n')[2:]
        self.assertEqual(before_body, after_body)


if __name__ == '__main__':
    unittest.main()
