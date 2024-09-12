#!/usr/bin/env python3
#Usage.. python3 built_qt.py

import sys
sys.path.append('../../scripts')
import base
import os
import subprocess
import deps
import automate

if not base.is_file("./node_js_setup_14.x"):
  print("install dependencies...")
  deps.install_deps()

if not base.is_dir("./qt_build/Qt-5.9.9"):  
  print("install qt...")
  automate.install_qt()