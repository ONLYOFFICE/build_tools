#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import package_utils as utils
import package_common as common
import package_branding as branding

def make():
  utils.log_h1("DESKTOP")
  if utils.is_windows():
    make_windows()
  elif utils.is_macos():
    make_macos()
  elif utils.is_linux():
    make_linux()
  else:
    utils.log("Unsupported host OS")
  return

def aws_s3_upload(local, key, ptype=None):
  if common.os_family == "windows":
    rc = utils.cmd(
        "aws", "s3", "cp", "--acl", "public-read", "--no-progress",
        local, "s3://" + common.s3_bucket + "/" + key,
        verbose=True
    )
  else:
    rc = utils.sh("aws s3 cp --acl public-read --no-progress " \
        + local + " s3://" + common.s3_bucket + "/" + key, verbose=True)
  if rc == 0 and ptype is not None:
    utils.add_deploy_data("desktop", ptype, local, key)
  return rc

#
# Windows
#

def make_windows():
  global package_version, iscc_args, source_dir, arch_list, inno_arch_list, \
    inno_file, inno_update_file, msi_file, zip_file, key_prefix
  utils.set_cwd("desktop-apps\\win-linux\\package\\windows")

  prefix = common.platforms[common.platform]["prefix"]
  company = branding.company_name.lower()
  product = branding.desktop_product_name.replace(" ","").lower()
  package_name = branding.desktop_package_name
  package_version = common.version + "." + common.build
  source_dir = "..\\..\\..\\..\\build_tools\\out\\%s\\%s\\%s" % (prefix, company, product)
  arch_list = {
    "windows_x64":    "x64",
    "windows_x64_xp": "x64",
    "windows_x86":    "x86",
    "windows_x86_xp": "x86"
  }
  inno_arch_list = {
    "windows_x64":    "64",
    "windows_x86":    "32",
    "windows_x64_xp": "64",
    "windows_x86_xp": "32"
  }
  suffix = arch_list[common.platform]
  if common.platform.endswith("_xp"): suffix += "_xp"
  zip_file = "%s_%s_%s.zip" % (package_name, package_version, suffix)
  inno_file = "%s_%s_%s.exe" % (package_name, package_version, suffix)
  inno_update_file = "update\\editors_update_%s.exe" % suffix
  msi_file = "%s_%s_%s.msi" % (package_name, package_version, suffix)
  key_prefix = "%s/%s/windows/desktop/%s/%s" % (branding.company_name_l, \
      common.release_branch, common.version, common.build)

  if common.clean:
    utils.log_h2("desktop clean")
    # utils.delete_dir("data\\vcredist")
    utils.delete_dir("DesktopEditors-cache")
    utils.delete_files("*.exe")
    utils.delete_files("*.msi")
    utils.delete_files("*.aic")
    utils.delete_files("*.tmp")
    utils.delete_files("*.zip")
    utils.delete_files("update\\*.exe")
    utils.delete_files("update\\*.xml")
    utils.delete_files("update\\*.html")

  make_zip()

  vcdl = True
  vcdl &= download_vcredist("2013")
  vcdl &= download_vcredist("2022")

  if not vcdl:
    utils.set_summary("desktop inno build", False)
    utils.set_summary("desktop inno update build", False)
    utils.set_summary("desktop advinst build", False)
    utils.set_cwd(common.workspace_dir)
    return

  make_inno()
  make_inno_update()

  if common.platform == "windows_x64":
    make_winsparkle_files()

  if common.platform in ["windows_x64", "windows_x86"]:
    make_msi()

  utils.set_cwd(common.workspace_dir)
  return

def make_zip():
  utils.log_h2("desktop zip build")
  rc = utils.cmd(
      "7z", "a", "-y", zip_file, source_dir + "\\*",
      creates=zip_file,
      verbose=True
  )
  utils.set_summary("desktop zip build", rc == 0)

  if rc == 0:
    utils.log_h2("desktop zip deploy")
    zip_key = key_prefix + "/" + utils.get_basename(zip_file)
    rc = aws_s3_upload(zip_file, zip_key, "Portable")
  utils.set_summary("desktop zip deploy", rc == 0)
  return

