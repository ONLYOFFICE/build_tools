import sys
sys.path.append('../..')
import base
import os
import config

def make_x265(src_dir):
    base.cmd("git", ["clone", "https://bitbucket.org/multicoreware/x265_git.git"])
    build_dir = src_dir + "/x265_git/build"
    os.chdir(build_dir)
    base.cmd("cmake", ["../source"])
    base.cmd("make", ["../source"])
    os.chdir(src_dir)
    return

def make_de265(src_dir):
    if not base.is_dir("libde265"):
        base.cmd("git", ["clone", "https://github.com/strukturag/libde265.git"])
    os.chdir(src_dir + "/libde265")
    if "windows" == base.host_platform():
        tmp_bat = []
        tmp_bat.append("call \"" + config.option("vs-path") + "/vcvarsall.bat\" x64")
        tmp_bat.append("call nmake -f Makefile.vc7 /nologo /s /c")
        tmp_bat.append("copy /y dec265\dec265.exe bin_x64\"")
        tmp_bat.append("copy /y enc265\enc265.exe bin_x64\"")
        tmp_bat.append("copy /y libde265\libde265.dll bin_x64\"")
        tmp_bat.append("copy /y libde265\libde265.lib bin_x64\lib\"")
        tmp_bat.append("copy /y libde265\libde265.exp bin_x64\lib\"")
        base.run_as_bat(tmp_bat, True)
    if "linux" == base.host_platform():
        base.cmd("cmake", [".."])
        base.cmd("make")
    os.chdir(src_dir)
    return
        

def make_heif(src_dir):
    base.cmd("git", ["clone", "https://github.com/strukturag/libheif.git"])
    build_dir = src_dir + "/libheif/build"
    base.create_dir(build_dir)
    os.chdir(build_dir)
    if "windows" == base.host_platform():

    if "linux" == base.host_platform():
        base.cmd("cmake", ["--preset=release", ".."])
        base.cmd("make")
    os.chdir(src_dir)
    return

def make():
    print("[fetch & build]: heif")
    new_dir = base.get_script_dir() + "/../../core/Common/3dParty/heif"
    base.create_dir(new_dir)
    old_dir = os.getcwd()
    os.chdir(new_dir)

    if not base.is_dir("heif"):
        #make_x265(new_dir)
        make_de265(new_dir)
        make_heif(new_dir)

    os.chdir(old_dir)
    return