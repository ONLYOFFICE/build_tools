import sys
sys.path.append('vendor')
import os
import base
import libwindows
import dependence
import traceback

if (sys.version_info[0] >= 3):
  unicode = str
  
def install_module(path):
  base.print_info('Install: ' + path)
  base.cmd_in_dir(path, 'npm', ['install'])

def run_module(directory, args=[]):
  base.run_nodejs_in_dir(directory, args)

def find_rabbitmqctl(base_path):
  return base.find_file(os.path.join(base_path, 'RabbitMQ Server'), 'rabbitmqctl.bat')

def restart_win_rabbit():
  base.print_info('restart RabbitMQ node to prevent "Erl.exe high CPU usage every Monday morning on Windows" https://groups.google.com/forum/#!topic/rabbitmq-users/myl74gsYyYg')
  rabbitmqctl = find_rabbitmqctl(os.environ['PROGRAMW6432']) or find_rabbitmqctl(os.environ['ProgramFiles(x86)'])
  if rabbitmqctl is not None:
    base.cmd_in_dir(base.get_script_dir(rabbitmqctl), 'rabbitmqctl.bat', ['stop_app'])
    base.cmd_in_dir(base.get_script_dir(rabbitmqctl), 'rabbitmqctl.bat', ['start_app'])
  else:
    base.print_info('Missing rabbitmqctl.bat')

def start_mac_services():
  base.print_info('Restart MySQL Server')
  base.run_process(['mysql.server', 'restart'])
  base.print_info('Start RabbitMQ Server')
  base.run_process(['rabbitmq-server'])
  base.print_info('Start Redis')
  base.run_process(['redis-server'])

def run_integration_example():
  base.cmd_in_dir('../../document-server-integration/web/documentserver-example/nodejs', 'python', ['run-develop.py'])

def check_dependencies():
  checksResult = dependence.CDependencies()
  
  checksResult.append(dependence.check_nodejs())
  checksResult.append(dependence.check_java())
  checksResult.append(dependence.check_erlang())
  checksResult.append(dependence.check_rabbitmq())
  checksResult.append(dependence.check_gruntcli())
  checksResult.append(dependence.check_buildTools())
  checksResult.append(dependence.check_mysqlServer())
  
  if (len(checksResult.install) > 0):
    install_args = ['install.py']
    install_args += checksResult.get_uninstall()
    install_args += checksResult.get_removepath()
    install_args += checksResult.get_install()
    install_args += ['--mysql-path', unicode(checksResult.mysqlPath)]
    code = libwindows.sudo(unicode(sys.executable), install_args)
  
  return dependence.check_MySQLConfig(checksResult.mysqlPath)
  
try:
  base.configure_common_apps()
  dependence.check_pythonPath()
  
  if not dependence.check_vc_components():
    sys.exit()
  if not check_dependencies():
    sys.exit()
  
  platform = base.host_platform()
  if ("windows" == platform):
    restart_win_rabbit()
  elif ("mac" == platform):
    start_mac_services()

  base.print_info('Build modules')
  base.cmd_in_dir('../', 'python', ['configure.py', '--branch', 'develop', '--module', 'develop', '--update', '1', '--update-light', '1', '--clean', '0', '--sdkjs-addon', 'comparison', '--sdkjs-addon', 'content-controls', '--web-apps-addon', 'mobile', '--sdkjs-addon', 'sheet-views'])
  base.cmd_in_dir('../', 'python', ['make.py'])
  
  run_integration_example()
  
  base.create_dir('../../server/App_Data')

  install_module('../../server/DocService')
  install_module('../../server/Common')
  install_module('../../server/FileConverter')
  install_module('../../server/SpellChecker')

  base.set_env('NODE_ENV', 'development-' + platform)
  base.set_env('NODE_CONFIG_DIR', '../../Common/config')

  if ("mac" == platform):
    base.set_env('DYLD_LIBRARY_PATH', '../../FileConverter/bin/')
  elif ("linux" == platform):
    base.set_env('LD_LIBRARY_PATH', '../../FileConverter/bin/')

  run_module('../../server/DocService/sources', ['server.js'])
  run_module('../../server/DocService/sources', ['gc.js'])
  run_module('../../server/FileConverter/sources', ['convertermaster.js'])
  run_module('../../server/SpellChecker/sources', ['server.js'])
except SystemExit:
  input("Ignoring SystemExit. Press Enter to continue...")
except KeyboardInterrupt:
  pass
except:
  input("Unexpected error. " + traceback.format_exc() + "Press Enter to continue...")
