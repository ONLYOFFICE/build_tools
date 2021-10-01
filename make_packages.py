#!/usr/bin/env python

import sys
sys.path.append('scripts')
import optparse
import config
import base
import packages

arguments = sys.argv[1:]
parser = optparse.OptionParser()
parser.add_option("--branding", action="store", type="string", dest="branding", default="", help="provides branding path")
parser.add_option("--product", action="store", type="string", dest="product", default="", help="defines product")
parser.add_option("--package", action="store", type="string", dest="package", default="", help="defines packages")

(options, args) = parser.parse_args(arguments)
configOptions = vars(options)

branding = configOptions["branding"]
product = configOptions["product"]
package_list = configOptions["package"]

# branding
if ("" != branding):
  base_dir = base.get_script_dir(__file__)
  branding_dir = base_dir + "/../" + configOptions["branding"]

  if base.is_file(branding_dir + "/build_tools/make_packages.py"):
    base.check_build_version(branding_dir + "/build_tools")
    base.cmd_in_dir(branding_dir + "/build_tools",
      "python", ["make_packages.py",
      '--product', product,
      '--package', package_list
    ])
    exit(0)

base.check_build_version(base_dir)

# build packages
packages.make(product, package_list)
