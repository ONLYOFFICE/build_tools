#!/usr/bin/env python3

import base
import os
import re
import time
from jinja2 import Template

company_name = base.get_env("COMPANY_NAME")
publisher_name = "Ascensio System SIA"
signing = base.get_env("ENABLE_SIGNING") == 1
version = base.get_env("PRODUCT_VERSION")
build = base.get_env("BUILD_NUMBER")

base_dir = base.get_script_dir() + "/../out"
git_dir = base.get_script_dir() + "/../.."
package_dir = os.path.abspath(git_dir + "/desktop-apps")

def make(platform, targets):
  if ("windows" == platform):
    make_windows(targets)
  elif ("macos" == platform):
    make_macos(targets)
  elif ("linux" == platform):
    if ("packages" in targets):
      build_dir = package_dir + "/win-linux/package/linux"
      print("Clean")
      base.cmd_in_dir(build_dir, "make", ["clean"])
      print("Build packages")
      base.cmd_in_dir(build_dir, "make", ["packages"])
  else:
    exit(1)
  return

def make_windows(targets):
  for target in targets:

    if (-1 != target.find("x64")):
      arch = "64"
      win_arch = "x64"
    elif (-1 != target.find("x86")):
      arch = "32"
      win_arch = "x86"

    aplatform = "win_" + arch
    suffix = win_arch
    if (-1 != target.find("xp")):
      xp = True
      aplatform += "_xp"
      suffix += "_xp"
    else:
      xp = False

    package_version = version + "." + build    
    prefix_dir = base_dir + "/" + aplatform + "/ONLYOFFICE/DesktopEditors"
    build_dir = package_dir + "/win-linux/package/windows"
    installer_exe_file = "ONLYOFFICE_DesktopEditors_" + package_version + "_" + suffix + ".exe"
    installer_msi_file = "ONLYOFFICE_DesktopEditors_" + package_version + "_" + suffix + ".msi"
    portable_zip_file = "ONLYOFFICE_DesktopEditors_" + package_version + "_" + suffix + ".zip"
    update_exe_file = "editors_update_" + suffix + ".exe"
    update_appcast_file = "appcast.xml"
    update_changes_en_file = "changes.html"
    update_changes_ru_file = "changes_ru.html"
    update_changes_dir = branding_dir + "/" + build_dir + "/update/changes/" + version

    print("Clean")
    base.delete_files(build_dir + "/data/vcredist/*.exe")
    base.delete_files(build_dir + "/*.exe")
    base.delete_files(build_dir + "/*.msi")
    base.delete_files(build_dir + "/*.zip")
    base.delete_dir(build_dir + "/DesktopEditors-cache")
    base.delete_files(build_dir + "/update/*.exe")
    base.delete_files(build_dir + "/update/*.xml")
    base.delete_files(build_dir + "/update/*.html")

    if (-1 != target.find("installer-is")):

      # vcr
      vcr2015_url = {
        "x64": "https://download.microsoft.com/download/2/E/6/2E61CFA4-993B-4DD4-91DA-3737CD5CD6E3/vcredist_x86.exe",
        "x86": "https://download.microsoft.com/download/d/e/c/dec58546-c2f5-40a7-b38e-4df8d60b9764/vc_redist.x86.exe"
      }
      # vcr2013_url = {
      #   "x64": "https://download.microsoft.com/download/2/E/6/2E61CFA4-993B-4DD4-91DA-3737CD5CD6E3/vcredist_x64.exe",
      #   "x86": "https://download.microsoft.com/download/2/c/6/2c675af0-2155-4961-b32e-289d7addfcec/vc_redist.x64.exe",
      # }
      base.download(vcr15_url.win_arch, build_dir + "/data/vcredist/vcredist_2015_" + win_arch + ".exe")

      print("Build inno setup installer")
      # inno
      iscc_args = [
        "/Qp",
        "/DsAppVersion=" + package_version,
        "/DsBrandingFolder=" + branding_dir,
        "/DsOutputFileName=" + installer_exe_file,
        "/DDEPLOY_PATH=" + prefix_dir,
        "/D_ARCH=" + arch
      ]
      if (company_name == "onlyoffice"):
        iscc_args.append("/D_ONLYOFFICE=1")
      if xp:
        iscc_args.append("/D_WIN_XP=1")
      if signing:
        iscc_args.append("/DENABLE_SIGNING=1")
        iscc_args.append("/S\"byparam=signtool.exe sign /v /n " + publisher_name + " /t http://timestamp.digicert.com $$f\"")
      base.cmd_in_dir(build_dir, "iscc", iscc_args + ["common.iss"])

      if (-1 != target.find("winsparkle-update")):
        print("Build inno setup update installer")
        base.cmd_in_dir(build_dir, "iscc", iscc_args + ["/DTARGET_NAME=" + installer_exe_file, "update_common.iss"])

      if (-1 != target.find("winsparkle-files")):
        print("Build winsparkle files")
        timestamp = time.time()

        file_path = build_dir + "/update/" + update_appcast_file
        template = Template(open(file_path + ".jn2").read())
        base.writeFile(file_path, template.render(version=version, build=build, timestamp=timestamp))

        file_path = build_dir + "/update/" + update_changes_en_file
        template = Template(open(file_path + ".jn2").read())
        base.writeFile(file_path, template.render(version=version, build=build, timestamp=timestamp))

        file_path = build_dir + "/update/" + update_changes_ru_file
        template = Template(open(file_path + ".jn2").read())
        base.writeFile(file_path, template.render(version=version, build=build, timestamp=timestamp))

    if (-1 != target.find("installer-ai")):
      print("Build package: advanced installer installer")
      # msi
      aic = "AdvancedInstaller.com"
      ai_args = ["/edit", "DesktopEditors.aip"]
      if (arch == "32"):
        base.cmd_in_dir(build_dir, aic, ai_args + ["/SetPackageType", "x86"])
      if signing:
        base.cmd_in_dir(build_dir, aic, ai_args + ["/SetDigitalCertificateFile",
          "-file", base.get_env("CODESIGN_CERT_PATH"),
          "-password", base.get_env("CODESIGN_CERT_PWD")])
        base.cmd_in_dir(build_dir, aic, ai_args + ["/SetSig"])
      base.cmd_in_dir(build_dir, aic, ai_args + ["/AddOsLc", "-buildname", "DefaultBuild", "-arch", win_arch])
      base.cmd_in_dir(build_dir, aic, ai_args + ["/UpdateFile", "APPDIR\\DesktopEditors.exe", prefix_dir + "\\DesktopEditors.exe"])
      base.cmd_in_dir(build_dir, aic, ai_args + ["/NewSync", "APPDIR", prefix_dir, "-existingfiles", "delete"])
      base.cmd_in_dir(build_dir, aic, ai_args + ["/SetVersion", package_version])
      base.cmd_in_dir(build_dir, aic, ai_args + ["/SetOutputLocation", "-buildname", "DefaultBuild", "-path", build_dir])
      base.cmd_in_dir(build_dir, aic, ai_args + ["/SetPackageName", installer_msi_file, "-buildname", "DefaultBuild"])
      base.cmd_in_dir(build_dir, aic, ["/rebuild", "DesktopEditors.aip", "-buildslist", "DefaultBuild"])

    if (-1 != target.find("portable")):
      print("Build package: portable")
      base.cmd_in_dir(package_dir, "7z", ["a", "-y", portable_zip_file, prefix_dir + "/*"])

  return

