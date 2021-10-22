#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import sys
sys.path.append('../..')
import config
import base
import os
import config

current_dir = base.get_script_dir() + "/../../core/Common/3dParty/socketrocket"

def buildIOS():

# Build for iphone
  base.cmd("xcodebuild", ["-sdk", "iphoneos", "BITCODE_GENERATION_MODE = bitcode", "ENABLE_BITCODE = YES", "OTHER_CFLAGS = -fembed-bitcode", "-configuration", "Release"])

# Build for simulator
  base.cmd("xcodebuild", ["-sdk", "iphonesimulator", "BITCODE_GENERATION_MODE = bitcode", "ENABLE_BITCODE = YES", "OTHER_CFLAGS = -fembed-bitcode", "-configuration", "Release"])

# Remove arm64 for simulator for SDK 14
  base.cmd("lipo", ["-remove", "arm64", "-output", "build/Release-iphonesimulator/libSocketRocket.a", "build/Release-iphonesimulator/libSocketRocket.a"])

  base.create_dir(current_dir + "/build/ios/lib")

# Create fat lib
  base.cmd("lipo", ["./build/Release-iphonesimulator/libSocketRocket.a", "./build/Release-iphoneos/libSocketRocket.a", "-create", "-output", 
     "./build/ios/lib/libSoсketRocket.a"])

  return

def buildMacOS():

# Build for iphone
  base.cmd("xcodebuild", ["-sdk", "macosx", "BITCODE_GENERATION_MODE = bitcode", "ENABLE_BITCODE = YES", "OTHER_CFLAGS = -fembed-bitcode", "-configuration", "Release"])

  base.create_dir(current_dir + "/build/mac_64/lib")
  base.create_dir(current_dir + "/build/mac_arm64/lib")

  base.cmd("lipo", ["build/Release/libSocketRocket.a", "-thin", "x86_64", "-output", "build/mac_64/lib/libSoсketRocket.a"])
  base.cmd("lipo", ["build/Release/libSocketRocket.a", "-thin", "arm64", "-output", "build/mac_arm64/lib/libSoсketRocket.a"])

  base.delete_file("build/Release/libSocketRocket.a")

  return

def make():
  if (-1 == config.option("platform").find("mac") and -1 == config.option("platform").find("ios")):
    return

  current_dir_old = os.getcwd()

  print("[build]: socketrocket")
  os.chdir(current_dir)

  if (-1 != config.option("platform").find("mac")):
    if not base.is_dir(current_dir + "/build/mac_64") or not base.is_dir(current_dir + "/build/mac_arm_64"):
      buildMacOS()
  elif (-1 != config.option("platform").find("ios")):
    if not base.is_dir(current_dir + "/build/ios"):
      buildIOS()
  os.chdir(current_dir_old)
  return
