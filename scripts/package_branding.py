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
    package_name = company_name + '_' + product_name_s
    vcredist_list = ['2022']
    update_changes_list = {
      'en': "changes",
      'ru': "changes_ru"
    }

  elif system == 'darwin':
    build_dir = "desktop-apps/macos"
    branding_build_dir = "desktop-apps/macos"
    package_name = company_name
    updates_dir = "build/update"
    changes_dir = "ONLYOFFICE/update/updates/ONLYOFFICE/changes"
    update_changes_list = {
      'en': "ReleaseNotes",
      'ru': "ReleaseNotesRU"
    }
    sparkle_base_url = "https://download.onlyoffice.com/install/desktop/editors/mac"

if product == 'builder':

  if system == 'windows':
    build_dir = "document-builder-package"
    product_name = 'Document Builder'
    product_name_s = product_name.replace(' ','')
    package_name = company_name + '_' + product_name_s
