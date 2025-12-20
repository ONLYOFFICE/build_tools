#!/usr/bin/env python3

import sys
import os
sys.path.append('../../../scripts')

import base

URL = "https://github.com/ONLYOFFICE-data/build_tools_data/raw/refs/heads/master/sysroot/"

SYSROOTS = {
  "amd64": "ubuntu16-amd64-sysroot.tar.gz",
  "arm64": "ubuntu16-arm64-sysroot.tar.gz",
}

def download_and_extract(name):
  archive = SYSROOTS[name]
  base.download(URL + archive, "./" + archive)
  base.cmd("tar", ["-xzf", "./" + archive])

def main():
  if len(sys.argv) != 2:
    print("Usage: fetch.py [amd64|arm64|all]")
    sys.exit(1)

  target = sys.argv[1]

  if target == "all":
    for name in SYSROOTS:
      download_and_extract(name)
  elif target in SYSROOTS:
    download_and_extract(target)
  else:
    print(f"Unknown target: {target}")
    print("Valid values: amd64, arm64, all")
    sys.exit(1)

if __name__ == "__main__":
    main()
