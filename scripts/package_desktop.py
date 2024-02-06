#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
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

def s3_upload(files, dst):
  if not files: return False
  ret = True
  for f in files:
    key = dst + utils.get_basename(f) if dst.endswith("/") else dst
    upload = utils.s3_upload(f, "s3://" + branding.s3_bucket + "/" + key)
    if upload:
      utils.add_deploy_data(key)
      utils.log("URL: " + branding.s3_base_url + "/" + key)
    ret &= upload
  return ret

#
# Windows
#

def make_windows():
  global package_version, arch_list, source_dir, branding_dir, desktop_dir, viewer_dir, \
    inno_file, inno_sa_file, inno_update_file, inno_update_file_new, advinst_file
  utils.set_cwd("desktop-apps\\win-linux\\package\\windows")

  package_name = branding.desktop_package_name
  package_version = common.version + "." + common.build
  arch_list = {
    "windows_x64":    "x64",
    "windows_x64_xp": "x64",
    "windows_x86":    "x86",
    "windows_x86_xp": "x86"
  }
  suffix = arch_list[common.platform]
  if common.platform.endswith("_xp"): suffix += "-xp"
  inno_file = "%s-%s-%s.exe" % (package_name, package_version, suffix)
  inno_sa_file = "%s-Standalone-%s-%s.exe" % (package_name, package_version, suffix)
  inno_update_file = "update\\editors_update_%s.exe" % suffix.replace("-","_")
  inno_update_file_new = "%s-Update-%s-%s.exe" % (package_name, package_version, suffix)
  advinst_file = "%s-%s-%s.msi" % (package_name, package_version, suffix)
  if branding.onlyoffice:
    branding_dir = "."
  else:
    branding_dir = common.workspace_dir + "\\" + common.branding + "\\desktop-apps\\win-linux\\package\\windows"

  if common.clean:
    utils.log_h2("desktop clean")
    utils.delete_dir("build")
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

  utils.log_h2("copy arifacts")
  source_dir = "%s\\build_tools\\out\\%s\\%s" \
    % (common.workspace_dir, common.prefix, branding.company_name)
  utils.create_dir("build")
  desktop_dir = "build\\" + branding.desktop_product_name_s
  utils.copy_dir(source_dir + "\\" + branding.desktop_product_name_s, desktop_dir)
  if not branding.onlyoffice:
    viewer_dir = "build\\" + branding.viewer_product_name_s
    utils.copy_dir(source_dir + "\\" + branding.viewer_product_name_s, viewer_dir)

  make_zip()

  if not download_vcredist():
    utils.set_summary("desktop inno build", False)
    utils.set_summary("desktop inno standalone build", False)
    utils.set_summary("desktop inno update build", False)
    utils.set_summary("desktop advinst build", False)
    utils.set_cwd(common.workspace_dir)
    return

  make_inno()

  if common.platform == "windows_x64":
    make_update_files()

  if common.platform in ["windows_x64", "windows_x86"]:
    make_advinst()

  utils.set_cwd(common.workspace_dir)
  return

def make_zip():
  utils.log_h2("desktop zip build")

  args = [
    "-Target", common.platform,
    "-BuildDir", "build",
    "-DesktopDir", branding.desktop_product_name_s
  ]
  if not branding.onlyoffice:
    args += ["-MultimediaDir", branding.viewer_product_name_s]
    args += ["-BrandingDir", branding_dir]
  if branding.onlyoffice and not common.platform.endswith("_xp"):
    args += ["-ExcludeHelp"]
  if common.sign:
    args += ["-Sign", "-CertName", branding.cert_name]
  ret = utils.ps1("make_zip.ps1", args, verbose=True)
  utils.set_summary("desktop zip build", ret)

  if common.deploy and ret:
    utils.log_h2("desktop zip deploy")
    ret = s3_upload(utils.glob_path("*.zip"), "desktop/win/generic/")
    utils.set_summary("desktop zip deploy", ret)
  return

