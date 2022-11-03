#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from package_utils import *
from package_branding import *

def make():
  if system == 'windows':
    make_windows()
  elif system == 'darwin':
    make_macos()
  elif system == 'linux':
    if 'packages' in targets:
      set_cwd(build_dir)
      log("Clean")
      cmd("make", ["clean"])
      log("Build packages")
      cmd("make", ["packages"])
  else:
    exit(1)
  return

#
# Windows
#

def make_windows():
  global package_version, sign, machine, arch, xp, iscc_args, \
    source_dir, source_help_dir, innosetup_file, innosetup_help_file, \
    innosetup_update_file, advinst_file, portable_zip_file

  set_cwd(get_abspath(git_dir, build_dir))

  if 'clean' in targets:
    log("\n=== Clean\n")
    delete_dir(get_path("data/vcredist"))
    delete_dir("DesktopEditors-cache")
    delete_files("*.exe")
    delete_files("*.msi")
    delete_files("*.aic")
    delete_files("*.tmp")
    delete_files("*.zip")
    delete_files(get_path("update/*.exe"))
    delete_files(get_path("update/*.xml"))
    delete_files(get_path("update/*.html"))

  package_version = version + '.' + build
  sign = 'sign' in targets

  for target in targets:
    if not (target.startswith('innosetup') or target.startswith('advinst') or 
            target.startswith('portable')):
      continue

    machine = get_platform(target)['machine']
    arch = get_platform(target)['arch']
    xp = get_platform(target)['xp']
    suffix = arch + ("_xp" if xp else "")
    source_prefix = "win_" + machine + ("_xp" if xp else "")
    source_dir = get_path("%s/%s/%s/%s" % (out_dir, source_prefix, company_name_l, product_name_s))
    source_help_dir = source_dir + "-help"

    if target.startswith('innosetup'):
      for year in vcredist_list:
        download_vcredist(year)

      innosetup_file = "%s_%s_%s.exe" % (package_name, package_version, suffix)
      make_innosetup()

      if 'winsparkle-update' in targets:
        innosetup_update_file = get_path("update/editors_update_%s.exe" % suffix)
        make_innosetup_update()

      if 'winsparkle-files' in targets:
        make_winsparkle_files()

    if target.startswith('innosetup-help'):
      innosetup_help_file = "%s_Help_%s_%s.exe" % (package_name, package_version, suffix)
      make_innosetup_help()

    if target.startswith('advinst'):
      advinst_file = "%s_%s_%s.msi" % (package_name, package_version, suffix)
      make_advinst()

    if target.startswith('portable'):
      portable_zip_file = "%s_%s_%s.zip" % (package_name, package_version, suffix)
      make_win_portable()

  return

def download_vcredist(year):
  log("\n=== Download vcredist " + year + "\n")
  vcredist = get_path("data/vcredist/vcredist_%s_%s.exe" % (year, arch))
  log("--- " + vcredist)
  if is_file(vcredist):
    log("! file exist, skip")
    return
  create_dir(get_dirname(vcredist))
  download_file(vcredist_links[year][machine], vcredist)
  return

def make_innosetup():
  log("\n=== Build innosetup project\n")
  global iscc_args
  iscc_args = [
    "/Qp",
    "/DsAppVersion=" + package_version,
    "/DDEPLOY_PATH=" + source_dir,
    "/D_ARCH=" + machine
  ]
  if onlyoffice:
    iscc_args.append("/D_ONLYOFFICE=1")
  else:
    iscc_args.append("/DsBrandingFolder=" + get_abspath(git_dir, branding_dir))
  if xp:
    iscc_args.append("/D_WIN_XP=1")
  if sign:
    iscc_args.append("/DENABLE_SIGNING=1")
    iscc_args.append("/Sbyparam=signtool.exe sign /v /n $q" + cert_name + "$q /t " + tsa_server + " $f")
  log("--- " + innosetup_file)
  if is_file(innosetup_file):
    log("! file exist, skip")
    return
  cmd("iscc", iscc_args + ["common.iss"])
  return

