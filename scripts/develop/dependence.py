import sys
sys.path.append('vendor')
sys.path.append('..')
import os
import base
import subprocess
import config

host_platform = base.host_platform()

if (sys.version_info[0] >= 3):
  unicode = str

if (host_platform == 'windows'):
  import libwindows
  if (sys.version_info[0] >= 3):
    import winreg
  else:
    import _winreg as winreg

class CDependencies:
  def __init__(self):
    self.install = []
    self.uninstall = []
    self.removepath = []
    self.sqlPath = ''

  def append(self, oCdependencies):
    for item in oCdependencies.install:
      self.append_install(item)
    for item in oCdependencies.uninstall:
      self.append_uninstall(item)
    for item in oCdependencies.removepath:
      self.append_removepath(item)
    
    if (oCdependencies.sqlPath != ''):
      self.sqlPath = oCdependencies.sqlPath

  def append_install(self, item):
    if (item not in self.install):
      self.install.append(item)

  def append_uninstall(self, item):
    if (item not in self.uninstall):
      self.uninstall.append(item)

  def append_removepath(self, item):
    if (item not in self.removepath):
      self.removepath.append(item)

  def get_install(self):
    res = []
    for item in self.install:
      res += ['--install', item]
    return res

  def get_uninstall(self):
    res = []
    for item in self.uninstall:
      res += ['--uninstall', item]
    return res

  def get_removepath(self):
    res = []
    for item in self.removepath:
      res += ['--remove-path', item]
    return res

def check__docker_dependencies():
  if (host_platform == 'windows' and not check_vc_components()):
    return False
  if (host_platform == 'mac'):
    return True

  checksResult = CDependencies()
  checksResult.append(check_nodejs())
  checksResult.append(check_7z())
  if (len(checksResult.install) > 0):
    install_args = ['install.py']
    install_args += checksResult.get_uninstall()
    install_args += checksResult.get_removepath()
    install_args += checksResult.get_install()
    base_dir = base.get_script_dir(__file__)
    install_args[0] = './scripts/develop/' + install_args[0]
    if (host_platform == 'windows'):
      code = libwindows.sudo(unicode(sys.executable), install_args)
    elif (host_platform == 'linux'):
      get_updates()
      base.cmd_in_dir(base_dir + "/../../", 'python', install_args, False)

def check_dependencies():
  if (host_platform == 'windows' and not check_vc_components()):
    return False
  if (host_platform == 'mac'):
    return True

  checksResult = CDependencies()

  checksResult.append(check_git())
  if (host_platform == 'linux'):
    checksResult.append(check_curl())
    checksResult.append(check_nodejs())
    checksResult.append(check_npm())
    checksResult.append(check_7z())

  checksResult.append(check_java())
  checksResult.append(check_erlang())
  checksResult.append(check_rabbitmq())
  checksResult.append(check_gruntcli())

  if (host_platform == 'windows'):
    checksResult.append(check_nodejs())

  print('\n=== Database Check ===')
  sql_type = config.option("sql-type")
  print('SQL type: ' + sql_type)
  print('Host platform: ' + host_platform)
  print('DB host: ' + config.option("db-host"))
  print('DB port: ' + config.option("db-port"))
  print('DB name: ' + config.option("db-name"))
  print('DB user: ' + config.option("db-user"))
  
  if (sql_type == 'mysql' and host_platform == 'windows'):
    print('\nCalling check_mysqlServer()...')
    checksResult.append(check_mysqlServer())
  else:
    print('\nCalling check_postgreSQL()...')
    checksResult.append(check_postgreSQL())

  server_addons = []
  if (config.option("server-addons") != ""):
    server_addons = config.option("server-addons").rsplit(", ")
  if ("server-lockstorage" in server_addons):
    checksResult.append(check_redis())

  if (len(checksResult.install) > 0):
    install_args = ['install.py']
    install_args += checksResult.get_uninstall()
    install_args += checksResult.get_removepath()
    install_args += checksResult.get_install()
    install_args[0] = './scripts/develop/' + install_args[0]
    if (host_platform == 'windows'):
      code = libwindows.sudo(unicode(sys.executable), install_args)
    elif (host_platform == 'linux'):
      get_updates()
      base.cmd('python', install_args, False)

  check_npmPath()
  if (config.option("sql-type") == 'mysql' and host_platform == 'windows'):
    return check_MySQLConfig(checksResult.sqlPath)
  return check_postgreConfig(checksResult.sqlPath)

def check_pythonPath():
  path = base.get_env('PATH')
  if (path.find(sys.exec_prefix) == -1):
    base.set_env('PATH', sys.exec_prefix + os.pathsep + path)

def check_npmPath():
  if (host_platform != 'windows'):
    return None
  path = base.get_env('PATH')
  npmPath = os.environ['AppData'] + '\\npm'
  if (path.find(npmPath) == -1):
    base.set_env('PATH', npmPath + os.pathsep + path)

def check_gitPath():
  path = base.get_env('PATH')
  gitExecPath = base.find_file(os.path.join(os.environ['PROGRAMW6432'], 'Git\\cmd'), 'git.exe') or base.find_file(os.path.join(os.environ['ProgramFiles(x86)'], 'Git\\cmd'), 'git.exe')
  gitDir = base.get_script_dir(gitExecPath)
  if (path.find(gitDir) == -1):
    base.set_env('PATH', gitDir + os.pathsep + path)

def check_git():
  dependence = CDependencies()
  base.print_info('Check installed Git')

  result = base.run_command('git --version')['stderr']

  if (result != ''):
    print('Git not found')
    dependence.append_install('Git')
    return dependence

  print('Git is installed')
  return dependence

def check_nodejs():
  dependence = CDependencies()

  isNeedReinstall = False
  base.print_info('Check installed Node.js')
  nodejs_version = base.run_command('node -v')['stdout']
  if (nodejs_version == ''):
    print('Node.js not found')
    if (host_platform == 'windows'):
      dependence.append_install('Node.js')
    elif (host_platform == 'linux'):
      dependence.append_install('NodeJs')
    return dependence

  nodejs_cur_version_major = int(nodejs_version.split('.')[0][1:])
  nodejs_cur_version_minor = int(nodejs_version.split('.')[1])
  print('Installed Node.js version: ' + nodejs_version[1:])
  nodejs_min_version = '18'
  nodejs_min_version_minor  = 0
  major_minor_min_version = nodejs_min_version.split('.')
  nodejs_min_version_major = int(major_minor_min_version[0])
  if len(major_minor_min_version) > 1:
    nodejs_min_version_minor = int(major_minor_min_version[1])
  nodejs_max_version = ""
  nodejs_max_version_minor = float("inf")
  major_minor_max_version = nodejs_max_version.split('.')
  # nodejs_max_version_major = int(major_minor_max_version[0])
  nodejs_max_version_major = float("inf")
  if len(major_minor_max_version) > 1:
    nodejs_max_version_minor = int(major_minor_max_version[1])

  if (nodejs_min_version_major > nodejs_cur_version_major or nodejs_cur_version_major > nodejs_max_version_major):
    isNeedReinstall = True
  elif (nodejs_min_version_major == nodejs_cur_version_major):
    if (nodejs_min_version_minor > nodejs_cur_version_minor):
      isNeedReinstall = True
  elif (nodejs_cur_version_major == nodejs_max_version_major):
    if (nodejs_cur_version_minor > nodejs_max_version_minor):
      isNeedReinstall = True

  if (True == isNeedReinstall):
    print('Installed Node.js version must be 18 or higher.')
    if (host_platform == 'windows'):
      dependence.append_uninstall('Node.js')
      dependence.append_install('Node.js')
    elif (host_platform == 'linux'):
      dependence.append_uninstall('nodejs')
      dependence.append_install('NodeJs')

    return dependence

  print('Installed Node.js is valid')
  return dependence

