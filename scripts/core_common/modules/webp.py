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

    build_type = "release"
    target_file = "/libwebp"
    if (-1 != config.option("config").lower().find("debug")):
        build_type = "debug"
        target_file = "/libwebp-debug"

    # WINDOWS
    if "windows" == base.host_platform():
        platform = "win_64"
        arch = "x64"
        build_type = build_type + "-static"
        make_bat = []

        if config.check_option("platform", "win_32"):
            platform = "win_32"
            arch = "x86"
        if config.check_option("platform", "win_arm64"):
            platform = "win_arm64"

        build_dir = "./../build/" + platform + "/"
        if not base.is_dir(build_dir):
            base.create_dir(build_dir)
        elif base.is_file(build_dir + build_type + "/" + arch + "/lib" + target_file + ".lib"):
            return

        make_bat.append("call \"" + config.option("vs-path") + "/vcvarsall.bat\" " + arch)
        make_bat.append("call nmake /f Makefile.vc CFG=" + build_type + " OBJDIR=" + build_dir)
        base.run_as_bat(make_bat, True)
    
    # LINUX
    elif "linux" == base.host_platform():
        platform = "linux_64"
        arch = "x86_64"
        target_file = "libwebp.a"
        make_args = ["-f", "makefile.unix", target_file]

        debug = ""
        if build_type == "debug":
            debug = " -g "

        if config.check_option("platform", "linux_arm64"):
            platform = "linux_arm64"
            arch = "armv8-a"

        build_dir = "./../build/" + platform + "/" + build_type
        make_args.append("CFLAGS=\"" + debug + "-march=" + arch + "\"")
        if not base.is_dir(build_dir):
            base.create_dir(build_dir)
        if base.is_file(build_dir + "/" + target_file):
            return

        base.cmd("make", make_args)
        base.copy_file(target_file, build_dir)

    os.chdir(old_dir)
    return