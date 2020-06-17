#!/usr/bin/env python

import os
import sys
import optparse

arguments = sys.argv[1:]

parser = optparse.OptionParser()
parser.add_option("--update", action="store", type="string", dest="update", default="1", help="is need update")
parser.add_option("--update-light", action="store", type="string", dest="update-light", default="", help="is need light update (if not exist: clone & go to branch, else: pull)")
parser.add_option("--branch", action="store", type="string", dest="branch", default="master", help="branch all repo [used only if update==1]")
parser.add_option("--clean", action="store", type="string", dest="clean", default="1", help="clean build")
parser.add_option("--module", action="store", type="string", dest="module", default="builder", help="list build modules [desktop | builder]")
parser.add_option("--platform", action="store", type="string", dest="platform", default="native", help="destination platform build [all: windows(win_64, win_32, win_64_xp, win_32_xp), linux(linux_64, linux_32), mac(mac_64); combination: native | win_64 | win_32 | win_64_xp | win_32_xp | linux_64 | mac_64 | ios | android")
parser.add_option("--config", action="store", type="string", dest="config", default="", help="qmake CONFIG addition")
parser.add_option("--qt-dir", action="store", type="string", dest="qt-dir", default="", help="qt (qmake) directory")
parser.add_option("--qt-dir-xp", action="store", type="string", dest="qt-dir-xp", default="", help="qt for Windows XP (qmake) directory")
parser.add_option("--compiler", action="store", type="string", dest="compiler", default="", help="compiler name")
parser.add_option("--no-apps", action="store", type="string", dest="no-apps", default="0", help="disable build desktop apps (qt)")
parser.add_option("--themesparams", action="store", type="string", dest="themesparams", default="", help="presentation themes thumbnails additions")
parser.add_option("--git-protocol", action="store", type="string", dest="git-protocol", default="https", help="presentation themes thumbnails additions")
parser.add_option("--branding", action="store", type="string", dest="branding", default="", help="branding path")
parser.add_option("--branding-name", action="store", type="string", dest="branding-name", default="", help="branding name")
parser.add_option("--branding-url", action="store", type="string", dest="branding-url", default="", help="branding url")
parser.add_option("--sdkjs-addon", action="append", type="string", dest="sdkjs-addons", default=[], help="sdkjs addons")
parser.add_option("--sdkjs-addon-desktop", action="append", type="string", dest="sdkjs-addons-desktop", default=[], help="sdkjs addons desktop")
parser.add_option("--server-addon", action="append", type="string", dest="server-addons", default=[], help="server addons")
parser.add_option("--web-apps-addon", action="append", type="string", dest="web-apps-addons", default=[], help="web-apps addons")
parser.add_option("--sdkjs-plugin", action="append", type="string", dest="sdkjs-plugin", default=["default"], help="sdkjs addons for all products")
parser.add_option("--sdkjs-plugin-server", action="append", type="string", dest="sdkjs-plugin-server", default=["default"], help="sdkjs addons for server")

(options, args) = parser.parse_args(arguments)
configOptions = vars(options)

configStore = open(os.path.dirname(os.path.realpath(__file__)) + "/config","w+")
for option in configOptions:
  writeOption = ""
  if (isinstance(configOptions[option], list)):
  	writeOption = ", ".join(configOptions[option])
  else:
  	writeOption = configOptions[option]

  if ("" != writeOption):
    configStore.write(option + "=\"" + writeOption + "\"\n")

configStore.close()