def check_java():
  dependence = CDependencies()

  base.print_info('Check installed Java')
  java_info = base.run_command('java -version')['stderr']

  version_pos = java_info.find('version "')
  java_v = 0
  if (version_pos != -1):
    try:
      java_v = float(java_info[version_pos + len('version "'): version_pos + len('version "') + 2])
    except:
      pass

  if (java_info.find('64-Bit') != -1 and java_v >= 11):
    print('Installed Java is valid')
  else: 
    print('Requires Java version 11+ x64-bit')
    dependence.append_install('Java')
    if (version_pos != -1):
      dependence.append_uninstall('Java')
  
  return dependence

def get_erlang_path_to_bin():
  erlangPath = ''
  if (host_platform == 'windows'):
    erlangPath = os.getenv("ERLANG_HOME", "")
    if (erlangPath != ""):
      erlangPath += "\\bin"
  return erlangPath
def check_erlang():
  dependence = CDependencies()
  base.print_info('Check installed Erlang')

  erlangBitness = ""
  erlang_path_home = get_erlang_path_to_bin()
  if base.is_exist(erlang_path_home) == False and host_platform == 'windows':
    dependence.append_uninstall('Erlang')
    dependence.append_uninstall('RabbitMQ')
    return dependence
  
  if ("" != erlang_path_home or host_platform != 'windows'):
    erlangBitness = base.run_command_in_dir(erlang_path_home, 'erl -eval "erlang:display(erlang:system_info(wordsize)), halt()." -noshell')['stdout']
  
  if (erlangBitness == '8'):
    print("Installed Erlang is valid")
    return dependence

  print('Need Erlang with bitness x64')

  if (host_platform == 'windows'):
    dependence.append_removepath(os.environ['AppData'] + '\\RabbitMQ\\db')
    dependence.append_uninstall('Erlang')
    dependence.append_uninstall('RabbitMQ')
  else:
    dependence.append_uninstall('erlang')
    dependence.append_uninstall('rabbitmq-server')
  dependence.append_install('Erlang')
  dependence.append_install('RabbitMQ')

  return dependence

def check_rabbitmq():
  dependence = CDependencies()
  base.print_info('Check installed RabbitMQ')

  if (host_platform == 'windows'):
    result = base.run_command('sc query RabbitMQ')['stdout']
    if (result.find('RabbitMQ') != -1):
      print('RabbitMQ is installed')
      return dependence
  elif (host_platform == 'linux'):
    # Try service command first
    command_result = base.run_command('service rabbitmq-server status')
    result = command_result['stdout']
    
    # Log command results
    print('Checking RabbitMQ with service command...')
    print('Command: service rabbitmq-server status')
    print('stdout: ' + (result if result else '[EMPTY]'))
    if command_result['stderr']:
      print('stderr: ' + command_result['stderr'])
    print('Return code: ' + str(command_result['returncode']))
    
    # If service command failed or returned empty, try systemctl
    if (result == '' or command_result['returncode'] != 0):
      print('\nTrying systemctl command...')
      systemctl_result = base.run_command('systemctl status rabbitmq-server')
      print('Command: systemctl status rabbitmq-server')
      print('stdout: ' + (systemctl_result['stdout'] if systemctl_result['stdout'] else '[EMPTY]'))
      if systemctl_result['stderr']:
        print('stderr: ' + systemctl_result['stderr'])
      print('Return code: ' + str(systemctl_result['returncode']))
      
      # Update result if systemctl worked
      if systemctl_result['stdout']:
        result = systemctl_result['stdout']
        command_result = systemctl_result
    
    # If still no result, try direct process check
    if (result == ''):
      print('\nTrying direct process check...')
      ps_result = base.run_command('ps aux | grep -i rabbitmq | grep -v grep')
      print('Command: ps aux | grep -i rabbitmq | grep -v grep')
      print('stdout: ' + (ps_result['stdout'] if ps_result['stdout'] else '[EMPTY]'))
      print('Return code: ' + str(ps_result['returncode']))
      
      # Check if rabbitmq process is running
      if ps_result['stdout']:
        result = ps_result['stdout']
        print('RabbitMQ process found: ' + result[:100] + '...' if len(result) > 100 else result)
    
    # Additional diagnostic checks
    if (result == ''):
      print('\nPerforming additional diagnostic checks...')
      
      # Check current user
      whoami_result = base.run_command('whoami')
      print('Current user: ' + whoami_result['stdout'])
      
      # Check for RabbitMQ binaries
      which_result = base.run_command('which rabbitmqctl')
      if which_result['stdout']:
        print('RabbitMQ binary found at: ' + which_result['stdout'])
        
        # Try rabbitmqctl status
        rabbitmqctl_result = base.run_command('rabbitmqctl status')
        print('\nTrying rabbitmqctl status...')
        print('stdout: ' + (rabbitmqctl_result['stdout'][:200] + '...' if len(rabbitmqctl_result['stdout']) > 200 else rabbitmqctl_result['stdout']))
        if rabbitmqctl_result['stderr']:
          print('stderr: ' + rabbitmqctl_result['stderr'])
      else:
        print('RabbitMQ binary (rabbitmqctl) not found in PATH')
      
      # Check for permission issues
      if (command_result['returncode'] == 126):
        print('\nPermission denied error (code 126).')
        print('You may need to run this script with elevated privileges (sudo).')
      elif (command_result['returncode'] == 127):
        print('\nCommand not found error (code 127).')
        print('The service command may not be available or RabbitMQ may not be installed.')
      elif (command_result['returncode'] == 1):
        print('\nService command failed (code 1).')
        print('This could mean RabbitMQ service is not installed or not running.')
      
      # Check common RabbitMQ installation paths
      print('\nChecking common RabbitMQ paths...')
      common_paths = ['/usr/lib/rabbitmq', '/opt/rabbitmq', '/etc/rabbitmq', '/var/lib/rabbitmq']
      for path in common_paths:
        if base.is_dir(path):
          print('Found RabbitMQ directory: ' + path)
    
    if (result != ''):
      print('\nInstalled RabbitMQ is valid')
      return dependence

  print('RabbitMQ not found')

  if (host_platform == 'windows'):
    dependence.append_removepath(os.environ['AppData'] + '\\RabbitMQ\\db')
    dependence.append_uninstall('Erlang')
    dependence.append_uninstall('RabbitMQ')
  else:
    dependence.append_uninstall('erlang')
    dependence.append_uninstall('rabbitmq-server')
  dependence.append_install('Erlang')
  dependence.append_install('RabbitMQ')

  return dependence

