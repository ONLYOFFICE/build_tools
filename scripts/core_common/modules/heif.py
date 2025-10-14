import sys
sys.path.append('../..')
import base
import os
import config

# NOTE:
#  - requires CMake >= 3.21, < 4.0.0

# libs versions
X265_VERSION = "4.1"
DE265_VERSION = "1.0.16"
# 1.18.2 - the latest version of libheif supporting C++11 builds (as for now)
HEIF_VERSION = "1.18.2"

# ios cmake toolchain
IOS_CMAKE_VERSION = "4.5.0"
IOS_CMAKE_TOOLCHAIN_FILE = base.get_script_dir() + "/../../core/Common/3dParty/heif/ios-cmake/ios.toolchain.cmake"

# android cmake toolchain
ANDROID_CMAKE_TOOLCHAIN_FILE = base.get_env("ANDROID_NDK_ROOT") + "/build/cmake/android.toolchain.cmake"

# linux arm64 cmake toolchain
LINUX_ARM64_CMAKE_TOOLCHAIN_FILE = base.get_script_dir() + "/../tools/linux/arm/cross_arm64/linux-arm64.toolchain.cmake"

LINUX_CUSTOM_SYSROOT_TOOLCHAIN_FILE = base.get_script_dir() + "/../tools/linux/sysroot/custom-sysroot.toolchain.cmake"

OLD_ENV = dict()

# get custom sysroot vars as str
def setup_custom_sysroot_env() -> str:
  env_vars = []
  env_vars += ['LD_LIBRARY_PATH=\"' + config.get_custom_sysroot_lib() + "\""]
  env_vars += ['PATH=\"' + config.option("sysroot") + "/usr/bin:" + base.get_env("PATH") + "\""]
  env_vars += ['CC=\"' + config.get_custom_sysroot_bin() + "/gcc\""]
  env_vars += ['CXX=\"' + config.get_custom_sysroot_bin() + "/g++\""]
  env_vars += ['AR=\"' + config.get_custom_sysroot_bin() + "/ar\""]
  env_vars += ['RABLIB=\"' + config.get_custom_sysroot_bin() + "/ranlib\""]
  env_vars += ['CFLAGS=\"' + "--sysroot=" + config.option("sysroot") + "\""]
  env_vars += ['CXXFLAGS=\"' + "--sysroot=" + config.option("sysroot") + "\""]
  env_vars += ['LDFLAGS=\"' + "--sysroot=" + config.option("sysroot") + "\""]

  env_str = ""
  for env_var in env_vars:
    env_str += env_var + " "

  return env_str

def get_vs_version():
  vs_version = "14 2015"
  if config.option("vs-version") == "2019":
    vs_version = "16 2019"
  return vs_version

def get_xcode_sdk(platform):
  xcode_sdk = "iphoneos"
  if "simulator" in platform:
    xcode_sdk = "iphonesimulator"
  return xcode_sdk

def fetch_repo(repo_url, branch_or_tag):
  base.cmd("git", ["clone", "--depth", "1", "--branch", branch_or_tag, repo_url])
  return

def get_build_dir(base_dir, repo_dir, platform, build_type):
  return os.path.join(base_dir, repo_dir, "build", platform, build_type.lower())

