import sys
sys.path.append('../..')
import base
import os
import config

def make_x265(src_dir):
    if not base.is_dir("x265_git"):
        base.cmd("git", ["clone", "https://bitbucket.org/multicoreware/x265_git.git"])
    build_dir = src_dir + "/x265_git/build"
    os.chdir(build_dir)
    base.cmd("cmake", ["-G", "Visual Studio 16 2019", "-A", "x64", "../source"])
    base.cmd("cmake", ["--build", ".", "--config", "Release"])
    base.copy_file(build_dir + "/x265_config.h", src_dir + "/x265_git/source")
    os.chdir(src_dir)
    return

def make_de265(src_dir):
    if not base.is_dir("libde265"):
        base.cmd("git", ["clone", "https://github.com/strukturag/libde265.git"])
    os.chdir(src_dir + "/libde265")
    base.cmd("cmake", ["./", "-DCMAKE_BUILD_TYPE=Release"])
    base.cmd("cmake", ["--build", ".", "--config", "Release"])
    os.chdir(src_dir)
    return
        

def make_heif(src_dir):
    if not base.is_dir("libheif"):
        base.cmd("git", ["clone", "https://github.com/strukturag/libheif.git"])
    build_dir = src_dir + "/libheif/libheif/api/libheif"
    os.chdir(build_dir)
    base.cmd("cmake", ["../../../", "-DCMAKE_TYPE_BUILD=Release", 
             "-DLIBDE265_INCLUDE_DIR=" + src_dir + "/libde265",
             "-DLIBDE265_LIBRARY=" + src_dir + "/libde265/libde265/Release/de265.lib",
             "-DX265_INCLUDE_DIR=" + src_dir + "/x265_git/source",
             "-DX265_LIBRARY=" + src_dir + "/x265_git/build/Release/libx265.lib",
             "-DWITH_X265=yes", "--preset=release"])
    base.cmd("cmake", ["--build", ".", "--config", "Release"])
    base.copy_file(build_dir + "/libheif/heif_version.h", build_dir)
    os.chdir(src_dir)
    return

def make():
    print("[fetch & build]: heif")
    new_dir = base.get_script_dir() + "/../../core/Common/3dParty/heif"
    base.create_dir(new_dir)
    old_dir = os.getcwd()
    os.chdir(new_dir)

    if not base.is_dir("heif"):
        make_x265(new_dir)
        make_de265(new_dir)
        make_heif(new_dir)

    os.chdir(old_dir)
    return