def download_vcredist():
  vcredist = {
    # Microsoft Visual C++ 2015-2022 Redistributable - 14.38.33135
    "windows_x64": {
      "url": "https://aka.ms/vs/17/release/vc_redist.x64.exe",
      "md5": "a8a68bcc74b5022467f12587baf1ef93"
    },
    "windows_x86": {
      "url": "https://aka.ms/vs/17/release/vc_redist.x86.exe",
      "md5": "9882a328c8414274555845fa6b542d1e"
    },
    # Microsoft Visual C++ 2015-2019 Redistributable - 14.27.29114
    "windows_x64_xp": {
      "url": "https://download.visualstudio.microsoft.com/download/pr/722d59e4-0671-477e-b9b1-b8da7d4bd60b/591CBE3A269AFBCC025681B968A29CD191DF3C6204712CBDC9BA1CB632BA6068/VC_redist.x64.exe",
      "md5": "bc8e3e714b727b3bb18614bd6a51a3d3"
    },
    "windows_x86_xp": {
      "url": "https://download.visualstudio.microsoft.com/download/pr/c168313d-1754-40d4-8928-18632c2e2a71/D305BAA965C9CD1B44EBCD53635EE9ECC6D85B54210E2764C8836F4E9DEFA345/VC_redist.x86.exe",
      "md5": "ec3bee79a85ae8e3581a8c181b336d1e"
    }
  }
  vcredist_file = "data\\vcredist_%s.exe" % arch_list[common.platform]

  utils.log_h2("vcredist download " + vcredist_file)
  ret = utils.download_file(
    vcredist[common.platform]["url"],
    vcredist_file,
    vcredist[common.platform]["md5"],
    verbose=True)
  utils.set_summary("vcredist download", ret)
  return ret

def make_inno():
  utils.log_h2("desktop inno build")

  inno_arch_list = {
    "windows_x64":    "64",
    "windows_x86":    "32",
    "windows_x64_xp": "64",
    "windows_x86_xp": "32"
  }
  iscc_args = [
    "/Qp",
    "/DVERSION=" + package_version,
    "/DsAppVersion=" + package_version,
    "/DDEPLOY_PATH=" + desktop_dir,
    "/DARCH=" + arch_list[common.platform],
    "/D_ARCH=" + inno_arch_list[common.platform],
  ]
  if branding.onlyoffice:
    iscc_args.append("/D_ONLYOFFICE=1")
  else:
    iscc_args.append("/DsBrandingFolder=" + \
        utils.get_abspath(common.workspace_dir + "\\" + common.branding + "\\desktop-apps"))
  if common.platform.endswith("_xp"):
    iscc_args.append("/D_WIN_XP=1")
  if common.sign:
    iscc_args.append("/DENABLE_SIGNING=1")
    iscc_args.append("/Sbyparam=signtool.exe sign /a /v /n $q" + \
        branding.cert_name + "$q /t " + common.tsa_server + " $f")
  args = ["iscc"] + iscc_args + ["common.iss"]
  ret = utils.cmd(*args, creates=inno_file, verbose=True)
  utils.set_summary("desktop inno build", ret)

  if branding.onlyoffice and not common.platform.endswith("_xp"):
    args = ["iscc"] + iscc_args + ["/DEMBED_HELP", "/DsPackageEdition=Standalone", "common.iss"]
    ret = utils.cmd(*args, creates=inno_sa_file, verbose=True)
    utils.set_summary("desktop inno standalone build", ret)

  if not (hasattr(branding, 'desktop_updates_skip_iss_wrapper') and branding.desktop_updates_skip_iss_wrapper):
    args = ["iscc"] + iscc_args + ["/DTARGET_NAME=" + inno_file, "update_common.iss"]
    ret = utils.cmd(*args, creates=inno_update_file, verbose=True)
    utils.set_summary("desktop inno update build", ret)

  if common.deploy:
    utils.log_h2("desktop inno deploy")
    ret = s3_upload([inno_file], "desktop/win/inno/")
    utils.set_summary("desktop inno deploy", ret)

    if branding.onlyoffice and not common.platform.endswith("_xp"):
      utils.log_h2("desktop inno standalone deploy")
      ret = s3_upload([inno_sa_file], "desktop/win/inno/")
      utils.set_summary("desktop inno standalone deploy", ret)

    utils.log_h2("desktop inno update deploy")
    if utils.is_file(inno_update_file):
      ret = s3_upload(
        [inno_update_file], "desktop/win/inno/" + inno_update_file_new)
    elif utils.is_file(inno_file):
      ret = s3_upload(
        [inno_file], "desktop/win/inno/" + inno_update_file_new)
    else:
      ret = False
    utils.set_summary("desktop inno update deploy", ret)
  return