def find_redis(base_path):
  return base.find_file(os.path.join(base_path, 'Redis'), 'redis-cli.exe')

def check_redis():
  dependence = CDependencies()
  base.print_info('Check Redis server')

  if (host_platform == 'windows'):
    if (len(get_programUninstalls('Redis on Windows')) == 0):
      print('Redis not found')
      dependence.append_install('RedisServer')
      return dependence

    checkService = base.run_command('sc query Redis')['stdout']
    if (checkService.find('Redis') != -1) and (checkService.find('STOPPED') != -1):
      print('Installed Redis is not valid')
      dependence.append_uninstall('Redis on Windows')
      dependence.append_install('RedisServer')
      return dependence

    redis_cli = find_redis(os.environ['PROGRAMW6432']) or find_redis(os.environ['ProgramFiles(x86)'])
  elif (host_platform == 'linux'):
    checkService = base.run_command('service redis-server status')['stderr']
    if (checkService == ''):
      print('Redis not found')
      dependence.append_install('Redis')
      return dependence
    redis_cli = 'redis-cli'

  if (redis_cli == None):
    print('Redis not found in default folder')
    dependence.append_uninstall('Redis on Windows')
    dependence.append_install('RedisServer')
    return dependence

  result = base.run_command('"' + redis_cli + '"' + ' info server')['stdout']
  if (result == ''):
    print('Redis client is invalid')
    if (host_platform == 'windows'):
      dependence.append_uninstall('Redis on Windows')
      dependence.append_install('RedisServer')
    else:
      dependence.append_uninstall('redis-server')
      dependence.append_install('Redis')
    return dependence

  info = result.split('tcp_port:')[1]
  tcp_port = info.split('\r', 1)[0]
  config_port = install_params['Redis'].split('PORT=', 1)[1]
  config_port = config_port.split(' ', 1)[0]
  if (tcp_port != config_port):
    print('Invalid Redis port, need reinstall')
    if (host_platform == 'windows'):
      dependence.append_uninstall('Redis on Windows')
      dependence.append_install('RedisServer')
    else:
      dependence.append_uninstall('redis-server')
      dependence.append_install('Redis')
    return dependence

  print('Installed Redis is valid')
  return dependence

def check_npm():
  dependence = CDependencies()
  base.print_info('Check installed Npm')

  result = base.run_command('npm')['stdout']
  if (result != ''):
    print('Npm is installed')
    return dependence

  print('Npm not found')
  dependence.append_install('Npm')

  return dependence

def check_vc_components():
  base.print_info('Check Visual C++ components')
  result = True
  if (len(get_programUninstalls('Microsoft Visual C++ 2015-')) == 0):
    print('Microsoft Visual C++ 2015-20** Redistributable (x64) not found')
    result = installProgram('VC2019x64') and result


  print('Installed Visual C++ components is valid')
  return result

def check_gruntcli():
  dependence = CDependencies()

  base.print_info('Check installed Grunt-Cli')
  result = base.run_command('npm list -g --depth=0')['stdout']

  if (result.find('grunt-cli') == -1):
    print('Grunt-Cli not found')
    dependence.append_install('GruntCli')
    return dependence

  print('Installed Grunt-Cli is valid')
  return dependence

def check_buildTools():
  dependence = CDependencies()

  base.print_info('Check installed Build Tools')
  result = base.run_command('vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property DisplayName')['stdout']
  if (result == ''):
    print('Build Tools not found')
    dependence.append_install('BuildTools')
  else:
    print('Installed Build Tools is valid')

  return dependence

def check_curl():
  dependence = CDependencies()
  base.print_info('Check installed Curl')

  if (base.run_command('curl -V')['stdout'] == ''):
    dependence.append_install('Curl')

  return dependence

def check_7z():
  dependence = CDependencies()
  base.print_info('Check installed 7z')

  if (base.run_command('7z')['stdout'] == ''):
    dependence.append_install('7z')

  return dependence

def check_gh():
  base.print_info('Check installed GitHub CLI')

  result = base.run_command('gh --version')['stdout']

  if (result == ''):
    base.print_info('GitHub CLI not found')
	# ToDo install
    return False

  base.print_info('GitHub CLI is installed')
  return True

def check_gh_auth():
  base.print_info('Check auth for GitHub CLI')

  result = base.run_command('gh auth status')['stderr']

  if (result.find('not logged') != -1):
    base.print_info('GitHub CLI not logged in to github')
    return False

  base.print_info('GitHub CLI logged in to github')
  return True

def get_mysql_path_to_bin(mysqlPath = ''):
  if (host_platform == 'windows'):
    if (mysqlPath == ''):
      mysqlPath = os.environ['PROGRAMW6432'] + '\\MySQL\\MySQL Server 8.0\\'
    mysqlPath += 'bin'
  return mysqlPath
def get_mysqlLoginString():
  return 'mysql -u ' + config.option("db-user") + ' -p' + config.option("db-pass")
def get_mysqlServersInfo():
  arrInfo = []

  try:
    aReg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    aKey = winreg.OpenKey(aReg, "SOFTWARE\\", 0, winreg.KEY_READ | winreg.KEY_WOW64_32KEY)

    asubkey = winreg.OpenKey(aKey, 'MySQL AB')
    count_subkey = winreg.QueryInfoKey(asubkey)[0]

    for i in range(count_subkey):
      MySQLsubkey_name = winreg.EnumKey(asubkey, i)
      if (MySQLsubkey_name.find('MySQL Server') != - 1):
        MySQLsubkey = winreg.OpenKey(asubkey, MySQLsubkey_name)
        dictInfo = {}
        dictInfo['Location']  = winreg.QueryValueEx(MySQLsubkey, 'Location')[0]
        dictInfo['Version'] = winreg.QueryValueEx(MySQLsubkey, 'Version')[0]
        dictInfo['DataLocation'] = winreg.QueryValueEx(MySQLsubkey, 'DataLocation')[0]
        arrInfo.append(dictInfo)
  except:
    pass

  return arrInfo
