import sys
sys.path.append('../..')
import base
import os
import config

ARCHES = {"win_64"              : "x64",
          "win_32"              : "x86",
          "linux_64"            : "x86_64-linux-gnu",
          "linux_arm64"         : "aarch64-linux-gnu",
          "mac_64"              : "x86_64-apple-darwin",
          "mac_arm64"           : "arm-apple-darwin",
          "android_arm64_v8a"   : "aarch64-linux-android",
          "android_armv7"       : "armv7a-linux-androideabi",
          "android_x86"         : "i686-linux-android",
          "android_x86_64"      : "x86_64-linux-android",
          "ios"                 : "arm-apple-darwin",
          "ios_simulator"       : "x86_64-apple-darwin"}

def get_xcode_sdk(platform):
    xcode_sdk = "iphoneos"
    if "simulator" in platform:
        xcode_sdk = "iphonesimulator"
    return xcode_sdk

def get_ios_min_version(platform):
    res = " -miphoneos-version-min=11.0"
    if "simulator" in platform:
        res = " -mios-simulator-version-min=11.0"
    return res

def fetch_repo():
    base_dir = base.get_script_dir() + "/../../core/Common/3dParty/webp"
    if not base.is_dir(base_dir):
        base.create_dir(base_dir)
    old_dir = os.getcwd()
    os.chdir(base_dir)

    if (base.is_dir("libwebp")):
        base.delete_dir_with_access_error("libwebp")

    if not base.is_dir("libwebp"):
        base.cmd("git", ["clone", "--branch","v1.6.0", "https://chromium.googlesource.com/webm/libwebp"])
    os.chdir(base_dir + "/libwebp")
    return old_dir

def create_build_dir(platform, build_type) -> str:
    build_dir = ""
    if "win" in platform:
        target_file = "libwebp"
        if build_type == "debug":
            target_file += "-debug"
        target_file += ".lib"
        build_dir = "./../build/" + platform + "/"
        if not base.is_dir(build_dir):
            base.create_dir(build_dir)
        elif base.is_file(build_dir + build_type + "/" + ARCHES[platform] + "/lib/" + target_file):
            build_dir = ""
    else:
        build_dir = "./../build/" + platform + "/" + build_type
        if not base.is_dir(build_dir):
            base.create_dir(build_dir)
        if base.is_file(build_dir + "/src/.libs/libwebp.a"):
            build_dir = ""
    return build_dir

def get_args(platform, build_type, build_dir):
    if "win" in platform:
        args = []
        args.append("call \"" + config.option("vs-path") + "/vcvarsall.bat\" " + ARCHES[platform])
        args.append("call nmake /f Makefile.vc CFG=" + build_type + "-static" + " OBJDIR=" + build_dir)
        return args
    elif "linux" in platform or "android" in platform:
        cflags = "-O3 -DNDEBUG"
        if build_type == "debug":
            cflags = "-O0 -g"

        if config.option("sysroot") != "":
            cflags += " --sysroot=" + config.option("sysroot")

        cross_arm64 = ""
        if platform == "linux_arm64":
            cross_cimpile_arm64 = config.option("arm64-toolchain-bin")
            if "" == cross_cimpile_arm64:
                cross_cimpile_arm64 = "/usr/bin"
            cross_arm64 = "--cross-compile-prefix=" + cross_cimpile_arm64 + "/" + base.get_prefix_cross_compiler_arm64()

        return ["--host=" + ARCHES[platform], "--enable-static", "--disable-shared",
                "--disable-libwebpdecoder", "--disable-libwebpdemux",
                "--disable-libwebpmux", "--disable-libwebpextras", 
                cross_arm64, "CFLAGS=" + cflags, "LDFLAGS=-static"]
    elif "mac" in platform:
        arch = ARCHES[platform]
        short_arch = arch[:arch.find("-")]
        if short_arch == "arm":
            short_arch += "64"
        
        cflags = "-O3 -DNDEBUG -arch " + short_arch + " -fPIC"
        if build_type == "debug":
            cflags = "-O0 -g -arch " + short_arch + " -fPIC"

        return ["--host=" + arch, "--enable-static", "--disable-shared",
                "--disable-libwebpdecoder", "--disable-libwebpdemux",
                "--disable-libwebpmux", "--disable-libwebpextras", 
                "CFLAGS=" + cflags, "LDFLAGS=-arch " + short_arch]
    elif "ios" in platform:
        arch = ARCHES[platform]
        short_arch = arch[:arch.find("-")]
        if short_arch == "arm":
            short_arch += "64"
        
        xcode_sdk = get_xcode_sdk(platform)
        version_min = get_ios_min_version(platform)
        cflags = "-O3 -DNDEBUG -arch " + short_arch + " -isysroot " + xcode_sdk + version_min + " -fPIC"
        if build_type == "debug":
            cflags = "-O0 -g -arch " + short_arch + " -isysroot " + xcode_sdk + version_min + " -fPIC"

        return ["--host=" + arch, "--enable-static", "--disable-shared",
                "--disable-libwebpdecoder", "--disable-libwebpdemux",
                "--disable-libwebpmux", "--disable-libwebpextras", 
                "CFLAGS=" + cflags, "LDFLAGS=-arch " + short_arch + " -isysroot " + xcode_sdk]

def make():
    print("[fetch & build]: webp")

    old_dir = fetch_repo()
    build_type = "release"
    if -1 != config.option("config").lower().find("debug"):
        build_type = "debug"
    platform = config.option("platform")
    build_dir = create_build_dir(platform, build_type)
    args = get_args(platform, build_type, build_dir)
    
    
    if build_dir == "":
        return

    # WINDOWS
    if "windows" == base.host_platform():
        base.run_as_bat(args, True)
    
    # LINUX, ANDROID
    elif -1 != platform.find("linux") or -1 != platform.find("android"):
        base.cmd("./autogen.sh")
        os.chdir(build_dir)

        if config.option("sysroot") != "":
            args += ["CROSS_COMPILE=" + config.get_custom_sysroot_bin() + "/"]

        base.cmd("./../../../libwebp/configure",  args)

        if config.option("sysroot") != "":
            base.setup_custom_sysroot_env()
        base.cmd("make", ["-j$(nproc)"])
        if config.option("sysroot") != "":
            base.restore_sysroot_env()

    #MAC, IOS
    elif -1 != platform.find("mac") or -1 != platform.find("ios"):
        base.cmd("./autogen.sh")
        os.chdir(build_dir)
        base.cmd("./../../../libwebp/configure",  args)
        base.cmd("make", ["-j$(sysctl -n hw.ncpu)"])

    os.chdir(old_dir)
    return