def download_vcredist(year):
  utils.log_h2("vcredist " + year + " download")

  arch = arch_list[common.platform]
  link = common.vcredist_links[year][arch]["url"]
  md5 = common.vcredist_links[year][arch]["md5"]
  vcredist_file = "data\\vcredist\\vcredist_%s_%s.exe" % (year, arch)

  utils.log_h2(vcredist_file)
  utils.create_dir(utils.get_dirname(vcredist_file))
  rc = utils.download_file(link, vcredist_file, md5, verbose=True)
  utils.set_summary("vcredist " + year + " download", rc == 0)
  return rc == 0

def make_inno():
  global iscc_args
  utils.log_h2("desktop inno build")
  utils.log_h2(inno_file)

  iscc_args = [
    # "/Qp",
    "/DsAppVersion=" + package_version,
    "/DDEPLOY_PATH=" + source_dir,
    "/D_ARCH=" + inno_arch_list[common.platform]
  ]
  if branding.onlyoffice:
    iscc_args.append("/D_ONLYOFFICE=1")
  else:
    iscc_args.append("/DsBrandingFolder=" + \
        utils.get_abspath(common.workspace_dir + "\\" + common.branding + "\\desktop-apps"))
  if common.platform in ["windows_x64_xp", "windows_x86_xp"]:
    iscc_args.append("/D_WIN_XP=1")
  if common.sign:
    iscc_args.append("/DENABLE_SIGNING=1")
    iscc_args.append("/Sbyparam=signtool.exe sign /v /n $q" + \
        branding.cert_name + "$q /t " + common.tsa_server + " $f")
  args = ["iscc"] + iscc_args + ["common.iss"]
  rc = utils.cmd(*args, creates=inno_file, verbose=True)
  utils.set_summary("desktop inno build", rc == 0)

  if rc == 0:
    utils.log_h2("desktop inno deploy")
    inno_key = key_prefix + "/" + utils.get_basename(inno_file)
    rc = aws_s3_upload(inno_file, inno_key, "Installer")
  utils.set_summary("desktop inno deploy", rc == 0)
  return

def make_inno_update():
  utils.log_h2("desktop inno update build")
  utils.log_h2(inno_update_file)

  args = ["iscc"] + iscc_args + ["/DTARGET_NAME=" + inno_file, "update_common.iss"]
  rc = utils.cmd(*args, creates=inno_update_file, verbose=True)
  utils.set_summary("desktop inno update build", rc == 0)

  if rc == 0:
    utils.log_h2("desktop inno update deploy")
    inno_update_key = key_prefix + "/" + utils.get_basename(inno_update_file)
    rc = aws_s3_upload(inno_update_file, inno_update_key, "WinSparkle")
  utils.set_summary("desktop inno update deploy", rc == 0)
  return

