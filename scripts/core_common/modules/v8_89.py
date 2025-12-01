#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import os
import subprocess

def clean():
  if base.is_dir("depot_tools"):
    base.delete_dir_with_access_error("depot_tools")
    base.delete_dir("depot_tools")
  if base.is_dir("v8"):
    base.delete_dir_with_access_error("v8")
    base.delete_dir("v8")
  if base.is_exist("./.gclient"):
    base.delete_file("./.gclient")
  if base.is_exist("./.gclient_entries"):
    base.delete_file("./.gclient_entries")
  if base.is_exist("./.gclient_previous_sync_commits"):
    base.delete_file("./.gclient_previous_sync_commits")
  if base.is_exist("./.gcs_entries"):
    base.delete_file("./.gcs_entries")
  if base.is_exist("./.cipd"):
    base.delete_dir("./.cipd")
  return

def change_bootstrap():
  base.move_file("./depot_tools/bootstrap/manifest.txt", "./depot_tools/bootstrap/manifest.txt.bak")
  content = "# changed by build_tools\n\n"
  content += "$VerifiedPlatform windows-amd64 windows-arm64 linux-amd64 mac-amd64 mac-arm64\n\n"

  content += "@Subdir python\n"
  content += "infra/3pp/tools/cpython/${platform} version:2@2.7.18.chromium.39\n\n"

  content += "@Subdir python3\n"

  if ("windows" == base.host_platform()):
    content += "infra/3pp/tools/cpython3/${platform} version:2@3.11.8.chromium.35\n\n"
  else:
    content += "infra/3pp/tools/cpython3/${platform} version:2@3.8.10.chromium.23\n\n"

  content += "@Subdir git\n"
  content += "infra/3pp/tools/git/${platform} version:2@2.41.0.chromium.11\n"

  base.replaceInFile("./depot_tools/bootstrap/bootstrap.py", 
    "raise subprocess.CalledProcessError(proc.returncode, argv, None)", "return")

  base.replaceInFile("./depot_tools/bootstrap/bootstrap.py", 
    "    _win_git_bootstrap_config()", "    #_win_git_bootstrap_config()")
  
  base.writeFile("./depot_tools/bootstrap/manifest.txt", content)
  return

def make_args(args, platform, is_64=True, is_debug=False):
  args_copy = args[:]
  if is_64:
    args_copy.append("target_cpu=\\\"x64\\\"") 
    args_copy.append("v8_target_cpu=\\\"x64\\\"")
  else:
    args_copy.append("target_cpu=\\\"x86\\\"") 
    args_copy.append("v8_target_cpu=\\\"x86\\\"")

  if (platform == "linux_arm64"):
    args_copy = args[:]
    args_copy.append("target_cpu=\\\"arm64\\\"")
    args_copy.append("v8_target_cpu=\\\"arm64\\\"")
    args_copy.append("use_sysroot=true")
    
  if (platform == "win_arm64"):
    args_copy = args[:]
    args_copy.append("target_cpu=\\\"arm64\\\"")
    args_copy.append("v8_target_cpu=\\\"arm64\\\"")
    args_copy.append("is_clang=false")
    
  if is_debug:
    args_copy.append("is_debug=true")
    if (platform == "windows"):
      args_copy.append("enable_iterator_debugging=true")
  else:
    args_copy.append("is_debug=false")
  
  linux_clang = False
  if platform == "linux":
    if "" != config.option("sysroot"):
      args_copy.append("use_sysroot=false")
      args_copy.append("is_clang=false")
    else:
      args_copy.append("is_clang=true")
      if "1" == config.option("use-clang"):
        linux_clang = True
      else:
        args_copy.append("use_sysroot=false")


  if (platform == "windows"):
    args_copy.append("is_clang=false")

  if (platform == "mac") and base.is_os_arm():
    args_copy.append("host_cpu=\\\"x64\\\"")

  if linux_clang != True:
    args_copy.append("use_custom_libcxx=false")

  return "--args=\"" + " ".join(args_copy) + "\""

