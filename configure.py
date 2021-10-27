#!/usr/bin/env python

import os
import sys
import optparse

arguments = sys.argv[1:]

parser = optparse.OptionParser()
parser.add_option("--update", action="store", type="string", dest="update", default="1", help="defines whether it's necessary to update/clone repos. If it's set to true (1 === true), build_tools automatically get the necessary subrepos. If it's set to false (0 === false), you should define which ones to use")
parser.add_option("--update-light", action="store", type="string", dest="update-light", default="", help="performs pull/clone without switching branches, can be used only if update is true.")
parser.add_option("--branch", action="store", type="string", dest="branch", default="master", help="branch/tag name, used only if update is true and update_light is not used. Updates/clones all the repos and switches the branch to the proper one deleting all the local changes")
parser.add_option("--clean", action="store", type="string", dest="clean", default="1", help="defines whether to build everything anew")
parser.add_option("--module", action="store", type="string", dest="module", default="builder", help="defines what modules to build. You can specify several of them, e.g. --module 'core desktop builder server mobile'")
parser.add_option("--develop", action="store", type="string", dest="develop", default="0", help="defines develop mode")
parser.add_option("--beta", action="store", type="string", dest="beta", default="0", help="defines beta mode")
parser.add_option("--platform", action="store", type="string", dest="platform", default="native", help="defines the destination platform for your build ['win_64', 'win_32', 'win_64_xp', 'win_32_xp', 'linux_64', 'linux_32', 'mac_64', 'ios', 'android_arm64_v8a', 'android_armv7', 'android_x86', 'android_x86_64'; combinations: 'native': your current system (windows/linux/mac only); 'all': all available systems; 'windows': win_64 win_32 win_64_xp win_32_xp; 'linux': linux_64 linux_32; 'mac': mac_64; 'android': android_arm64_v8a android_armv7 android_x86 android_x86_64]")
parser.add_option("--config", action="store", type="string", dest="config", default="", help="provides ability to specify additional parameters for qmake")
parser.add_option("--qt-dir", action="store", type="string", dest="qt-dir", default="", help="defines qmake directory path. qmake can be found in qt-dir/compiler/bin directory")
parser.add_option("--qt-dir-xp", action="store", type="string", dest="qt-dir-xp", default="", help="defines qmake directory path for Windows XP. qmake can be found in 'qt-dir/compiler/bin directory")
parser.add_option("--external-folder", action="store", type="string", dest="external-folder", default="", help="defines a directory with external folder")
parser.add_option("--sql-type", action="store", type="string", dest="sql-type", default="postgres", help="defines the sql type wich will be used")
parser.add_option("--db-port", action="store", type="string", dest="db-port", default="5432", help="defines the sql db-port wich will be used")
parser.add_option("--db-user", action="store", type="string", dest="db-user", default="onlyoffice", help="defines the sql db-user wich will be used")
parser.add_option("--db-pass", action="store", type="string", dest="db-pass", default="onlyoffice", help="defines the sql db-pass wich will be used")
parser.add_option("--compiler", action="store", type="string", dest="compiler", default="", help="defines compiler name. It is not recommended to use it as it's defined automatically (msvc2015, msvc2015_64, gcc, gcc_64, clang, clang_64, etc)")
parser.add_option("--no-apps", action="store", type="string", dest="no-apps", default="0", help="disables building desktop apps that use qt")
parser.add_option("--themesparams", action="store", type="string", dest="themesparams", default="", help="provides settings for generating presentation themes thumbnails")
parser.add_option("--git-protocol", action="store", type="string", dest="git-protocol", default="https", help="can be used only if update is set to true - 'https', 'ssh'")
parser.add_option("--branding", action="store", type="string", dest="branding", default="", help="provides branding path")
parser.add_option("--branding-name", action="store", type="string", dest="branding-name", default="", help="provides branding name")
parser.add_option("--branding-url", action="store", type="string", dest="branding-url", default="", help="provides branding url")
parser.add_option("--sdkjs-addon", action="append", type="string", dest="sdkjs-addons", default=[], help="provides sdkjs addons")
parser.add_option("--sdkjs-addon-desktop", action="append", type="string", dest="sdkjs-addons-desktop", default=[], help="provides sdkjs addons for desktop")
parser.add_option("--server-addon", action="append", type="string", dest="server-addons", default=[], help="provides server addons")
parser.add_option("--web-apps-addon", action="append", type="string", dest="web-apps-addons", default=[], help="provides web-apps addons")
parser.add_option("--sdkjs-plugin", action="append", type="string", dest="sdkjs-plugin", default=["default"], help="provides plugins for server-based and desktop versions of the editors")
parser.add_option("--sdkjs-plugin-server", action="append", type="string", dest="sdkjs-plugin-server", default=["default"], help="provides plugins for server-based version of the editors")
parser.add_option("--features", action="store", type="string", dest="features", default="", help="native features (config addon)")
parser.add_option("--vs-version", action="store", type="string", dest="vs-version", default="2015", help="version of visual studio")
parser.add_option("--vs-path", action="store", type="string", dest="vs-path", default="", help="path to vcvarsall")
parser.add_option("--siteUrl", action="store", type="string", dest="siteUrl", default="127.0.0.1", help="site url")

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
