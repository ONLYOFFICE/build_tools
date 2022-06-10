#!/usr/bin/env python
# -*- coding: utf-8 -*-

import package_utils as utils

onlyoffice = True
company_name = "ONLYOFFICE"
company_name_l = company_name.lower()
publisher_name = "Ascensio System SIA"
cert_name = "Ascensio System SIA"

builder_product_name = "Document Builder"

packages = {
  "windows_x64":      [
    "core",
    "builder-portable",
    "builder-innosetup"
  ],
  "windows_x64_xp":   [
    "core",
    "builder-portable",
    "builder-innosetup"
  ],
  "windows_x86":      [],
  "windows_x86_xp":   [],
  "darwin_x86_64":    [
    "core"
  ],
  "darwin_x86_64_v8": [],
  "darwin_arm64":     [],
  "linux_x86_64":     [
    "core"
  ],
  "linux_aarch64":    []
}