def make_update_files():
  utils.log_h2("desktop update files build")

  changes_dir = common.workspace_dir + "\\" + utils.get_path(branding.desktop_changes_dir) + "\\" + common.version

  if common.deploy and utils.glob_path(changes_dir + "\\*.html"):
    utils.log_h2("desktop update files deploy")
    ret = s3_upload(
      utils.glob_path(changes_dir + "\\*.html"),
      "desktop/win/update/%s/%s/" % (common.version, common.build))
    utils.set_summary("desktop update files deploy", ret)
  return

def make_advinst():
  utils.log_h2("desktop advinst build")

  msi_build = {
    "windows_x64": "MsiBuild64",
    "windows_x86": "MsiBuild32"
  }[common.platform]

  if not branding.onlyoffice:
    multimedia_dir = common.workspace_dir + "\\" + common.branding + "\\multimedia"
    utils.copy_file(branding_dir + "\\dictionary.ail", "dictionary.ail")
    utils.copy_dir_content(branding_dir + "\\data", "data", ".bmp")
    utils.copy_dir_content(branding_dir + "\\data", "data", ".png")
    utils.copy_dir_content(
      branding_dir + "\\..\\..\\extras\\projicons\\res",
      "..\\..\\extras\\projicons\\res",
      ".ico")
    utils.copy_file(
      branding_dir + "\\..\\..\\..\\common\\package\\license\\eula_" + common.branding + ".rtf",
      "..\\..\\..\\common\\package\\license\\agpl-3.0.rtf")
    utils.copy_file(
      multimedia_dir + "\\imageviewer\\icons\\ico\\" + common.branding + ".ico",
      "..\\..\\extras\\projicons\\res\\icons\\gallery.ico")
    utils.copy_file(
      multimedia_dir + "\\videoplayer\\icons\\" + common.branding + ".ico",
      "..\\..\\extras\\projicons\\res\\icons\\media.ico")

  utils.write_file(desktop_dir + "\\converter\\package.config", "package=msi")

  aic_content = [";aic"]
  if not common.sign:
    aic_content += [
      "ResetSig"
    ]
  if branding.onlyoffice:
    for path in utils.glob_path(desktop_dir + "\\editors\\web-apps\\apps\\*\\main\\resources\\help"):
      utils.delete_dir(path)
    aic_content += [
      "DelFolder CUSTOM_PATH"
    ]
  else:
    aic_content += [
      "SetProperty UpgradeCode=\"" + branding.desktop_upgrade_code + "\"",
      "AddUpgradeCode {47EEF706-B0E4-4C43-944B-E5F914B92B79} \
        -min_ver 7.1.1 -include_min_ver \
        -max_ver 7.2.2 -include_max_ver \
        -include_lang 1049 \
        -property_name UPGRADE_2 -enable_migrate",
      "DelLanguage 1029 -buildname " + msi_build,
      "DelLanguage 1031 -buildname " + msi_build,
      "DelLanguage 1041 -buildname " + msi_build,
      "DelLanguage 1046 -buildname " + msi_build,
      "DelLanguage 2070 -buildname " + msi_build,
      "DelLanguage 1060 -buildname " + msi_build,
      "DelLanguage 1036 -buildname " + msi_build,
      "DelLanguage 3082 -buildname " + msi_build,
      "DelLanguage 1033 -buildname " + msi_build,
      "SetCurrentFeature ExtendedFeature",
      "NewSync CUSTOM_PATH " + viewer_dir,
      "UpdateFile CUSTOM_PATH\\ImageViewer.exe " + viewer_dir + "\\ImageViewer.exe",
      "UpdateFile CUSTOM_PATH\\VideoPlayer.exe " + viewer_dir + "\\VideoPlayer.exe",
      "SetProperty ProductName=\"" + branding.desktop_product_name_full + "\"",
      "SetProperty ASCC_REG_PREFIX=" + branding.ascc_reg_prefix
    ]
    if common.platform == "windows_x86":
      aic_content += [
        "SetComponentAttribute -feature_name ExtendedFeature -unset -64bit_component"
      ]
  if common.platform == "windows_x86":
    aic_content += [
      "SetComponentAttribute -feature_name MainFeature -unset -64bit_component",
      "SetComponentAttribute -feature_name FileProgIds -unset -64bit_component",
      "SetComponentAttribute -feature_name FileOpenWith -unset -64bit_component",
      "SetComponentAttribute -feature_name FileProgramCapatibilities -unset -64bit_component",
      "SetComponentAttribute -feature_name FileTypeAssociations -unset -64bit_component",
      "SetComponentAttribute -feature_name FileNewTemplates -unset -64bit_component"
    ]
  aic_content += [
    "SetCurrentFeature MainFeature",
    "NewSync APPDIR " + desktop_dir,
    "UpdateFile APPDIR\\DesktopEditors.exe " + desktop_dir + "\\DesktopEditors.exe",
    "UpdateFile APPDIR\\updatesvc.exe " + desktop_dir + "\\updatesvc.exe",
    "SetProperty VERSION=\"" + package_version + "\"",
    "SetProperty VERSION_SHORT=\"" + re.sub(r"^(\d+\.\d+).+", "\\1", package_version) + "\"",
    "SetVersion " + package_version,
    "SetPackageName " + advinst_file + " -buildname " + msi_build,
    "Rebuild -buildslist " + msi_build
  ]
  utils.write_file("DesktopEditors.aic", "\r\n".join(aic_content), "utf-8-sig")
  ret = utils.cmd("AdvancedInstaller.com", "/execute", \
    "DesktopEditors.aip", "DesktopEditors.aic", verbose=True)
  utils.set_summary("desktop advinst build", ret)

  if common.deploy and ret:
    utils.log_h2("desktop advinst deploy")
    ret = s3_upload([advinst_file], "desktop/win/advinst/")
    utils.set_summary("desktop advinst deploy", ret)
  return