def make_innosetup_help():
  log("\n=== Build innosetup help project\n")
  global iscc_args
  iscc_args = [
    "/Qp",
    "/DsAppVersion=" + package_version,
    "/DDEPLOY_PATH=" + source_help_dir,
    "/D_ARCH=" + machine
  ]
  if onlyoffice:
    iscc_args.append("/D_ONLYOFFICE=1")
  else:
    iscc_args.append("/DsBrandingFolder=" + get_abspath(git_dir, branding_dir))
  if sign:
    iscc_args.append("/DENABLE_SIGNING=1")
    iscc_args.append("/Sbyparam=signtool.exe sign /v /n $q" + cert_name + "$q /t " + tsa_server + " $f")
  log("--- " + innosetup_help_file)
  if is_file(innosetup_help_file):
    log("! file exist, skip")
    return
  cmd("iscc", iscc_args + ["help.iss"])
  return

def make_innosetup_update():
  log("\n=== Build innosetup update project\n")
  log("--- " + innosetup_update_file)
  if is_file(innosetup_update_file):
    log("! file exist, skip")
    return
  cmd("iscc", iscc_args + ["/DTARGET_NAME=" + innosetup_file, "update_common.iss"])
  return

def make_winsparkle_files():
  log("\n=== Build winsparkle files\n")

  awk_branding = "update/branding.awk"
  if not onlyoffice:
    build_branding_dir = get_abspath(git_dir, branding_dir, "win-linux/package/windows")
  else:
    build_branding_dir = get_path(".")
  awk_args = [
    "-v", "Version=" + version,
    "-v", "Build=" + build,
    "-v", "Branch=" + get_env("RELEASE_BRANCH"),
    "-v", "Timestamp=" + timestamp,
    "-i", get_path(build_branding_dir, awk_branding)
  ]

  appcast = get_path("update/appcast.xml")
  log("--- " + appcast)
  if is_file(appcast):
    log("! file exist, skip")
  else:
    command = "env LANG=en_US.UTF-8 awk " + \
        ' '.join(awk_args) + " -f update/appcast.xml.awk"
    appcast_result = proc_open(command)
    if appcast_result['stderr'] != "":
      log("! error: " + appcast_result['stderr'])
    write_file(appcast, appcast_result['stdout'])

  appcast_prod = get_path("update/appcast-prod.xml")
  log("--- " + appcast_prod)
  if is_file(appcast_prod):
    log("! file exist, skip")
  else:
    command = "env LANG=en_US.UTF-8 awk -v Prod=1 " + \
        ' '.join(awk_args) + " -f update/appcast.xml.awk"
    appcast_result = proc_open(command)
    if appcast_result['stderr'] != "":
      log("! error: " + appcast_result['stderr'])
    write_file(appcast_prod, appcast_result['stdout'])

  changes_dir = get_path(build_branding_dir, "update/changes", version)
  for lang, base in update_changes_list.items():
    changes = get_path("update/" + base + ".html")
    if   lang == 'en': encoding = 'en_US.UTF-8'
    elif lang == 'ru': encoding = 'ru_RU.UTF-8'
    log("--- " + changes)
    if is_file(changes):
      log("! file exist, skip")
    else:
      command = "env LANG=" + encoding + " awk " + ' '.join(awk_args) + \
        " -f update\\changes.html.awk " + changes_dir + "\\" + lang + ".html"
      changes_result = proc_open(command)
      if changes_result['stderr'] != "":
        log("! error: " + changes_result['stderr'])
      write_file(changes, changes_result['stdout'])
  return

