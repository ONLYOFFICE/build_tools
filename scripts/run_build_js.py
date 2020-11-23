#!/usr/bin/env python

import build_js
import config
import base
import sys

branch = base.run_command('git rev-parse --abbrev-ref HEAD')['stdout']

config.parse()
base.cmd_in_dir('../', 'python', ['configure.py', '--branch', branch or 'develop', '--develop', '1', '--module', 'server', '--update', '0', '--update-light', '0', '--clean', '0'])
build_js.build_js_develop(sys.argv[1])
