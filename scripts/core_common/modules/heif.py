import sys
sys.path.append('../..')
import config
import base
import os

def make_x265(src_dir):
    new_dir = src_dir + "/x256"
    os.chdir(new_dir)

    if not base.is_dir("x256"):
        base.cmd("git", ["clone", "https://bitbucket.org/multicoreware/x265_git.git"])
        build_dir = new_dir + "/build"
        os.chdir(build_dir)
        base.cmd("cmake", "../source")
        base.cmd("make")
        os.chdir(new_dir)

    os.chdir(new_dir)
    return

def make_de265(src_dir):
    new_dir = src_dir + "/de265"
    os.chdir(new_dir)

    if not base.is_dir("de265"):
        base.cmd("git", ["clone", "https://github.com/strukturag/libde265.git"])
        build_dir = new_dir + "/build"
        os.chdir(build_dir)
        base.cmd("cmake", "..")
        base.cmd("make")
        os.chdir(new_dir)

    os.chdir(src_dir)
    return
        

def make_heif(src_dir):
    new_dir = src_dir + "/libheif"
    os.chdir(new_dir)

    if not base.is_dir("libheif"):
        base.cmd("git", ["clone", "https://github.com/strukturag/libheif.git"])
        build_dir = new_dir + "/build"
        os.chdir(build_dir)
        base.cmd("cmake", ["--preset=release", ".."])
        base.cmd("make")
        os.chdir(new_dir)

    os.chdir(src_dir)
    return

def make():
    print("[fetch & build]: heif")
    new_dir = base.get_script_dir() + "/../../core/Common/3dParty/heif"
    old_dir = os.getcwd()
    os.chdir(new_dir)

    if not base.is_dir("heif"):
        make_x265(new_dir)
        make_de265(new_dir)
        make_heif(new_dir)

    os.chdir(old_dir)
    return