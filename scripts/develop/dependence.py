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
    checksResult.append(check_buildTools())

  if (config.option("sql-type") == 'mysql' and host_platform == 'windows'):
    checksResult.append(check_mysqlServer())
  else:
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
  nodejs_min_version = '10.20'
  nodejs_min_version_minor  = 0
  major_minor_min_version = nodejs_min_version.split('.')
  nodejs_min_version_major = int(major_minor_min_version[0])
  if len(major_minor_min_version) > 1:
    nodejs_min_version_minor = int(major_minor_min_version[1])
  nodejs_max_version = '14'
  nodejs_max_version_minor = float("inf")
  major_minor_max_version = nodejs_max_version.split('.')
  nodejs_max_version_major = int(major_minor_max_version[0])
  if len(major_minor_max_version) > 1:
    nodejs_max_version_minor = int(major_minor_max_version[1])

  if (nodejs_min_version_major > nodejs_cur_version_major or nodejs_cur_version_major > nodejs_max_version_major):
    print('Installed Node.js version must be 10.20 to 14.x')
    isNeedReinstall = True
  elif (nodejs_min_version_major == nodejs_cur_version_major):
    if (nodejs_min_version_minor > nodejs_cur_version_minor):
      isNeedReinstall = True
  elif (nodejs_cur_version_major == nodejs_max_version_major):
    if (nodejs_cur_version_minor > nodejs_max_version_minor):
      isNeedReinstall = True

  if (True == isNeedReinstall):
    print('Installed Node.js version must be 10.20 to 14.x')
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
  java_version = base.run_command('java -version')['stderr']

  if (java_version.find('64-Bit') != -1):
    print('Installed Java is valid')
    return dependence

  if (java_version.find('32-Bit') != -1):
    print('Installed Java must be x64')
  else:
    print('Java not found')

  dependence.append_install('Java')
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
    result = base.run_command('service rabbitmq-server status')['stdout']
    if (result != ''):
      print('Installed RabbitMQ is valid')
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
def get_mysqlLoginSrting():
  return 'mysql -u ' + install_params['MySQLServer']['user'] + ' -p' +  install_params['MySQLServer']['pass']
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
  mysqlLoginSrt = get_mysqlLoginSrting()
  connectionString = mysqlLoginSrt + ' -e "SHOW GLOBAL VARIABLES LIKE ' + r"'PORT';" + '"'

  if (host_platform != 'windows'):
    result = os.system(mysqlLoginSrt + ' -e "exit"')
    if (result == 0):
      connectionResult = base.run_command(connectionString)['stdout']
      if (connectionResult.find('port') != -1 and connectionResult.find(install_params['MySQLServer']['port']) != -1):
        print('MySQL configuration is valid')
        dependence.sqlPath = 'mysql'
        return dependence
    print('Valid MySQL Server not found')
    dependence.append_install('MySQLServer')
    dependence.append_uninstall('mysql-server')
    return dependence

  arrInfo = get_mysqlServersInfo()
  for info in arrInfo:
    if (base.is_dir(info['Location']) == False):
      continue

    mysql_full_name = 'MySQL Server ' + info['Version'] + ' '

    connectionResult = base.run_command_in_dir(get_mysql_path_to_bin(info['Location']), connectionString)['stdout']
    if (connectionResult.find('port') != -1 and connectionResult.find(install_params['MySQLServer']['port']) != -1):
      print(mysql_full_name + 'configuration is valid')
      dependence.sqlPath = info['Location']
      return dependence
    print(mysql_full_name + 'configuration is not valid')

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
  mysqlLoginSrt = get_mysqlLoginSrting()
  mysql_path_to_bin = get_mysql_path_to_bin(mysqlPath)

  if (base.run_command_in_dir(mysql_path_to_bin, mysqlLoginSrt + ' -e "SHOW DATABASES;"')['stdout'].find('onlyoffice') == -1):
    print('Database onlyoffice not found')
    creatdb_path = base.get_script_dir() + "/../../server/schema/mysql/createdb.sql"
    result = execMySQLScript(mysql_path_to_bin, creatdb_path)
  if (base.run_command_in_dir(mysql_path_to_bin, mysqlLoginSrt + ' -e "SELECT plugin from mysql.user where User=' + "'" + install_params['MySQLServer']['user'] + "';" + '"')['stdout'].find('mysql_native_password') == -1):
    print('Password encryption is not valid')
    result = set_MySQLEncrypt(mysql_path_to_bin, 'mysql_native_password') and result

  return result
def execMySQLScript(mysql_path_to_bin, scriptPath):
  print('Execution ' + scriptPath)
  mysqlLoginSrt = get_mysqlLoginSrting()
  
  code = base.exec_command_in_dir(mysql_path_to_bin, get_mysqlLoginSrting() + ' < "' + scriptPath + '"')
  if (code != 0):
    print('Execution failed!')
    return False
  print('Execution completed')
  return True
