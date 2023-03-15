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

def aws_s3_upload(files, key, ptype=None):
  if not files:
    return False
  ret = True
  key = "desktop/" + key
  for file in files:
    args = ["aws"]
    if hasattr(branding, "s3_endpoint_url"):
      args += ["--endpoint-url=" + branding.s3_endpoint_url]
    args += [
      "s3", "cp", "--no-progress", "--acl", "public-read",
      file, "s3://" + branding.s3_bucket + "/" + key
    ]
    if common.os_family == "windows":
      upload = utils.cmd(*args, verbose=True)
    else:
      upload = utils.sh(" ".join(args), verbose=True)
    ret &= upload
    if upload and ptype is not None:
      full_key = key
      if full_key.endswith("/"): full_key += utils.get_basename(file)
      utils.add_deploy_data(
          "desktop", ptype, file, full_key,
          branding.s3_bucket, branding.s3_region
      )
  return ret

#
# Windows
#

def make_windows():
  global package_version, iscc_args, source_dir, source_help_dir, \
    inno_file, inno_help_file, inno_update_file, advinst_file, zip_file, \
    arch_list, inno_arch_list
  utils.set_cwd("desktop-apps\\win-linux\\package\\windows")

  prefix = common.platforms[common.platform]["prefix"]
  company = branding.company_name.lower()
  product = branding.desktop_product_name.replace(" ","").lower()
  package_name = branding.desktop_package_name
  package_version = common.version + "." + common.build
  source_dir = "..\\..\\..\\..\\build_tools\\out\\%s\\%s\\%s" % (prefix, company, product)
  source_help_dir = source_dir + "-help"
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
  inno_help_file = "%s_Help_%s_%s.exe" % (package_name, package_version, suffix)
  inno_update_file = "update\\editors_update_%s.exe" % suffix
  advinst_file = "%s_%s_%s.msi" % (package_name, package_version, suffix)

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
    utils.set_summary("desktop inno help build", False)
    utils.set_summary("desktop inno update build", False)
    utils.set_summary("desktop advinst build", False)
    utils.set_cwd(common.workspace_dir)
    return

  make_inno()

  if branding.onlyoffice and common.platform in ["windows_x64", "windows_x86"]:
    make_inno_help()

  make_inno_update()

  if common.platform == "windows_x64":
    make_update_files()

  if common.platform in ["windows_x64", "windows_x86"]:
    make_advinst()

  utils.set_cwd(common.workspace_dir)
  return

def make_zip():
  utils.log_h2("desktop zip build")
  ret = utils.cmd(
      "7z", "a", "-y", zip_file, source_dir + "\\*",
      creates=zip_file, verbose=True
  )
  utils.set_summary("desktop zip build", ret)

  if common.deploy and ret:
    utils.log_h2("desktop zip deploy")
    ret = aws_s3_upload(
        [zip_file],
        "win/generic/%s/" % common.channel,
        "Portable"
    )
    utils.set_summary("desktop zip deploy", ret)
  return

def download_vcredist(year):
  utils.log_h2("vcredist " + year + " download")

  arch = arch_list[common.platform]
  link = common.vcredist_links[year][arch]["url"]
  md5 = common.vcredist_links[year][arch]["md5"]
  vcredist_file = "data\\vcredist\\vcredist_%s_%s.exe" % (year, arch)

  utils.log_h2(vcredist_file)
  utils.create_dir(utils.get_dirname(vcredist_file))
  ret = utils.download_file(link, vcredist_file, md5, verbose=True)
  utils.set_summary("vcredist " + year + " download", ret)
  return ret

