#!/usr/bin/env python3
"""
Git Operations Script
Creates and removes branches across all repositories using Gitea API.
Uses existing config system from base module to discover repositories dynamically.
"""

import sys
import os
import json
import argparse
import logging
import urllib.request
import urllib.error
import urllib.parse

sys.path.append('../')
import base
import config
import dependence

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GitOperations:
    def __init__(self, branding="onlyoffice", base_branch="develop",
                 branding_url="ONLYOFFICE/onlyoffice.git", branch_name=None,
                 modules="core desktop builder server mobile"):
        self.branding = branding
        self.base_branch = base_branch
        self.branding_url = branding_url
        self.branch_name = branch_name
        self.modules = modules

        # Derive owner and API URL from git origin or environment
        self.owner = "ONLYOFFICE"
        self.api_url = ""
        self.token = os.environ.get('GIT_TOKEN', '')

        self.origin = base.git_get_origin().rstrip('/')
        if '://' in self.origin:
            parts = self.origin.split('/')
            self.owner = parts[-2]
            self.api_url = parts[0] + '//' + parts[2]
        else:
            host = self.origin.split(':')[0].split('@')[-1]
            self.owner = self.origin.split(':')[1].split('/')[0]
            self.api_url = 'https://' + host

        # GITEA_URL env var takes precedence (set by workflow)
        env_url = os.environ.get('GITEA_URL', '')
        if env_url:
            self.api_url = env_url.rstrip('/')

        logger.info(f"API: {self.api_url}, owner: {self.owner}")

        self._configure()

    def _api(self, endpoint, method="GET", data=None):
        """Make Gitea REST API request."""
        url = self.api_url + '/api/v1/' + endpoint
        body = json.dumps(data).encode('utf-8') if data else None
        req = urllib.request.Request(url, data=body, method=method)
        req.add_header('Authorization', 'token ' + self.token)
        if data:
            req.add_header('Content-Type', 'application/json')
        try:
            resp = urllib.request.urlopen(req, timeout=30)
            return {'ok': True, 'status': resp.status, 'body': resp.read().decode('utf-8')}
        except urllib.error.HTTPError as e:
            return {'ok': False, 'status': e.code, 'body': e.read().decode('utf-8')}
        except urllib.error.URLError as e:
            return {'ok': False, 'status': 0, 'body': str(e.reason)}

    def _configure(self):
        """Configure repo list using existing config system. Fetches branding defaults via API."""
        logger.info(f"Configuring repositories for branch: {self.base_branch}")

        if '://' in self.origin:
            host_base = self.origin.split('/', 3)[0] + '//' + self.origin.split('/', 3)[2] + '/'
        else:
            host_base = self.origin.split(':', 1)[0] + ':'

        branding_url = host_base + self.branding_url

        platform = base.host_platform()
        if platform == "windows":
            dependence.check_pythonPath()
            dependence.check_gitPath()

        configure_args = [
            'configure.py',
            '--branding', self.branding,
            '--branding-url', branding_url,
            '--branch', self.base_branch,
            '--module', self.modules,
            '--update', '0',
            '--clean', '0'
        ]
        base.cmd_in_dir('../../', 'python', configure_args)

        config.parse()

        # Fetch branding defaults file via API (no clone needed)
        branding_repo = self.branding_url.replace('.git', '').split('/')[-1]
        encoded_ref = urllib.parse.quote(self.base_branch, safe='')
        result = self._api(
            f"repos/{self.owner}/{branding_repo}/raw/build_tools/defaults?ref={encoded_ref}"
        )
        if result['ok']:
            defaults_dir = base.get_script_dir() + "/../../" + self.branding + "/build_tools"
            os.makedirs(defaults_dir, exist_ok=True)
            with open(defaults_dir + "/defaults", 'w') as f:
                f.write(result['body'])
            logger.info(f"Fetched branding defaults for '{self.branding}'")
        else:
            logger.warning(f"Could not fetch branding defaults (status {result['status']}), using local defaults")

        config.parse_defaults()
        logger.info("Configuration complete")

    def get_configured_repositories(self):
        """Get repo list dynamically from config system (same as release.py)."""
        repositories = base.get_repositories()
        repositories.pop('onlyoffice.github.io', None)
        repositories['core-ext'] = [True, False]
        repositories['build_tools'] = [True, False]
        repositories[self.branding] = [True, False]
        repositories['Docker-DocumentServer'] = [True, False]
        repositories['DocumentBuilder'] = [True, False]
        repositories['document-builder-package'] = [True, False]
        repositories['document-server-package'] = [True, False]
        repositories['documents-pipeline'] = [True, False]
        return repositories

    def create_branches(self):
        """Create branch in all repositories using Gitea API."""
        repositories = self.get_configured_repositories()
        success = 0
        skipped = 0
        failed = 0

        for repo_name in repositories:
            logger.info(f"--- {repo_name} ---")

            result = self._api(
                f"repos/{self.owner}/{repo_name}/branches",
                method="POST",
                data={
                    "new_branch_name": self.branch_name,
                    "old_branch_name": self.base_branch
                }
            )

            if result['ok']:
                logger.info(f"Created '{self.branch_name}' in {repo_name}")
                success += 1
            elif result['status'] == 404:
                logger.warning(f"Repo or base branch not found: {repo_name}, skipping")
                skipped += 1
            elif result['status'] == 409:
                logger.warning(f"Branch already exists in {repo_name}")
                failed += 1
            else:
                logger.warning(f"Failed in {repo_name} (status {result['status']}): {result['body']}")
                failed += 1

        logger.info(f"Results: {success} created, {skipped} skipped, {failed} failed")
        return failed == 0

    def remove_branches(self):
        """Remove branch from all repositories using Gitea API."""
        repositories = self.get_configured_repositories()
        encoded_branch = urllib.parse.quote(self.branch_name, safe='')
        success = 0
        skipped = 0
        failed = 0

        for repo_name in repositories:
            logger.info(f"--- {repo_name} ---")

            result = self._api(
                f"repos/{self.owner}/{repo_name}/branches/{encoded_branch}",
                method="DELETE"
            )

            if result['ok']:
                logger.info(f"Deleted '{self.branch_name}' from {repo_name}")
                success += 1
            elif result['status'] == 404:
                logger.warning(f"Branch not found in {repo_name}, skipping")
                skipped += 1
            else:
                logger.warning(f"Failed in {repo_name} (status {result['status']}): {result['body']}")
                failed += 1

        logger.info(f"Results: {success} deleted, {skipped} skipped, {failed} failed")
        return failed == 0

    def protect_branches(self, teams):
        """Set branch protection in all repositories using Gitea API."""
        repositories = self.get_configured_repositories()
        success = 0
        skipped = 0
        failed = 0

        data = {
            "branch_name": self.branch_name,
            "enable_push": True,
            "enable_push_whitelist": True,
            "push_whitelist_teams": teams,
            "enable_deletions": False,
            "enable_merge_whitelist": True,
            "merge_whitelist_teams": teams,
        }

        for repo_name in repositories:
            logger.info(f"--- {repo_name} ---")

            result = self._api(
                f"repos/{self.owner}/{repo_name}/branch_protections",
                method="POST",
                data=data
            )

            if result['ok']:
                logger.info(f"Protected '{self.branch_name}' in {repo_name}")
                success += 1
            elif result['status'] == 404:
                logger.warning(f"Repo not found: {repo_name}, skipping")
                skipped += 1
            elif result['status'] == 422:
                logger.warning(f"Protection already exists in {repo_name}, skipping")
                skipped += 1
            else:
                logger.warning(f"Failed in {repo_name} (status {result['status']}): {result['body']}")
                failed += 1

        logger.info(f"Results: {success} protected, {skipped} skipped, {failed} failed")
        return failed == 0

    def unprotect_branches(self):
        """Remove branch protection from all repositories using Gitea API."""
        repositories = self.get_configured_repositories()
        encoded_branch = urllib.parse.quote(self.branch_name, safe='')
        success = 0
        skipped = 0
        failed = 0

        for repo_name in repositories:
            logger.info(f"--- {repo_name} ---")

            result = self._api(
                f"repos/{self.owner}/{repo_name}/branch_protections/{encoded_branch}",
                method="DELETE"
            )

            if result['ok']:
                logger.info(f"Unprotected '{self.branch_name}' in {repo_name}")
                success += 1
            elif result['status'] == 404:
                logger.warning(f"Protection not found in {repo_name}, skipping")
                skipped += 1
            else:
                logger.warning(f"Failed in {repo_name} (status {result['status']}): {result['body']}")
                failed += 1

        logger.info(f"Results: {success} unprotected, {skipped} skipped, {failed} failed")
        return failed == 0


