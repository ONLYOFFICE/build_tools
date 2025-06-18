import sys
sys.path.append('scripts')
sys.path.append('scripts/develop')
sys.path.append('scripts/develop/vendor')
import base 
import shutil
import optparse
import dependence
import config

arguments = sys.argv[1:]

parser = optparse.OptionParser()
parser.add_option("--install", action="append", type="string", dest="install", default=[], help="provides install dependencies")
parser.add_option("--uninstall", action="append", type="string", dest="uninstall", default=[], help="provides uninstall dependencies")
parser.add_option("--remove-path", action="append", type="string", dest="remove-path", default=[], help="provides path dependencies to remove")

(options, args) = parser.parse_args(arguments)
configOptions = vars(options)

# parse configuration
config.parse()
config.parse_defaults()

for item in configOptions["uninstall"]:
  dependence.uninstallProgram(item)
for item in configOptions["remove-path"]:
  if (base.is_dir(item) == True):
    shutil.rmtree(item)
for item in configOptions["install"]:
  dependence.installProgram(item)
