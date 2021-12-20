#!/usr/bin/env python3

import sys
sys.path.append('scripts')
import argparse
import config
import base
import packages

parser = argparse.ArgumentParser(description='Build packages.')
parser.add_argument("-B", "--branding", dest="branding", type=str,
  action="store", help="provides branding path")
parser.add_argument("-P", "--product",  dest="product",  type=str,
  action="store", help="defines product")
parser.add_argument("-O", "--platform", dest="platform", type=str,
  action="store", help="defines platform")
parser.add_argument("-T", "--targets",  dest="targets",  type=str, nargs='+',
  action="store", help="defines targets")
args = parser.parse_args()

base_dir = base.get_script_dir(__file__)

# branding
if (None != args.branding):
  branding_dir = base_dir + "/../" + args.branding

  if base.is_file(args.branding_dir + "/build_tools/make_packages.py"):
    base.check_build_version(args.branding_dir + "/build_tools")
    base.cmd_in_dir(args.branding_dir + "/build_tools",
      "python", ["make_packages.py",
      '--product', args.product,
      '--platform', args.platform,
      '--targets', args.targets
    ])
    exit(0)

base.check_build_version(base_dir)

# build packages
packages.make(args.product, args.platform, args.targets)
