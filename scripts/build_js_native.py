#!/usr/bin/env python

import config
import base
import os
import build_js

# parse configuration
config.parse()
config.extend_option("jsminimize", "0")

branding = config.option("branding-name")
if ("" == branding):
  branding = "onlyoffice"

base_dir = base.get_script_dir() + "/.."
out_dir = base_dir + "/../native-sdk/examples/win-linux-mac/build/sdkjs"
base.create_dir(out_dir)

build_js.build_sdk_native(base_dir + "/../sdkjs/build")
vendor_dir_src = base_dir + "/../web-apps/vendor/"
sdk_dir_src = base_dir + "/../sdkjs/deploy/sdkjs/"

base.join_scripts([vendor_dir_src + "xregexp/xregexp-all-min.js", 
               vendor_dir_src + "underscore/underscore-min.js",
               base_dir + "/../sdkjs/common/externs/jszip-utils.js",
               base_dir + "/../sdkjs/common/Native/native.js",
               base_dir + "/../sdkjs/common/Native/Wrappers/common.js",
               base_dir + "/../sdkjs/common/Native/jquery_native.js"], 
               out_dir + "/banners_word.js")

base.join_scripts([vendor_dir_src + "xregexp/xregexp-all-min.js", 
                   vendor_dir_src + "underscore/underscore-min.js",
                   base_dir + "/../sdkjs/common/externs/jszip-utils.js",
                   base_dir + "/../sdkjs/common/Native/native.js",
                   base_dir + "/../sdkjs/cell/native/common.js",
                   base_dir + "/../sdkjs/common/Native/jquery_native.js"], 
                   out_dir + "/banners_cell.js")

base.join_scripts([vendor_dir_src + "xregexp/xregexp-all-min.js", 
                   vendor_dir_src + "underscore/underscore-min.js",
                   base_dir + "/../sdkjs/common/externs/jszip-utils.js",
                   base_dir + "/../sdkjs/common/Native/native.js",
                   base_dir + "/../sdkjs/common/Native/Wrappers/common.js",
                   base_dir + "/../sdkjs/common/Native/jquery_native.js"], 
                   out_dir + "/banners_slide.js")

base.create_dir(out_dir + "/word")
base.join_scripts([out_dir + "/banners_word.js", sdk_dir_src + "word/sdk-all-min.js", sdk_dir_src + "word/sdk-all.js"], out_dir + "/word/script.bin")
base.create_dir(out_dir + "/cell")
base.join_scripts([out_dir + "/banners_cell.js", sdk_dir_src + "cell/sdk-all-min.js", sdk_dir_src + "cell/sdk-all.js"], out_dir + "/cell/script.bin")
base.create_dir(out_dir + "/slide")
base.join_scripts([out_dir + "/banners_slide.js", sdk_dir_src + "slide/sdk-all-min.js", sdk_dir_src + "slide/sdk-all.js"], out_dir + "/slide/script.bin")

base.delete_file(out_dir + "/banners_word.js")
base.delete_file(out_dir + "/banners_cell.js")
base.delete_file(out_dir + "/banners_slide.js")
  