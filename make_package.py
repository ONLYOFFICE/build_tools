#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('scripts')
import package_utils as utils

# config
utils.parse()

# branding
if (None != utils.branding):
  branding_dir = "..\\" + utils.branding
  if utils.is_file(branding_dir + "\\build_tools\\scripts\\package_branding.py"):
    sys.path.insert(-1,branding_dir + "\\build_tools\\scripts")

# build
import package

package.make(utils.product)
