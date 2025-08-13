import sys
sys.path.append('../..')
import base
import os
import config

# NOTE:
#  - requires CMake >= 3.21, < 4.0.0

def get_vs_version():
  vs_version = "14 2015"
  if config.option("vs-version") == "2019":
    vs_version = "16 2019"
  return vs_version

def make_x265(base_dir, build_type):
  # clones repo
  def fetch(version):
    branch_name = f"Release_{version}"
    base.cmd("git", ["clone", "--depth", "1", "--branch", branch_name, "https://bitbucket.org/multicoreware/x265_git.git"])
    return

  # builds library (Unix specific)
  def build_unix(platform, cmake_args):
    # check build dir
    build_dir = os.path.join(base_dir, "x265_git/build", platform, build_type.lower())
    if base.is_file(build_dir + "/libx265.a"):
      return
    base.create_dir(build_dir)
    # go to build dir
    old_dir = os.getcwd()
    os.chdir(build_dir)
    # build
    base.cmd("cmake", cmake_args)
    base.cmd("make", ["-j4"])
    # copy files
    base.copy_file(base_dir + "/x265_git/source/x265.h", build_dir)
    # restore old dir
    os.chdir(old_dir)
    return

  # builds library (Windows specific)
  def build_win(platform, cmake_args):
    # check build dir
    build_dir = os.path.join(base_dir, "x265_git/build", platform, build_type.lower())
    if base.is_file(os.path.join(build_dir, build_type, "x265-static.lib")):
      return
    base.create_dir(build_dir)
    # go to build dir
    old_dir = os.getcwd()
    os.chdir(build_dir)
    # build
    base.cmd("cmake", cmake_args)
    base.cmd("cmake", ["--build", ".", "--config", build_type])
    # copy files
    base.copy_file(base_dir + "/x265_git/source/x265.h", build_dir)
    # restore old dir
    os.chdir(old_dir)
    return

  # set version here
  x265_version = "4.1"
  if not base.is_dir("x265_git"):
    fetch(x265_version)
    # fix x265 version detection so it reads version from x265Version.txt instead of parsing it from .git
    base.replaceInFile(
      base_dir + "/x265_git/source/cmake/Version.cmake",
      "elseif(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/../x265Version.txt)",
      "endif()\n    if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/../x265Version.txt)"
    )

  cmake_dir = base_dir + "/x265_git/source"
  cmake_args = [
    cmake_dir,
    "-DCMAKE_BUILD_TYPE=" + build_type,
    "-DENABLE_CLI=OFF",                 # do not build standalone CLI app
    "-DENABLE_SHARED=OFF"               # do not build shared libs
  ]

  # WINDOWS
  if "windows" == base.host_platform():
    cmake_args += [
      "-G", f"Visual Studio {get_vs_version()}"
    ]
    # win_64
    if config.check_option("platform", "win_64"):
      cmake_args_ext = ["-A", "x64"]
      build_win("win_64", cmake_args + cmake_args_ext)
    # win_32
    if config.check_option("platform", "win_32"):
      cmake_args_ext = ["-A", "Win32"]
      build_win("win_32", cmake_args + cmake_args_ext)

  # LINUX
  if "linux" == base.host_platform():
    cmake_args += [
      "-G", "Unix Makefiles",
      "-DCMAKE_POSITION_INDEPENDENT_CODE=ON"
    ]
    # linux_64
    if config.check_option("platform", "linux_64"):
      build_unix("linux_64", cmake_args)
    # linux_arm64
    if config.check_option("platform", "linux_arm64"):
      build_unix("linux_arm64", cmake_args)

  # MAC
  if "mac" == base.host_platform():
    cmake_args += [
      "-G", "Unix Makefiles",
      "-DCMAKE_POSITION_INDEPENDENT_CODE=ON",
      "-DENABLE_ASSEMBLY=OFF"                   # disable assembly optimizations
    ]
    # mac_64
    if config.check_option("platform", "mac_64"):
      cmake_args_ext = ["-DCMAKE_OSX_DEPLOYMENT_TARGET=10.11"]
      if base.is_os_arm():
        cmake_args_ext += [
          "-DCMAKE_OSX_ARCHITECTURES=x86_64"
        ]
      build_unix("mac_64", cmake_args + cmake_args_ext)
    # mac_arm64
    if config.check_option("platform", "mac_arm64"):
      cmake_args_ext = ["-DCMAKE_OSX_DEPLOYMENT_TARGET=11.0"]
      build_unix("mac_arm64", cmake_args + cmake_args_ext)

  os.chdir(base_dir)
  return

