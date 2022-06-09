#!/usr/bin/env python
# -*- coding: utf-8 -*-

import package_utils as utils

onlyoffice = True
company_name = 'ONLYOFFICE'
company_name_l = company_name.lower()
publisher_name = 'Ascensio System SIA'
cert_name = 'Ascensio System SIA'

packages = {
  "windows": {
    "core-x64":    { "prefix": "win_64",   "arch": "x64" },
    "core-x86":    { "prefix": "win_32",   "arch": "x86" }
  },
  "darwin": {
    "core-x86_64": { "prefix": "mac_64",   "arch": "x64" }
  },
  "linux": {
    "core-x86_64": { "prefix": "linux_64", "arch": "x64" }
  }
}
