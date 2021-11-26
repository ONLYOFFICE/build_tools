#!/usr/bin/env python

import sys
sys.path.append('modules')
sys.path.append('..')

import config
import base
import glob

import boost
import cef
import icu
import openssl
import curl
import websocket
import v8
import html2
import hunspell
import glew

def check_android_ndk_macos_arm(dir):
  if base.is_dir(dir + "/darwin-x86_64") and not base.is_dir(dir + "/darwin-arm64"):
    print("copy toolchain... [" + dir + "]")
    base.copy_dir(dir + "/darwin-x86_64", dir + "/darwin-arm64")
  return


def make():
  if (config.check_option("platform", "android")) and (base.host_platform() == "mac") and (base.is_os_arm()):
    for toolchain in glob.glob(base.get_env("ANDROID_NDK_ROOT") + "/toolchains/*"):
      if base.is_dir(toolchain):
        check_android_ndk_macos_arm(toolchain + "/prebuilt")

  boost.make()
  cef.make()
  icu.make()
  openssl.make()
  v8.make()
  html2.make()
  hunspell.make(False)
  glew.make()
  if config.check_option("module", "mobile"):
    curl.make()
    websocket.make()
  return
