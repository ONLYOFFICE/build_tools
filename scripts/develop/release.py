#!/usr/bin/env python

import sys
sys.path.append('../')

import base
import dependence
import config

def protect_brunch(branch, repo, strict = False):
  team = '' if strict else 'dep-application-development-leads'
  command = 'echo {"required_status_checks": null,"enforce_admins":true,"required_pull_request_reviews": null,"restrictions": {"users":[],"teams":["'
  command += team + '"]}} | gh api -X PUT repos/ONLYOFFICE/' + repo + '/branches/' + branch + '/protection --input -'
  result = base.run_command(command)
  if ('' != result['stderr']):
    print(result['stderr'])
  return

branch_from = 'release/v6.2.0'
branches_to = ['develop']

platform = base.host_platform()
if ("windows" == platform):
  dependence.check_pythonPath()
  dependence.check_gitPath()

if (dependence.check_gh() != True or dependence.check_gh_auth() != True):
  sys.exit(0)

base.cmd_in_dir('../../', 'python', ['configure.py', '--branding', 'onlyoffice', '--branding-url', 'https://github.com/ONLYOFFICE/onlyoffice.git', '--branch', branch_from, '--module', 'core desktop builder server mobile', '--update', '1', '--update-light', '1', '--clean', '0'])

# parse configuration
config.parse()

base.git_update('onlyoffice')

# correct defaults (the branding repo is already updated)
config.parse_defaults()

repositories = base.get_repositories()

# Add other plugins
repositories.update(base.get_plugins('autocomplete, easybib, glavred, wordpress'))
# Add other repositories
repositories['core-ext'] = [True, False]

base.update_repositories(repositories)

repositories['onlyoffice'] = [True, False]

for repo in repositories:
  current_dir = repositories[repo][1]
  if current_dir != False:
    cur_dir = os.getcwd()
    os.chdir(current_dir)
  
  base.create_pull_request(branches_to, repo, True, current_dir)
  
  if current_dir != False:
    os.chdir(cur_dir)

sys.exit(0)
