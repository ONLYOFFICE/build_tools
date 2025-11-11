#!/usr/bin/env python

platformPrefixes = {
  "windows_x64":      "win_64",
  "windows_x86":      "win_32",
  "windows_arm64":    "win_arm64",
  "windows_x64_xp":   "win_64_xp",
  "windows_x86_xp":   "win_32_xp",
  "darwin_arm64":     "mac_arm64",
  "darwin_x86_64":    "mac_64",
  "darwin_x86_64_v8": "mac_64",
  "linux_x86_64":     "linux_64",
  "linux_aarch64":    "linux_arm64",
}

out_dir = "build_tools/out"
tsa_server = "http://timestamp.digicert.com"
