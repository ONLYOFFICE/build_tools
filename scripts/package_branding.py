#!/usr/bin/env python
# -*- coding: utf-8 -*-

from package_utils import *

onlyoffice = True
company_name = "ONLYOFFICE"
company_name_l = company_name.lower()
publisher_name = "Ascensio System SIA"
cert_name = "Ascensio System SIA"

if (product == "desktop"):
  if (system == "windows"):
    desktop_dir = git_dir + "\\desktop-apps"
    build_dir = "win-linux\\package\\windows"
    branding_dir = desktop_dir + "\\" + build_dir
    product_name = "Desktop Editors"
    product_name_s = product_name.replace(" ","")
    vcredist_list = ["2015"]
    update_changes_list = {
      "en": "changes",
      "ru": "changes_ru"
    }

  elif (system == "darwin"):
    desktop_dir = git_dir + "/desktop-apps/macos"
    branding_desktop_dir = desktop_dir
    updates_dir = "build/update"
    changes_dir = "ONLYOFFICE/update/updates/ONLYOFFICE/changes"
    update_changes_list = {
      "en": "ReleaseNotes",
      "ru": "ReleaseNotesRU"
    }
    dateformat = "+%B %e, %Y"
    sparkle_base_url = "https://download.onlyoffice.com/install/desktop/editors/mac"