def make_advinst():
  log("\n=== Build advanced installer project\n")
  log("--- " + advinst_file)
  if is_file(advinst_file):
    log("! file exist, skip")
    return
  if not onlyoffice:
    branding_path = get_abspath(git_dir, branding_dir)
    copy_dir_content(
      branding_path + "\\win-linux\\package\\windows\\data", "data", ".bmp")
    copy_dir_content(
      branding_path + "\\win-linux\\package\\windows\\data", "data", ".png")
    copy_dir_content(
      branding_path + "\\win-linux\\extras\\projicons\\res",
      "..\\..\\extras\\projicons\\res", ".ico")
    copy_file(
      branding_path + "\\win-linux\\package\\windows\\dictionary.ail",
      "dictionary.ail")
    copy_file(
      branding_path + "\\common\\package\\license\\eula_" + branding + ".rtf",
      "..\\..\\..\\common\\package\\license\\agpl-3.0.rtf")
    copy_file(
      branding_path + "\\..\\multimedia\\videoplayer\\icons\\" + branding + ".ico",
      "..\\..\\extras\\projicons\\res\\media.ico")
    copy_file(
      branding_path + "\\..\\multimedia\\imageviewer\\icons\\ico\\" + branding + ".ico",
      "..\\..\\extras\\projicons\\res\\gallery.ico")
  aic_content = [";aic"]
  if not sign:
    aic_content += [
      "ResetSig"
    ]
  if machine == '32': 
    aic_content += [
      "SetPackageType x86",
      "SetAppdir -buildname DefaultBuild -path [ProgramFilesFolder][MANUFACTURER_INSTALL_FOLDER]\\[PRODUCT_INSTALL_FOLDER]",
      'DelPrerequisite "Microsoft Visual C++ 2015-2022 Redistributable (x64)"',
      'DelPrerequisite "Microsoft Visual C++ 2013 Redistributable (x64)"'
    ]
  if machine == '64': 
    aic_content += [
      'DelPrerequisite "Microsoft Visual C++ 2015-2022 Redistributable (x86)"',
      'DelPrerequisite "Microsoft Visual C++ 2013 Redistributable (x86)"'
    ]
  if onlyoffice:
    aic_content += [
      "DelFolder CUSTOM_PATH"
    ]
  else:
    aic_content += [
      "DelLanguage 1029 -buildname DefaultBuild",
      "DelLanguage 1031 -buildname DefaultBuild",
      "DelLanguage 1041 -buildname DefaultBuild",
      "DelLanguage 1046 -buildname DefaultBuild",
      "DelLanguage 2070 -buildname DefaultBuild",
      "DelLanguage 1060 -buildname DefaultBuild",
      "DelLanguage 1036 -buildname DefaultBuild",
      "DelLanguage 3082 -buildname DefaultBuild",
      "DelLanguage 1033 -buildname DefaultBuild",
      "NewSync CUSTOM_PATH " + source_dir + "\\..\\MediaViewer",
      "UpdateFile CUSTOM_PATH\\ImageViewer.exe " + source_dir + "\\..\\MediaViewer\\ImageViewer.exe",
      "UpdateFile CUSTOM_PATH\\VideoPlayer.exe " + source_dir + "\\..\\MediaViewer\\VideoPlayer.exe",
      "SetProperty ASCC_REG_PREFIX=" + ascc_reg_prefix
    ]
  aic_content += [
    "AddOsLc -buildname DefaultBuild -arch " + arch,
    "NewSync APPDIR " + source_dir,
    "UpdateFile APPDIR\\DesktopEditors.exe " + source_dir + "\\DesktopEditors.exe",
    "SetVersion " + package_version,
    "SetPackageName " + advinst_file + " -buildname DefaultBuild",
    "Rebuild -buildslist DefaultBuild"
  ]
  write_file("DesktopEditors.aic", "\r\n".join(aic_content), 'utf-8-sig')
  cmd("AdvancedInstaller.com",
      ["/execute", "DesktopEditors.aip", "DesktopEditors.aic"])
  return

def make_win_portable():
  log("\n=== Build portable\n")
  log("--- " + portable_zip_file)
  if is_file(portable_zip_file):
    log("! file exist, skip")
    return
  cmd("7z", ["a", "-y", portable_zip_file, get_path(source_dir, "*")])
  return

#
# macOS
#

def make_macos():
  global suffix, lane, scheme

  set_cwd(git_dir + "/" + branding_build_dir)

  if 'clean' in targets:
    log("\n=== Clean\n")
    delete_dir(get_env("HOME") + "/Library/Developer/Xcode/Archives")
    delete_dir(get_env("HOME") + "/Library/Caches/Sparkle_generate_appcast")

  for target in targets:
    if not target.startswith('diskimage'):
      continue

    if target.startswith('diskimage'):
      if   (target == 'diskimage-x86_64'):    suffix = 'x86_64'
      elif (target == 'diskimage-x86_64-v8'): suffix = 'v8'
      elif (target == 'diskimage-arm64'):  suffix = 'arm'
      else: exit(1)
      lane = "release_" + suffix
      scheme = package_name + '-' + suffix

      make_diskimage(target)

      if ('sparkle-updates' in targets):
        make_sparkle_updates()
  return