def make_de265(base_dir, build_type):
  # clones repo
  def fetch(version):
    tag_name = f"v{version}"
    base.cmd("git", ["clone", "--depth", "1", "--branch", tag_name, "https://github.com/strukturag/libde265.git"])
    return

  # builds library (Unix specific)
  def build_unix(platform, cmake_args):
    # prepare build dir
    build_dir = os.path.join(base_dir, "libde265/build", platform, build_type.lower())
    if base.is_file(build_dir + "/libde265/libde265.a"):
      return
    base.create_dir(build_dir)
    # go to build dir
    old_dir = os.getcwd()
    os.chdir(build_dir)
    # build
    base.cmd("cmake", cmake_args)
    base.cmd("make", ["-j4"])
    # copy files
    base.copy_file(base_dir + "/libde265/libde265/de265.h", build_dir + "/libde265")
    # restore old dir
    os.chdir(old_dir)
    return

  # builds library (Windows specific)
  def build_win(platform, cmake_args):
    # check build dir
    build_dir = os.path.join(base_dir, "libde265/build", platform, build_type.lower())
    if base.is_file(os.path.join(build_dir, "libde265", build_type, "libde265.lib")):
      return
    base.create_dir(build_dir)
    # go to build dir
    old_dir = os.getcwd()
    os.chdir(build_dir)
    # build
    base.cmd("cmake", cmake_args)
    base.cmd("cmake", ["--build", ".", "--config", build_type])
    # copy files
    base.copy_file(base_dir + "/libde265/libde265/de265.h", build_dir + "/libde265")
    # restore old dir
    os.chdir(old_dir)
    return

  # set version here
  de265_version = "1.0.16"
  if not base.is_dir("libde265"):
    fetch(de265_version)

  cmake_dir = base_dir + "/libde265"
  cmake_args = [
    cmake_dir,
    "-DCMAKE_BUILD_TYPE=" + build_type,
    "-DBUILD_SHARED_LIBS=OFF",            # do not build shared libs
    "-DENABLE_SDL=OFF",                   # disable SDL
    "-DENABLE_DECODER=OFF",               # do not build decoder CLI executable 
    "-DENABLE_ENCODER=OFF",               # do not build encoder CLI executable
  ]

  # WINDOWS
  if "windows" == base.host_platform():
    cmake_args += [
      "-G", f"Visual Studio {get_vs_version()}"
    ]
    # win_64
    if config.check_option("platform", "win_64"):
      cmake_args_ext = ["-A", "x64"]
      build_win("win_64", cmake_args + cmake_args_ext)
    # win_32
    if config.check_option("platform", "win_32"):
      cmake_args_ext = ["-A", "Win32"]
      build_win("win_32", cmake_args + cmake_args_ext)

  # LINUX
  if "linux" == base.host_platform():
    cmake_args += [
      "-G", "Unix Makefiles",
      "-DCMAKE_POSITION_INDEPENDENT_CODE=ON"
    ]
    # linux_64
    if config.check_option("platform", "linux_64"):
      build_unix("linux_64", cmake_args)
    # linux_arm64
    if config.check_option("platform", "linux_arm64"):
      build_unix("linux_arm64", cmake_args)

  # MAC
  if "mac" == base.host_platform():
    cmake_args += [
      "-G", "Unix Makefiles",
      "-DCMAKE_POSITION_INDEPENDENT_CODE=ON"
    ]
    # mac_64
    if config.check_option("platform", "mac_64"):
      cmake_args_ext = ["-DCMAKE_OSX_DEPLOYMENT_TARGET=10.11"]
      if base.is_os_arm():
        cmake_args_ext += [
          "-DCMAKE_OSX_ARCHITECTURES=x86_64"
        ]
      build_unix("mac_64", cmake_args + cmake_args_ext)
    # mac_arm64
    if config.check_option("platform", "mac_arm64"):
      cmake_args_ext = ["-DCMAKE_OSX_DEPLOYMENT_TARGET=11.0"]
      build_unix("mac_arm64", cmake_args + cmake_args_ext)

  os.chdir(base_dir)
  return

