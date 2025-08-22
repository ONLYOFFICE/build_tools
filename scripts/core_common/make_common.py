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
import websocket_all
import v8
import html2
import iwork
import md
import hunspell
import glew
import harfbuzz
import oo_brotli
import hyphen
import googletest
import libvlc
import heif

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
  iwork.make(False)
  md.make()
  hunspell.make(False)
  harfbuzz.make()
  glew.make()
  hyphen.make()
  googletest.make()
  oo_brotli.make()
  heif.make()

  if config.check_option("build-libvlc", "1"):
    libvlc.make()

  if config.check_option("module", "mobile"):
    if (config.check_option("platform", "android")):
      curl.make()
    websocket_all.make()
  return
