#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Packaging data of a build without a branding. A branding replaces this module
# with its <branding>/build_tools/scripts/package_branding.py: the names, the s3
# bucket, the desktop variants, the server editions and the closure maps are all
# its own. The values here are the defaults of the packaging repositories, and
# there is nothing to deploy to.

import package_utils as utils

company_name = "ONLYOFFICE"
company_name_l = company_name.lower()

s3_bucket = None
s3_base_url = None

# the sets of desktop packages, the keys are described in package_desktop.py;
# the empty variant builds the defaults of the packaging repositories
desktop_variants = [{}]

# the targets server_<edition> of make_package.py: the make arguments per host
# os, as {"<edition>": {"windows": [...], "linux": [...]}}
server_editions = {}

# the closure maps targets of make_package.py, as {"<target>": ["sdkjs" or
# "webapps", "<s3 subdirectory>"]}
closuremaps_targets = {}

if utils.is_windows():
  desktop_product_name = "Desktop Editors"
  desktop_product_name_s = desktop_product_name.replace(" ","")
  desktop_package_name = company_name + "-" + desktop_product_name_s
  desktop_changes_dir = "desktop-apps/win-linux/package/windows/update/changes"

if utils.is_macos():
  desktop_package_name = "ONLYOFFICE"
  desktop_build_dir = "desktop-apps/macos"
  desktop_branding_dir = "desktop-apps/macos"
  desktop_updates_dir = "build/update"
  desktop_changes_dir = "ONLYOFFICE/update/updates/ONLYOFFICE/changes"

builder_product_name = "Document Builder"

if utils.is_linux():
  desktop_make_targets = [
    {
      "make": "tar",
      "src": "tar/*.tar*",
      "dst": "desktop/linux/generic/"
    },
    {
      "make": "deb",
      "src": "deb/*.deb",
      "dst": "desktop/linux/debian/"
    },
    {
      "make": "rpm",
      "src": "rpm/build/RPMS/*/*.rpm",
      "dst": "desktop/linux/rhel/"
    },
    {
      "make": "rpm-suse",
      "src": "rpm-suse/build/RPMS/*/*.rpm",
      "dst": "desktop/linux/suse/"
    }
  ]
  server_make_targets = [
    {
      "make": "deb",
      "src": "deb/*.deb",
      "dst": "server/linux/debian/"
    },
    {
      "make": "rpm",
      "src": "rpm/builddir/RPMS/*/*.rpm",
      "dst": "server/linux/rhel/"
    },
    {
      "make": "tar",
      "src": "*.tar*",
      "dst": "server/linux/snap/"
    }
  ]
