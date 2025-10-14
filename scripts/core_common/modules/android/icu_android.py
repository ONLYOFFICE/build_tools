#!/usr/bin/env python

import sys
sys.path.append('../../../scripts')
import base
import os
import android_ndk

current_dir = base.get_script_dir() + "/../../core/Common/3dParty/icu/android"
current_dir = os.path.abspath(current_dir)
if not current_dir.endswith("/"):
  current_dir += "/"

icu_major = "74"
icu_minor = "2"

options = {
  "--enable-strict"       : "no",
  "--enable-extras"       : "no",
  "--enable-draft"        : "yes",
  "--enable-samples"      : "no",
  "--enable-tests"        : "no",
  "--enable-renaming"     : "yes",
  "--enable-icuio"        : "no",
  "--enable-layoutex"     : "no",
  "--with-library-bits"   : "nochange",
  "--with-library-suffix" : "",
  "--enable-static"       : "yes",
  "--enable-shared"       : "no",
  "--with-data-packaging" : "archive"
}

cpp_flags_base = [
  "-Os",
  "-ffunction-sections",
  "-fdata-sections",
  "-fvisibility=hidden",
  "-fPIC"
]

cpp_flags = [
  "-fno-short-wchar",
  "-fno-short-enums",

  "-DU_USING_ICU_NAMESPACE=0",
  "-DU_HAVE_NL_LANGINFO_CODESET=0",
  "-DU_TIMEZONE=0",
  "-DU_DISABLE_RENAMING=0",

  "-DUCONFIG_NO_COLLATION=0",
  "-DUCONFIG_NO_FORMATTING=0",
  "-DUCONFIG_NO_REGULAR_EXPRESSIONS=0",
  "-DUCONFIG_NO_TRANSLITERATION=0",

  "-DU_STATIC_IMPLEMENTATION"
]

def fetch_icu(major, minor):
  if not base.is_dir(current_dir + "icu"):
    base.cmd("git", ["clone", "--depth", "1", "--branch", "release-" + major + "-" + minor, "https://github.com/unicode-org/icu.git", current_dir + "icu2"])
    base.copy_dir(current_dir + "icu2/icu4c", current_dir + "icu")
    base.delete_dir_with_access_error(current_dir + "icu2")
  return

def build_host():
  cross_build_dir = os.path.abspath(current_dir + "icu/cross_build")
  if not base.is_dir(cross_build_dir):
    base.create_dir(cross_build_dir)
    os.chdir(cross_build_dir)

    ld_flags = "-pthread"
    if ("linux" == base.host_platform()):
      ld_flags += " -Wl,--gc-sections"
    else:
      # gcc on OSX does not support --gc-sections
      ld_flags += " -Wl,-dead_strip"

    base.set_env("LDFLAGS", ld_flags)
    base.set_env("CPPFLAGS", android_ndk.get_options_array_as_string(cpp_flags_base + cpp_flags))

    host_type = "Linux"
    if ("mac" == base.host_platform()):
      host_type = "MacOSX/GCC"

    base.cmd("../source/runConfigureICU", [host_type, "--prefix=" + cross_build_dir] + android_ndk.get_options_dict_as_array(options))
    base.cmd("make", ["-j4"])
    base.cmd("make", ["install"], True)

    base.create_dir(current_dir + "build")
    base.copy_dir(cross_build_dir + "/include", current_dir + "build/include")

    os.chdir(current_dir)
  return

def build_arch(arch):
  dst_dir = current_dir + "build/" + android_ndk.platforms[arch]["dst"]
  if base.is_dir(dst_dir):
    return

  android_ndk.prepare_platform(arch)
  android_ndk.extend_cflags(" ".join(cpp_flags))

  ndk_dir = android_ndk.ndk_dir()
  toolchain = android_ndk.toolchain_dir()

  cross_build_dir = os.path.abspath(current_dir + "icu/cross_build")
  arch_build_dir = os.path.abspath(current_dir + "build/tmp")
  base.create_dir(arch_build_dir)

  os.chdir(arch_build_dir)
  base.cmd("./../../icu/source/configure", ["--with-cross-build=" + cross_build_dir] +
    android_ndk.get_options_dict_as_array(options) + ["--host=" + android_ndk.platforms[arch]["target"], "--prefix=" + arch_build_dir])
  base.cmd("make", ["-j4"])
  os.chdir(current_dir)

  base.create_dir(dst_dir)
  base.copy_file(arch_build_dir + "/lib/libicuuc.a", dst_dir)
  base.copy_file(arch_build_dir + "/stubdata/libicudata.a", dst_dir)
  base.copy_file(arch_build_dir + "/data/out/icudt" + icu_major + "l.dat", dst_dir)

  base.delete_dir(arch_build_dir)
  return

def make():
  if not base.is_dir(current_dir):
    base.create_dir(current_dir)

  old_env = dict(os.environ)

  fetch_icu(icu_major, icu_minor)

  build_host()

  for arch in android_ndk.archs:
    build_arch(arch)

  os.environ.clear()
  os.environ.update(old_env)
  return

if __name__ == "__main__":
  make()
