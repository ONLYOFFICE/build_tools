#!/usr/bin/env python

platforms = {
  "windows_x64":      { "title": "Windows x64",     "prefix": "win_64"      },
  "windows_x64_xp":   { "title": "Windows x64 XP",  "prefix": "win_64_xp"   },
  "windows_x86":      { "title": "Windows x86",     "prefix": "win_32"      },
  "windows_x86_xp":   { "title": "Windows x86 XP",  "prefix": "win_32_xp"   },
  "darwin_x86_64":    { "title": "macOS x86_64",    "prefix": "mac_64"      },
  "darwin_x86_64_v8": { "title": "macOS x86_64 V8", "prefix": "mac_64"      },
  "darwin_arm64":     { "title": "macOS arm64",     "prefix": "mac_arm64"   },
  "linux_x86_64":     { "title": "Linux x86_64",    "prefix": "linux_64"    },
  "linux_aarch64":    { "title": "Linux aarch64",   "prefix": "linux_arm64" },
  "android":          { "title": "Android" }
}

out_dir = "build_tools/out"
tsa_server = "http://timestamp.digicert.com"
vcredist_links = {
  "2022": {
    "x64": {
      "url": "https://aka.ms/vs/17/release/vc_redist.x64.exe",
      "md5": "119dde89a20674349a51893114eae5ed"
    },
    "x86": {
      "url": "https://aka.ms/vs/17/release/vc_redist.x86.exe",
      "md5": "ca8c521c30f57c0c199d526b9a23fc4a"
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
