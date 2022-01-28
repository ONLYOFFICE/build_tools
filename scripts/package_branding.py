#!/usr/bin/env python
# -*- coding: utf-8 -*-

from package_utils import *

onlyoffice = True
company_name = 'ONLYOFFICE'
company_name_l = company_name.lower()
publisher_name = 'Ascensio System SIA'
cert_name = 'Ascensio System SIA'

if product == 'desktop':

  if system == 'windows':
    build_dir = get_path("desktop-apps/win-linux/package/windows")
    # branding_dir = get_path(branding, build_dir)
    product_name = 'Desktop Editors'
    product_name_s = product_name.replace(' ','')
    vcredist_list = ['2015']
    update_changes_list = {
      'en': "changes",
      'ru': "changes_ru"
    }

  elif system == 'darwin':
    desktop_dir = get_path(git_dir + "/desktop-apps/macos")
    branding_desktop_dir = get_path(desktop_dir)
    updates_dir = get_path("build/update")
    changes_dir = get_path("ONLYOFFICE/update/updates/ONLYOFFICE/changes")
    update_changes_list = {
      'en': "ReleaseNotes",
      'ru': "ReleaseNotesRU"
    }
    dateformat = '+%B %e, %Y'
    sparkle_base_url = "https://download.onlyoffice.com/install/desktop/editors/mac"