def make_winsparkle_files():
  utils.log_h2("desktop winsparkle files build")

  if branding.onlyoffice:
    awk_branding = "update/branding.awk"
  else:
    awk_branding = "../../../../" + common.branding + \
        "/desktop-apps/win-linux/package/windows/update/branding.awk"
  awk_args = [
    "-v", "Version=" + common.version,
    "-v", "Build=" + common.build,
    "-v", "Branch=" + common.release_branch,
    "-v", "Timestamp=" + common.timestamp,
    "-i", awk_branding
  ]

  appcast = "update/appcast.xml"
  utils.log_h2(appcast)
  args = ["env", "LANG=en_US.UTF-8", "awk"] + \
      awk_args + ["-f", "update/appcast.xml.awk"]
  appcast_result = utils.cmd_output(*args, verbose=True)
  utils.write_file(appcast, appcast_result)

  appcast_prod = "update/appcast-prod.xml"
  utils.log_h2(appcast_prod)
  args = ["env", "LANG=en_US.UTF-8", "awk", "-v", "Prod=1"] + \
      awk_args + ["-f", "update/appcast.xml.awk"]
  appcast_result = utils.cmd_output(*args, verbose=True)
  utils.write_file(appcast_prod, appcast_result)

  if branding.onlyoffice:
    changes_dir = "update/changes/" + common.version
  else:
    changes_dir = "../../../../" + common.branding + \
        "/desktop-apps/win-linux/package/windows/update/changes/" + common.version
  for lang, base in branding.desktop_update_changes_list.items():
    changes = "update/%s.html" % base
    if   lang == "en": encoding = "en_US.UTF-8"
    elif lang == "ru": encoding = "ru_RU.UTF-8"
    utils.log_h2(changes)
    changes_file = "%s/%s.html" % (changes_dir, lang)
    args = ["env", "LANG=" + encoding, "awk"] + awk_args + \
      ["-f", "update/changes.html.awk", changes_file]

    if utils.is_exist(changes_file):
      changes_result = utils.cmd_output(*args, verbose=True)
      print(changes_result)
      utils.write_file(changes, changes_result)
    else:
      utils.log("! file not exist: " + changes_file)

  utils.log_h2("desktop winsparkle files deploy")
  rc = 0

  appcast_key = key_prefix + "/" + utils.get_basename(appcast)
  rc_appcast = aws_s3_upload(appcast, appcast_key, "WinSparkle")
  rc += rc_appcast

  appcast_prod_key = key_prefix + "/" + utils.get_basename(appcast_prod)
  rc_appcast_prod = aws_s3_upload(appcast_prod, appcast_prod_key, "WinSparkle")
  rc += rc_appcast_prod

  for lang, base in branding.desktop_update_changes_list.items():
    changes_file = "update/%s.html" % base
    changes_key = key_prefix + "/" + utils.get_basename(changes_file)
    if utils.is_exist(changes_file):
      rc_changes = aws_s3_upload(changes_file, changes_key, "WinSparkle")
      rc += rc_changes

  utils.set_summary("desktop winsparkle files deploy", rc == 0)
  return