def check_mysqlServer():
  base.print_info('Check MySQL Server')
  dependence = CDependencies()
  mysqlLoginSrt = get_mysqlLoginString()
  print('MySQL login string: ' + mysqlLoginSrt)
  connectionString = mysqlLoginSrt + ' -e "SHOW GLOBAL VARIABLES LIKE ' + r"'PORT';" + '"'
  print('Connection string: ' + connectionString)

  if (host_platform != 'windows'):
    print('\nTesting MySQL connection...')
    result = os.system(mysqlLoginSrt + ' -e "exit"')
    print('Connection test result code: ' + str(result))
    
    if (result == 0):
      connectionResult = base.run_command(connectionString)
      print('Port check stdout: ' + connectionResult['stdout'])
      if connectionResult['stderr']:
        print('Port check stderr: ' + connectionResult['stderr'])
      
      expected_port = config.option("db-port")
      print('Expected port: ' + expected_port)
      
      if (connectionResult['stdout'].find('port') != -1 and connectionResult['stdout'].find(expected_port) != -1):
        print('MySQL configuration is valid')
        dependence.sqlPath = 'mysql'
        return dependence
      else:
        print('Port not found or does not match. Found: ' + connectionResult['stdout'])
    else:
      print('MySQL connection failed with code: ' + str(result))
    print('Valid MySQL Server not found')
    dependence.append_install('MySQLServer')
    dependence.append_uninstall('mysql-server')
    return dependence

  arrInfo = get_mysqlServersInfo()
  print('\nFound MySQL installations: ' + str(len(arrInfo)))
  for info in arrInfo:
    print('\nChecking MySQL at: ' + info['Location'])
    if (base.is_dir(info['Location']) == False):
      print('Directory does not exist, skipping...')
      continue

    mysql_full_name = 'MySQL Server ' + info['Version'] + ' '
    mysql_bin_path = get_mysql_path_to_bin(info['Location'])
    print('MySQL bin path: ' + mysql_bin_path)

    connectionResult = base.run_command_in_dir(mysql_bin_path, connectionString)
    print('Connection result stdout: ' + connectionResult['stdout'])
    if connectionResult['stderr']:
      print('Connection result stderr: ' + connectionResult['stderr'])
    print('Return code: ' + str(connectionResult['returncode']))
    
    expected_port = config.option("db-port")
    if (connectionResult['stdout'].find('port') != -1 and connectionResult['stdout'].find(expected_port) != -1):
      print(mysql_full_name + 'configuration is valid')
      dependence.sqlPath = info['Location']
      return dependence
    print(mysql_full_name + 'configuration is not valid. Expected port: ' + expected_port)
    # if path exists, then further removal and installation fails(according to startup statistics). it is better to fix issue manually.
    return dependence

  print('Valid MySQL Server not found')
  dependence.append_uninstall('MySQL Server')
  dependence.append_uninstall('MySQL Installer')
  dependence.append_install('MySQLInstaller')
  dependence.append_install('MySQLServer')

  MySQLData = os.environ['ProgramData'] + '\\MySQL\\'
  if base.is_exist(MySQLData) == False:
    return dependence

  dir = os.listdir(MySQLData)
  for path in dir:
    if (path.find('MySQL Server') != -1) and (base.is_file(MySQLData + path) == False):
      dependence.append_removepath(MySQLData + path)

  return dependence
def check_MySQLConfig(mysqlPath = ''):
  result = True
  mysqlLoginSrt = get_mysqlLoginString()
  mysql_path_to_bin = get_mysql_path_to_bin(mysqlPath)

  if (base.run_command_in_dir(mysql_path_to_bin, mysqlLoginSrt + ' -e "SHOW DATABASES;"')['stdout'].lower().find(config.option("db-name").lower()) == -1):
    print('Database "' + config.option("db-name") + '" not found')
    result = create_MySQLDb(mysql_path_to_bin, config.option("db-name"), config.option("db-user"), config.option("db-pass"))
    if (not result):
        return False
    print('Creating ' + config.option("db-name") + ' tables ...')
    creatdb_path = base.get_script_dir() + "/../../server/schema/mysql/createdb.sql"
    result = execMySQLScript(mysql_path_to_bin, config.option("db-name"), creatdb_path)
  if (base.run_command_in_dir(mysql_path_to_bin, mysqlLoginSrt + ' -e "SELECT plugin from mysql.user where User=' + "'" + config.option("db-user") + "';" + '"')['stdout'].find('mysql_native_password') == -1):
    print('Password encryption is not valid')
    result = set_MySQLEncrypt(mysql_path_to_bin, 'mysql_native_password') and result

  return result
def create_MySQLDb(mysql_path_to_bin, dbName, dbUser, dbPass):
  mysqlLoginSrt = get_mysqlLoginString()
  print('CREATE DATABASE ' + dbName + ';')
  if (base.exec_command_in_dir(mysql_path_to_bin, mysqlLoginSrt + ' -e "CREATE DATABASE ' + dbName + ';"') != 0):
    print('failed CREATE DATABASE ' + dbName + ';')
    return False
  # print('CREATE USER IF NOT EXISTS ' + dbUser + ' IDENTIFIED BY \'' + dbPass + '\';')
  # if (base.exec_command_in_dir(mysql_path_to_bin, mysqlLoginSrt + ' -e "CREATE USER IF NOT EXISTS ' + dbUser + ' IDENTIFIED BY \'' + dbPass + '\';"') != 0):
    # print('failed: CREATE USER IF NOT EXISTS ' + dbUser + ' IDENTIFIED BY \'' + dbPass + '\';')
    # return False
  # print('GRANT ALL PRIVILEGES ON ' + dbName + '.* TO ' + dbUser + ';')
  # if (base.exec_command_in_dir(mysql_path_to_bin, mysqlLoginSrt + ' -e "GRANT ALL PRIVILEGES ON ' + dbName + '.* TO ' + dbUser + ';"') != 0):
    # print('failed: GRANT ALL PRIVILEGES ON ' + dbName + '.* TO ' + dbUser + ';')
    # return False
  return True
  
def execMySQLScript(mysql_path_to_bin, dbName, scriptPath):
  print('Execution ' + scriptPath)
  mysqlLoginSrt = get_mysqlLoginString()
  
  code = base.exec_command_in_dir(mysql_path_to_bin, get_mysqlLoginString() + ' -D ' + dbName + ' < "' + scriptPath + '"')
  if (code != 0):
    print('Execution failed!')
    return False
  print('Execution completed')
  return True
def set_MySQLEncrypt(mysql_path_to_bin, sEncrypt):
  print('Setting MySQL password encrypting...')

  code = base.exec_command_in_dir(mysql_path_to_bin, get_mysqlLoginString() + ' -e "' + "ALTER USER '" + config.option("db-user") + "'@'localhost' IDENTIFIED WITH " + sEncrypt + " BY '" + config.option("db-pass") + "';" + '"')
  if (code != 0):
    print('Setting password encryption failed!')
    return False

  print('Setting password encryption completed')
  return True
