import sys
sys.path.append('../')
sys.path.append('vendor')
import os
import base
import dependence
import traceback
import config

platform = base.host_platform()

if ("windows" == platform):
  import libwindows

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
  base.cmd_in_dir('../../../document-server-integration/web/documentserver-example/nodejs', 'python', ['run-develop.py'])

def check_dependencies():
  checksResult = dependence.CDependencies()
  
  checksResult.append(dependence.check_git())
  checksResult.append(dependence.check_nodejs())
  if (platform == 'linux'):
    checksResult.append(dependence.check_npm())
    checksResult.append(dependence.check_curl())
    checksResult.append(dependence.check_7z())
  checksResult.append(dependence.check_java())
  checksResult.append(dependence.check_erlang())
  checksResult.append(dependence.check_rabbitmq())
  checksResult.append(dependence.check_gruntcli())
  if (platform == 'windows'):
    checksResult.append(dependence.check_buildTools())
  checksResult.append(dependence.check_mysqlServer())
  #checksResult.append(dependence.check_postgreSQL())
  
  server_addons = []
  if (config.option("server-addons") != ""):
    server_addons = config.option("server-addons").rsplit(", ")
  if ("server-lockstorage" in server_addons):
    checksResult.append(dependence.check_redis())
  
  if (len(checksResult.install) > 0):
    install_args = ['install.py']
    install_args += checksResult.get_uninstall()
    install_args += checksResult.get_removepath()
    install_args += checksResult.get_install()
    install_args += ['--mysql-path', unicode(checksResult.mysqlPath)]
    if (platform == 'windows'):
      code = libwindows.sudo(unicode(sys.executable), install_args)
    else:
      dependence.get_updates()
      base.cmd_in_dir('./', 'python', ['install.py'] + install_args[1:])
  
  return dependence.check_MySQLConfig(checksResult.mysqlPath)
  #return dependence.check_postgreConfig(checksResult.postgrePath)

def make(args = []):
  try:
    base.cmd_in_dir('../../', 'python', ['configure.py', '--branch', 'develop', '--develop', '1', '--module', 'server', '--update', '1', '--update-light', '1', '--clean', '0'] + args)
    
    # parse configuration
    config.parse()
    # correct defaults (the branding repo is already updated)
    config.parse_defaults()
    
    base.configure_common_apps()
  
    if ("mac" == platform):
      start_mac_services()
    else:
      if ("windows" == platform):
        dependence.check_pythonPath()
        dependence.check_gitPath()
        if not dependence.check_vc_components():
          sys.exit()
        if not check_dependencies():
          sys.exit()
        restart_win_rabbit()
      else:
        if not check_dependencies():
          sys.exit()
    
    base.print_info('Build modules')
    base.cmd_in_dir('../../', 'python', ['make.py'])
  
    run_integration_example()
  
    base.create_dir('../../../server/App_Data')

    install_module('../../../server/DocService')
    install_module('../../../server/Common')
    install_module('../../../server/FileConverter')
    install_module('../../../server/SpellChecker')

    base.set_env('NODE_ENV', 'development-' + platform)
    base.set_env('NODE_CONFIG_DIR', '../../Common/config')

    if ("mac" == platform):
      base.set_env('DYLD_LIBRARY_PATH', '../../FileConverter/bin/')
    elif ("linux" == platform):
      base.set_env('LD_LIBRARY_PATH', '../../FileConverter/bin/')

    run_module('../../../server/DocService/sources', ['server.js'])
    run_module('../../../server/DocService/sources', ['gc.js'])
    run_module('../../../server/FileConverter/sources', ['convertermaster.js'])
    run_module('../../../server/SpellChecker/sources', ['server.js'])
  except SystemExit:
    input("Ignoring SystemExit. Press Enter to continue...")
    exit(0)
  except KeyboardInterrupt:
    pass
  except:
    input("Unexpected error. " + traceback.format_exc() + "Press Enter to continue...")
