#!/usr/bin/env python

import os
from package_utils import *

out_dir = os.path.abspath(os.path.dirname(__file__) + "/../out")
desktop_dir = git_dir + "\\desktop-apps"

onlyoffice = True
company_name = "ONLYOFFICE"
company_name_l = company_name.lower()
publisher_name = "Ascensio System SIA"
cert_name = "Ascensio System SIA"

if (product == "desktop") and (system == "windows"):
  build_dir = "win-linux\\package\\windows"
  branding_dir = desktop_dir + "\\" + build_dir
  product_name = "Desktop Editors"
  product_name_s = product_name.replace(" ","")
  vcredist_list = ["2015"]
  update_changes_list = {
    "en": "changes",
    "ru": "changes_ru"
  }
