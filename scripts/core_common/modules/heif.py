import sys
sys.path.append('../..')
import base
import os
import config

def make_x265(src_dir, lib_dir):
    if not base.is_dir("x265_git"):
        base.cmd("git", ["clone", "https://bitbucket.org/multicoreware/x265_git.git"])
    cmake_dir = src_dir + "/x265_git/build"
    os.chdir(cmake_dir)

    cmake_args = [
        "-DBUILD_SHARED_LIBS=OFF", "-DENABLE_SHARED=OFF", "../source"
    ]

    if "windows" == base.host_platform():
        cmake_args.extend(["-G", "Visual Studio 16 2019", "-A", "x64"])
        base.cmd("cmake", cmake_args)
        base.cmd("cmake", ["--build", ".", "--config", "Release"])
        base.copy_files(cmake_dir + "/Release/*.lib", lib_dir)
    
    if "linux" == base.host_platform():
        cmake_args.extend(["-G", "Unix Makefiles", "-DCMAKE_POSITION_INDEPENDENT_CODE=ON"])
        base.cmd("cmake", cmake_args)
        base.cmd("make", ["-j$(nproc)"])
        base.copy_file(cmake_dir + "/*.a", lib_dir)
    
    base.copy_files(cmake_dir + "/*.h", src_dir + "/x265_git/source")
    os.chdir(src_dir)
    
    return

def make_de265(src_dir, lib_dir):
    if not base.is_dir("libde265"):
        base.cmd("git", ["clone", "https://github.com/strukturag/libde265.git"])
    cmake_dir = src_dir + "/libde265"
    os.chdir(cmake_dir)
    
    cmake_args = [
        "./", "-DCMAKE_BUILD_TYPE=Release", "-DBUILD_SHARED_LIBS=OFF",
        "-DENABLE_SHARED=OFF", "-DENABLE_DECODER=ON", "-DENABLE_ENCODER=ON"
    ]
    
    if "windows" == base.host_platform():
        base.cmd("cmake", cmake_args)
        base.cmd("cmake", ["--build", ".", "--config", "Release"])
        base.copy_files(cmake_dir + "/libde265/Release/*.lib", lib_dir)

    if "linux" == base.host_platform():
        cmake_args.extend(["-DCMAKE_POSITION_INDEPENDENT_CODE=ON"])
        base.cmd("cmake", cmake_args)
        base.cmd("make", ["-j$(nproc)"])
        base.copy_files(cmake_dir + "/libde265/*.a", lib_dir)
    
    os.chdir(src_dir)
    
    return
        

def make_heif(src_dir, lib_dir):
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
        "../../../", "-DCMAKE_BUILD_TYPE=Release", "--preset=release-noplugins", 
        "-DENABLE_PLUGIN_LOADING=OFF", "-DWITH_X265=ON", "-DWITH_LIBDE265=ON", 
        "-DBUILD_SHARED_LIBS=OFF"
    ]

    if "windows" == base.host_platform():
        cmake_args.extend(["-DLIBDE265_INCLUDE_DIR=" + src_dir + "/libde265",
                           "-DLIBDE265_LIBRARY=" + lib_dir + "/libde265.lib",
                           "-DX265_INCLUDE_DIR=" + src_dir + "/x265_git/source",
                           "-DX265_LIBRARY=" + lib_dir + "/x265-static.lib",])        
        base.cmd("cmake", cmake_args)
        base.cmd("cmake", ["--build", ".", "--config", "Release"])
        base.copy_files(cmake_dir + "/libheif/Release/*.lib", lib_dir)

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
    new_dir = base.get_script_dir() + "/../../core/Common/3dParty/heif"
    base.create_dir(new_dir)
    old_dir = os.getcwd()
    os.chdir(new_dir)
    lib_dir = new_dir + "/lib"
    base.create_dir(lib_dir)

    if not base.is_dir("heif"):
        make_x265(new_dir, lib_dir)
        make_de265(new_dir, lib_dir)
        make_heif(new_dir, lib_dir)

    os.chdir(old_dir)
    return