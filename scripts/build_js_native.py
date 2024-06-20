#!/usr/bin/env python

import base
import build_js
import config
import optparse
import sys

arguments = sys.argv[1:]
parser = optparse.OptionParser()
parser.add_option("--output", 
                  action="store", type="string", dest="output",
                  help="Directory for output the build result")
parser.add_option("--write-version",
                  action="store_true", dest="write_version", default=False,
                  help="Create version file of build")
parser.add_option("--minimize",
                  action="store", type="string", dest="minimize", default="0",
                  help="Is minimized version")
(options, args) = parser.parse_args(arguments)

def write_version_files(output_dir):
  if (base.is_dir(output_dir)):
    last_version_tag = base.run_command('git describe --abbrev=0 --tags')['stdout']
    version_numbers=last_version_tag.replace('v', '').split('.')
    major=(version_numbers[0:1] or ('0',))[0]
    minor=(version_numbers[1:2] or ('0',))[0]
    maintenance=(version_numbers[2:3] or ('0',))[0]
    build=(version_numbers[3:4] or ('0',))[0]
    full_version='%s.%s.%s.%s' % (major, minor, maintenance, build)

    for name in ['word', 'cell', 'slide']:
      base.writeFile(output_dir + '/%s/sdk.version' % name, full_version)

# parse configuration
config.parse()
config.parse_defaults()

isMinimize = False
if ("1" == options.minimize or "true" == options.minimize):
  isMinimize = True
config.set_option("jsminimize", "disable")

branding = config.option("branding-name")
if ("" == branding):
  branding = "onlyoffice"

base_dir = base.get_script_dir() + "/.."
out_dir = base_dir + "/../native-sdk/examples/win-linux-mac/build/sdkjs"

if (options.output):
  out_dir = options.output

base.create_dir(out_dir)

build_js.build_sdk_native(base_dir + "/../sdkjs/build", isMinimize)
vendor_dir_src = base_dir + "/../web-apps/vendor/"
sdk_dir_src = base_dir + "/../sdkjs/deploy/sdkjs/"

prefix_js = [
  vendor_dir_src + "xregexp/xregexp-all-min.js", 
  base_dir + "/../sdkjs/common/Native/native.js",
  base_dir + "/../sdkjs-native/common/common.js",
  base_dir + "/../sdkjs/common/Native/jquery_native.js"
]

postfix_js = [
  base_dir + "/../sdkjs/common/libfont/engine/fonts_native.js",
  base_dir + "/../sdkjs/common/Charts/ChartStyles.js"
]

base.join_scripts(prefix_js, out_dir + "/banners.js")

base.create_dir(out_dir + "/word")
base.join_scripts([out_dir + "/banners.js", sdk_dir_src + "word/sdk-all-min.js", sdk_dir_src + "word/sdk-all.js"] + postfix_js, out_dir + "/word/script.bin")
base.create_dir(out_dir + "/cell")
base.join_scripts([out_dir + "/banners.js", sdk_dir_src + "cell/sdk-all-min.js", sdk_dir_src + "cell/sdk-all.js"] + postfix_js, out_dir + "/cell/script.bin")
base.create_dir(out_dir + "/slide")
base.join_scripts([out_dir + "/banners.js", sdk_dir_src + "slide/sdk-all-min.js", sdk_dir_src + "slide/sdk-all.js"] + postfix_js, out_dir + "/slide/script.bin")

base.delete_file(out_dir + "/banners.js")

# Write sdk version mark file if needed
if (options.write_version):
  write_version_files(out_dir)