#!/usr/bin/env python

import sys
sys.path.append('../')

import argparse
import config
import base
import os

parser = argparse.ArgumentParser(description="Print repositories list.")
parser.add_argument('-P', '--platform', type=str, dest='platform',
                    action='store', default="native", help="Defines platform")
parser.add_argument('-M', '--module', type=str, dest='module',
                    action='store', default="core desktop builder server",
                    help="Defines modules")
parser.add_argument('-B', '--branding', type=str, dest='branding',
                    action='store', help="Defines branding path")
args = parser.parse_args()

config_args = [
  'configure.py',
  '--platform', args.platform,
  '--module',   args.module
]
if args.branding != None:
  config_args += ['--branding', args.branding]

base.cmd_in_dir('../../', 'python', config_args)

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