# general build function that builds for ONE platform (supposing we are located in the build directory)
def build_with_cmake(platform, cmake_args, build_type):
  # extend cmake arguments
  cmake_args_ext = []
  # WINDOWS
  if "win" in platform:
    cmake_args_ext = [
      "-G", f"Visual Studio {get_vs_version()}"
    ]
    if platform == "win_64" or platform == "win_64_xp":
      cmake_args_ext += ["-A", "x64"]
    elif platform == "win_32" or platform == "win_32_xp":
      cmake_args_ext += ["-A", "Win32"]
    elif platform == "win_arm64":
      cmake_args_ext += ["-A", "ARM64"]
  # LINUX, MAC
  elif "linux" in platform or "mac" in platform:
    cmake_args_ext = [
      "-G", "Unix Makefiles",
      "-DCMAKE_POSITION_INDEPENDENT_CODE=ON"  # on UNIX we need to compile with fPIC
    ]
    if platform == "mac_64":
      cmake_args_ext += ["-DCMAKE_OSX_DEPLOYMENT_TARGET=10.11", "-DCMAKE_OSX_ARCHITECTURES=x86_64"]
    elif platform == "mac_arm64":
      cmake_args_ext += ["-DCMAKE_OSX_DEPLOYMENT_TARGET=11.0", "-DCMAKE_OSX_ARCHITECTURES=arm64"]
    elif platform == "linux_arm64":
      cmake_args += ["-DCMAKE_TOOLCHAIN_FILE=" + LINUX_ARM64_CMAKE_TOOLCHAIN_FILE]
    elif config.option("sysroot") != "":
      cmake_args += ["-DCMAKE_TOOLCHAIN_FILE=" + LINUX_CUSTOM_SYSROOT_TOOLCHAIN_FILE] # force use custom CXXFLAGS with Release/Debug build
  # IOS
  elif "ios" in platform:
    cmake_args_ext = [
      "-G", "Xcode",
      "-DCMAKE_TOOLCHAIN_FILE=" + IOS_CMAKE_TOOLCHAIN_FILE,
      "-DDEPLOYMENT_TARGET=11.0"
    ]
    if platform == "ios":
      cmake_args_ext += ["-DPLATFORM=OS64"]
    elif platform == "ios_simulator":
      cmake_args_ext += ["-DPLATFORM=SIMULATOR64COMBINED"]
  # ANDROID
  elif "android" in platform:
    cmake_args_ext = [
      "-G", "Unix Makefiles",
      "-DCMAKE_TOOLCHAIN_FILE=" + ANDROID_CMAKE_TOOLCHAIN_FILE,
      "-DCMAKE_POSITION_INDEPENDENT_CODE=ON"
    ]
    def get_cmake_args_android(arch, api_level):
      return [
        "-DANDROID_ABI=" + arch,
        "-DANDROID_NATIVE_API_LEVEL=" + api_level
      ]
    if platform == "android_arm64_v8a":
      cmake_args_ext += get_cmake_args_android("arm64-v8a", "21")
    elif platform == "android_armv7":
      cmake_args_ext += get_cmake_args_android("armeabi-v7a", "16")
    elif platform == "android_x86":
      cmake_args_ext += get_cmake_args_android("x86", "16")
    elif platform == "android_x86_64":
      cmake_args_ext += get_cmake_args_android("x86_64", "21")

  # env setup for custom sysroot
  env_str = setup_custom_sysroot_env() if config.option("sysroot") != "" else ""

  # run cmake
  base.cmd(env_str + "cmake", cmake_args + cmake_args_ext)

  # build
  if "Unix Makefiles" in cmake_args_ext:
    base.cmd(env_str + "make", ["-j4"])
  else:
    base.cmd("cmake", ["--build", ".", "--config", build_type])
  return

# general make function that calls `build_func` callback for configured platform(s) with specified cmake arguments
def make_common(build_func, cmake_args):
  # WINDOWS
  if "windows" == base.host_platform():
    # win_64
    if config.check_option("platform", "win_64") or config.check_option("platform", "win_64_xp"):
      build_func("win_64", cmake_args)
    # win_32
    if config.check_option("platform", "win_32") or config.check_option("platform", "win_32_xp"):
      build_func("win_32", cmake_args)
    # win_arm64
    if config.check_option("platform", "win_arm64"):
      build_func("win_arm64", cmake_args)

  # LINUX
  elif "linux" == base.host_platform():
    # linux_64
    if config.check_option("platform", "linux_64"):
      build_func("linux_64", cmake_args)
    # linux_arm64
    if config.check_option("platform", "linux_arm64"):
      build_func("linux_arm64", cmake_args)

  # MAC
  elif "mac" == base.host_platform():
    # mac_64
    if config.check_option("platform", "mac_64"):
      build_func("mac_64", cmake_args)
    # mac_arm64
    if config.check_option("platform", "mac_arm64"):
      build_func("mac_arm64", cmake_args)

    # IOS
    if -1 != config.option("platform").find("ios"):
      # ios (arm64)
      build_func("ios", cmake_args)
      # ios simulator (x86_64 and arm64 FAT lib)
      build_func("ios_simulator", cmake_args)

  # ANDROID
  if -1 != config.option("platform").find("android"):
    # android_arm64_v8a
    if config.check_option("platform", "android_arm64_v8a"):
      build_func("android_arm64_v8a", cmake_args)
    # android_armv7
    if config.check_option("platform", "android_armv7"):
      build_func("android_armv7", cmake_args)
    # android_x86
    if config.check_option("platform", "android_x86"):
      build_func("android_x86", cmake_args)
    # android_x86_64
    if config.check_option("platform", "android_x86_64"):
      build_func("android_x86_64", cmake_args)

  return