def set_MySQLEncrypt(mysql_path_to_bin, sEncrypt):
  print('Setting MySQL password encrypting...')

  code = base.exec_command_in_dir(mysql_path_to_bin, get_mysqlLoginSrting() + ' -e "' + "ALTER USER '" + install_params['MySQLServer']['user'] + "'@'localhost' IDENTIFIED WITH " + sEncrypt + " BY '" + install_params['MySQLServer']['pass'] + "';" + '"')
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
    return 'psql -U' + userName + ' '
  return 'PGPASSWORD="' + install_params['PostgreSQL']['dbPass'] + '" psql -U' + userName + ' -hlocalhost '
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
  connectionString = postgreLoginSrt + ' -c "SELECT setting FROM pg_settings WHERE name = ' + "'port'" + ';"'

  if (host_platform == 'linux'):
    result = os.system(postgreLoginSrt + ' -c "\q"')
    connectionResult = base.run_command(connectionString)['stdout']

    if (result != 0 or connectionResult.find(install_params['PostgreSQL']['dbPort']) == -1):
      print('Valid PostgreSQL not found!')
      dependence.append_install('PostgreSQL')
      dependence.append_uninstall('PostgreSQL')
    else:
      print('PostreSQL is installed')
      dependence.sqlPath = 'psql'
    return dependence

  arrInfo = get_postgreSQLInfo()
  base.set_env('PGPASSWORD', install_params['PostgreSQL']['dbPass'])
  for info in arrInfo:
    if (base.is_dir(info['Location']) == False):
      continue
    
    postgre_full_name = 'PostgreSQL ' + info['Version'][:2] + ' '
    connectionResult = base.run_command_in_dir(get_postrgre_path_to_bin(info['Location']), connectionString)['stdout']

    if (connectionResult.find(install_params['PostgreSQL']['dbPort']) != -1):
      print(postgre_full_name + 'configuration is valid')
      dependence.sqlPath = info['Location']
      return dependence
    print(postgre_full_name + 'configuration is not valid')

  print('Valid PostgreSQL not found')

  dependence.append_uninstall('PostgreSQL')
  dependence.append_install('PostgreSQL')

  for info in arrInfo:
    dependence.append_removepath(info['DataLocation'])

  return dependence
def check_postgreConfig(postgrePath = ''):
  result = True
  if (host_platform == 'windows'):
    base.set_env('PGPASSWORD', install_params['PostgreSQL']['dbPass'])

  rootUser = install_params['PostgreSQL']['root']
  dbUser = install_params['PostgreSQL']['dbUser']
  dbName = install_params['PostgreSQL']['dbName']
  dbPass = install_params['PostgreSQL']['dbPass']
  postgre_path_to_bin = get_postrgre_path_to_bin(postgrePath)
  postgreLoginRoot = get_postgreLoginSrting(rootUser)
  postgreLoginDbUser = get_postgreLoginSrting(dbUser)
  creatdb_path = base.get_script_dir() + "/../../server/schema/postgresql/createdb.sql"

  if (base.run_command_in_dir(postgre_path_to_bin, postgreLoginRoot + ' -c "\du ' + dbUser + '"')['stdout'].find(dbUser) != -1):
    print('User ' + dbUser + ' is exist')
    if (os.system(postgreLoginDbUser + '-c "\q"') != 0):
      print('Invalid user password!')
      base.print_info('Changing password...')
      result = change_userPass(dbUser, dbPass, postgre_path_to_bin) and result
  else:
    print('User ' + dbUser + ' not exist!')
    base.print_info('Creating ' + dbName + ' user...')
    result = create_postgreUser(dbUser, dbPass, postgre_path_to_bin) and result

  if (base.run_command_in_dir(postgre_path_to_bin, postgreLoginRoot + ' -c "SELECT datname FROM pg_database;"')['stdout'].find('onlyoffice') == -1):
    print('Database ' + dbName + ' not found')
    base.print_info('Creating ' + dbName + ' database...')
    result = create_postgreDb(dbName, postgre_path_to_bin) and configureDb(dbUser, dbName, creatdb_path, postgre_path_to_bin)
  else:
    if (base.run_command_in_dir(postgre_path_to_bin, postgreLoginRoot + '-c "SELECT pg_size_pretty(pg_database_size(' + "'" + dbName + "'" + '));"')['stdout'].find('7559 kB') != -1):
      print('Database ' + dbName + ' not configured')
      base.print_info('Configuring ' + dbName + ' database...')
      result = configureDb(dbName, creatdb_path, postgre_path_to_bin) and result
    print('Database ' + dbName + ' is valid')

  if (base.run_command_in_dir(postgre_path_to_bin, postgreLoginRoot + '-c "\l+ ' + dbName + '"')['stdout'].find(dbUser +'=CTc/' + rootUser) == -1):
    print('User ' + dbUser + ' has no database privileges!')
    base.print_info('Setting database privileges for user ' + dbUser + '...')
    result = set_dbPrivilegesForUser(dbUser, dbName, postgre_path_to_bin) and result
  print('User ' + dbUser + ' has database privileges')

  return result