def make_msi():
  utils.log_h2("desktop msi build")
  utils.log_h2(msi_file)

  arch = arch_list[common.platform]

  if not branding.onlyoffice:
    branding_path = common.workspace_dir + "\\" + common.branding
    utils.copy_dir_content(
      branding_path + "\\desktop-apps\\win-linux\\package\\windows\\data", "data", ".bmp")
    utils.copy_dir_content(
      branding_path + "\\desktop-apps\\win-linux\\package\\windows\\data", "data", ".png")
    utils.copy_dir_content(
      branding_path + "\\desktop-apps\\win-linux\\extras\\projicons\\res",
      "..\\..\\extras\\projicons\\res", ".ico")
    utils.copy_file(
      branding_path + "\\desktop-apps\\win-linux\\package\\windows\\dictionary.ail",
      "dictionary.ail")
    utils.copy_file(
      branding_path + "\\desktop-apps\\common\\package\\license\\eula_" + common.branding + ".rtf",
      "..\\..\\..\\common\\package\\license\\agpl-3.0.rtf")
    utils.copy_file(
      branding_path + "\\multimedia\\videoplayer\\icons\\" + common.branding + ".ico",
      "..\\..\\extras\\projicons\\res\\media.ico")
    utils.copy_file(
      branding_path + "\\multimedia\\imageviewer\\icons\\ico\\" + common.branding + ".ico",
      "..\\..\\extras\\projicons\\res\\gallery.ico")

  aic_content = [";aic"]
  if not common.sign:
    aic_content += [
      "ResetSig"
    ]
  if arch == "x86": 
    aic_content += [
      "SetPackageType x86",
      "SetAppdir -buildname DefaultBuild -path [ProgramFilesFolder][MANUFACTURER_INSTALL_FOLDER]\\[PRODUCT_INSTALL_FOLDER]",
      'DelPrerequisite "Microsoft Visual C++ 2015-2022 Redistributable (x64)"',
      'DelPrerequisite "Microsoft Visual C++ 2013 Redistributable (x64)"'
    ]
  if arch == "x64": 
    aic_content += [
      'DelPrerequisite "Microsoft Visual C++ 2015-2022 Redistributable (x86)"',
      'DelPrerequisite "Microsoft Visual C++ 2013 Redistributable (x86)"'
    ]
  if branding.onlyoffice:
    aic_content += [
      "DelFolder CUSTOM_PATH"
    ]
  else:
    utils.replace_in_file('DesktopEditors.aip','(<ROW Property="UpgradeCode" Value=")(.*)("/>)', r'\1%s\3' % (branding.desktop_upgrade_code))
    aic_content += [
      "AddUpgradeCode {47EEF706-B0E4-4C43-944B-E5F914B92B79} \
        -min_ver 7.1.1 -include_min_ver \
        -max_ver 7.2.2 -include_max_ver \
        -include_lang 1049 \
        -property_name UPGRADE_2 -enable_migrate",
      "DelLanguage 1029 -buildname DefaultBuild",
      "DelLanguage 1031 -buildname DefaultBuild",
      "DelLanguage 1041 -buildname DefaultBuild",
      "DelLanguage 1046 -buildname DefaultBuild",
      "DelLanguage 2070 -buildname DefaultBuild",
      "DelLanguage 1060 -buildname DefaultBuild",
      "DelLanguage 1036 -buildname DefaultBuild",
      "DelLanguage 3082 -buildname DefaultBuild",
      "DelLanguage 1033 -buildname DefaultBuild",
      "SetCurrentFeature ExtendedFeature",
      "NewSync CUSTOM_PATH " + source_dir + "\\..\\MediaViewer",
      "UpdateFile CUSTOM_PATH\\ImageViewer.exe " + source_dir + "\\..\\MediaViewer\\ImageViewer.exe",
      "UpdateFile CUSTOM_PATH\\VideoPlayer.exe " + source_dir + "\\..\\MediaViewer\\VideoPlayer.exe"
    ]
  aic_content += [
    "AddOsLc -buildname DefaultBuild -arch " + arch,
    "SetCurrentFeature MainFeature",
    "NewSync APPDIR " + source_dir,
    "UpdateFile APPDIR\\DesktopEditors.exe " + source_dir + "\\DesktopEditors.exe",
    "SetVersion " + package_version,
    "SetPackageName " + msi_file + " -buildname DefaultBuild",
    "Rebuild -buildslist DefaultBuild"
  ]
  utils.write_file("DesktopEditors.aic", "\r\n".join(aic_content), "utf-8-sig")
  rc = utils.cmd("AdvancedInstaller.com", "/execute", \
    "DesktopEditors.aip", "DesktopEditors.aic", verbose=True)
  utils.set_summary("desktop msi build", rc == 0)

  if rc == 0:
    utils.log_h2("desktop msi deploy")
    msi_key = key_prefix + "/" + utils.get_basename(msi_file)
    rc = aws_s3_upload(msi_file, msi_key, "Installer")
  utils.set_summary("desktop msi deploy", rc == 0)
  return

#
# macOS
#