#
# macOS
#

def make_macos():
  global package_name, build_dir, branding_dir, updates_dir, changes_dir, \
    suffix, lane, scheme, released_updates_dir
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
  sparkle_updates = False

  utils.set_cwd(branding_dir)

  if common.clean:
    utils.log_h2("clean")
    utils.delete_dir(utils.get_env("HOME") + "/Library/Developer/Xcode/Archives")
    utils.delete_dir(utils.get_env("HOME") + "/Library/Caches/Sparkle_generate_appcast")

  utils.log_h2("build")
  source_dir = "%s/build_tools/out/%s/%s" \
    % (common.workspace_dir, common.prefix, branding.company_name)
  if branding.onlyoffice:
    for path in utils.glob_path(source_dir \
        + "/desktopeditors/editors/web-apps/apps/*/main/resources/help"):
      utils.delete_dir(path)

  if utils.get_env("ARCHIVES_DIR"):
    sparkle_updates = True
    released_updates_dir = "%s/%s/_updates" % (utils.get_env("ARCHIVES_DIR"), scheme)
    plistbuddy = "/usr/libexec/PlistBuddy"
    plist_path = "%s/%s/ONLYOFFICE/Resources/%s-%s/Info.plist" \
        % (common.workspace_dir, branding_dir, package_name, suffix)

    appcast = utils.sh_output('%s -c "Print :SUFeedURL" %s' \
        % (plistbuddy, plist_path), verbose=True).rstrip()
    appcast = released_updates_dir + "/" + appcast[appcast.rfind("/")+1:]

    release_version_string = utils.sh_output(
        'xmllint --xpath "/rss/channel/item[1]/*[name()=\'sparkle:shortVersionString\']/text()" ' + appcast,
        verbose=True).rstrip()
    release_version = utils.sh_output(
        'xmllint --xpath "/rss/channel/item[1]/*[name()=\'sparkle:version\']/text()" ' + appcast,
        verbose=True).rstrip()
    bundle_version = str(int(release_version) + 1)
    help_url = "https://download.onlyoffice.com/install/desktop/editors/help/v" + common.version + "/apps"

    utils.sh('%s -c "Set :CFBundleShortVersionString %s" %s' \
        % (plistbuddy, common.version, plist_path), verbose=True)
    utils.sh('%s -c "Set :CFBundleVersion %s" %s' \
        % (plistbuddy, bundle_version, plist_path), verbose=True)
    utils.sh('%s -c "Set :ASCBundleBuildNumber %s" %s' \
        % (plistbuddy, common.build, plist_path), verbose=True)
    utils.sh('%s -c "Add :ASCWebappsHelpUrl string %s" %s' \
        % (plistbuddy, help_url, plist_path), verbose=True)

    utils.log("RELEASE=" + release_version_string + "(" + release_version + ")" \
          + "\nCURRENT=" + common.version + "(" + bundle_version + ")")

  dmg = make_dmg()
  if dmg and sparkle_updates:
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
    ret = s3_upload(
      utils.glob_path("build/*.dmg"),
      "desktop/mac/%s/%s/%s/" % (suffix, common.version, common.build))
    utils.set_summary("desktop dmg deploy", ret)

    utils.log_h2("desktop zip deploy")
    ret = s3_upload(
      ["build/%s-%s.zip" % (scheme, common.version)],
      "desktop/mac/%s/%s/%s/" % (suffix, common.version, common.build))
    utils.set_summary("desktop zip deploy", ret)
  return dmg

