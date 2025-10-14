#!/usr/bin/env python

import sys
sys.path.append('../')
import os
import base
import dependence
import traceback
import develop

# if (sys.version_info[0] >= 3):
  # unicode = str
  
# host_platform = base.host_platform()
# if (host_platform == 'windows'):
  # import libwindows

base_dir = base.get_script_dir(__file__)

def install_module(path):
  base.print_info('Install: ' + path)
  base.cmd_in_dir(path, 'npm', ['ci'])

def run_module(directory, args=[]):
  base.run_nodejs_in_dir(directory, args)

def find_rabbitmqctl(base_path):
  return base.find_file(os.path.join(base_path, 'RabbitMQ Server'), 'rabbitmqctl.bat')

def restart_win_rabbit():
  # todo maybe restarting is not relevant after many years and versions?
  base.print_info('restart RabbitMQ node to prevent "Erl.exe high CPU usage every Monday morning on Windows" https://groups.google.com/forum/#!topic/rabbitmq-users/myl74gsYyYg')
  rabbitmqctl = find_rabbitmqctl(os.environ['PROGRAMW6432']) or find_rabbitmqctl(os.environ['ProgramFiles(x86)'])
  if rabbitmqctl is not None:
    try:
      # code = libwindows.sudo(unicode(sys.executable), ['net', 'stop', 'rabbitmq'])
      # code = libwindows.sudo(unicode(sys.executable), ['net', 'start', 'rabbitmq'])
      base.cmd_in_dir(base.get_script_dir(rabbitmqctl), 'rabbitmqctl.bat', ['stop_app'])
      base.cmd_in_dir(base.get_script_dir(rabbitmqctl), 'rabbitmqctl.bat', ['start_app'])
    except SystemExit:
      base.print_error('Perhaps Erlang cookies are different: Replace %userprofile%/.erlang.cookie with %WINDIR%/System32/config/systemprofile/.erlang.cookie')
      raise
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
  if base.is_exist(base_dir + '/../../../document-server-integration/web/documentserver-example/nodejs'):
    base.cmd_in_dir(base_dir + '/../../../document-server-integration/web/documentserver-example/nodejs', 'python', ['run-develop.py'])

def start_linux_services():
  base.print_info('Restart MySQL Server')


def update_config(args):
  platform = base.host_platform()
  branch = base.run_command('git rev-parse --abbrev-ref HEAD')['stdout']

  if ("linux" == platform):
  	base.cmd_in_dir(base_dir + '/../../', 'python', ['configure.py', '--branch', branch or 'develop', '--develop', '1', '--module', 'server', '--update', '1', '--update-light', '1', '--clean', '0'] + args)
  else:
  	base.cmd_in_dir(base_dir + '/../../', 'python', ['configure.py', '--branch', branch or 'develop', '--develop', '1', '--module', 'server', '--update', '1', '--update-light', '1', '--clean', '0', '--sql-type', 'mysql', '--db-port', '3306', '--db-name', 'onlyoffice', '--db-user', 'root', '--db-pass', 'onlyoffice'] + args)
  	

def make_start():
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

def make_configure(args):
  base.print_info('Build modules')
  update_config(args)
  base.cmd_in_dir(base_dir + '/../../', 'python', ['make.py'])
def make_install():
  platform = base.host_platform()
  run_integration_example()
  
  base.create_dir(base_dir + '/../../../server/App_Data')
  
  install_module(base_dir + '/../../../server/DocService')
  install_module(base_dir + '/../../../server/Common')
  install_module(base_dir + '/../../../server/FileConverter')

def make_run():
  platform = base.host_platform()
  base.set_env('NODE_ENV', 'development-' + platform)
  base.set_env('NODE_CONFIG_DIR', '../Common/config')
  
  if ("mac" == platform):
    base.set_env('DYLD_LIBRARY_PATH', '../FileConverter/bin/')
  elif ("linux" == platform):
    base.set_env('LD_LIBRARY_PATH', '../FileConverter/bin/')
  
  run_module(base_dir + '/../../../server/DocService', ['sources/server.js'])
  #run_module(base_dir + '/../../../server/DocService', ['sources/gc.js'])
  run_module(base_dir + '/../../../server/FileConverter', ['sources/convertermaster.js'])
  #run_module(base_dir + '/../../../server/SpellChecker', ['sources/server.js'])

def run_docker_server(args = []):
  try:
    make_start()
    develop.build_docker_server()
    make_install()

  except SystemExit:
    input("Ignoring SystemExit. Press Enter to continue...")
    exit(0)
  except KeyboardInterrupt:
    pass
  except:
    input("Unexpected error. " + traceback.format_exc() + "Press Enter to continue...")
	
def run_docker_sdk_web_apps(dir):
  try:
    develop.build_docker_sdk_web_apps(dir)

  except SystemExit:
    input("Ignoring SystemExit. Press Enter to continue...")
    exit(0)
  except KeyboardInterrupt:
    pass
  except:
    input("Unexpected error. " + traceback.format_exc() + "Press Enter to continue...")

def make(args = []):
  try:
    make_start()
    make_configure(args)
    make_install()
    make_run()

  except SystemExit:
    input("Ignoring SystemExit. Press Enter to continue...")
    exit(0)
  except KeyboardInterrupt:
    pass
  except:
    input("Unexpected error. " + traceback.format_exc() + "Press Enter to continue...")

if __name__ == "__main__":
  make(sys.argv[1:])