def make_macos():
  global package_name, build_dir, branding_dir, updates_dir, changes_dir, \
    update_changes_list, suffix, lane, scheme, key_prefix
  package_name = branding.desktop_package_name
  build_dir = branding.desktop_build_dir
  branding_dir = branding.desktop_branding_dir
  updates_dir = branding.desktop_updates_dir
  changes_dir = branding.desktop_changes_dir
  update_changes_list = branding.desktop_update_changes_list
  suffixes = {
    "macos_x86_64":    "x86_64",
    "macos_x86_64_v8": "v8",
    "macos_arm64":     "arm64"
  }
  suffix = suffixes[common.platform]
  lane = "release_" + suffix
  scheme = package_name + "-" + suffix
  key_prefix = "%s/%s/macos/%s/%s/%s" % (branding.company_name_l, \
      common.release_branch, suffix, common.version, common.build)

  utils.set_cwd(build_dir)

  if 'clean' in targets:
    utils.log("\n=== Clean\n")
    utils.delete_dir(utils.get_env("HOME") + "/Library/Developer/Xcode/Archives")
    utils.delete_dir(utils.get_env("HOME") + "/Library/Caches/Sparkle_generate_appcast")

  script = '''
    appcast=$(curl -s ''' + branding.sparkle_base_url + '''/''' + suffix + '''/onlyoffice.xml 2> /dev/null)
    echo -n \"RELEASE_MACOS_VERSION=\"
    echo $appcast \
      | xmllint --xpath \"/rss/channel/item[1]/enclosure/@*[name()='sparkle:shortVersionString']\" - \
      | cut -f 2 -d \\\\\"
    echo -n \"RELEASE_MACOS_BUILD=\"
    echo $appcast \
      | xmllint --xpath \"/rss/channel/item[1]/enclosure/@*[name()='sparkle:version']\" - \
      | cut -f 2 -d \\\\\"

    path=desktop-apps/macos/ONLYOFFICE/Resources/ONLYOFFICE-''' + suffix + '''/Info.plist
    echo -n \"CURRENT_MACOS_VERSION=\"
    /usr/libexec/PlistBuddy -c 'print :CFBundleShortVersionString' $path
    echo -n \"CURRENT_MACOS_BUILD=\"
    /usr/libexec/PlistBuddy -c 'print :CFBundleVersion' $path
  '''
  utils.sh_output(script, verbose=True)

  make_dmg()
  # if :
  make_sparkle_updates()

  utils.set_cwd(common.workspace_dir)
  return

def make_dmg():
  utils.log_h2("desktop dmg build")
  utils.log_h2(scheme)
  utils.log_h2("build/" + package_name + ".app")
  rc = utils.sh(
      "bundler exec fastlane " + lane + " git_bump:false",
      verbose=True
  )
  utils.set_summary("desktop dmg build", rc == 0)

  if rc == 0:
    utils.log_h2("desktop dmg deploy")
    dmg_file = utils.glob_file("build/*.dmg")
    dmg_key = key_prefix + "/" + utils.get_basename(dmg_file)
    rc = aws_s3_upload(dmg_file, dmg_key, "Disk Image")
  utils.set_summary("desktop msi deploy", rc == 0)
  return

