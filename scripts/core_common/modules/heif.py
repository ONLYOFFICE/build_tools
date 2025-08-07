import sys
sys.path.append('../..')
import base
import os
import config

def make_x265(base_dir, build_type):
  # clones repo
  def fetch(version_major, version_minor):
    branch_name = f"Release_{version_major}.{version_minor}"
    base.cmd("git", ["clone", "--depth", "1", "--branch", branch_name, "https://bitbucket.org/multicoreware/x265_git.git"])

  # gets build directory
  def get_build_dir(platform):
    return os.path.join(base_dir, "build", platform, build_type, "x265")

  # set versions here
  x265_major = "4"
  x265_minor = "1"
  if not base.is_dir("x265_git"):
    fetch(x265_major, x265_minor)

  cmake_dir = base_dir + "/x265_git/build"
  cmake_args = [
    "../../source",
    "-DCMAKE_BUILD_TYPE=" + build_type,
    "-DENABLE_CLI=OFF",                 # do not build standalone CLI app
    "-DENABLE_SHARED=OFF"               # do not build shared libs
  ]

  # if "windows" == base.host_platform():
  #   # TODO: separate win32 and win64 builds
  #   cmake_args.extend(["-G", "Visual Studio 16 2019", "-A", "x64"])
  #   base.cmd("cmake", cmake_args)
  #   base.cmd("cmake", ["--build", ".", "--config", build_type])
  #   base.copy_files(cmake_dir + "/" + build_type + "/*.lib", lib_dir)

  # if "linux" == base.host_platform():
  #   cmake_args.extend(["-G", "Unix Makefiles", "-DCMAKE_POSITION_INDEPENDENT_CODE=ON"])
  #   base.cmd("cmake", cmake_args)
  #   base.cmd("make", ["-j4"])
  #   base.copy_files(cmake_dir + "/*.a", lib_dir)

  if "mac" == base.host_platform():
    # change directory
    cmake_dir += "/linux"
    os.chdir(cmake_dir)
    # extend cmake args
    cmake_args += ["-G", "Unix Makefiles"]

    # mac_64
    if config.check_option("platform", "mac_64") and not base.is_dir(get_build_dir("mac_64")):
      build_dir = get_build_dir("mac_64")
      base.create_dir(build_dir)
      if base.is_os_arm():
        # disable assembly optimizations for cross-arch build
        cmake_args += ["-DENABLE_ASSEMBLY=OFF"]
      base.cmd("cmake", cmake_args)
      base.cmd("make", ["-j4"])
      base.copy_files("*.a", build_dir)
      base.create_dir(build_dir + "/include")
      base.copy_file(base_dir + "/x265_git/source/x265.h", build_dir + "/include")

    # mac_arm64
    if config.check_option("platform", "mac_arm64") and not base.is_dir(get_build_dir("mac_arm64")):
      build_dir = get_build_dir("mac_arm64")
      base.create_dir(build_dir)
      base.cmd("cmake", cmake_args)
      base.cmd("make", ["-j4"])
      base.copy_files("*.a", build_dir)
      base.create_dir(build_dir + "/include")
      base.copy_file(base_dir + "/x265_git/source/x265.h", build_dir + "/include")

  os.chdir(base_dir)
  return

def make_de265(src_dir, lib_dir, build_type):
  if not base.is_dir("libde265"):
    base.cmd("git", ["clone", "https://github.com/strukturag/libde265.git"])
  cmake_dir = src_dir + "/libde265"
  os.chdir(cmake_dir)

  cmake_args = [
    "./", "-DCMAKE_BUILD_TYPE=" + build_type, "-DBUILD_SHARED_LIBS=OFF",
    "-DENABLE_SHARED=OFF", "-DENABLE_DECODER=ON", "-DENABLE_ENCODER=ON"
  ]

  if "windows" == base.host_platform():
    base.cmd("cmake", cmake_args)
    base.cmd("cmake", ["--build", ".", "--config", build_type])
    base.copy_files(cmake_dir + "/libde265/" + build_type + "/*.lib", lib_dir)

  if "linux" == base.host_platform():
    cmake_args.extend(["-DCMAKE_POSITION_INDEPENDENT_CODE=ON"])
    base.cmd("cmake", cmake_args)
    base.cmd("make", ["-j$(nproc)"])
    base.copy_files(cmake_dir + "/libde265/*.a", lib_dir)

  os.chdir(src_dir)

  return


def make_heif(src_dir, lib_dir, build_type):
  if not base.is_dir("libheif"):
    base.cmd("git", ["clone", "https://github.com/strukturag/libheif.git"])

  src_str = "option(BUILD_SHARED_LIBS \"Build shared libraries\" ON)"
  rep_str = "option(BUILD_SHARED_LIBS \"Build shared libraries\" ON)\n\n" \
        "if(NOT BUILD_SHARED_LIBS)\n" \
         "\tadd_definitions(-DLIBDE265_STATIC_BUILD)\n" \
         "endif()"
  base.replaceInFile(src_dir + "/libheif/CmakeLists.txt", src_str, rep_str)

  cmake_dir = src_dir + "/libheif/libheif/api/libheif"
  os.chdir(cmake_dir)

  cmake_args = [
    "../../../", "-DCMAKE_BUILD_TYPE=" + build_type, "--preset=release-noplugins",
    "-DENABLE_PLUGIN_LOADING=OFF", "-DWITH_X265=ON", "-DWITH_LIBDE265=ON",
    "-DBUILD_SHARED_LIBS=OFF"
  ]

  if "windows" == base.host_platform():
    cmake_args.extend(["-DLIBDE265_INCLUDE_DIR=" + src_dir + "/libde265",
               "-DLIBDE265_LIBRARY=" + lib_dir + "/libde265.lib",
               "-DX265_INCLUDE_DIR=" + src_dir + "/x265_git/source",
               "-DX265_LIBRARY=" + lib_dir + "/x265-static.lib",])
    base.cmd("cmake", cmake_args)
    base.cmd("cmake", ["--build", ".", "--config", build_type])
    base.copy_files(cmake_dir + "/libheif/" + build_type + "/*.lib", lib_dir)

  if "linux" == base.host_platform():
    cmake_args.extend(["-DCMAKE_POSITION_INDEPENDENT_CODE=ON",
               "-DWITH_GDK_PIXBUF=OFF", "-DWITH_GNOME=OFF",
               "-DLIBDE265_INCLUDE_DIR=" + src_dir + "/libde265",
               "-DLIBDE265_LIBRARY=" + lib_dir + "/libde265.a",
               "-DX265_INCLUDE_DIR=" + src_dir + "/x265_git/source",
               "-DX265_LIBRARY=" + lib_dir + "/libx265.a"])
    base.cmd("cmake", cmake_args)
    base.cmd("make", ["-j$(nproc)"])
    base.copy_files(cmake_dir + "/libheif/*.a", lib_dir)

  base.copy_files(cmake_dir + "/libheif/*.h", cmake_dir)
  os.chdir(src_dir)

  return

def make():
  print("[fetch & build]: heif")

  base_dir = base.get_script_dir() + "/../../core/Common/3dParty/heif"
  old_dir = os.getcwd()
  os.chdir(base_dir)

  # TODO: do we really need debug libheif libraries ???
  build_type = "Release"
  if (-1 != config.option("config").lower().find("debug")):
    build_type = "Debug"

  # build encoder libraries
  make_x265(base_dir, build_type)
  # build decoder libraries
  # make_de265(base_dir, build_type)

  # build libheif
  # make_heif(base_dir, build_type)

  os.chdir(old_dir)
  return

if __name__ == '__main__':
  make()
