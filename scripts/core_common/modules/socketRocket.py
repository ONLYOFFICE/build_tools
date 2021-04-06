#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import sys
sys.path.append('../..')
import base
import os

current_dir = base.get_script_dir() + "/../../core/Common/3dParty/socketRocket"

def buildIOS():

# Build for iphone
  base.cmd("xcodebuild", ["-sdk", "iphoneos", "BITCODE_GENERATION_MODE = bitcode", "ENABLE_BITCODE = YES", "OTHER_CFLAGS = -fembed-bitcode", "-configuration", "Release"])

# Build for simulator
  base.cmd("xcodebuild", ["-sdk", "iphonesimulator", "BITCODE_GENERATION_MODE = bitcode", "ENABLE_BITCODE = YES", "OTHER_CFLAGS = -fembed-bitcode", "-configuration", "Release"])

# Remove arm64 for simulator for SDK 14
  base.cmd("lipo", ["-remove", "arm64", "-output", "build/Release-iphonesimulator/libSocketRocket.a", "build/Release-iphonesimulator/libSocketRocket.a"])

  base.create_dir(current_dir + "/build/lib/ios")

# Create fat lib
  base.cmd("lipo", ["build/Release-iphonesimulator/libSocketRocket.a", "build/Release-iphoneos/libSocketRocket.a", "-create", "-output", 
     "build/lib/ios/libSoсketRocket.a"])

  return

def buildMacOS():

# Build for iphone
  base.cmd("xcodebuild", ["-sdk", "macosx", "BITCODE_GENERATION_MODE = bitcode", "ENABLE_BITCODE = YES", "OTHER_CFLAGS = -fembed-bitcode", "-configuration", "Release"])

  base.create_dir(current_dir + "/build/lib/mac")

  base.copy_file("build/Release/libSocketRocket.a", current_dir + "/build/lib/mac")

  os.remove("build/Release/libSocketRocket.a")

  return

def make():
 
  if base.is_dir(current_dir + "/build"):
    return

  current_dir_old = os.getcwd()

  print("[build]: socketRocket")
  os.chdir(current_dir)

  if (-1 != config.option("platform").find("mac")):
    buildMacOS()
  if (-1 != config.option("platform").find("ios")):
    buildIOS()
  os.chdir(current_dir_old)
  return
