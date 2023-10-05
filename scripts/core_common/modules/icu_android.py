#!/usr/bin/env python

import sys
sys.path.append('../..')
import base
import os

current_dir = base.get_script_dir() + "/../../core/Common/3dParty/icu/android"

toolshains_dir = current_dir + "/toolchains"
icu_major = "58"
icu_minor = "2"
icu_is_shared = False

current_path = base.get_env("PATH")

platforms = {
  "arm64" : {
    "arch" : "aarch64-linux-android",
    "bin" : "aarch64-linux-android"
  },
  "arm" : {
    "arch" : "arm-linux-androideabi",
    "bin" : "arm-linux-androideabi"
  },
  "x86_64" : {
    "arch" : "x86_64-linux-android",
    "bin" : "x86_64-linux-android"
  },
  "x86" : {
    "arch" : "x86-linux-android",
    "bin" : "i686-linux-android"
  }
}

def build_arch(arch, api_version):
  print("icu build: " + arch + " ----------------------------------------")

  if base.is_dir(current_dir + "/icu/" + arch):
    base.delete_dir(current_dir + "/icu/" + arch)
  base.create_dir(current_dir + "/icu/" + arch)
  os.chdir(current_dir + "/icu/" + arch)

  base.cmd(base.get_env("ANDROID_NDK_ROOT") + "/build/tools/make-standalone-toolchain.sh", [
    "--platform=android-" + api_version, 
    "--install-dir=" + current_dir + "/toolchain/" + arch,
    "--toolchain=" + platforms[arch]["arch"], 
    "--force"
    ])

  base.set_env("PATH", current_dir + "/toolchain/" + arch + "/bin:" + current_path)

  command_args = "--prefix=" + current_dir + "/build_tmp/" + arch + " --host=!!!MASK!!! --with-cross-build=" + current_dir + "/icu/cross_build CFLAGS=-Os CXXFLAGS=--std=c++11 CC=!!!MASK!!!-clang CXX=!!!MASK!!!-clang++ AR=!!!MASK!!!-ar RANLIB=!!!MASK!!!-ranlib"
  if not icu_is_shared:
    command_args += " --enable-static --enable-shared=no --with-data-packaging=archive CFLAGS=-fPIC CXXFLAGS=-fPIC"
  command_args = command_args.replace("!!!MASK!!!", platforms[arch]["bin"])

  base.cmd("../source/configure", command_args.split())
  base.cmd("make", ["-j4"])
  base.cmd("make", ["install"])

  base.set_env("PATH", current_path)
  os.chdir(current_dir)

  return