def uninstall_mysqlserver():
  code = os.system('yes | sudo systemctl stop mysqld')
  code = os.system('sudo apt-get remove --purge mysql* -y') and code
  code = os.system('sudo rm -Rf /var/lib/mysql/') and code
  code = os.system('sudo rm -Rf /etc/mysql/') and code
  code = os.system('sudo rm -rf /var/log/mysql') and code
  code = os.system('sudo deluser --remove-home mysql') and code
  code = os.system('sudo delgroup mysql') and code

  return code

def get_postrgre_path_to_bin(postgrePath = ''):
  if (host_platform == 'windows'):
    if (postgrePath == ''):
      postgrePath = os.environ['PROGRAMW6432'] + '\\PostgreSQL\\13'
    postgrePath += '\\bin'
  return postgrePath
def get_postgreLoginSrting(userName):
  if (host_platform == 'windows'):
    # Note: PGPASSWORD should be set as environment variable on Windows
    return 'psql -U ' + userName + ' -h localhost '
  return 'PGPASSWORD="' + config.option("db-pass") + '" psql -U ' + userName + ' -h localhost '
def get_postgreSQLInfoByFlag(flag):
  arrInfo = []

  try:
    aReg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    aKey = winreg.OpenKey(aReg, "SOFTWARE\\PostgreSQL\\Installations", 0, winreg.KEY_READ | flag)

    count_subkey = winreg.QueryInfoKey(aKey)[0]

    for i in range(count_subkey):
      PostgreSQLsubkey_name = winreg.EnumKey(aKey, i)
      PostgreSQLsubkey = winreg.OpenKey(aKey, PostgreSQLsubkey_name)
      dictInfo = {}
      dictInfo['Location']  = winreg.QueryValueEx(PostgreSQLsubkey, 'Base Directory')[0]
      dictInfo['Version'] = winreg.QueryValueEx(PostgreSQLsubkey, 'CLT_Version')[0]
      dictInfo['DataLocation'] = winreg.QueryValueEx(PostgreSQLsubkey, 'Data Directory')[0]
      arrInfo.append(dictInfo)
  except:
    pass

  return arrInfo
def get_postgreSQLInfo():
  return get_postgreSQLInfoByFlag(winreg.KEY_WOW64_32KEY) + get_postgreSQLInfoByFlag(winreg.KEY_WOW64_64KEY)
def check_postgreSQL():
  base.print_info('Check PostgreSQL')

  dependence = CDependencies()
  
  postgreLoginSrt = get_postgreLoginSrting(install_params['PostgreSQL']['root'])
  print('PostgreSQL login string: ' + postgreLoginSrt)
  connectionString = postgreLoginSrt + ' -c "SELECT setting FROM pg_settings WHERE name = ' + "'port'" + ';"'
  print('Connection string: ' + connectionString)

  if (host_platform == 'linux'):
    print('\nTesting PostgreSQL connection...')
    result = os.system(postgreLoginSrt + ' -c "\q"')
    print('Connection test result code: ' + str(result))
    
    connectionResult = base.run_command(connectionString)
    print('Port check stdout: ' + connectionResult['stdout'])
    if connectionResult['stderr']:
      print('Port check stderr: ' + connectionResult['stderr'])
    print('Port check return code: ' + str(connectionResult['returncode']))
    
    expected_port = config.option("db-port")
    print('Expected port: ' + expected_port)

    if (result != 0 or connectionResult['stdout'].find(expected_port) == -1):
      print('Valid PostgreSQL not found!')
      dependence.append_install('PostgreSQL')
      dependence.append_uninstall('PostgreSQL')
    else:
      print('PostreSQL is installed')
      dependence.sqlPath = 'psql'
    return dependence

  arrInfo = get_postgreSQLInfo()
  print('\nFound PostgreSQL installations: ' + str(len(arrInfo)))
  db_pass = config.option("db-pass")
  print('Setting PGPASSWORD environment variable')
  base.set_env('PGPASSWORD', db_pass)
  
  for info in arrInfo:
    print('\nChecking PostgreSQL at: ' + info['Location'])
    if (base.is_dir(info['Location']) == False):
      print('Directory does not exist, skipping...')
      continue
    
    postgre_full_name = 'PostgreSQL ' + info['Version'][:2] + ' '
    postgre_bin_path = get_postrgre_path_to_bin(info['Location'])
    print('PostgreSQL bin path: ' + postgre_bin_path)
    
    connectionResult = base.run_command_in_dir(postgre_bin_path, connectionString)
    print('Connection result stdout: ' + connectionResult['stdout'])
    if connectionResult['stderr']:
      print('Connection result stderr: ' + connectionResult['stderr'])
    print('Return code: ' + str(connectionResult['returncode']))
    
    expected_port = config.option("db-port")
    if (connectionResult['stdout'].find(expected_port) != -1):
      print(postgre_full_name + 'configuration is valid')
      dependence.sqlPath = info['Location']
      return dependence
    print(postgre_full_name + 'configuration is not valid. Expected port: ' + expected_port)

  print('Valid PostgreSQL not found')

  dependence.append_uninstall('PostgreSQL')
  dependence.append_install('PostgreSQL')

  for info in arrInfo:
    dependence.append_removepath(info['DataLocation'])

  return dependence