def make_x265(base_dir, build_type):
  # fetch lib repo
  if not base.is_dir("x265_git"):
    fetch_repo("https://bitbucket.org/multicoreware/x265_git.git", f"Release_{X265_VERSION}")
    # fix x265 version detection so it reads version from x265Version.txt instead of parsing it from .git
    base.replaceInFile(
      base_dir + "/x265_git/source/cmake/Version.cmake",
      "elseif(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/../x265Version.txt)",
      "endif()\n    if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/../x265Version.txt)"
    )

  # prepare cmake args
  cmake_dir = base_dir + "/x265_git/source"
  cmake_args = [
    cmake_dir,
    "-DCMAKE_BUILD_TYPE=" + build_type,
    "-DENABLE_CLI=OFF",                 # do not build standalone CLI app
    "-DENABLE_SHARED=OFF",              # do not build shared libs
    "-DENABLE_ASSEMBLY=OFF",            # disable assembly optimizations
    "-DENABLE_LIBNUMA=OFF",             # disable libnuma usage (affects Linux only)
  ]

  # lib build function
  def build_x265(platform, cmake_args):
    # check if target lib has already been built
    build_dir = get_build_dir(base_dir, "x265_git", platform, build_type)
    if platform.find("win") != -1:
      target_lib = os.path.join(build_dir, build_type, "x265-static.lib")
    else:
      target_lib = os.path.join(build_dir, "libx265.a")
    if base.is_file(target_lib):
      return
    # go to the build directory
    base.create_dir(build_dir)
    os.chdir(build_dir)
    # run build
    build_with_cmake(platform, cmake_args, build_type)
    # for iOS there is no target for building libx265.a, so we need to form it ourselves from libcommon.a and libencoder.a
    if platform.find("ios") != -1:
      xcode_sdk = get_xcode_sdk(platform)
      base.cmd("libtool", [
        "-static",
        "-o", "libx265.a",
        f"build/common.build/{build_type}-{xcode_sdk}/libcommon.a",
        f"build/encoder.build/{build_type}-{xcode_sdk}/libencoder.a"
      ])
    # copy header
    base.copy_file(base_dir + "/x265_git/source/x265.h", build_dir)
    # reset directory
    os.chdir(base_dir)
    return

  make_common(build_x265, cmake_args)
  return

def make_de265(base_dir, build_type):
  # fetch lib repo
  if not base.is_dir("libde265"):
    fetch_repo("https://github.com/strukturag/libde265.git", f"v{DE265_VERSION}")

  # prepare cmake args
  cmake_dir = base_dir + "/libde265"
  cmake_args = [
    cmake_dir,
    "-DCMAKE_BUILD_TYPE=" + build_type,
    "-DBUILD_SHARED_LIBS=OFF",            # do not build shared libs
    "-DENABLE_SDL=OFF",                   # disable SDL
    "-DENABLE_DECODER=OFF",               # do not build decoder CLI executable
    "-DENABLE_ENCODER=OFF",               # do not build encoder CLI executable
  ]

  # lib build function
  def build_de265(platform, cmake_args):
    # check if target lib has already been built
    build_dir = get_build_dir(base_dir, "libde265", platform, build_type)
    if platform.find("win") != -1:
      target_lib = os.path.join(build_dir, "libde265", build_type, "libde265.lib")
    else:
      target_lib = os.path.join(build_dir, "libde265/libde265.a")
    if base.is_file(target_lib):
      return
    # go to the build directory
    base.create_dir(build_dir)
    os.chdir(build_dir)
    # run build
    build_with_cmake(platform, cmake_args, build_type)
    # for ios copy target library from the default build path
    if platform.find("ios") != -1:
      xcode_sdk = get_xcode_sdk(platform)
      base.copy_file(f"libde265/{build_type}-{xcode_sdk}/libde265.a", "libde265")
    # copy header
    base.copy_file(base_dir + "/libde265/libde265/de265.h", "libde265")
    # reset directory
    os.chdir(base_dir)
    return

  make_common(build_de265, cmake_args)
  return

