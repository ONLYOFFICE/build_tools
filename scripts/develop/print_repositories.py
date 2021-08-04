#!/usr/bin/env python

import sys
sys.path.append('../')

import config
import base
import os

base.cmd_in_dir('../../', 'python',['configure.py', '--branding', 'onlyoffice', '--module', 'core desktop builder server'])

# parse configuration
config.parse()
config.parse_defaults()

repositories = base.get_repositories()

# Add other plugins
repositories.update(base.get_plugins('autocomplete, easybib, wordpress'))

# Add other repositories
if config.check_option("module", "builder"):
  repositories['document-builder-package'] = [False, False]

if (config.check_option("module", "server")):
  repositories['document-server-package'] = [False, False]
  repositories['Docker-DocumentServer'] = [False, False]

for repo in repositories:
  line = repo
  repo_dir = repositories[repo][1]
  if repo_dir != False:
    repo_dir = os.path.relpath(repo_dir, base.get_script_dir() + "../../..")
    line += " " + repo_dir
  print(line)

sys.exit(0)