def check_postgreConfig(postgrePath = ''):
  result = True
  base.print_info('Checking PostgreSQL configuration')
  
  if (host_platform == 'windows'):
    print('Setting PGPASSWORD for Windows')
    base.set_env('PGPASSWORD', config.option("db-pass"))

  rootUser = install_params['PostgreSQL']['root']
  dbUser = config.option("db-user")
  dbName = config.option("db-name")
  dbPass = config.option("db-pass")
  
  print('Configuration:')
  print('  Root user: ' + rootUser)
  print('  DB user: ' + dbUser)
  print('  DB name: ' + dbName)
  print('  PostgreSQL path: ' + postgrePath)
  
  postgre_path_to_bin = get_postrgre_path_to_bin(postgrePath)
  print('  Bin path: ' + postgre_path_to_bin)
  
  postgreLoginRoot = get_postgreLoginSrting(rootUser)
  postgreLoginDbUser = get_postgreLoginSrting(dbUser)
  print('  Root login string: ' + postgreLoginRoot)
  print('  User login string: ' + postgreLoginDbUser)
  
  creatdb_path = base.get_script_dir() + "/../../server/schema/postgresql/createdb.sql"
  print('  CreateDB script path: ' + creatdb_path)
  if base.is_file(creatdb_path):
    print('  CreateDB script exists: YES')
  else:
    print('  CreateDB script exists: NO - THIS IS A PROBLEM!')

  print('\nChecking if user exists...')
  check_user_cmd = postgreLoginRoot + ' -c "\du ' + dbUser + '"'
  user_check_result = base.run_command_in_dir(postgre_path_to_bin, check_user_cmd)
  print('User check command: ' + check_user_cmd)
  print('User check stdout: ' + user_check_result['stdout'])
  if user_check_result['stderr']:
    print('User check stderr: ' + user_check_result['stderr'])
  
  if (user_check_result['stdout'].find(dbUser) != -1):
    print('User ' + dbUser + ' exists')
    print('\nTesting user password...')
    password_test_result = os.system(postgreLoginDbUser + '-c "\q"')
    print('Password test result code: ' + str(password_test_result))
    
    if (password_test_result != 0):
      print('Invalid user password!')
      base.print_info('Changing password...')
      result = change_userPass(dbUser, dbPass, postgre_path_to_bin) and result
      print('Password change result: ' + str(result))
  else:
    print('User ' + dbUser + ' not exist!')
    base.print_info('Creating ' + dbName + ' user...')
    result = create_postgreUser(dbUser, dbPass, postgre_path_to_bin) and result

  print('\nChecking if database exists...')
  db_check_cmd = postgreLoginRoot + ' -c "SELECT datname FROM pg_database;"'
  db_check_result = base.run_command_in_dir(postgre_path_to_bin, db_check_cmd)
  print('Database check command: ' + db_check_cmd)
  print('Database check stdout: ' + db_check_result['stdout'])
  if db_check_result['stderr']:
    print('Database check stderr: ' + db_check_result['stderr'])
  
  if (db_check_result['stdout'].find(config.option("db-name")) == -1):
    print('Database ' + dbName + ' not found')
    base.print_info('Creating ' + dbName + ' database...')
    create_result = create_postgreDb(dbName, postgre_path_to_bin)
    print('Database creation result: ' + str(create_result))
    
    if create_result:
      # Give user rights to database and schema
      print('\nGranting database privileges to user ' + dbUser + '...')
      db_grant_cmd = postgreLoginRoot + '-c "GRANT ALL privileges ON DATABASE ' + dbName + ' TO ' + dbUser + ';"'
      db_grant_result = base.run_command_in_dir(postgre_path_to_bin, db_grant_cmd)
      print('Database grant result: ' + str(db_grant_result['returncode']))
      
      print('Granting schema privileges to user ' + dbUser + '...')
      schema_cmd = postgreLoginRoot + '-d ' + dbName + ' -c "GRANT ALL ON SCHEMA public TO ' + dbUser + ';"'
      schema_result = base.run_command_in_dir(postgre_path_to_bin, schema_cmd)
      print('Schema grant result: ' + str(schema_result['returncode']))
      
      print('\nConfiguring database with createdb.sql...')
      configure_result = configureDb(dbUser, dbName, creatdb_path, postgre_path_to_bin)
      print('Database configuration result: ' + str(configure_result))
      result = create_result and configure_result
    else:
      result = False
  else:
    print('Database ' + dbName + ' exists')
    # Simple check: if 0 tables, configure database
    print('Checking tables in database...')
    table_count_result = base.run_command_in_dir(postgre_path_to_bin, postgreLoginRoot + '-c "SELECT count(*) FROM information_schema.tables WHERE table_schema = \'public\';"')
    print('Table count result: ' + table_count_result['stdout'].strip())
    
    if table_count_result['stdout'].find(' 0') != -1:
      print('Database ' + dbName + ' has no tables - configuring...')
    else:
      print('Database ' + dbName + ' has tables - checking ownership...')
      # Check if tables belong to postgres instead of onlyoffice user
      owner_check = base.run_command_in_dir(postgre_path_to_bin, postgreLoginRoot + '-d ' + dbName + ' -c "\dt"')
      if owner_check['stdout'].find('postgres') != -1 and owner_check['stdout'].find(dbUser) == -1:
        print('Tables belong to postgres, not ' + dbUser + ' - need to recreate')
        print('Dropping existing tables...')
        drop_result = base.run_command_in_dir(postgre_path_to_bin, postgreLoginRoot + '-d ' + dbName + ' -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"')
        print('Schema recreation result: ' + str(drop_result['returncode']))
        print('Will proceed to recreate tables with correct owner...')
      else:
        print('Database ' + dbUser + ' already has correct tables - skipping configuration')
        return result

    # Configure database (either empty or after recreation)
    print('Granting database privileges to user ' + dbUser + '...')
    db_grant_cmd = postgreLoginRoot + '-c "GRANT ALL privileges ON DATABASE ' + dbName + ' TO ' + dbUser + ';"'
    db_grant_result = base.run_command_in_dir(postgre_path_to_bin, db_grant_cmd)
    print('Database grant result: ' + str(db_grant_result['returncode']))
    
    print('Granting schema privileges to user ' + dbUser + '...')
    schema_cmd = postgreLoginRoot + '-d ' + dbName + ' -c "GRANT ALL ON SCHEMA public TO ' + dbUser + ';"'
    schema_result = base.run_command_in_dir(postgre_path_to_bin, schema_cmd)
    print('Schema grant result: ' + str(schema_result['returncode']))
    
    base.print_info('Configuring ' + dbName + ' database...')
    configure_result = configureDb(dbUser, dbName, creatdb_path, postgre_path_to_bin)
    print('Configuration completed: ' + ('SUCCESS' if configure_result else 'FAILED'))
    result = configure_result and result

  # User privileges are set above when configuring database

  print('\n=== PostgreSQL Configuration Summary ===')
  print('Database: ' + dbName + ' - ' + ('READY' if result else 'FAILED'))
  print('User: ' + dbUser + ' - configured')
  
  return result
def create_postgreDb(dbName, postgre_path_to_bin = ''):
  print('\nCreating database: ' + dbName)
  postgreLoginUser = get_postgreLoginSrting(install_params['PostgreSQL']['root'])
  create_cmd = postgreLoginUser + '-c "CREATE DATABASE ' + dbName +';"'
  print('Create database command: ' + create_cmd)
  
  result = base.run_command_in_dir(postgre_path_to_bin, create_cmd)
  print('Create database return code: ' + str(result['returncode']))
  if result['stdout']:
    print('Create database stdout: ' + result['stdout'])
  if result['stderr']:
    print('Create database stderr: ' + result['stderr'])
  
  if (result['returncode'] != 0):
    print('Database creation FAILED!')
    return False
  
  print('Database created successfully')
  return True
