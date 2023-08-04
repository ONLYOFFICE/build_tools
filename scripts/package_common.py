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
  "2022": {
    "x64": {
      "url": "https://aka.ms/vs/17/release/vc_redist.x64.exe",
      "md5": "077f0abdc2a3881d5c6c774af821f787"
    },
    "x86": {
      "url": "https://aka.ms/vs/17/release/vc_redist.x86.exe",
      "md5": "ae427c1329c3b211a6d09f8d9506eb74"
    }
  },
  "2015": {
    "x64": {
      "url": "https://download.microsoft.com/download/9/3/F/93FCF1E7-E6A4-478B-96E7-D4B285925B00/vc_redist.x64.exe",
      "md5": "27b141aacc2777a82bb3fa9f6e5e5c1c"
    },
    "x86": {
      "url": "https://download.microsoft.com/download/9/3/F/93FCF1E7-E6A4-478B-96E7-D4B285925B00/vc_redist.x86.exe",
      "md5": "1a15e6606bac9647e7ad3caa543377cf"
    }
  },
  "2013": {
    "x64": {
      "url": "https://download.microsoft.com/download/2/E/6/2E61CFA4-993B-4DD4-91DA-3737CD5CD6E3/vcredist_x64.exe",
      "md5": "96b61b8e069832e6b809f24ea74567ba"
    },
    "x86": {
      "url": "https://download.microsoft.com/download/2/E/6/2E61CFA4-993B-4DD4-91DA-3737CD5CD6E3/vcredist_x86.exe",
      "md5": "0fc525b6b7b96a87523daa7a0013c69d"
    }
  }
}