def make_sparkle_updates():
  utils.log_h2("desktop sparkle files build")

  app_version = utils.sh_output("/usr/libexec/PlistBuddy \
    -c 'print :CFBundleShortVersionString' \
    build/" + package_name + ".app/Contents/Info.plist", verbose=True)
  zip_filename = scheme + '-' + app_version
  macos_zip = "build/" + zip_filename + ".zip"
  updates_storage_dir = "%s/%s/_updates" % (get_env('ARCHIVES_DIR'), scheme)
  utils.create_dir(updates_dir)
  utils.copy_dir_content(updates_storage_dir, updates_dir, ".zip")
  # utils.copy_dir_content(updates_storage_dir, updates_dir, ".html")
  utils.copy_file(macos_zip, updates_dir)

  if "en" in update_changes_list:
    notes_src = "%s/%s/%s.html" % (changes_dir, app_version, update_changes_list["en"])
    if utils.is_file(notes_src):
      notes_dst = "%s/%s.html" % (updates_dir, zip_filename)
      utils.copy_file(notes_src, notes_dst)
      cur_date = utils.sh_output("env LC_ALL=en_US.UTF-8 date -u \"+%B %e, %Y\"", verbose=True)
      utils.replace_in_file(notes_dst,
                      r"(<span class=\"releasedate\">).+(</span>)",
                      "\\1 - " + cur_date + "\\2")
    else:
      utils.write_file(notes_dst, '<html></html>\n')

  if "ru" in update_changes_list:
    notes_src = "%s/%s/%s.html" % (changes_dir, app_version, update_changes_list["ru"])
    if utils.is_file(notes_src):
      if update_changes_list["ru"] != "ReleaseNotes":
        notes_dst = "%s/%s.ru.html" % (updates_dir, zip_filename)
      else:
        notes_dst = "%s/%s.html" % (updates_dir, zip_filename)
      utils.copy_file(notes_src, notes_dst)
      cur_date = utils.sh_output("env LC_ALL=ru_RU.UTF-8 date -u \"+%e %B %Y\"", verbose=True)
      utils.replace_in_file(notes_dst,
                      r"(<span class=\"releasedate\">).+(</span>)",
                      "\\1 - " + cur_date + "\\2")
    else:
      utils.write_file(notes_dst, '<html></html>\n')

  sparkle_download_url = "%s/%s/updates/" % (branding.sparkle_base_url, suffix)
  sparkle_release_notes_url = "%s/%s/updates/changes/%s/" % (branding.sparkle_base_url, suffix, app_version)
  utils.sh(common.workspace_dir \
      + "/desktop-apps/macos/Vendor/Sparkle/bin/generate_appcast " \
      + updates_dir \
      + " --download-url-prefix " + sparkle_download_url \
      + " --release-notes-url-prefix " + sparkle_release_notes_url)

  utils.log_h3("edit sparkle appcast links")
  appcast_url = branding.sparkle_base_url + "/" + suffix
  appcast = "%s/%s.xml" % (updates_dir, package_name.lower())

  for lang, base in update_changes_list.items():
    if base == "ReleaseNotes":
      utils.replace_in_file(appcast,
          r'(<sparkle:releaseNotesLink>.+/).+(\.html</sparkle:releaseNotesLink>)',
          "\\1" + base + "\\2")
    else:
      utils.replace_in_file(appcast,
          r'(<sparkle:releaseNotesLink xml:lang="' + lang + r'">).+(\.html</sparkle:releaseNotesLink>)',
          "\\1" + base + "\\2")

  utils.log_h3("delete unnecessary files")
  for file in os.listdir(updates_dir):
    if (-1 == file.find(app_version)) and (file.endswith(".zip") or
          file.endswith(".html")):
      utils.delete_file(updates_dir + '/' + file)

  utils.log_h3("generate checksums")
  utils.sh(
      "md5 *.zip *.delta > md5sums.txt && " \
      + "shasum -a 256 *.zip *.delta > sha256sums.txt",
      chdir="build/update",
      verbose=True
  )

  utils.log_h2("desktop sparkle files deploy")
  rc = 0

  zip_key = key_prefix + "/" + utils.get_basename(macos_zip)
  rc_zip = aws_s3_upload(macos_zip, zip_key, "Sparkle")
  rc += rc_zip

  for path in utils.glob_files("build/update/*.delta") \
      + utils.glob_files("build/update/*.xml") \
      + utils.glob_files("build/update/*.html"):
    sparkle_key = key_prefix + "/" + utils.get_basename(path)
    rc_sparkle = aws_s3_upload(path, sparkle_key, "Sparkle")
    rc += rc_sparkle

  utils.set_summary("desktop sparkle files deploy", rc == 0)

  utils.log_h2("desktop checksums deploy")
  rc = 0

  for path in utils.glob_files("build/update/*.txt"):
    checksums_key = key_prefix + "/" + utils.get_basename(path)
    rc_checksums = aws_s3_upload(path, checksums_key, "Checksums")
    rc += rc_checksums

  utils.set_summary("desktop checksums deploy", rc == 0)
  return

#
# Linux
#

