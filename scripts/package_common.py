#!/usr/bin/env python

out_dir = "build_tools/out"
# s3_bucket = "repo-doc-onlyoffice-com"
s3_bucket = "deploytest-static.teamlab.com"
s3_region = "eu-west-1"
tsa_server = "http://timestamp.digicert.com"
vcredist_links = {
  '2022': {
    '64': "https://aka.ms/vs/17/release/vc_redist.x64.exe",
    '32': "https://aka.ms/vs/17/release/vc_redist.x86.exe"
  },
  '2015': {
    '64': "https://download.microsoft.com/download/9/3/F/93FCF1E7-E6A4-478B-96E7-D4B285925B00/vc_redist.x64.exe",
    '32': "https://download.microsoft.com/download/9/3/F/93FCF1E7-E6A4-478B-96E7-D4B285925B00/vc_redist.x86.exe"
  },
  '2013': {
    '64': "https://download.microsoft.com/download/2/E/6/2E61CFA4-993B-4DD4-91DA-3737CD5CD6E3/vcredist_x64.exe",
    '32': "https://download.microsoft.com/download/2/E/6/2E61CFA4-993B-4DD4-91DA-3737CD5CD6E3/vcredist_x86.exe"
  }
}
