#!/usr/bin/env python

import sys
sys.path.append('../')

import base
import dependence
import config

branch_from = ''
branches_to = []

platform = base.host_platform()
if ("windows" == platform):
  dependence.check_pythonPath()
  dependence.check_gitPath()

base.cmd_in_dir('../../', 'python', ['configure.py', '--branding', 'onlyoffice', '--branding-url', 'https://github.com/ONLYOFFICE/onlyoffice.git', '--branch', branch_from, '--module', 'core desktop builder server mobile', '--update', '1', '--update-light', '1', '--clean', '0'])

# parse configuration
config.parse()

base.git_update('onlyoffice')

# correct defaults (the branding repo is already updated)
config.parse_defaults()

repositories = base.get_repositories()

# Add other plugins
repositories.update(base.get_plugins("autocomplete, easybib, glavred, wordpress"))
# Add other repositories
repositories["core-ext"] = [True, False]

base.update_repositories(repositories)

#for repo in repositories
#  base.create_pull_request(branches_to, repo, True)

sys.exit(0)
