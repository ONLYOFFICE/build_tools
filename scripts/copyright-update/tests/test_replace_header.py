"""Unit tests for replace_header.py."""

import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIXTURES = os.path.join(HERE, 'fixtures')

sys.path.insert(0, ROOT)
import replace_header  # noqa: E402


OLD_TEMPLATE_PATH = os.path.join(ROOT, 'templates', 'old.license')
NEW_TEMPLATE_PATH = os.path.join(ROOT, 'templates', 'new.license')


def read_bytes(path):
    with open(path, 'rb') as fh:
        return fh.read()


def load_template_text(path):
    return replace_header.load_template(path)


def make_git_repo(work_dir, files):
    """Init a git repo at work_dir; copy fixture files into it; commit them."""
    subprocess.run(['git', 'init', '-q'], cwd=work_dir, check=True)
    subprocess.run(['git', 'config', 'user.email', 'test@test'], cwd=work_dir, check=True)
    subprocess.run(['git', 'config', 'user.name', 'test'], cwd=work_dir, check=True)
    for src_name, dst_rel in files:
        src = os.path.join(FIXTURES, src_name)
        dst = os.path.join(work_dir, dst_rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
    subprocess.run(['git', 'add', '-A'], cwd=work_dir, check=True)
    subprocess.run(['git', '-c', 'commit.gpgsign=false', 'commit', '-q', '-m', 'init'], cwd=work_dir, check=True)


class FindCandidateBlockTests(unittest.TestCase):
    def test_leading_blanks_then_block(self):
        text = '\n\n/*\n * hi\n */\ncode\n'
        span = replace_header.find_candidate_block(text)
        self.assertIsNotNone(span)
        self.assertEqual(text[span[0]:span[1]], '/*\n * hi\n */')

    def test_first_of_two_blocks(self):
        text = '/* first */\n/* second */\n'
        span = replace_header.find_candidate_block(text)
        self.assertEqual(text[span[0]:span[1]], '/* first */')

    def test_line_comment_only_rejected(self):
        text = '// not a block\nfunction f(){}\n'
        self.assertIsNone(replace_header.find_candidate_block(text))

    def test_unterminated_block_rejected(self):
        text = '/*\n * never closed\n'
        self.assertIsNone(replace_header.find_candidate_block(text))

    def test_empty_file(self):
        self.assertIsNone(replace_header.find_candidate_block(''))

    def test_block_with_leading_whitespace(self):
        text = '   /*\n * hi\n */\n'
        span = replace_header.find_candidate_block(text)
        self.assertIsNotNone(span)
        self.assertTrue(text[span[0]:span[1]].startswith('/*'))


class HolderCheckTests(unittest.TestCase):
    def test_holder_present_in_old(self):
        old_text = load_template_text(OLD_TEMPLATE_PATH)
        norm = replace_header.normalize_block(old_text)
        self.assertIn('ascensio system sia', norm)

    def test_holder_absent_in_chromium(self):
        block = read_bytes(os.path.join(FIXTURES, 'vendor_chromium.js')).decode('utf-8')
        span = replace_header.find_candidate_block(block)
        norm = replace_header.normalize_block(block[span[0]:span[1]])
        self.assertNotIn('ascensio system sia', norm)


class ClassifyTests(unittest.TestCase):
    def setUp(self):
        self.old_norm = replace_header.normalize_block(load_template_text(OLD_TEMPLATE_PATH))
        self.new_norm = replace_header.normalize_block(load_template_text(NEW_TEMPLATE_PATH))

    def _classify_fixture(self, name):
        text = read_bytes(os.path.join(FIXTURES, name)).decode('utf-8')
        return replace_header.classify(text, self.old_norm, self.new_norm)[0]

    def test_exact_old_replace(self):
        self.assertEqual(self._classify_fixture('exact_old.js'), replace_header.CLASS_REPLACE)

    def test_drifted_year_replace(self):
        self.assertEqual(self._classify_fixture('drifted_year_old.js'), replace_header.CLASS_REPLACE)

    def test_drifted_address_replace(self):
        self.assertEqual(self._classify_fixture('drifted_address_old.js'), replace_header.CLASS_REPLACE)

    def test_already_new_idempotent(self):
        self.assertEqual(self._classify_fixture('already_new.js'), replace_header.CLASS_SKIP_ALREADY_NEW)

    def test_vendor_chromium_skipped(self):
        self.assertEqual(self._classify_fixture('vendor_chromium.js'), replace_header.CLASS_SKIP_VENDOR)

    def test_no_header_skipped(self):
        self.assertEqual(self._classify_fixture('no_header.js'), replace_header.CLASS_SKIP_NO_HEADER)


class ProcessFileTests(unittest.TestCase):
    """End-to-end tests through process_file (no git involved)."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.old_norm = replace_header.normalize_block(load_template_text(OLD_TEMPLATE_PATH))
        self.new_norm = replace_header.normalize_block(load_template_text(NEW_TEMPLATE_PATH))
        self.new_template_text = load_template_text(NEW_TEMPLATE_PATH)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _copy(self, fixture_name, dst_name=None):
        dst = os.path.join(self.tmp, dst_name or fixture_name)
        shutil.copyfile(os.path.join(FIXTURES, fixture_name), dst)
        return dst

    def test_exact_old_replaces_byte_for_byte(self):
        path = self._copy('exact_old.js')
        original = read_bytes(path)
        cls, changed, err = replace_header.process_file(
            path, self.old_norm, self.new_norm, self.new_template_text, dry_run=False
        )
        self.assertEqual(cls, replace_header.CLASS_REPLACE)
        self.assertTrue(changed)
        self.assertIsNone(err)
        result = read_bytes(path)
        # Expected content: NEW template (without trailing newline) + tail starting at \n\nfunction hello()
        new_body = self.new_template_text
        if new_body.endswith('\n'):
            new_body = new_body[:-1]
        tail = b'\n\nfunction hello() {\n    return 42;\n}\n'
        # The fixture on disk may have CRLF if git autocrlf'd; normalize for comparison.
        original_norm = original.replace(b'\r\n', b'\n')
        # The original ends with \n after `}`. Locate where the original /* */ block ends.
        end = original_norm.find(b'*/') + 2
        expected_tail = original_norm[end:]
        expected = new_body.encode('utf-8') + expected_tail
        result_norm = result.replace(b'\r\n', b'\n')
        self.assertEqual(result_norm, expected)

    def test_already_new_idempotent_no_write(self):
        path = self._copy('already_new.js')
        before = read_bytes(path)
        cls, changed, _ = replace_header.process_file(
            path, self.old_norm, self.new_norm, self.new_template_text, dry_run=False
        )
        self.assertEqual(cls, replace_header.CLASS_SKIP_ALREADY_NEW)
        self.assertFalse(changed)
        self.assertEqual(read_bytes(path), before)

    def test_vendor_chromium_not_touched(self):
        path = self._copy('vendor_chromium.js')
        before = read_bytes(path)
        cls, changed, _ = replace_header.process_file(
            path, self.old_norm, self.new_norm, self.new_template_text, dry_run=False
        )
        self.assertEqual(cls, replace_header.CLASS_SKIP_VENDOR)
        self.assertFalse(changed)
        self.assertEqual(read_bytes(path), before)

    def test_no_header_not_touched(self):
        path = self._copy('no_header.js')
        before = read_bytes(path)
        cls, changed, _ = replace_header.process_file(
            path, self.old_norm, self.new_norm, self.new_template_text, dry_run=False
        )
        self.assertEqual(cls, replace_header.CLASS_SKIP_NO_HEADER)
        self.assertFalse(changed)
        self.assertEqual(read_bytes(path), before)

    def test_bom_preserved(self):
        path = self._copy('bom.js')
        cls, changed, _ = replace_header.process_file(
            path, self.old_norm, self.new_norm, self.new_template_text, dry_run=False
        )
        self.assertEqual(cls, replace_header.CLASS_REPLACE)
        self.assertTrue(changed)
        result = read_bytes(path)
        self.assertTrue(result.startswith(b'\xef\xbb\xbf'))

    def test_crlf_preserved(self):
        path = os.path.join(self.tmp, 'generated_crlf.h')
        source = read_bytes(os.path.join(FIXTURES, 'exact_old.js')).replace(b'\r\n', b'\n')
        with open(path, 'wb') as fh:
            fh.write(source.replace(b'\n', b'\r\n'))
        cls, changed, _ = replace_header.process_file(
            path, self.old_norm, self.new_norm, self.new_template_text, dry_run=False
        )
        self.assertEqual(cls, replace_header.CLASS_REPLACE)
        self.assertTrue(changed)
        result = read_bytes(path)
        self.assertIn(b'\r\n', result)
        # No bare LF (each \n must be preceded by \r).
        bare_lf = sum(
            1 for i in range(len(result))
            if result[i] == 0x0a and (i == 0 or result[i - 1] != 0x0d)
        )
        self.assertEqual(bare_lf, 0)

    def test_dry_run_no_writes(self):
        path = self._copy('exact_old.js')
        before = read_bytes(path)
        cls, changed, _ = replace_header.process_file(
            path, self.old_norm, self.new_norm, self.new_template_text, dry_run=True
        )
        self.assertEqual(cls, replace_header.CLASS_REPLACE)
        self.assertTrue(changed)
        self.assertEqual(read_bytes(path), before)


class ReportDirGuardUnitTests(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.work, ignore_errors=True)

    def test_outside_repo_ok(self):
        repo = os.path.join(self.work, 'repo')
        report = os.path.join(self.work, 'reports')
        os.makedirs(repo)
        self.assertFalse(replace_header.report_dir_inside_repo(repo, report))

    def test_equal_to_repo_rejected(self):
        repo = os.path.join(self.work, 'repo')
        os.makedirs(repo)
        self.assertTrue(replace_header.report_dir_inside_repo(repo, repo))

    def test_nested_inside_repo_rejected(self):
        repo = os.path.join(self.work, 'repo')
        os.makedirs(repo)
        nested = os.path.join(repo, 'a', 'b', 'reports')
        self.assertTrue(replace_header.report_dir_inside_repo(repo, nested))

    def test_sibling_with_similar_prefix_ok(self):
        # /tmp/work/repo  vs  /tmp/work/repo-reports
        # commonpath should be /tmp/work, not /tmp/work/repo.
        repo = os.path.join(self.work, 'repo')
        sibling = os.path.join(self.work, 'repo-reports')
        os.makedirs(repo)
        self.assertFalse(replace_header.report_dir_inside_repo(repo, sibling))


class CLITests(unittest.TestCase):
    """Exercise main() with a temporary git repo and report dir."""

    def setUp(self):
        self.work = tempfile.mkdtemp()
        self.repo = os.path.join(self.work, 'repo')
        self.reports = os.path.join(self.work, 'reports')
        os.makedirs(self.repo)

    def tearDown(self):
        shutil.rmtree(self.work, ignore_errors=True)

    def _run(self, extra_args=()):
        argv = [
            '--repo-path', self.repo,
            '--old', OLD_TEMPLATE_PATH,
            '--new', NEW_TEMPLATE_PATH,
            '--report-dir', self.reports,
        ] + list(extra_args)
        return replace_header.main(argv)

    def test_report_file_written_outside_repo(self):
        make_git_repo(self.repo, [('exact_old.js', 'src/a.js')])
        rc = self._run()
        self.assertEqual(rc, 0)
        self.assertTrue(os.path.isfile(os.path.join(self.reports, 'report.txt')))
        # Nothing leaked into the repo.
        for entry in os.listdir(self.repo):
            self.assertNotIn(entry, ('report.txt',))

    def test_zero_replacements_exit_zero(self):
        make_git_repo(self.repo, [('no_header.js', 'a.js')])
        rc = self._run()
        self.assertEqual(rc, 0)
        with open(os.path.join(self.reports, 'report.txt'), encoding='utf-8') as fh:
            text = fh.read()
        self.assertIn('replaced=0', text)
        self.assertIn('no_header=1', text)

    def test_missing_template_exit_nonzero(self):
        make_git_repo(self.repo, [('exact_old.js', 'a.js')])
        argv = [
            '--repo-path', self.repo,
            '--old', os.path.join(self.work, 'does-not-exist.license'),
            '--new', NEW_TEMPLATE_PATH,
            '--report-dir', self.reports,
        ]
        self.assertNotEqual(replace_header.main(argv), 0)

    def test_missing_repo_exit_nonzero(self):
        argv = [
            '--repo-path', os.path.join(self.work, 'no-such-repo'),
            '--old', OLD_TEMPLATE_PATH,
            '--new', NEW_TEMPLATE_PATH,
            '--report-dir', self.reports,
        ]
        self.assertNotEqual(replace_header.main(argv), 0)

    def test_report_dir_inside_repo_rejected(self):
        make_git_repo(self.repo, [('exact_old.js', 'a.js')])
        inside = os.path.join(self.repo, 'sub', 'reports')
        argv = [
            '--repo-path', self.repo,
            '--old', OLD_TEMPLATE_PATH,
            '--new', NEW_TEMPLATE_PATH,
            '--report-dir', inside,
        ]
        rc = replace_header.main(argv)
        self.assertNotEqual(rc, 0)
        # Files in the repo must not have been touched and the rejected
        # report dir must not exist on disk.
        self.assertFalse(os.path.exists(inside))

    def test_report_dir_equal_to_repo_rejected(self):
        make_git_repo(self.repo, [('exact_old.js', 'a.js')])
        argv = [
            '--repo-path', self.repo,
            '--old', OLD_TEMPLATE_PATH,
            '--new', NEW_TEMPLATE_PATH,
            '--report-dir', self.repo,
        ]
        self.assertNotEqual(replace_header.main(argv), 0)

    def test_excludes_skip_vendor_paths(self):
        make_git_repo(self.repo, [
            ('exact_old.js', 'src/ok.js'),
            ('exact_old.js', 'third_party/lib.js'),
            ('exact_old.js', 'node_modules/x/y.js'),
        ])
        rc = self._run()
        self.assertEqual(rc, 0)
        # Only src/ok.js should have been replaced.
        with open(os.path.join(self.reports, 'report.txt'), encoding='utf-8') as fh:
            text = fh.read()
        self.assertIn('replaced=1', text)
        # third_party and node_modules files weren't even scanned.
        self.assertIn('scanned=1', text)


class EmitTargetsTests(unittest.TestCase):
    """--emit-targets parses config.json and prints GITHUB_OUTPUT lines."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write_config(self, content):
        path = os.path.join(self.tmp, 'config.json')
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(content)
        return path

    def _emit(self, path):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = replace_header.main(['--emit-targets', path])
        return rc, buf.getvalue()

    def test_bare_names_get_default_owner(self):
        path = self._write_config('{"repositories":["sdkjs","server"]}')
        rc, out = self._emit(path)
        self.assertEqual(rc, 0)
        self.assertIn('repos=["ONLYOFFICE/sdkjs", "ONLYOFFICE/server"]', out)
        self.assertIn('enabled=true', out)

    def test_owner_repo_left_as_is(self):
        path = self._write_config('{"repositories":["other-org/lib","ONLYOFFICE/sdkjs"]}')
        rc, out = self._emit(path)
        self.assertEqual(rc, 0)
        self.assertIn('repos=["other-org/lib", "ONLYOFFICE/sdkjs"]', out)
        self.assertIn('enabled=true', out)

    def test_base_branch_passed_through(self):
        path = self._write_config('{"base_branch":"release/v9.4.0","repositories":["sdkjs"]}')
        rc, out = self._emit(path)
        self.assertEqual(rc, 0)
        self.assertIn('base_branch=release/v9.4.0', out)

    def test_missing_base_branch_is_empty(self):
        path = self._write_config('{"repositories":["sdkjs"]}')
        rc, out = self._emit(path)
        self.assertEqual(rc, 0)
        self.assertIn('base_branch=\n', out)

    def test_empty_repositories(self):
        path = self._write_config('{"repositories":[]}')
        rc, out = self._emit(path)
        self.assertEqual(rc, 0)
        self.assertIn('repos=[]', out)
        self.assertIn('enabled=false', out)

    def test_missing_repositories_treated_as_empty(self):
        path = self._write_config('{}')
        rc, out = self._emit(path)
        self.assertEqual(rc, 0)
        self.assertIn('repos=[]', out)
        self.assertIn('base_branch=\n', out)
        self.assertIn('enabled=false', out)

    def test_only_whitespace_entries_disables(self):
        # If every entry is whitespace-only, the resulting list is empty
        # and the workflow must skip the replace job.
        path = self._write_config('{"repositories":["   ","\\t"]}')
        rc, out = self._emit(path)
        self.assertEqual(rc, 0)
        self.assertIn('repos=[]', out)
        self.assertIn('enabled=false', out)

    def test_whitespace_only_entries_skipped(self):
        path = self._write_config('{"repositories":["sdkjs","   ",""]}')
        rc, out = self._emit(path)
        self.assertEqual(rc, 0)
        self.assertIn('repos=["ONLYOFFICE/sdkjs"]', out)

    def test_bad_json_returns_nonzero(self):
        path = self._write_config('this is not json')
        rc, _ = self._emit(path)
        self.assertNotEqual(rc, 0)

    def test_repositories_not_array_returns_nonzero(self):
        path = self._write_config('{"repositories":"sdkjs"}')
        rc, _ = self._emit(path)
        self.assertNotEqual(rc, 0)

    def test_non_string_entry_returns_nonzero(self):
        path = self._write_config('{"repositories":[123]}')
        rc, _ = self._emit(path)
        self.assertNotEqual(rc, 0)

    def test_base_branch_wrong_type_returns_nonzero(self):
        path = self._write_config('{"base_branch":42,"repositories":["sdkjs"]}')
        rc, _ = self._emit(path)
        self.assertNotEqual(rc, 0)

    def test_missing_config_file_returns_nonzero(self):
        rc, _ = self._emit(os.path.join(self.tmp, 'does-not-exist.json'))
        self.assertNotEqual(rc, 0)

    def test_emit_targets_ignores_report_dir_requirement(self):
        # Sanity: --emit-targets does not require --report-dir.
        path = self._write_config('{"repositories":["sdkjs"]}')
        rc, _ = self._emit(path)
        self.assertEqual(rc, 0)


if __name__ == '__main__':
    unittest.main()
