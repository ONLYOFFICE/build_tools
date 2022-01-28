#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('scripts')
import package_utils as utils

# config
utils.parse()

# branding
if utils.branding is not None:
  branding_path = utils.get_path('..', utils.branding)
  sys.path.insert(-1, utils.get_path(branding_path, 'build_tools/scripts'))

# build
import package
package.make(utils.product)
