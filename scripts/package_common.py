#!/usr/bin/env python

platformPrefixes = {
  "windows_x64":      "win_64",
  "windows_x86":      "win_32",
  "windows_x64_xp":   "win_64_xp",
  "windows_x86_xp":   "win_32_xp",
  "darwin_x86_64":    "mac_64",
  "darwin_arm64":     "mac_arm64",
  "darwin_x86_64_v8": "mac_64",
  "linux_x86_64":     "linux_64",
  "linux_aarch64":    "linux_arm64",
  "linux_x86_64_cef": "linux_64",
}

out_dir = "build_tools/out"
tsa_server = "http://timestamp.digicert.com"
vcredist_links = {
  # Microsoft Visual C++ 2015-2022 Redistributable - 14.38.33130
  "2022": {
    "x64": {
      "url": "https://aka.ms/vs/17/release/vc_redist.x64.exe",
      "md5": "101b0b9f74cdc6cdbd2570bfe92e302c"
    },
    "x86": {
      "url": "https://aka.ms/vs/17/release/vc_redist.x86.exe",
      "md5": "0d762264d9765e21c15a58edc43f4706"
    }
  }
}