def main():
    parser = argparse.ArgumentParser(description='Git Operations Tool - Create and Remove Branches')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    for cmd_name, cmd_help in [('create', 'Create branch in all repositories'),
                                ('remove', 'Remove branch from all repositories'),
                                ('protect', 'Set branch protection in all repositories'),
                                ('unprotect', 'Remove branch protection from all repositories')]:
        sub = subparsers.add_parser(cmd_name, help=cmd_help)
        sub.add_argument('branch_name', help='Branch name')
        sub.add_argument('--base-branch', default='develop', help='Base branch (default: develop)')
        sub.add_argument('--branding', default='onlyoffice', help='Branding name')
        sub.add_argument('--branding-url', default='ONLYOFFICE/onlyoffice.git',
                         help='Relative path from git host base')
        sub.add_argument('--modules', default='core desktop builder server mobile', help='Modules to include')
        if cmd_name == 'protect':
            sub.add_argument('--teams', required=True, help='Comma-separated list of teams for push/merge whitelist')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    git_ops = GitOperations(args.branding, args.base_branch, args.branding_url,
                            args.branch_name, args.modules)

    success = False
    if args.command == 'create':
        success = git_ops.create_branches()
    elif args.command == 'remove':
        success = git_ops.remove_branches()
    elif args.command == 'protect':
        teams = [t.strip() for t in args.teams.split(',')]
        success = git_ops.protect_branches(teams)
    elif args.command == 'unprotect':
        success = git_ops.unprotect_branches()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
