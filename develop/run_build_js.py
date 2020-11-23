#!/usr/bin/env python

import build_js
import config
import base
import sys

base.cmd_in_dir('../', 'python', ['configure.py'])
config.parse()

build_js.build_js_develop(sys.argv[1])