def make_inno():
  global iscc_args
  utils.log_h2("desktop inno build")
  utils.log_h3(inno_file)

  iscc_args = [
    "/Qp",
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
  ret = utils.cmd(*args, creates=inno_file, verbose=True)
  utils.set_summary("desktop inno build", ret)

  if common.deploy and ret:
    utils.log_h2("desktop inno deploy")
    ret = aws_s3_upload(
        [inno_file],
        "win/inno/%s/%s/" % (common.version, common.build),
        "Installer"
    )
    utils.set_summary("desktop inno deploy", ret)
  return

def make_inno_help():
  utils.log_h2("desktop inno help build")
  utils.log_h3(inno_help_file)

  args = [
    "iscc",
    "/Qp",
    "/DsAppVersion=" + package_version,
    "/DDEPLOY_PATH=" + source_help_dir,
    "/D_ARCH=" + inno_arch_list[common.platform]
  ]
  if branding.onlyoffice:
    args.append("/D_ONLYOFFICE=1")
  else:
    args.append("/DsBrandingFolder=" + \
        utils.get_abspath(common.workspace_dir + "\\" + common.branding + "\\desktop-apps"))
  if common.sign:
    args.append("/DENABLE_SIGNING=1")
    args.append("/Sbyparam=signtool.exe sign /v /n $q" + \
        branding.cert_name + "$q /t " + common.tsa_server + " $f")
  args.append("help.iss")
  ret = utils.cmd(*args, creates=inno_help_file, verbose=True)
  utils.set_summary("desktop inno help build", ret)

  if common.deploy and ret:
    utils.log_h2("desktop inno help deploy")
    ret = aws_s3_upload(
        [inno_help_file],
        "win/inno/%s/%s/" % (common.version, common.build),
        "Installer"
    )
    utils.set_summary("desktop inno help deploy", ret)
  return

def make_inno_update():
  utils.log_h2("desktop inno update build")
  utils.log_h3(inno_update_file)

  args = ["iscc"] + iscc_args + ["/DTARGET_NAME=" + inno_file, "update_common.iss"]
  ret = utils.cmd(*args, creates=inno_update_file, verbose=True)
  utils.set_summary("desktop inno update build", ret)

  if common.deploy and ret:
    utils.log_h2("desktop inno update deploy")
    ret = aws_s3_upload(
        [inno_update_file],
        "win/inno/%s/%s/" % (common.version, common.build),
        "WinSparkle"
    )
    utils.set_summary("desktop inno update deploy", ret)
  return

def make_update_files():
  utils.log_h2("desktop update files build")

  if branding.onlyoffice:
    changes_dir = "update\\changes\\" + common.version
  else:
    changes_dir = "..\\..\\..\\..\\" + common.branding + "\\desktop-apps\\" + \
        "win-linux\\package\\windows\\update\\changes\\" + common.version
  for lang, base in branding.desktop_update_changes_list.items():
    utils.log_h3("changes " + lang + " html")
    utils.copy_file(changes_dir + "\\" + lang + ".html", "update\\" + base + ".html")

  appcast_args = [
    "-Version", package_version,
    "-Timestamp", common.timestamp
  ]
  if branding.onlyoffice:
    appcast_args.append("-Multilang")
  appcast_prod_args = [
    "-UpdatesUrlPrefix", branding.desktop_updates_url,
    "-ReleaseNotesUrlPrefix", branding.desktop_changes_url
  ]
  appcast_test_base_url = "%s/desktop/win/inno/%s/%s" % (branding.s3_base_url, common.version, common.build)
  appcast_test_args = [
    "-UpdatesUrlPrefix", appcast_test_base_url,
    "-ReleaseNotesUrlPrefix", appcast_test_base_url
  ]

  utils.log_h3("appcast prod json")
  utils.ps1(
      "update\\make_appcast.ps1",
      appcast_args + appcast_prod_args,
      creates="update\\appcast.json", verbose=True
  )
  utils.log_h3("appcast prod xml")
  utils.ps1(
      "update\\make_appcast_xml.ps1",
      appcast_args + appcast_prod_args,
      creates="update\\appcast.xml", verbose=True
  )
  utils.log_h3("appcast test json")
  utils.ps1(
      "update\\make_appcast.ps1",
      appcast_args + appcast_test_args + ["-OutFile", "appcast-test.json"],
      creates="update\\appcast-test.json", verbose=True
  )
  utils.log_h3("appcast test xml")
  utils.ps1(
      "update\\make_appcast_xml.ps1",
      appcast_args + appcast_test_args + ["-OutFile", "appcast-test.xml"],
      creates="update\\appcast-test.xml", verbose=True
  )

  if common.deploy:
    utils.log_h2("desktop update files deploy")
    ret = aws_s3_upload(
        utils.glob_path("update/*.json") + utils.glob_path("update/*.xml") + \
            utils.glob_path("update/*.html"),
        "win/inno/%s/%s/" % (common.version, common.build),
        "Update"
    )
    utils.set_summary("desktop update files deploy", ret)
  return

def make_advinst():
  utils.log_h2("desktop advinst build")
  utils.log_h3(advinst_file)

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
  if arch == "x64": 
    aic_content += [
      "SetPackageType x64 -buildname DefaultBuild",
      "AddOsLc -buildname DefaultBuild -arch x64",
      "DelOsLc -buildname DefaultBuild -arch x86",
      'DelPrerequisite "Microsoft Visual C++ 2015-2022 Redistributable (x86)"',
      'DelPrerequisite "Microsoft Visual C++ 2013 Redistributable (x86)"'
    ]
  if arch == "x86": 
    aic_content += [
      "SetPackageType x86 -buildname DefaultBuild",
      "AddOsLc -arch x86 -buildname DefaultBuild",
      "DelOsLc -arch x64 -buildname DefaultBuild",
      "SetAppdir -path [ProgramFilesFolder][MANUFACTURER_INSTALL_FOLDER]\\[PRODUCT_INSTALL_FOLDER] -buildname DefaultBuild",
      'DelPrerequisite "Microsoft Visual C++ 2015-2022 Redistributable (x64)"',
      'DelPrerequisite "Microsoft Visual C++ 2013 Redistributable (x64)"'
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
      "UpdateFile CUSTOM_PATH\\VideoPlayer.exe " + source_dir + "\\..\\MediaViewer\\VideoPlayer.exe",
      "SetProperty ASCC_REG_PREFIX=" + branding.ascc_reg_prefix
    ]
  aic_content += [
    "SetCurrentFeature MainFeature",
    "NewSync APPDIR " + source_dir,
    "UpdateFile APPDIR\\DesktopEditors.exe " + source_dir + "\\DesktopEditors.exe",
    "SetVersion " + package_version,
    "SetPackageName " + advinst_file + " -buildname DefaultBuild",
    "Rebuild -buildslist DefaultBuild"
  ]
  utils.write_file("DesktopEditors.aic", "\r\n".join(aic_content), "utf-8-sig")
  ret = utils.cmd("AdvancedInstaller.com", "/execute", \
    "DesktopEditors.aip", "DesktopEditors.aic", verbose=True)
  utils.set_summary("desktop advinst build", ret)

  if common.deploy and ret:
    utils.log_h2("desktop advinst deploy")
    ret = aws_s3_upload(
        [advinst_file],
        "win/advinst/%s/" % common.channel,
        "Installer"
    )
    utils.set_summary("desktop advinst deploy", ret)
  return

#
# macOS
#

def make_macos():
  global package_name, build_dir, branding_dir, updates_dir, changes_dir, \
    suffix, lane, scheme, app_version
  package_name = branding.desktop_package_name
  build_dir = branding.desktop_build_dir
  branding_dir = branding.desktop_branding_dir
  updates_dir = branding.desktop_updates_dir
  changes_dir = branding.desktop_changes_dir
  suffix = {
    "darwin_x86_64":    "x86_64",
    "darwin_x86_64_v8": "v8",
    "darwin_arm64":     "arm"
  }[common.platform]
  lane = "release_" + suffix
  scheme = package_name + "-" + suffix

  utils.set_cwd(branding_dir)

  if common.clean:
    utils.log_h2("clean")
    utils.delete_dir(utils.get_env("HOME") + "/Library/Developer/Xcode/Archives")
    utils.delete_dir(utils.get_env("HOME") + "/Library/Caches/Sparkle_generate_appcast")

  appcast_url = branding.sparkle_base_url + "/" + suffix + "/" + branding.desktop_package_name.lower() + ".xml"
  release_bundle_version_string = utils.sh_output(
    'curl -Ls ' + appcast_url + ' 2> /dev/null' \
    + ' | xmllint --xpath "/rss/channel/item[1]/enclosure/@*[name()=\'sparkle:shortVersionString\']" -' \
    + ' | cut -f2 -d\\\"',
    verbose=True).rstrip()
  release_bundle_version = utils.sh_output(
    'curl -Ls ' + appcast_url + ' 2> /dev/null' \
    + ' | xmllint --xpath "/rss/channel/item[1]/enclosure/@*[name()=\'sparkle:version\']" -' \
    + ' | cut -f2 -d\\\"',
    verbose=True).rstrip()

  app_version = common.version
  bundle_version = str(int(release_bundle_version) + 1)
  plist_path = "%s/%s/ONLYOFFICE/Resources/%s-%s/Info.plist" \
      % (common.workspace_dir, branding.desktop_branding_dir, branding.desktop_package_name, suffix)
  utils.sh('/usr/libexec/PlistBuddy -c "Set :CFBundleShortVersionString %s" %s' \
      % (common.version, plist_path), verbose=True)
  utils.sh('/usr/libexec/PlistBuddy -c "Set :CFBundleVersion %s" %s' \
      % (bundle_version, plist_path), verbose=True)

  utils.log("RELEASE=" + release_bundle_version_string + "(" + release_bundle_version + ")" \
        + "\nCURRENT=" + common.version + "(" + bundle_version + ")")

  dmg = make_dmg()
  if dmg:
    make_sparkle_updates()

  utils.set_cwd(common.workspace_dir)
  return

def make_dmg():
  utils.log_h2("desktop dmg build")
  utils.log_h3(scheme)
  utils.log_h3("build/" + package_name + ".app")
  dmg = utils.sh(
      "bundler exec fastlane " + lane + " skip_git_bump:true",
      verbose=True
  )
  utils.set_summary("desktop dmg build", dmg)

  if common.deploy and dmg:
    utils.log_h2("desktop dmg deploy")
    ret = aws_s3_upload(
        utils.glob_path("build/*.dmg"),
        "mac/%s/%s/%s/" % (suffix, common.version, common.build),
        "Disk Image"
    )
    utils.set_summary("desktop dmg deploy", ret)

    utils.log_h2("desktop zip deploy")
    ret = aws_s3_upload(
        ["build/%s-%s.zip" % (scheme, app_version)],
        "mac/%s/%s/%s/" % (suffix, common.version, common.build),
        "Archive"
    )
    utils.set_summary("desktop zip deploy", ret)
  return dmg

def make_sparkle_updates():
  utils.log_h2("desktop sparkle files build")

  zip_filename = scheme + '-' + app_version
  macos_zip = "build/" + zip_filename + ".zip"
  updates_storage_dir = "%s/%s/_updates" % (utils.get_env('ARCHIVES_DIR'), scheme)
  utils.create_dir(updates_dir)
  utils.copy_file(macos_zip, updates_dir)
  utils.copy_dir_content(updates_storage_dir, updates_dir, ".zip")
  utils.copy_file(
      changes_dir + "/" + app_version + "/ReleaseNotes.html",
      updates_dir + "/" + zip_filename + ".html"
  )
  utils.copy_file(
      changes_dir + "/" + app_version + "/ReleaseNotesRU.html",
      updates_dir + "/" + zip_filename + ".ru.html"
  )

  sparkle_base_url = "%s/%s/updates/" % (branding.sparkle_base_url, suffix)
  ret = utils.sh(
      common.workspace_dir \
      + "/desktop-apps/macos/Vendor/Sparkle/bin/generate_appcast " \
      + updates_dir \
      + " --download-url-prefix " + sparkle_base_url \
      + " --release-notes-url-prefix " + sparkle_base_url,
      verbose=True
  )
  utils.set_summary("desktop sparkle files build", ret)

  # utils.log_h3("edit sparkle appcast links")
  # appcast_url = branding.sparkle_base_url + "/" + suffix
  # appcast = "%s/%s.xml" % (updates_dir, package_name.lower())
  # for lang, base in update_changes_list.items():
  #   if base == "ReleaseNotes":
  #     utils.replace_in_file(appcast,
  #         r'(<sparkle:releaseNotesLink>.+/).+(\.html</sparkle:releaseNotesLink>)',
  #         "\\1" + base + "\\2")
  #   else:
  #     utils.replace_in_file(appcast,
  #         r'(<sparkle:releaseNotesLink xml:lang="' + lang + r'">).+(\.html</sparkle:releaseNotesLink>)',
  #         "\\1" + base + "\\2")

  utils.log("")
  utils.log_h3("generate checksums")
  utils.sh(
      "md5 *.zip *.delta > md5sums.txt",
      chdir="build/update", verbose=True
  )
  utils.sh(
      "shasum -a 256 *.zip *.delta > sha256sums.txt",
      chdir="build/update", verbose=True
  )

  if common.deploy:
    utils.log_h2("desktop sparkle files deploy")
    ret = aws_s3_upload(
        utils.glob_path("build/update/*.delta") \
        + utils.glob_path("build/update/*.xml") \
        + utils.glob_path("build/update/*.html"),
        "mac/%s/%s/%s/" % (suffix, common.version, common.build),
        "Sparkle"
    )
    utils.set_summary("desktop sparkle files deploy", ret)

    utils.log_h2("desktop checksums deploy")
    ret = aws_s3_upload(
        utils.glob_path("build/update/*.txt"),
        "mac/%s/%s/%s/" % (suffix, common.version, common.build),
        "Checksums"
    )
    utils.set_summary("desktop checksums deploy", ret)
  return

#
# Linux
#

def make_linux():
  utils.set_cwd("desktop-apps/win-linux/package/linux")

  utils.log_h2("desktop build")
  make_args = branding.desktop_make_targets
  if common.platform == "linux_aarch64":
    make_args += ["-e", "UNAME_M=aarch64"]
  if not branding.onlyoffice:
    make_args += ["-e", "BRANDING_DIR=../../../../" + common.branding + "/desktop-apps/win-linux/package/linux"]
  ret = utils.sh("make clean && make " + " ".join(make_args), verbose=True)
  utils.set_summary("desktop build", ret)

  rpm_arch = "x86_64"
  if common.platform == "linux_aarch64": rpm_arch = "aarch64"

  if common.deploy:
    utils.log_h2("desktop deploy")
    if ret:
      utils.log_h2("desktop tar deploy")
      if "tar" in branding.desktop_make_targets:
        ret = aws_s3_upload(
            utils.glob_path("tar/*.tar.gz") + utils.glob_path("tar/*.tar.xz"),
            "linux/generic/%s/" % common.channel,
            "Portable"
        )
        utils.set_summary("desktop tar deploy", ret)
      if "deb" in branding.desktop_make_targets:
        utils.log_h2("desktop deb deploy")
        ret = aws_s3_upload(
            utils.glob_path("deb/*.deb"),
            "linux/debian/%s/" % common.channel,
            "Debian"
        )
        utils.set_summary("desktop deb deploy", ret)
      if "deb-astra" in branding.desktop_make_targets:
        utils.log_h2("desktop deb-astra deploy")
        ret = aws_s3_upload(
            utils.glob_path("deb-astra/*.deb"),
            "linux/astra/",
            "Astra Linux Signed"
        )
        utils.set_summary("desktop deb-astra deploy", ret)
      if "rpm" in branding.desktop_make_targets:
        utils.log_h2("desktop rpm deploy")
        ret = aws_s3_upload(
            utils.glob_path("rpm/builddir/RPMS/" + rpm_arch + "/*.rpm") \
            + utils.glob_path("rpm/builddir/RPMS/noarch/*.rpm"),
            "linux/rhel/%s/" % common.channel,
            "CentOS"
        )
        utils.set_summary("desktop rpm deploy", ret)
      if "suse-rpm" in branding.desktop_make_targets:
        utils.log_h2("desktop suse-rpm deploy")
        ret = aws_s3_upload(
            utils.glob_path("suse-rpm/builddir/RPMS/" + rpm_arch + "/*.rpm") \
            + utils.glob_path("suse-rpm/builddir/RPMS/noarch/*.rpm"),
            "linux/suse/%s/" % common.channel,
            "SUSE Linux"
        )
        utils.set_summary("desktop suse-rpm deploy", ret)
      if "apt-rpm" in branding.desktop_make_targets:
        utils.log_h2("desktop apt-rpm deploy")
        ret = aws_s3_upload(
            utils.glob_path("apt-rpm/builddir/RPMS/" + rpm_arch + "/*.rpm") \
            + utils.glob_path("apt-rpm/builddir/RPMS/noarch/*.rpm"),
            "linux/altlinux/%s/" % common.channel,
            "ALT Linux"
        )
        utils.set_summary("desktop apt-rpm deploy", ret)
      if "urpmi" in branding.desktop_make_targets:
        utils.log_h2("desktop urpmi deploy")
        ret = aws_s3_upload(
            utils.glob_path("urpmi/builddir/RPMS/" + rpm_arch + "/*.rpm") \
            + utils.glob_path("urpmi/builddir/RPMS/noarch/*.rpm"),
            "linux/rosa/%s/" % common.channel,
            "ROSA"
        )
        utils.set_summary("desktop urpmi deploy", ret)
    else:
      if "tar" in branding.desktop_make_targets:
        utils.set_summary("desktop tar deploy", False)
      if "deb" in branding.desktop_make_targets:
        utils.set_summary("desktop deb deploy", False)
      if "deb-astra" in branding.desktop_make_targets:
        utils.set_summary("desktop deb-astra deploy", False)
      if "rpm" in branding.desktop_make_targets:
        utils.set_summary("desktop rpm deploy", False)
      if "suse-rpm" in branding.desktop_make_targets:
        utils.set_summary("desktop suse-rpm deploy", False)
      if "apt-rpm" in branding.desktop_make_targets:
        utils.set_summary("desktop apt-rpm deploy", False)
      if "urpmi" in branding.desktop_make_targets:
        utils.set_summary("desktop urpmi deploy", False)

  utils.set_cwd(common.workspace_dir)
  return
