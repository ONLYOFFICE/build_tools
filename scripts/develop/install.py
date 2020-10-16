import sys
sys.path.append('../')
import base
import dependence
import shutil
import optparse

arguments = sys.argv[1:]

parser = optparse.OptionParser()
parser.add_option("--install", action="append", type="string", dest="install", default=[], help="provides install dependencies")
parser.add_option("--uninstall", action="append", type="string", dest="uninstall", default=[], help="provides uninstall dependencies")
parser.add_option("--remove-path", action="append", type="string", dest="remove-path", default=[], help="provides path dependencies to remove")
parser.add_option("--mysql-path", action="store", type="string", dest="mysql-path", default="", help="provides path to mysql")

(options, args) = parser.parse_args(arguments)
configOptions = vars(options)
  
for item in configOptions["uninstall"]:
  dependence.uninstallProgram(item)
for item in configOptions["remove-path"]:
  if (base.is_dir(item) == True):
    shutil.rmtree(item)
for item in configOptions["install"]:
  dependence.installProgram(item)
