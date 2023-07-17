#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import os

def docker_build(image_name, dockerfile_dir, vlc_dir):
  base.cmd('docker', ['build', '-t', image_name, dockerfile_dir])
  base.cmd('docker', ['run', '--rm', '-v', vlc_dir + ':/vlc', image_name])
  base.cmd('docker', ['image', 'rm', image_name])
  return

def copy_build(src_dir, dest_dir):
  if not base.is_dir(dest_dir):
    base.create_dir(dest_dir)
  # copy include
  base.copy_dir(src_dir + '/sdk/include', dest_dir + '/include')
  # form lib dir
  base.create_dir(dest_dir + '/lib')
  base.copy_file(src_dir + '/sdk/lib/libvlc.lib', dest_dir + '/lib/vlc.lib')
  base.copy_file(src_dir + '/sdk/lib/libvlccore.lib', dest_dir + '/lib/vlccore.lib')
  base.copy_dir(src_dir + '/plugins', dest_dir + '/lib/plugins')
  base.copy_file(src_dir + '/libvlc.dll', dest_dir + '/lib')
  base.copy_file(src_dir + '/libvlccore.dll', dest_dir + '/lib')
  base.copy_file(src_dir + '/vlc-cache-gen.exe', dest_dir + '/lib')
  # generate cache file 'plugins.dat' for plugins loading
  base.cmd_exe(dest_dir + '/lib/vlc-cache-gen', [dest_dir + '/lib/plugins'])
  return


def make():

  print("[fetch & build]: libvlc")

  base_dir = base.get_script_dir() + "/../../core/Common/3dParty/libvlc"
  vlc_dir = base_dir + '/vlc'
  vlc_version = '3.0.18'

  old_cur = os.getcwd()
  os.chdir(base_dir)

  if not base.is_dir(vlc_dir):
    # temporary disable auto CRLF for Windows
    if "windows" == base.host_platform():
      autocrlf_old = base.run_command('git config --global core.autocrlf')['stdout']
      base.cmd("git", ["config", "--global", "core.autocrlf", "false"])
    base.cmd("git", ["clone", "https://code.videolan.org/videolan/vlc.git", "--branch", vlc_version])
    if "windows" == base.host_platform():
      base.cmd("git", ["config", "--global", "core.autocrlf", autocrlf_old])

  if "windows" == base.host_platform():
    if config.check_option("platform", "win_64"):
      docker_build('libvlc-win64', base_dir + '/tools/win_64', vlc_dir)
      copy_build(vlc_dir + '/build/win64/vlc-' + vlc_version, base_dir + '/build/win_64')
      
    if config.check_option("platform", "win_32"):
      docker_build('libvlc-win32', base_dir + '/tools/win_32', vlc_dir)
      copy_build(vlc_dir + '/build/win32/vlc-' + vlc_version, base_dir + '/build/win_32')


  if (-1 != config.option("platform").find("linux")):
    if not base.is_file("tools/linux_64/.deps_complete"):
      print("Dependencies for building libvlc are not installed!\n")
      print("Please, run " + base_dir + "/tools/linux_64/deps.py to install all neccessary dependencies.")
      exit(0)
    
    os.chdir("vlc")
    base.cmd("./bootstrap")
    # build contribs
    os.chdir("contrib")
    base.cmd("mkdir", ["-p", "native"])
    os.chdir("native")
    base.cmd("../bootstrap")
    base.cmd("make")
    # configure
    os.chdir(vlc_dir)
    base.cmd("mkdir", ["-p", "build"])
    base.cmd("./configure", ["--prefix=/home/mihail/main/libvlc/vlc/build", "--disable-vlc", "--disable-qt", "--disable-skins2", "--disable-chromecast"])
    # build libvlc
    base.cmd("make", ["-j$(nproc)"])
    # install in build
    base.cmd("make", ["-j$(nproc)", "install-strip"])
    
    # form build
    os.chdir(base_dir)
    base.create_dir(base_dir + "/build/linux_64")
    os.chdir("build/linux_64")
    base.copy_dir(vlc_dir + "build/lib", "./lib")
    base.copy_dir(vlc_dir + "build/include", "./include")
    base.cmd("find", [".", "-name", "*.la", "-type", "f", "-delete"])
    base.delete_dir("lib/pkgconfig")
    base.delete_dir("lib/vlc/lua")
    base.cmd("lib/vlc/vlc-cache-gen", ["lib/vlc/plugins"])

  os.chdir(old_cur)
  return
