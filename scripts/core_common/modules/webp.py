import sys
sys.path.append('../..')
import base
import os
import config

def make():
    print("[fetch & build]: webp")

    base_dir = base.get_script_dir() + "/../../core/Common/3dParty/webp"
    old_dir = os.getcwd()
    os.chdir(base_dir)

    if not base.is_dir("libwebp"):
        base.cmd("git", ["clone", "https://chromium.googlesource.com/webm/libwebp"])

    base_dir = base_dir + "/libwebp"
    os.chdir(base_dir)

    build_type = "release-static"
    if (-1 != config.option("config").lower().find("debug")):
        build_type = "debug-static"

    # WINDOWS
    if "windows" == base.host_platform():
        if (-1 != config.option("platform").find("win_64") and not base.is_dir("../build/win_64")):
            build_dir = "./../build/win_64/"
            if not base.is_dir(build_dir):
                base.create_dir(build_dir)
            make_bat = []
            make_bat.append("call \"" + config.option("vs-path") + "/vcvarsall.bat\" x64")
            make_bat.append("call nmake /f Makefile.vc CFG=" + build_type + " OBJDIR=" + build_dir)
            base.run_as_bat(make_bat, True)
        if (-1 != config.option("platform").find("win_32") and not base.is_dir("../build/win_32")):
            build_dir = "./../build/win_32/"
            if not base.is_dir(build_dir):
                base.create_dir(build_dir)
            make_bat = []
            make_bat.append("call \"" + config.option("vs-path") + "/vcvarsall.bat\" x86")
            make_bat.append("call nmake /f Makefile.vc CFG=" + build_type + " OBJDIR=" + build_dir)
            base.run_as_bat(make_bat, True)
        if (-1 != config.option("platform").find("win_arm64") and not base.is_dir("../build/win_arm64")):
            build_dir = "./../build/win_arm64/"
            if not base.is_dir(build_dir):
                base.create_dir(build_dir)
            make_bat = []
            make_bat.append("call \"C:/Program Files (x86)/Microsoft Visual Studio/2019/Community/VC/Auxiliary/Build/vcvarsall.bat\" x64_arm64")
            make_bat.append("call nmake /f Makefile.vc CFG=" + build_type + " OBJDIR=" + build_dir)
            base.run_as_bat(make_bat, True)
    
    os.chdir(old_dir)
    return