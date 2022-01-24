#!/usr/bin/env python

import sys
sys.path.append('scripts')
import base
import package_utils as utils

# config
utils.parse()

# branding
# if (None != config.branding_dir):
#   branding_path = '../' + config.branding_dir + '/build_tools'
#   if base.is_file(branding_path + '/package_branding.py'):
#     del sys.modules['package_branding']
#     sys.path.insert(0,branding_path)
#     sys.modules['package_branding'] = __import__('package_branding')
#     import package_branding as branding
#     branding.export()

# build
import package_desktop
if ("desktop" == utils.product):
  package_desktop.make()
else:
  exit(1)
