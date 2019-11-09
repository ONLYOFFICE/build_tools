import os
import sys
import optparse

arguments = sys.argv[1:]

parser = optparse.OptionParser()
parser.add_option("--update", action="store", type="string", dest="update", default="1", help="is need update")
parser.add_option("--branch", action="store", type="string", dest="branch", default="master", help="branch all repo [used only if update==1]")
parser.add_option("--clean", action="store", type="string", dest="clean", default="1", help="clean build")
parser.add_option("--module", action="store", type="string", dest="module", default="builder", help="list build modules [desktop | builder]")
parser.add_option("--platform", action="store", type="string", dest="platform", default="native", help="destination platform build [all: windows(win_64, win_32, win_64_xp, win_32_xp), linux(linux_64, linux_32), mac(mac_64); combination: native | win_64 | win_32 | win_64_xp | win_32_xp | linux_64 | mac_64 | ios | android")
parser.add_option("--config", action="store", type="string", dest="config", default="", help="qmake CONFIG addition")
parser.add_option("--qt-dir", action="store", type="string", dest="qt-dir", default="", help="qt (qmake) directory")
parser.add_option("--compiler", action="store", type="string", dest="compiler", default="", help="compiler name")
parser.add_option("--no-apps", action="store", type="string", dest="no-apps", default="0", help="disable build desktop apps (qt)")
parser.add_option("--themesparams", action="store", type="string", dest="themesparams", default="", help="presentation themes thumbnails additions")

(options, args) = parser.parse_args(arguments)
configOptions = vars(options)

configStore = open(os.path.dirname(os.path.realpath(__file__)) + "/config","w+")
for option in configOptions:
	configStore.write(option + "=\"" + configOptions[option] + "\"\n")

configStore.close()