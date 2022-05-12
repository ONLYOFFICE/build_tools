#!/usr/bin/env python

import sys
sys.path.append('../')
import os
import base
import dependence
import traceback

def install_module(path):
  base.print_info('Install: ' + path)
  base.cmd_in_dir(path, 'npm', ['ci'])

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
#  base.print_info('Start Redis')
#  base.run_process(['redis-server'])

def start_linux_services():
  base.print_info('Restart MySQL Server')
  os.system('sudo service mysql restart')
  base.print_info('Restart RabbitMQ Server')
  os.system('sudo service rabbitmq-server restart')
  
def run_integration_example():
  base.cmd_in_dir('../../../document-server-integration/web/documentserver-example/nodejs', 'python', ['run-develop.py'])

def start_linux_services():
  base.print_info('Restart MySQL Server')
  
def make(args = []):
  try:
    base.configure_common_apps()
    
    platform = base.host_platform()
    if ("windows" == platform):
      dependence.check_pythonPath()
      dependence.check_gitPath()
      restart_win_rabbit()
    elif ("mac" == platform):
      start_mac_services()
    elif ("linux" == platform):
      start_linux_services()
      

    branch = base.run_command('git rev-parse --abbrev-ref HEAD')['stdout']
    
    base.print_info('Build modules')
    if ("linux" == platform):
    	base.cmd_in_dir('../../', 'python', ['configure.py', '--branch', branch or 'develop', '--develop', '1', '--module', 'server', '--update', '1', '--update-light', '1', '--clean', '0'] + args)
    else:
    	base.cmd_in_dir('../../', 'python', ['configure.py', '--branch', branch or 'develop', '--develop', '1', '--module', 'server', '--update', '1', '--update-light', '1', '--clean', '0', '--sql-type', 'mysql', '--db-port', '3306', '--db-user', 'root', '--db-pass', 'onlyoffice'] + args)
    	
    base.cmd_in_dir('../../', 'python', ['make.py'])
  
    run_integration_example()
  
    base.create_dir('../../../server/App_Data')

    install_module('../../../server/DocService')
    install_module('../../../server/Common')
    install_module('../../../server/FileConverter')

    base.set_env('NODE_ENV', 'development-' + platform)
    base.set_env('NODE_CONFIG_DIR', '../Common/config')

    if ("mac" == platform):
      base.set_env('DYLD_LIBRARY_PATH', '../FileConverter/bin/')
    elif ("linux" == platform):
      base.set_env('LD_LIBRARY_PATH', '../FileConverter/bin/')

    run_module('../../../server/DocService', ['sources/server.js'])
#    run_module('../../../server/DocService', ['sources/gc.js'])
    run_module('../../../server/FileConverter', ['sources/convertermaster.js'])
#    run_module('../../../server/SpellChecker', ['sources/server.js'])
  except SystemExit:
    input("Ignoring SystemExit. Press Enter to continue...")
    exit(0)
  except KeyboardInterrupt:
    pass
  except:
    input("Unexpected error. " + traceback.format_exc() + "Press Enter to continue...")

if __name__ == "__main__":
  make(sys.argv[1:])