def set_dbPrivilegesForUser(userName, dbName, postgre_path_to_bin = ''):
  print('\nSetting database privileges for user: ' + userName)
  postgreLoginUser = get_postgreLoginSrting(install_params['PostgreSQL']['root'])
  grant_cmd = postgreLoginUser + '-c "GRANT ALL privileges ON DATABASE ' + dbName + ' TO ' + userName + ';"'
  print('Grant command: ' + grant_cmd)
  
  result = base.run_command_in_dir(postgre_path_to_bin, grant_cmd)
  print('Grant return code: ' + str(result['returncode']))
  if result['stdout']:
    print('Grant stdout: ' + result['stdout'])
  if result['stderr']:
    print('Grant stderr: ' + result['stderr'])
  
  if (result['returncode'] != 0):
    print('Grant privileges FAILED!')
    return False
  
  print('Privileges granted successfully')
  return True
def create_postgreUser(userName, userPass, postgre_path_to_bin = ''):
  print('\nCreating user: ' + userName)
  postgreLoginRoot = get_postgreLoginSrting(install_params['PostgreSQL']['root'])
  create_cmd = postgreLoginRoot + '-c "CREATE USER ' + userName + ' WITH password ' + "'" + userPass + "'" + ';"'
  print('Create user command: ' + create_cmd[:50] + '... [password hidden]')
  
  result = base.run_command_in_dir(postgre_path_to_bin, create_cmd)
  print('Create user return code: ' + str(result['returncode']))
  if result['stdout']:
    print('Create user stdout: ' + result['stdout'])
  if result['stderr']:
    print('Create user stderr: ' + result['stderr'])
  
  if (result['returncode'] != 0):
    print('User creation FAILED!')
    return False
  
  print('User created successfully')
  return True
def change_userPass(userName, userPass, postgre_path_to_bin = ''):
  postgreLoginRoot = get_postgreLoginSrting(install_params['PostgreSQL']['root'])
  if (base.exec_command_in_dir(postgre_path_to_bin, postgreLoginRoot + '-c "ALTER USER ' + userName + " WITH PASSWORD '" +  userPass + "';" + '"') != 0):
    return False
  return True
def configureDb(userName, dbName, scriptPath, postgre_path_to_bin = ''):
  print('\n=== Configuring Database ===')
  print('Script path: ' + scriptPath)
  print('User: ' + userName)
  print('Database: ' + dbName)
  print('Bin path: ' + postgre_path_to_bin)
  
  # Check if script exists
  if not base.is_file(scriptPath):
    print('ERROR: Script file does not exist: ' + scriptPath)
    return False
  
  print('Script file size: ' + str(os.path.getsize(scriptPath)) + ' bytes')
  
  postgreLoginSrt = get_postgreLoginSrting(userName)
  print('Login string: ' + postgreLoginSrt)
  
  full_command = postgreLoginSrt + ' -d ' + dbName + ' -f "' + scriptPath + '"'
  print('Full command: ' + full_command)
  
  print('\nExecuting createdb.sql script...')
  
  # Use run_command_in_dir instead of exec_command_in_dir to capture output
  result = base.run_command_in_dir(postgre_path_to_bin, full_command)
  code = result['returncode']
  
  print('Execution return code: ' + str(code))
  if result['stdout']:
    print('Script output:\n' + result['stdout'])
  if result['stderr']:
    print('Script errors:\n' + result['stderr'])
  
  if (code != 0):
    print('Execution FAILED! Return code: ' + str(code))
    
    # Try to get more info about the failure
    print('\nTrying to connect and check database...')
    test_cmd = postgreLoginSrt + ' -d ' + dbName + ' -c "SELECT version();"'
    test_result = base.run_command_in_dir(postgre_path_to_bin, test_cmd)
    print('Connection test stdout: ' + test_result['stdout'])
    if test_result['stderr']:
      print('Connection test stderr: ' + test_result['stderr'])
    
    return False
  
  print('Execution completed successfully!')
  
  # Verify tables were created
  print('\nVerifying table creation...')
  verify_cmd = postgreLoginSrt + ' -d ' + dbName + ' -c "\dt;"'
  verify_result = base.run_command_in_dir(postgre_path_to_bin, verify_cmd)
  
  # Count lines with table names (skip header)
  table_lines = [line for line in verify_result['stdout'].split('\n') if '|' in line and 'table' in line.lower()]
  table_count = len(table_lines)
  
  if table_count > 0:
    print('SUCCESS: Created ' + str(table_count) + ' tables')
    print('Database is ready for use!')
  else:
    print('WARNING: No tables found after script execution')
    print(verify_result['stdout'])
  
  return True
def uninstall_postgresql():
  code = os.system('sudo DEBIAN_FRONTEND=noninteractive apt-get purge --auto-remove postgresql* -y')
  code = os.system('sudo rm -rf /var/lib/postgresql/') and code
  code = os.system('sudo rm -rf /var/log/postgresql/') and code
  code = os.system('sudo rm -rf /etc/postgresql/') and code
  code = os.system('sudo userdel -r postgres') and code
  code = os.system('sudo groupdel postgres') and code
  os.system('sudo kill ' + base.run_command('sudo fuser -vn tcp 5432')['stdout'])

  return  code