def make_heif(base_dir, build_type):
  # clones repo
  def fetch(version):
    tag_name = f"v{version}"
    base.cmd("git", ["clone", "--depth", "1", "--branch", tag_name, "https://github.com/strukturag/libheif.git"])
    return

  # builds library (Unix specific)
  def build_unix(platform, cmake_args):
    # prepare build dir
    build_dir = os.path.join(base_dir, "libheif/build", platform, build_type.lower())
    if base.is_file(build_dir + "/libheif/libheif.a"):
      return
    base.create_dir(build_dir)
    # go to build dir
    old_dir = os.getcwd()
    os.chdir(build_dir)
    # add paths to dependent libraries and includes to cmake args
    de265_build_dir = os.path.join(base_dir, "libde265/build", platform, build_type.lower())
    x265_build_dir = os.path.join(base_dir, "x265_git/build", platform, build_type.lower())
    cmake_args_ext = [
      f"-DLIBDE265_INCLUDE_DIR={de265_build_dir}",
      f"-DLIBDE265_LIBRARY={de265_build_dir}/libde265/libde265.a",
      f"-DX265_INCLUDE_DIR={x265_build_dir}",
      f"-DX265_LIBRARY={x265_build_dir}/libx265.a"
    ]
    # build
    base.cmd("cmake", cmake_args + cmake_args_ext)
    base.cmd("make", ["-j4"])
    # restore old dir
    os.chdir(old_dir)
    return

  # builds library (Windows specific)
  def build_win(platform, cmake_args):
    # check build dir
    build_dir = os.path.join(base_dir, "libheif/build", platform, build_type.lower())
    if base.is_file(os.path.join(build_dir, "libheif", build_type, "heif.lib")):
      return
    base.create_dir(build_dir)
    # go to build dir
    old_dir = os.getcwd()
    os.chdir(build_dir)
    # add paths to dependent libraries and includes to cmake args
    de265_build_dir = os.path.join(base_dir, "libde265/build", platform, build_type.lower())
    x265_build_dir = os.path.join(base_dir, "x265_git/build", platform, build_type.lower())
    cmake_args_ext = [
      f"-DLIBDE265_INCLUDE_DIR={de265_build_dir}",
      f"-DLIBDE265_LIBRARY={de265_build_dir}/libde265/{build_type}/libde265.lib",
      f"-DX265_INCLUDE_DIR={x265_build_dir}",
      f"-DX265_LIBRARY={x265_build_dir}/{build_type}/x265-static.lib"
    ]
    # build
    base.cmd("cmake", cmake_args + cmake_args_ext)
    base.cmd("cmake", ["--build", ".", "--config", build_type])
    # restore old dir
    os.chdir(old_dir)
    return

  # set version here
  # NOTE: 1.18.2 - the latest version of libheif supporting C++11 build (as for now)
  heif_version = "1.18.2"
  if not base.is_dir("libheif"):
    fetch(heif_version)
    # do not build heifio module
    base.replaceInFile(
      base_dir + "/libheif/CMakeLists.txt",
      "add_subdirectory(heifio)",
      "# add_subdirectory(heifio)"
    )

  cmake_dir = base_dir + "/libheif"
  cmake_args = [
    cmake_dir,
    "--preset=release-noplugins",                     # preset to disable plugins system
    "-DCMAKE_BUILD_TYPE=" + build_type,
    "-DBUILD_SHARED_LIBS=OFF",                        # do not build shared libs
    "-DWITH_LIBSHARPYUV=OFF",                         # do not build libsharpyuv (for RGB <--> YUV color space conversions)
    "-DWITH_AOM_DECODER=OFF",                         # do not build AOM V1 decoder (for AVIF image format)
    "-DWITH_AOM_ENCODER=OFF",                         # do not build AOM V1 encoder (for AVIF image format)
    "-DWITH_EXAMPLES=OFF",                            # do not build examples
    "-DWITH_EXAMPLE_HEIF_VIEW=OFF",                   # do not build heif-view CLI tool
    "-DWITH_X265=ON",                                 # enable x265 codec
    "-DWITH_LIBDE265=ON",                             # enable de265 codec
    "-DCMAKE_CXX_FLAGS=-DLIBDE265_STATIC_BUILD",      # add define to properly compile with de265 static library
    "-DCMAKE_C_FLAGS=-DLIBDE265_STATIC_BUILD",        # ^
  ]

  # WINDOWS
  if "windows" == base.host_platform():
    cmake_args += [
      "-G", f"Visual Studio {get_vs_version()}"
    ]
    # win_64
    if config.check_option("platform", "win_64"):
      cmake_args_ext = ["-A", "x64"]
      build_win("win_64", cmake_args + cmake_args_ext)
    # win_32
    if config.check_option("platform", "win_32"):
      cmake_args_ext = ["-A", "Win32"]
      build_win("win_32", cmake_args + cmake_args_ext)

  # LINUX
  if "linux" == base.host_platform():
    cmake_args += [
      "-G", "Unix Makefiles",
      "-DCMAKE_POSITION_INDEPENDENT_CODE=ON",
      "-DWITH_GDK_PIXBUF=OFF",                  # do not build gdk-pixbuf plugin
      "-DWITH_GNOME=OFF",                       # do not build gnome plugin
    ]
    # linux_64
    if config.check_option("platform", "linux_64"):
      build_unix("linux_64", cmake_args)
    # linux_arm64
    if config.check_option("platform", "linux_arm64"):
      build_unix("linux_arm64", cmake_args)

  # MAC
  if "mac" == base.host_platform():
    cmake_args += [
      "-G", "Unix Makefiles",
      "-DCMAKE_POSITION_INDEPENDENT_CODE=ON",
      "-DWITH_GDK_PIXBUF=OFF",                  # do not build gdk-pixbuf plugin
    ]
    # mac_64
    if config.check_option("platform", "mac_64"):
      cmake_args_ext = ["-DCMAKE_OSX_DEPLOYMENT_TARGET=10.11"]
      if base.is_os_arm():
        cmake_args_ext += [
          "-DCMAKE_OSX_ARCHITECTURES=x86_64"
        ]
      build_unix("mac_64", cmake_args + cmake_args_ext)
    # mac_arm64
    if config.check_option("platform", "mac_arm64"):
      cmake_args_ext = ["-DCMAKE_OSX_DEPLOYMENT_TARGET=11.0"]
      build_unix("mac_arm64", cmake_args + cmake_args_ext)

  os.chdir(base_dir)
  return

def make():
  print("[fetch & build]: heif")

  base_dir = base.get_script_dir() + "/../../core/Common/3dParty/heif"
  old_dir = os.getcwd()
  os.chdir(base_dir)

  # TODO: do we really need debug builds for libheif ???
  build_type = "Release"
  if (-1 != config.option("config").lower().find("debug")):
    build_type = "Debug"

  # build encoder libraries
  make_x265(base_dir, build_type)
  # build decoder libraries
  make_de265(base_dir, build_type)

  # build libheif
  make_heif(base_dir, build_type)

  os.chdir(old_dir)
  return

if __name__ == '__main__':
  make()
