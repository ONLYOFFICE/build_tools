#!/usr/bin/env python3

import sys
sys.path.append(sys.argv[1] + '/build_tools/scripts')
import build_js
import config
import base

base.cmd_in_dir(sys.argv[1] + '/build_tools/', 'python3', ['configure.py'])
config.parse()

build_js.build_js_develop(sys.argv[1])