def make_sparkle_updates():
  utils.log_h2("desktop sparkle files build")

  zip_filename = scheme + '-' + common.version
  macos_zip = "build/" + zip_filename + ".zip"
  utils.create_dir(updates_dir)
  utils.copy_file(macos_zip, updates_dir)
  utils.copy_dir_content(released_updates_dir, updates_dir, ".zip")

  for file in utils.glob_path(changes_dir + "/" + common.version + "/*.html"):
    filename = utils.get_basename(file).replace("changes", zip_filename)
    utils.copy_file(file, updates_dir + "/" + filename)

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
    ret = s3_upload(
      utils.glob_path("build/update/*.delta") \
      + utils.glob_path("build/update/*.xml") \
      + utils.glob_path("build/update/*.html"),
      "desktop/mac/%s/%s/%s/" % (suffix, common.version, common.build))
    utils.set_summary("desktop sparkle files deploy", ret)
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

  rpm_arch = "*"
  if common.platform == "linux_aarch64": rpm_arch = "aarch64"

  if common.deploy:
    if ret:
      utils.log_h2("desktop tar deploy")
      if "tar" in branding.desktop_make_targets:
        ret = s3_upload(
          utils.glob_path("tar/*.tar*"),
          "desktop/linux/generic/")
        utils.set_summary("desktop tar deploy", ret)
      if "deb" in branding.desktop_make_targets:
        utils.log_h2("desktop deb deploy")
        ret = s3_upload(
          utils.glob_path("deb/*.deb"),
          "desktop/linux/debian/")
        utils.set_summary("desktop deb deploy", ret)
      if "deb-astra" in branding.desktop_make_targets:
        utils.log_h2("desktop deb-astra deploy")
        ret = s3_upload(
          utils.glob_path("deb-astra/*.deb"),
          "desktop/linux/astra/")
        utils.set_summary("desktop deb-astra deploy", ret)
      if "rpm" in branding.desktop_make_targets:
        utils.log_h2("desktop rpm deploy")
        ret = s3_upload(
          utils.glob_path("rpm/builddir/RPMS/" + rpm_arch + "/*.rpm"),
          "desktop/linux/rhel/")
        utils.set_summary("desktop rpm deploy", ret)
      if "suse-rpm" in branding.desktop_make_targets:
        utils.log_h2("desktop suse-rpm deploy")
        ret = s3_upload(
          utils.glob_path("suse-rpm/builddir/RPMS/" + rpm_arch + "/*.rpm"),
          "desktop/linux/suse/")
        utils.set_summary("desktop suse-rpm deploy", ret)
      if "apt-rpm" in branding.desktop_make_targets:
        utils.log_h2("desktop apt-rpm deploy")
        ret = s3_upload(
          utils.glob_path("apt-rpm/builddir/RPMS/" + rpm_arch + "/*.rpm"),
          "desktop/linux/altlinux/")
        utils.set_summary("desktop apt-rpm deploy", ret)
      if "urpmi" in branding.desktop_make_targets:
        utils.log_h2("desktop urpmi deploy")
        ret = s3_upload(
          utils.glob_path("urpmi/builddir/RPMS/" + rpm_arch + "/*.rpm"),
          "desktop/linux/rosa/")
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