def make_diskimage(target):
  log("\n=== Build package " + scheme + "\n")
  log("--- build/" + package_name + ".app")
  cmd("bundler", ["exec", "fastlane", lane, "skip_git_bump:true"])
  return

def make_sparkle_updates():
  log("\n=== Build sparkle updates\n")

  app_version = proc_open("/usr/libexec/PlistBuddy \
    -c 'print :CFBundleShortVersionString' \
    build/" + package_name + ".app/Contents/Info.plist")['stdout']
  zip_filename = scheme + '-' + app_version
  macos_zip = "build/" + zip_filename + ".zip"
  updates_storage_dir = "%s/%s/_updates" % (get_env('ARCHIVES_DIR'), scheme)
  create_dir(updates_dir)
  copy_dir_content(updates_storage_dir, updates_dir, ".zip")
  # copy_dir_content(updates_storage_dir, updates_dir, ".html")
  copy_file(macos_zip, updates_dir)

  if "en" in update_changes_list:
    notes_src = "%s/%s/%s.html" % (changes_dir, app_version, update_changes_list["en"])
    notes_dst = "%s/%s.html" % (updates_dir, zip_filename)
    if is_file(notes_src):
      copy_file(notes_src, notes_dst)
      cur_date = sh_output("env LC_ALL=en_US.UTF-8 date -u \"+%B %e, %Y\"", verbose=True)
      replace_in_file(notes_dst,
                      r"(<span class=\"releasedate\">).+(</span>)",
                      "\\1 - " + cur_date + "\\2")
    else:
      write_file(notes_dst, '<html></html>\n')

  if "ru" in update_changes_list:
    notes_src = "%s/%s/%s.html" % (changes_dir, app_version, update_changes_list["ru"])
    if update_changes_list["ru"] != "ReleaseNotes":
      notes_dst = "%s/%s.ru.html" % (updates_dir, zip_filename)
    else:
      notes_dst = "%s/%s.html" % (updates_dir, zip_filename)
    if is_file(notes_src):
      copy_file(notes_src, notes_dst)
      cur_date = sh_output("env LC_ALL=ru_RU.UTF-8 date -u \"+%e %B %Y\"", verbose=True)
      replace_in_file(notes_dst,
                      r"(<span class=\"releasedate\">).+(</span>)",
                      "\\1 - " + cur_date + "\\2")
    else:
      write_file(notes_dst, '<html></html>\n')

  sparkle_download_url = "%s/%s/updates/" % (sparkle_base_url, suffix)
  sparkle_release_notes_url = "%s/%s/updates/changes/%s/" % (sparkle_base_url, suffix, app_version)
  cmd(git_dir + "/" + build_dir + "/Vendor/Sparkle/bin/generate_appcast", [
      updates_dir,
      "--download-url-prefix", sparkle_download_url,
      "--release-notes-url-prefix", sparkle_release_notes_url
    ])

  log("\n=== Edit Sparkle appcast links\n")
  appcast_url = sparkle_base_url + "/" + suffix
  appcast = "%s/%s.xml" % (updates_dir, package_name.lower())

  for lang, base in update_changes_list.items():
    if base == "ReleaseNotes":
      replace_in_file(appcast,
        r'(<sparkle:releaseNotesLink>.+/).+(\.html</sparkle:releaseNotesLink>)',
        "\\1" + base + "\\2")
    else:
      replace_in_file(appcast,
        r'(<sparkle:releaseNotesLink xml:lang="' + lang + r'">).+(\.html</sparkle:releaseNotesLink>)',
        "\\1" + sparkle_release_notes_url + base + "\\2")

  log("\n=== Delete unnecessary files\n")
  for file in os.listdir(updates_dir):
    if (-1 == file.find(app_version)) and (file.endswith(".zip") or
          file.endswith(".html")):
      delete_file(updates_dir + '/' + file)
  return