def make_heif(base_dir, build_type):
  # fetch lib repo
  if not base.is_dir("libheif"):
    fetch_repo("https://github.com/strukturag/libheif.git", f"v{HEIF_VERSION}")
    # do not build heifio module
    base.replaceInFile(
      base_dir + "/libheif/CMakeLists.txt",
      "add_subdirectory(heifio)",
      "# add_subdirectory(heifio)"
    )
    base.replaceInFile(
      base_dir + "/libheif/CMakeLists.txt",
      "if (DOXYGEN_FOUND)",
      "if (FALSE)"
    )

  # prepare cmake args
  cmake_dir = base_dir + "/libheif"
  cmake_args = [
    cmake_dir,
    "--preset=release-noplugins",                     # preset to disable plugins system
    "-DCMAKE_BUILD_TYPE=" + build_type,
    "-DBUILD_SHARED_LIBS=OFF",                        # do not build shared libs
    "-DWITH_LIBSHARPYUV=OFF",                         # do not build libsharpyuv (for RGB <--> YUV color space conversions)
    "-DWITH_AOM_DECODER=OFF",                         # do not build AOM V1 decoder (for AVIF image format)
    "-DWITH_AOM_ENCODER=OFF",                         # do not build AOM V1 encoder (for AVIF image format)
    "-DWITH_GDK_PIXBUF=OFF",                          # do not build gdk-pixbuf plugin (UNIX only)
    "-DWITH_GNOME=OFF",                               # do not build gnome plugin (Linux only)
    "-DWITH_EXAMPLES=OFF",                            # do not build examples
    "-DWITH_EXAMPLE_HEIF_VIEW=OFF",                   # do not build heif-view CLI tool
    "-DWITH_X265=ON",                                 # enable x265 codec
    "-DWITH_LIBDE265=ON",                             # enable de265 codec
    "-DCMAKE_CXX_FLAGS=-DLIBDE265_STATIC_BUILD",      # add macro definition to properly compile with de265 static library
    "-DCMAKE_C_FLAGS=-DLIBDE265_STATIC_BUILD",        # same ^
  ]

  # lib build function
  def build_heif(platform, cmake_args):
    # check if target lib has already been built
    build_dir = get_build_dir(base_dir, "libheif", platform, build_type)
    if platform.find("win") != -1:
      target_lib = os.path.join(build_dir, "libheif", build_type, "heif.lib")
    else:
      target_lib = os.path.join(build_dir, "libheif/libheif.a")
    if base.is_file(target_lib):
      return
    # go to the build directory
    base.create_dir(build_dir)
    os.chdir(build_dir)
    # add paths to dependent libraries and includes to cmake args
    de265_build_dir = get_build_dir(base_dir, "libde265", platform, build_type)
    x265_build_dir = get_build_dir(base_dir, "x265_git", platform, build_type)
    cmake_args_ext = [
      f"-DLIBDE265_INCLUDE_DIR={de265_build_dir}",
      f"-DX265_INCLUDE_DIR={x265_build_dir}"
    ]
    if platform.find("win") != -1:
      cmake_args_ext += [
        f"-DLIBDE265_LIBRARY={de265_build_dir}/libde265/{build_type}/libde265.lib",
        f"-DX265_LIBRARY={x265_build_dir}/{build_type}/x265-static.lib"
      ]
    else:
      cmake_args_ext += [
        f"-DLIBDE265_LIBRARY={de265_build_dir}/libde265/libde265.a",
        f"-DX265_LIBRARY={x265_build_dir}/libx265.a"
      ]
    # run build
    build_with_cmake(platform, cmake_args + cmake_args_ext, build_type)
    # for ios copy target library from the default build path
    if platform.find("ios") != -1:
      xcode_sdk = get_xcode_sdk(platform)
      base.copy_file(f"libheif/{build_type}-{xcode_sdk}/libheif.a", "libheif")
    # reset directory
    os.chdir(base_dir)
    return

  make_common(build_heif, cmake_args)
  return

def clear_module():
  if base.is_dir("libde265"):
    base.delete_dir_with_access_error("libde265")
  if base.is_dir("x265_git"):
    base.delete_dir_with_access_error("x265_git")
  if base.is_dir("libheif"):
    base.delete_dir_with_access_error("libheif")
  return

def make():
  print("[fetch & build]: heif")

  base_dir = base.get_script_dir() + "/../../core/Common/3dParty/heif"
  old_dir = os.getcwd()
  os.chdir(base_dir)

  base.check_module_version("2", clear_module)

  build_type = "Release"
  if (-1 != config.option("config").lower().find("debug")):
    build_type = "Debug"

  # fetch custom cmake toolchain for ios
  if -1 != config.option("platform").find("ios"):
    if not base.is_file(IOS_CMAKE_TOOLCHAIN_FILE):
      fetch_repo("https://github.com/leetal/ios-cmake.git", IOS_CMAKE_VERSION)

  # build encoder library
  make_x265(base_dir, build_type)
  # build decoder library
  make_de265(base_dir, build_type)

  # build libheif
  make_heif(base_dir, build_type)

  os.chdir(old_dir)
  return

if __name__ == '__main__':
  make()