def create_postgreDb(dbName, postgre_path_to_bin = ''):
  postgreLoginUser = get_postgreLoginSrting(install_params['PostgreSQL']['root'])
  if (base.exec_command_in_dir(postgre_path_to_bin, postgreLoginUser + '-c "CREATE DATABASE ' + dbName +';"') != 0):
    return False
  return True
def set_dbPrivilegesForUser(userName, dbName, postgre_path_to_bin = ''):
  postgreLoginUser = get_postgreLoginSrting(install_params['PostgreSQL']['root'])
  if (base.exec_command_in_dir(postgre_path_to_bin, postgreLoginUser + '-c "GRANT ALL privileges ON DATABASE ' + dbName + ' TO ' + userName + ';"') != 0):
    return False
  return True
def create_postgreUser(userName, userPass, postgre_path_to_bin = ''):
  postgreLoginRoot = get_postgreLoginSrting(install_params['PostgreSQL']['root'])
  if (base.exec_command_in_dir(postgre_path_to_bin, postgreLoginRoot + '-c "CREATE USER ' + userName + ' WITH password ' + "'" + userPass + "'" + ';"') != 0):
    return False
  return True
def change_userPass(userName, userPass, postgre_path_to_bin = ''):
  postgreLoginRoot = get_postgreLoginSrting(install_params['PostgreSQL']['root'])
  if (base.exec_command_in_dir(postgre_path_to_bin, postgreLoginRoot + '-c "ALTER USER ' + userName + " WITH PASSWORD '" +  userPass + "';" + '"') != 0):
    return False
  return True
def configureDb(userName, dbName, scriptPath, postgre_path_to_bin = ''):
  print('Execution ' + scriptPath)
  postgreLoginSrt = get_postgreLoginSrting(userName)

  code = base.exec_command_in_dir(postgre_path_to_bin, postgreLoginSrt + ' -d ' + dbName + ' -f "' + scriptPath + '"')
  if (code != 0):
    print('Execution failed!')
    return False
  print('Execution completed')
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
    return os.system('"' + os.environ['ProgramFiles(x86)'] + '\\MySQL\\MySQL Installer for Windows\\MySQLInstallerConsole" community install server;' + install_params['MySQLServer']['version'] + ';x64:*:type=config;openfirewall=true;generallog=true;binlog=true;serverid=' + install_params['MySQLServer']['port'] + 'enable_tcpip=true;port=' + install_params['MySQLServer']['port'] + ';rootpasswd=' + install_params['MySQLServer']['pass'] + ' -silent')
  elif (host_platform == 'linux'):
    os.system('sudo kill ' + base.run_command('sudo fuser -vn tcp ' + install_params['MySQLServer']['port'])['stdout'])
    code = os.system('sudo ufw enable && sudo ufw allow 22 && sudo ufw allow 3306')
    code = os.system('sudo apt-get -y install zsh htop') and code
    code = os.system('echo "mysql-server mysql-server/root_password password ' + install_params['MySQLServer']['pass'] + '" | sudo debconf-set-selections') and code
    code = os.system('echo "mysql-server mysql-server/root_password_again password ' + install_params['MySQLServer']['pass'] + '" | sudo debconf-set-selections') and code
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
    install_command = file_name + ' --mode unattended --unattendedmodeui none --superpassword ' + install_params['PostgreSQL']['dbPass'] + ' --serverport ' + install_params['PostgreSQL']['dbPort']
  else:
    base.print_info("Install PostgreSQL...")
    install_command = 'sudo apt install postgresql -y'

  print(install_command)
  code = os.system(install_command)

  if (host_platform == 'windows'):
    base.delete_file(file_name)
  else:
    code = os.system('sudo -i -u postgres psql -c "ALTER USER postgres PASSWORD ' + "'" + install_params['PostgreSQL']['dbPass'] + "'" + ';"') and code

  return code

def install_nodejs():
  os.system('curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -')
  base.print_info("Install node.js...")
  install_command = 'yes | sudo apt install nodejs'
  print(install_command)
  return os.system(install_command)

downloads_list = {
  'Windows': {
    'Git': 'https://github.com/git-for-windows/git/releases/download/v2.29.0.windows.1/Git-2.29.0-64-bit.exe',
    'Node.js': 'https://nodejs.org/download/release/v14.15.1/node-v14.15.1-x64.msi',
    'Java': 'https://javadl.oracle.com/webapps/download/AutoDL?BundleId=242990_a4634525489241b9a9e1aa73d9e118e6',
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
  'Java': '/s',
  'MySQLServer': {
    'port': '3306',
	'user': 'root',
	'pass': 'onlyoffice',
	'version': '8.0.21'
  },
  'Redis': 'PORT=6379 ADD_FIREWALL_RULE=1',
  'PostgreSQL': {
    'root': 'postgres',
    'dbPort': '5432',
    'dbName': 'onlyoffice',
    'dbUser': 'onlyoffice',
    'dbPass': 'onlyoffice'
  }
}
uninstall_params = {
  'PostgreSQL': '--mode unattended --unattendedmodeui none'
}