def make_linux():
  utils.set_cwd("desktop-apps/win-linux/package/linux")

  rc = utils.sh("make clean", verbose=True)
  utils.set_summary("desktop clean", rc == 0)

  args = []
  if common.platform == "linux_aarch64":
    args += ["-e", "UNAME_M=aarch64"]
  if not branding.onlyoffice:
    args += ["-e", "BRANDING_DIR=../../../../" + common.branding + "/desktop-apps/win-linux/package/linux"]
  rc = utils.sh("make packages " + " ".join(args), verbose=True)
  utils.set_summary("desktop build", rc == 0)

  key_prefix = branding.company_name_l + "/" + common.release_branch
  if common.platform == "linux_x86_64":
    rpm_arch = "x86_64"
  elif common.platform == "linux_aarch64":
    rpm_arch = "aarch64"
  if rc == 0:
    utils.log_h2("desktop tar deploy")
    tar_file = utils.glob_file("tar/*.tar.gz")
    tar_key = key_prefix + "/linux/" + utils.get_basename(tar_file)
    rc = aws_s3_upload(tar_file, tar_key, "Portable")
    utils.set_summary("desktop tar deploy", rc == 0)

    utils.log_h2("desktop deb deploy")
    deb_file = utils.glob_file("deb/*.deb")
    deb_key = key_prefix + "/ubuntu/" + utils.get_basename(deb_file)
    rc = aws_s3_upload(deb_file, deb_key, "Ubuntu")
    utils.set_summary("desktop deb deploy", rc == 0)

    utils.log_h2("desktop rpm deploy")
    rpm_file = utils.glob_file("rpm/builddir/RPMS/" + rpm_arch + "/*.rpm")
    rpm_key = key_prefix + "/centos/" + utils.get_basename(rpm_file)
    rc = aws_s3_upload(rpm_file, rpm_key, "CentOS")
    utils.set_summary("desktop rpm deploy", rc == 0)

    utils.log_h2("desktop apt-rpm deploy")
    apt_rpm_file = utils.glob_file("apt-rpm/builddir/RPMS/" + rpm_arch + "/*.rpm")
    apt_rpm_key = key_prefix + "/altlinux/" + utils.get_basename(apt_rpm_file)
    rc = aws_s3_upload(apt_rpm_file, apt_rpm_key, "AltLinux")
    utils.set_summary("desktop apt-rpm deploy", rc == 0)

    utils.log_h2("desktop urpmi deploy")
    urpmi_file = utils.glob_file("urpmi/builddir/RPMS/" + rpm_arch + "/*.rpm")
    urpmi_key = key_prefix + "/rosa/" + utils.get_basename(urpmi_file)
    rc = aws_s3_upload(urpmi_file, urpmi_key, "Rosa")
    utils.set_summary("desktop urpmi deploy", rc == 0)

    # utils.log_h2("desktop suse-rpm deploy")
    # suse_rpm_file = utils.glob_file("suse-rpm/builddir/RPMS/" + rpm_arch + "/*.rpm")
    # suse_rpm_key = key_prefix + "/suse/" + utils.get_basename(suse_rpm_file)
    # rc = aws_s3_upload(suse_rpm_file, suse_rpm_key, "SUSE Linux")
    # utils.set_summary("desktop suse-rpm deploy", rc == 0)

    if not branding.onlyoffice:
      utils.log_h2("desktop deb-astra deploy")
      deb_astra_file = utils.glob_file("deb-astra/*.deb")
      deb_astra_key = key_prefix + "/" + utils.get_basename(deb_astra_file)
      rc = aws_s3_upload(deb_astra_file, deb_astra_key, "AstraLinux Signed")
      utils.set_summary("desktop deb-astra deploy", rc == 0)

  else:
    utils.set_summary("desktop tar deploy", False)
    utils.set_summary("desktop deb deploy", False)
    utils.set_summary("desktop rpm deploy", False)
    utils.set_summary("desktop apt-rpm deploy", False)
    utils.set_summary("desktop urpmi deploy", False)
    utils.set_summary("desktop suse-rpm deploy", False)
    if not branding.onlyoffice:
      utils.set_summary("desktop deb-astra deploy", False)

  utils.set_cwd(common.workspace_dir)
  return