def make_macos(targets):
  for target in targets:

    macos_dir = package_dir + "/macos"
    update_dir = macos_dir + "/build/update"
    changes_dir = macos_dir + "/ONLYOFFICE/update/updates/ONLYOFFICE/changes"

    if (-1 != target.find("diskimage")):

      if (target == "diskimage-x86_64"):
        lane = "release_x86_64"
        scheme = "ONLYOFFICE-x86_64"
      elif (target == "diskimage-v8-x86_64"):
        lane = "release_v8"
        scheme = "ONLYOFFICE-v8"
      elif (target == "diskimage-arm64"):
        lane = "release_arm"
        scheme = "ONLYOFFICE-arm"
      else:
        exit(1)

      print("Build package " + scheme)

      print("$ bundler exec fastlane " + lane + " skip_git_bump:true")
      base.cmd_in_dir(macos_dir, "bundler", ["exec", "fastlane", lane, "skip_git_bump:true"])

    if (-1 != target.find("diskimage")) and (-1 != target.find("sparkle-updates")):

      print("Build updates")

      app_version = base.run_command("/usr/libexec/PlistBuddy -c 'print :CFBundleShortVersionString' " +
        macos_dir + "/build/ONLYOFFICE.app/Contents/Info.plist")['stdout']
      zip_filename = scheme + "-" + app_version
      macos_zip = macos_dir + "/build/" + zip_filename + ".zip"
      update_storage_dir = base.get_env("ARCHIVES_DIR") + "/" + scheme + "/_updates"

      base.create_dir(update_dir)
      base.copy_dir_content(update_storage_dir, update_dir, ".zip")
      base.copy_dir_content(update_storage_dir, update_dir, ".html")
      base.copy_file(macos_zip, update_dir)

      notes_src = changes_dir + "/" + app_version + "/ReleaseNotes.html"
      notes_dst = update_dir + "/" + zip_filename + ".html"
      cur_date = base.run_command("LC_ALL=en_US.UTF-8 date -u \"+%B %e, %Y\"")['stdout']
      if base.is_exist(notes_src):
        base.copy_file(notes_src, notes_dst)
        base.replaceInFileRE(notes_dst,
          r"(<span class=\"releasedate\">).+(</span>)", "\\1 - " + cur_date + "\\2")
      else:
        base.writeFile(notes_dst, "placeholder\n")

      notes_src = changes_dir + "/" + app_version + "/ReleaseNotesRU.html"
      notes_dst = update_dir + "/" + zip_filename + ".ru.html"
      cur_date = base.run_command("LC_ALL=ru_RU.UTF-8 date -u \"+%e %B %Y\"")['stdout']
      if base.is_exist(notes_src):
        base.copy_file(notes_src, notes_dst)
        base.replaceInFileRE(notes_dst,
          r"(<span class=\"releasedate\">).+(</span>)", "\\1 - " + cur_date + "\\2")
      else:
        base.writeFile(notes_dst, "placeholder\n")

      print("$ ./generate_appcast " + update_dir)
      base.cmd(macos_dir + "/Vendor/Sparkle/bin/generate_appcast", [update_dir])

      print("Edit Sparkle appcast links")

      sparkle_base_url = "https://download.onlyoffice.com/install/desktop/editors/mac"
      if (target == "diskimage-x86_64"):      sparkle_base_url += "/x86_64"
      elif (target == "diskimage-v8-x86_64"): sparkle_base_url += "/v8"
      elif (target == "diskimage-arm64"):     sparkle_base_url += "/arm"

      base.replaceInFileRE(update_dir + "/onlyoffice.xml",
        r"(<sparkle:releaseNotesLink>)(?:.+ONLYOFFICE-(?:x86|x86_64|v8|arm)-([0-9.]+)\..+)(</sparkle:releaseNotesLink>)",
        "\\1" + sparkle_base_url + "/updates/changes/\\2/ReleaseNotes.html\\3")
      base.replaceInFileRE(update_dir + "/onlyoffice.xml",
        r"(<sparkle:releaseNotesLink xml:lang=\"ru\">)(?:ONLYOFFICE-(?:x86|x86_64|v8|arm)-([0-9.]+)\..+)(</sparkle:releaseNotesLink>)",
        "\\1" + sparkle_base_url + "/updates/changes/\\2/ReleaseNotesRU.html\\3")
      base.replaceInFileRE(update_dir + "/onlyoffice.xml",
        r"(url=\")(?:.+/)(ONLYOFFICE.+\")", "\\1" + sparkle_base_url + "/updates/\\2")

      print("Delete unnecessary files")

      for file in os.listdir(update_dir):
        if (-1 == file.find(app_version)) and (file.endswith(".zip") or file.endswith(".html")):
          base.delete_file(update_dir + "/" + file)

  return