def make():
  if not base.is_dir(current_dir):
    base.create_dir(current_dir)

  if base.is_dir(current_dir + "/build"):
    return

  current_dir_old = os.getcwd()

  print("[fetch & build]: icu_android")
  os.chdir(current_dir)

  if not base.is_dir("icu"):
    base.cmd("svn", ["export", "https://github.com/unicode-org/icu/tags/release-" + icu_major + "-" + icu_minor + "/icu4c", "./icu", "--non-interactive", "--trust-server-cert"])
    if ("linux" == base.host_platform()):
      base.replaceInFile(current_dir + "/icu/source/i18n/digitlst.cpp", "xlocale", "locale")
    if ("mac" == base.host_platform()):
      base.replaceInFile(current_dir + "/icu/source/tools/pkgdata/pkgdata.cpp", "cmd, \"%s %s -o %s%s %s %s%s %s %s\",", "cmd, \"%s %s -o %s%s %s %s %s %s %s\",")

  if not base.is_dir(current_dir + "/icu/cross_build"):
    base.create_dir(current_dir + "/icu/cross_build")
    os.chdir(current_dir + "/icu/cross_build")
    base.cmd("../source/runConfigureICU", ["Linux" if "linux" == base.host_platform() else "MacOSX",
      "--prefix=" + current_dir + "/icu/cross_build", "CFLAGS=-Os CXXFLAGS=--std=c++11"])
    base.cmd("make", ["-j4"])
    base.cmd("make", ["install"], True)

  os.chdir(current_dir)

  build_arch("arm64", "21")
  build_arch("arm", "16")
  build_arch("x86_64","21")
  build_arch("x86", "16")

  os.chdir(current_dir)

  base.create_dir(current_dir + "/build")
  base.copy_dir(current_dir + "/build_tmp/arm64/include", current_dir + "/build/include")

  if icu_is_shared:
    base.create_dir(current_dir + "/build/arm64_v8a")
    base.copy_file(current_dir + "/build_tmp/arm64/lib/libicudata.so." + icu_major + "." + icu_minor, current_dir + "/build/arm64_v8a/libicudata.so")
    base.copy_file(current_dir + "/build_tmp/arm64/lib/libicuuc.so." + icu_major + "." + icu_minor, current_dir + "/build/arm64_v8a/libicuuc.so")

    base.create_dir(current_dir + "/build/armv7")
    base.copy_file(current_dir + "/build_tmp/arm/lib/libicudata.so." + icu_major + "." + icu_minor, current_dir + "/build/armv7/libicudata.so")
    base.copy_file(current_dir + "/build_tmp/arm/lib/libicuuc.so." + icu_major + "." + icu_minor, current_dir + "/build/armv7/libicuuc.so")

    base.create_dir(current_dir + "/build/x86_64")
    base.copy_file(current_dir + "/build_tmp/x86_64/lib/libicudata.so." + icu_major + "." + icu_minor, current_dir + "/build/x86_64/libicudata.so")
    base.copy_file(current_dir + "/build_tmp/x86_64/lib/libicuuc.so." + icu_major + "." + icu_minor, current_dir + "/build/x86_64/libicuuc.so")

    base.create_dir(current_dir + "/build/x86")
    base.copy_file(current_dir + "/build_tmp/x86/lib/libicudata.so." + icu_major + "." + icu_minor, current_dir + "/build/x86/libicudata.so")
    base.copy_file(current_dir + "/build_tmp/x86/lib/libicuuc.so." + icu_major + "." + icu_minor, current_dir + "/build/x86/libicuuc.so")

    # patch elf information
    os.chdir(current_dir + "/build")
    base.cmd("git", ["clone", "https://github.com/NixOS/patchelf.git"])
    os.chdir("./patchelf")
    base.cmd("./bootstrap.sh")
    base.cmd("./configure", ["--prefix=" + current_dir + "/build/patchelf/usr"])
    base.cmd("make")
    base.cmd("make", ["install"])

    base.cmd("./usr/bin/patchelf", ["--set-soname", "libicudata.so", "./../arm64_v8a/libicudata.so"])
    base.cmd("./usr/bin/patchelf", ["--set-soname", "libicuuc.so", "./../arm64_v8a/libicuuc.so"])
    base.cmd("./usr/bin/patchelf", ["--replace-needed", "libicudata.so." + icu_major, "libicudata.so", "./../arm64_v8a/libicuuc.so"])

    base.cmd("./usr/bin/patchelf", ["--set-soname", "libicudata.so", "./../armv7/libicudata.so"])
    base.cmd("./usr/bin/patchelf", ["--set-soname", "libicuuc.so", "./../armv7/libicuuc.so"])
    base.cmd("./usr/bin/patchelf", ["--replace-needed", "libicudata.so." + icu_major, "libicudata.so", "./../armv7/libicuuc.so"])

    base.cmd("./usr/bin/patchelf", ["--set-soname", "libicudata.so", "./../x86_64/libicudata.so"])
    base.cmd("./usr/bin/patchelf", ["--set-soname", "libicuuc.so", "./../x86_64/libicuuc.so"])
    base.cmd("./usr/bin/patchelf", ["--replace-needed", "libicudata.so." + icu_major, "libicudata.so", "./../x86_64/libicuuc.so"])

    base.cmd("./usr/bin/patchelf", ["--set-soname", "libicudata.so", "./../x86/libicudata.so"])
    base.cmd("./usr/bin/patchelf", ["--set-soname", "libicuuc.so", "./../x86/libicuuc.so"])
    base.cmd("./usr/bin/patchelf", ["--replace-needed", "libicudata.so." + icu_major, "libicudata.so", "./../x86/libicuuc.so"])

    base.delete_dir(current_dir + "/build/patchelf")
  
  if not icu_is_shared:
    base.create_dir(current_dir + "/build/arm64_v8a")
    base.copy_file(current_dir + "/build_tmp/arm64/lib/libicudata.a", current_dir + "/build/arm64_v8a/libicudata.a")
    base.copy_file(current_dir + "/build_tmp/arm64/lib/libicuuc.a", current_dir + "/build/arm64_v8a/libicuuc.a")
    base.copy_file(current_dir + "/icu/arm64/data/out/icudt58l.dat", current_dir + "/build/arm64_v8a/icudt58l.dat")

    base.create_dir(current_dir + "/build/armv7")
    base.copy_file(current_dir + "/build_tmp/arm/lib/libicudata.a", current_dir + "/build/armv7/libicudata.a")
    base.copy_file(current_dir + "/build_tmp/arm/lib/libicuuc.a", current_dir + "/build/armv7/libicuuc.a")
    base.copy_file(current_dir + "/icu/arm/data/out/icudt58l.dat", current_dir + "/build/armv7/icudt58l.dat")

    base.create_dir(current_dir + "/build/x86_64")
    base.copy_file(current_dir + "/build_tmp/x86_64/lib/libicudata.a", current_dir + "/build/x86_64/libicudata.a")
    base.copy_file(current_dir + "/build_tmp/x86_64/lib/libicuuc.a", current_dir + "/build/x86_64/libicuuc.a")
    base.copy_file(current_dir + "/icu/x86_64/data/out/icudt58l.dat", current_dir + "/build/x86_64/icudt58l.dat")

    base.create_dir(current_dir + "/build/x86")
    base.copy_file(current_dir + "/build_tmp/x86/lib/libicudata.a", current_dir + "/build/x86/libicudata.a")
    base.copy_file(current_dir + "/build_tmp/x86/lib/libicuuc.a", current_dir + "/build/x86/libicuuc.a")
    base.copy_file(current_dir + "/icu/x86/data/out/icudt58l.dat", current_dir + "/build/x86/icudt58l.dat")

  os.chdir(current_dir_old)
  return