def ninja_windows_make(args, is_64=True, is_debug=False, is_arm=False):
  directory_out = "out.gn/"
    
  if is_arm:
    directory_out += "win_arm64/"
  else:
    directory_out += ("win_64/" if is_64 else "win_32/")
    
  directory_out += ("debug" if is_debug else "release")

  if is_arm:
    base.cmd2("gn", ["gen", directory_out, make_args(args, "win_arm64", is_64, is_debug)])
  else:
    base.cmd2("gn", ["gen", directory_out, make_args(args, "windows", is_64, is_debug)])
    
  base.copy_file("./" + directory_out + "/obj/v8_wrappers.ninja", "./" + directory_out + "/obj/v8_wrappers.ninja.bak")
  base.replaceInFile("./" + directory_out + "/obj/v8_wrappers.ninja", "target_output_name = v8_wrappers", "target_output_name = v8_wrappers\nbuild obj/v8_wrappers.obj: cxx ../../../src/base/platform/wrappers.cc")
  base.replaceInFile("./" + directory_out + "/obj/v8_wrappers.ninja", "build obj/v8_wrappers.lib: alink", "build obj/v8_wrappers.lib: alink obj/v8_wrappers.obj")

  win_toolset_wrapper_file = "build/toolchain/win/tool_wrapper.py"
  win_toolset_wrapper_file_content = base.readFile("build/toolchain/win/tool_wrapper.py")
  if (-1 == win_toolset_wrapper_file_content.find("line = line.decode('utf8')")):
    base.replaceInFile(win_toolset_wrapper_file, "for line in link.stdout:\n", "for line in link.stdout:\n      line = line.decode('utf8')\n")


  base.cmd("ninja", ["-C", directory_out, "v8_wrappers"])
  if is_arm:
    base.copy_file('./' + directory_out + '/obj/v8_wrappers.lib', './' + directory_out + '/x64/obj/v8_wrappers.lib')
  base.cmd("ninja", ["-C", directory_out])
  base.delete_file("./" + directory_out + "/obj/v8_wrappers.ninja")
  base.move_file("./" + directory_out + "/obj/v8_wrappers.ninja.bak", "./" + directory_out + "/obj/v8_wrappers.ninja")
  return

# patch v8 for build ---------------------------------------------------
def patch_windows_debug():
  # v8 8.9 version does not built with enable_iterator_debugging flag
  # patch heap.h file:
  file_patch = "./src/heap/heap.h"
  base.copy_file(file_patch, file_patch + ".bak")
  content_old = base.readFile(file_patch)
  posStart = content_old.find("class StrongRootBlockAllocator {")
  posEnd = content_old.find("};", posStart + 1)
  posEnd = content_old.find("};", posEnd + 1)
  content = content_old[0:posStart]
  content += base.readFile("./../../../../../build_tools/scripts/core_common/modules/v8_89.patch")
  content += content_old[posEnd + 2:]
  base.writeFile(file_patch, content)
  return

def unpatch_windows_debug():
  file_patch = "./src/heap/heap.h"
  base.move_file(file_patch + ".bak", file_patch)
  return
# ----------------------------------------------------------------------

