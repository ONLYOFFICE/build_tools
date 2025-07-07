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
    if "windows" == base.host_platform():
        base.cmd("cmake", ["-G", "Visual Studio 16 2019", "-A", "x64", "../source"])
        base.cmd("cmake", ["--build", ".", "--config", "Release"])
    if "linux" == base.host_platform():
        base.cmd("cmake", ["-G", "Unix Makefiles", "../source"])
        base.cmd("cmake", ["../source"])
        base.cmd("make", ["-j$(nproc)"])
    if "mac" == base.host_platform():
        base.cmd("cmake", ["-G", "Unix Makefiles", "../source"])
        base.cmd("make", ["-j$(sysctl -n hw.ncpu)"])
    base.copy_file(build_dir + "/x265_config.h", src_dir + "/x265_git/source")
    os.chdir(src_dir)
    return

def make_de265(src_dir):
    if not base.is_dir("libde265"):
        base.cmd("git", ["clone", "https://github.com/strukturag/libde265.git"])
    os.chdir(src_dir + "/libde265")
    base.cmd("cmake", ["./", "-DCMAKE_BUILD_TYPE=Release"])
    if "windows" == base.host_platform():
        base.cmd("cmake", ["--build", ".", "--config", "Release"])
    if "linux" == base.host_platform():
        base.cmd("make", ["-j$(nproc)"])
    if "mac" == base.host_platform():
        base.cmd("make", ["-j$(sysctl -n hw.ncpu)"])
    os.chdir(src_dir)
    return
        

def make_heif(src_dir):
    if not base.is_dir("libheif"):
        base.cmd("git", ["clone", "https://github.com/strukturag/libheif.git"])
    build_dir = src_dir + "/libheif/libheif/api/libheif"
    os.chdir(build_dir)
    if "windows" == base.host_platform():
        base.cmd("cmake", ["../../../", "-DCMAKE_BUILD_TYPE=Release", 
             "-DLIBDE265_INCLUDE_DIR=" + src_dir + "/libde265",
             "-DLIBDE265_LIBRARY=" + src_dir + "/libde265/libde265/Release/de265.lib",
             "-DX265_INCLUDE_DIR=" + src_dir + "/x265_git/source",
             "-DX265_LIBRARY=" + src_dir + "/x265_git/build/Release/libx265.lib",
             "-DWITH_X265_PLUGIN=ON", "-DENABLE_PLUGIN_LOADING=ON","--preset=release"])
        base.cmd("cmake", ["--build", ".", "--config", "Release"])
    if "linux" == base.host_platform():
        base.cmd("cmake", ["../../../", "-DCMAKE_BUILD_TYPE=Release", 
             "-DLIBDE265_INCLUDE_DIR=" + src_dir + "/libde265",
             "-DLIBDE265_LIBRARY=" + src_dir + "/libde265/libde265/libde265.so",
             "-DX265_INCLUDE_DIR=" + src_dir + "/x265_git/source",
             "-DX265_LIBRARY=" + src_dir + "/x265_git/build/libx265.so",
             "-DWITH_X265_PLUGIN=ON", "-DENABLE_PLUGIN_LOADING=ON","--preset=release"])
        base.cmd("make", ["-j$(nproc)"])
    if "mac" == base.host_platform():
        base.cmd("cmake", ["../../../", "-DCMAKE_BUILD_TYPE=Release", 
             "-DLIBDE265_INCLUDE_DIR=" + src_dir + "/libde265",
             "-DLIBDE265_LIBRARY=" + src_dir + "/libde265/libde265/libde265.dylib",
             "-DX265_INCLUDE_DIR=" + src_dir + "/x265_git/source",
             "-DX265_LIBRARY=" + src_dir + "/x265_git/build/libx265.dylib",
             "-DWITH_X265_PLUGIN=ON", "-DENABLE_PLUGIN_LOADING=ON","--preset=release"])
        base.cmd("make", ["-j$(sysctl -n hw.ncpu)"])
    
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

if __name__ == '__main__':
    make()