def get_programUninstallsByFlag(sName, flag):
  info = []
  aReg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
  aKey = winreg.OpenKey(aReg, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall", 0, winreg.KEY_READ | flag)
  count_subkey = winreg.QueryInfoKey(aKey)[0]

  for i in range(count_subkey):
    try:
      asubkey_name = winreg.EnumKey(aKey, i)
      asubkey = winreg.OpenKey(aKey, asubkey_name)
      progName = winreg.QueryValueEx(asubkey, 'DisplayName')[0]

      if (progName.find(sName) != -1):
        info.append(winreg.QueryValueEx(asubkey, 'UninstallString')[0])

    except:
      pass

  return info
def get_programUninstalls(sName):
  return get_programUninstallsByFlag(sName, winreg.KEY_WOW64_32KEY) + get_programUninstallsByFlag(sName, winreg.KEY_WOW64_64KEY)

def uninstallProgram(sName):
  base.print_info("Uninstalling all versions " + sName + "...")
  info = ''
  code = 0
  if (host_platform == 'windows'):
    unInfo = get_programUninstalls(sName)
    for info in unInfo:
      info = info.replace('"', '')
      if (base.is_file(info) == False):
        info = info.replace('/I', '/x').replace('/i', '/x') + ' /qn'
      else:
        if (sName in uninstall_params):
          info = '"' + info + '" ' + uninstall_params[sName]
        else:
          info = '"' + info + '" /S'
  elif (host_platform == 'linux'):
    if (sName in uninstall_special):
      code = uninstall_special[sName]()
    else:
      info = 'sudo apt-get remove --purge ' + sName + '* -y && ' + 'sudo apt-get autoremove -y && ' + 'sudo apt-get autoclean'
  
  if (info != ''):
    print("Uninstalling " + sName + "...")
    print(info)
    
    popen = subprocess.Popen(info, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    popen.communicate()
    code = popen.wait()
  
  if (code != 0):
    print("Uninstalling was failed!")
    return False

  return True

def installProgram(sName):
  base.print_info("Installing " + sName + "...")
  if (host_platform == 'windows'):
    if (sName in install_special):
      code = install_special[sName]()
    else:
      if (sName not in downloads_list['Windows']):
        print("Url for install not found!")
        return False

      download_url = downloads_list['Windows'][sName]
      file_name = "install."
      is_msi = download_url.endswith('msi')
      if is_msi:
        file_name += "msi"
      else:
        file_name += "exe"
      base.download(download_url, file_name)

      base.print_info("Install " + sName + "...")
      install_command = ("msiexec.exe /i " + file_name) if is_msi else file_name

      if (sName in install_params):
        install_command += " " + install_params.get(sName, '')
      if (is_msi == True):
        install_command += " /qn "
      elif sName not in install_params:
        install_command += " /S"

      print(install_command)
      code = os.system(install_command)
      base.delete_file(file_name)
      
  elif (host_platform == 'linux'):
    if (sName in install_special):
      code = install_special[sName]()
    else:
      if (sName not in downloads_list['Linux']):
        print("Program for install not found!")
        return False

      base.print_info("Install " + sName + "...")
      install_command = 'yes | sudo apt install ' + downloads_list['Linux'][sName]
      print(install_command)
      code = os.system(install_command)

  if (code != 0):
    print("Installing was failed!")
    return False

  return True

def install_gruntcli():
  check_npmPath()
  
  install_command = 'npm install -g grunt-cli'
  if (host_platform != 'windows'):
    install_command = 'sudo ' + install_command

  return os.system(install_command)

def install_mysqlserver():
  if (host_platform == 'windows'):
    return os.system('"' + os.environ['ProgramFiles(x86)'] + '\\MySQL\\MySQL Installer for Windows\\MySQLInstallerConsole" community install server;' + install_params['MySQLServer']['version'] + ';x64:*:type=config;openfirewall=true;generallog=true;binlog=true;serverid=' + config.option("db-port") + 'enable_tcpip=true;port=' + config.option("db-port") + ';rootpasswd=' + config.option("db-pass") + ' -silent')
  elif (host_platform == 'linux'):
    os.system('sudo kill ' + base.run_command('sudo fuser -vn tcp ' + config.option("db-port"))['stdout'])
    code = os.system('sudo ufw enable && sudo ufw allow 22 && sudo ufw allow 3306')
    code = os.system('sudo apt-get -y install zsh htop') and code
    code = os.system('echo "mysql-server mysql-server/root_password password ' + config.option("db-pass") + '" | sudo debconf-set-selections') and code
    code = os.system('echo "mysql-server mysql-server/root_password_again password ' + config.option("db-pass") + '" | sudo debconf-set-selections') and code
    return os.system('yes | sudo apt install mysql-server') and code
  return 1

def get_updates():
  return os.system('yes | sudo apt-get update')

def install_redis():
  base.print_info("Installing Redis...")
  pid = base.run_command('netstat -ano | findstr ' + install_params['Redis'].split(' ')[0].split('=')[1])['stdout'].split(' ')[-1]
  if (pid != ''):
    os.system('taskkill /F /PID ' + pid)
  os.system('sc delete Redis')

  return installProgram('Redis')

def install_postgresql():
  if (host_platform == 'windows'):
    download_url = downloads_list['PostgreSQL']
    file_name = "install.exe"
    base.download(download_url, file_name)
    base.print_info("Install PostgreSQL...")
    install_command = file_name + ' --mode unattended --unattendedmodeui none --superpassword ' + config.option("db-pass") + ' --serverport ' + config.option("db-port")
  else:
    base.print_info("Install PostgreSQL...")
    install_command = 'sudo apt install postgresql -y'

  print(install_command)
  code = os.system(install_command)

  if (host_platform == 'windows'):
    base.delete_file(file_name)
  else:
    code = os.system('sudo -i -u postgres psql -c "ALTER USER postgres PASSWORD ' + "'" + config.option("db-pass") + "'" + ';"') and code

  return code

def install_nodejs():
  os.system('curl -sSL https://deb.nodesource.com/setup_18.x | sudo -E bash -')
  base.print_info("Install node.js...")
  install_command = 'yes | sudo apt install nodejs'
  print(install_command)
  return os.system(install_command)

downloads_list = {
  'Windows': {
    'Git': 'https://github.com/git-for-windows/git/releases/download/v2.29.0.windows.1/Git-2.29.0-64-bit.exe',
    'Node.js': 'https://nodejs.org/dist/v18.17.1/node-v18.17.1-x64.msi',
    'Java': 'https://aka.ms/download-jdk/microsoft-jdk-11.0.18-windows-x64.msi',
    'RabbitMQ': 'https://github.com/rabbitmq/rabbitmq-server/releases/download/v3.8.9/rabbitmq-server-3.8.9.exe',
    'Erlang': 'http://erlang.org/download/otp_win64_23.1.exe',
    'VC2019x64': 'https://aka.ms/vs/17/release/vc_redist.x64.exe',
    'MySQLInstaller': 'https://dev.mysql.com/get/Downloads/MySQLInstaller/mysql-installer-web-community-8.0.21.0.msi',
    'BuildTools': 'https://download.visualstudio.microsoft.com/download/pr/11503713/e64d79b40219aea618ce2fe10ebd5f0d/vs_BuildTools.exe',
    'Redis': 'https://github.com/tporadowski/redis/releases/download/v5.0.9/Redis-x64-5.0.9.msi',
    'PostgreSQL': 'https://sbp.enterprisedb.com/getfile.jsp?fileid=12851'
  },
  'Linux': {
    'Git': 'git',
    'Npm': 'npm',
    'Java': 'openjdk-11-jdk',
    'RabbitMQ': 'rabbitmq-server',
    'Redis': 'redis-server',
    'Erlang': 'erlang',
    'Curl': 'curl',
    '7z': 'p7zip-full',
    'PostgreSQL': 'postgresql'
  }
}
install_special = {
  'NodeJs': install_nodejs,
  'GruntCli': install_gruntcli,
  'MySQLServer': install_mysqlserver,
  'RedisServer' : install_redis,
  'PostgreSQL': install_postgresql
}
uninstall_special = {
  'MySQLServer': uninstall_mysqlserver,
  'PostgreSQL' : uninstall_postgresql
}
install_params = {
  'BuildTools': '--add Microsoft.VisualStudio.Workload.VCTools --includeRecommended --quiet --wait',
  'Git': '/VERYSILENT /NORESTART',
  'MySQLServer': {
	'version': '8.0.21'
  },
  'Redis': 'PORT=6379 ADD_FIREWALL_RULE=1',
  'PostgreSQL': {
    'root': 'postgres'
  }
}
uninstall_params = {
  'PostgreSQL': '--mode unattended --unattendedmodeui none'
}