def make():
  old_env = dict(os.environ)
  old_cur = os.getcwd()

  base_dir = base.get_script_dir() + "/../../core/Common/3dParty/v8_89"
  if not base.is_dir(base_dir):
    base.create_dir(base_dir)

  base.common_check_version("v8", "1", clean)

  if ("mac" == base.host_platform()):
    base.cmd("git", ["config", "--global", "http.postBuffer", "157286400"], True)

  os.chdir(base_dir)
  if not base.is_dir("depot_tools"):
    base.cmd("git", ["clone", "https://chromium.googlesource.com/chromium/tools/depot_tools.git"])
    change_bootstrap()

  os.environ["PATH"] = base_dir + "/depot_tools" + os.pathsep + os.environ["PATH"]

  if ("windows" == base.host_platform()):
    base.set_env("DEPOT_TOOLS_WIN_TOOLCHAIN", "0")
    base.set_env("GYP_MSVS_VERSION", config.option("vs-version"))

  if not base.is_dir("v8"):
    base.cmd("./depot_tools/fetch", ["v8"], True)
    base.copy_dir("./v8/third_party", "./v8/third_party_new")
    if ("windows" == base.host_platform()):
      os.chdir("v8")
      base.cmd("git", ["config", "--system", "core.longpaths", "true"], True)
      os.chdir("../")
    v8_branch_version = "remotes/branch-heads/8.9"
    if ("mac" == base.host_platform()):
      v8_branch_version = "remotes/branch-heads/9.9"
    base.cmd("./depot_tools/gclient", ["sync", "-r", v8_branch_version], True)
    base.cmd("gclient", ["sync", "--force"], True)
    base.copy_dir("./v8/third_party_new/ninja", "./v8/third_party/ninja")

  if ("windows" == base.host_platform()):
    base.replaceInFile("v8/build/config/win/BUILD.gn", ":static_crt", ":dynamic_crt")
    
    # fix for new depot_tools and vs2019, as VC folder contains a folder with a symbol in the name
    # sorting is done by increasing version, so 0 is a dummy value
    replace_src = "  def to_int_if_int(x):\n    try:\n      return int(x)\n    except ValueError:\n      return x"
    replace_dst = "  def to_int_if_int(x):\n    try:\n      return int(x)\n    except ValueError:\n      return 0"
    base.replaceInFile("v8/build/vs_toolchain.py", replace_src, replace_dst)
    
    
    if not base.is_file("v8/src/base/platform/wrappers.cc"):
      base.writeFile("v8/src/base/platform/wrappers.cc", "#include \"src/base/platform/wrappers.h\"\n")
  
    if config.check_option("platform", "win_arm64"):
      base.replaceInFile("v8/build/toolchain/win/setup_toolchain.py", "SDK_VERSION = \'10.0.26100.0\'", "SDK_VERSION = \'10.0.22621.0\'")
  else:
    base.replaceInFile("depot_tools/gclient_paths.py", "@functools.lru_cache", "")

  if ("mac" == base.host_platform()):
    if not base.is_file("v8/build/config/compiler/BUILD.gn.bak"):
      base.copy_file("v8/build/config/compiler/BUILD.gn", "v8/build/config/compiler/BUILD.gn.bak")
      base.replaceInFile("v8/build/config/compiler/BUILD.gn", "\"-Wloop-analysis\",", "\"-Wloop-analysis\", \"-D_Float16=short\",")

  if not base.is_file("v8/third_party/jinja2/tests.py.bak"):
    base.copy_file("v8/third_party/jinja2/tests.py", "v8/third_party/jinja2/tests.py.bak")
    base.replaceInFile("v8/third_party/jinja2/tests.py", "from collections import Mapping", "try:\n    from collections.abc import Mapping\nexcept ImportError:\n    from collections import Mapping")

  os.chdir("v8")
  
  gn_args = ["v8_static_library=true",
             "is_component_build=false",
             "v8_monolithic=true",
             "v8_use_external_startup_data=false",
             "treat_warnings_as_errors=false"]

  if config.check_option("platform", "linux_64"):
    if config.option("sysroot") != "":
      src_replace = "config(\"compiler\") {\n  asmflags = []\n  cflags = []\n  cflags_c = []\n  cflags_cc = []\n  cflags_objc = []\n  cflags_objcc = []\n  ldflags = []"
      dst_replace = "config(\"compiler\") {\n  asmflags = []\n  cflags = [\"--sysroot=" + config.option("sysroot") + "\"]" + "\n  cflags_c = []\n  cflags_cc = [\"--sysroot=" + config.option("sysroot") + "\"]" + "\n  cflags_objc = []\n  cflags_objcc = []\n  ldflags = [\"--sysroot=" + config.option("sysroot") + "\"]"
      base.replaceInFile("build/config/compiler/BUILD.gn", src_replace, dst_replace)

      src_replace = "gcc_toolchain(\"x64\") {\n  cc = \"gcc\"\n  cxx = \"g++\""
      dst_replace = "gcc_toolchain(\"x64\") {\n  cc = \""+ config.get_custom_sysroot_bin() + "/gcc\"\n  cxx = \"" + config.get_custom_sysroot_bin() + "/g++\""
      base.replaceInFile("build/toolchain/linux/BUILD.gn", src_replace, dst_replace)
      
      old_env = dict(os.environ)
      base.set_sysroot_env()
      base.cmd2("gn", ["gen", "out.gn/linux_64", make_args(gn_args, "linux")], False)
      base.cmd2("ninja", ["-C", "out.gn/linux_64"], False)
      base.restore_sysroot_env()
    else:
      base.cmd2("gn", ["gen", "out.gn/linux_64", make_args(gn_args, "linux")], False)
      base.cmd2("ninja", ["-C", "out.gn/linux_64"], False)


  if config.check_option("platform", "linux_32"):
    base.cmd2("gn", ["gen", "out.gn/linux_32", make_args(gn_args, "linux", False)])
    base.cmd("ninja", ["-C", "out.gn/linux_32"])

  if config.check_option("platform", "linux_arm64"):
    base.cmd("build/linux/sysroot_scripts/install-sysroot.py", ["--arch=arm64"], False)
    base.cmd2("gn", ["gen", "out.gn/linux_arm64", make_args(gn_args, "linux_arm64", False)])
    base.cmd("ninja", ["-C", "out.gn/linux_arm64"])

  if config.check_option("platform", "mac_64"):
    base.cmd2("gn", ["gen", "out.gn/mac_64", make_args(gn_args, "mac")])
    base.cmd("ninja", ["-C", "out.gn/mac_64"])
    
  if config.check_option("platform", "win_arm64") and not base.is_file("out.gn/win_arm64/release/obj/v8_monolith.lib"):
    ninja_windows_make(gn_args, True, False, True)

  if config.check_option("platform", "win_64"):
    if (-1 != config.option("config").lower().find("debug")):
      if not base.is_file("out.gn/win_64/debug/obj/v8_monolith.lib"):
        patch_windows_debug()
        ninja_windows_make(gn_args, True, True)
        unpatch_windows_debug()

    if not base.is_file("out.gn/win_64/release/obj/v8_monolith.lib"):
      ninja_windows_make(gn_args)

  if config.check_option("platform", "win_32"):
    if (-1 != config.option("config").lower().find("debug")):
      if not base.is_file("out.gn/win_32/debug/obj/v8_monolith.lib"):
        patch_windows_debug()
        ninja_windows_make(gn_args, False, True)
        unpatch_windows_debug()

    if not base.is_file("out.gn/win_32/release/obj/v8_monolith.lib"):
      ninja_windows_make(gn_args, False)

  os.chdir(old_cur)
  os.environ.clear()
  os.environ.update(old_env)
