import sys
sys.path.append('../')
import os
import base
import subprocess

if (sys.version_info[0] >= 3):
  import winreg
else:
  import _winreg as winreg

class CDependencies:
  def __init__(self):
    self.install = []
    self.uninstall = []
    self.removepath = []
    self.mysqlPath = ''
  
  def append(self, oCdependencies):
    for item in oCdependencies.install:
      self.append_install(item)
    for item in oCdependencies.uninstall:
      self.append_uninstall(item)
    for item in oCdependencies.removepath:
      self.append_removepath(item)
    self.mysqlPath = oCdependencies.mysqlPath
  
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
    res = [];
    for item in self.install:
      res += ['--install', item]
    return res
    
  def get_uninstall(self):
    res = [];
    for item in self.uninstall:
      res += ['--uninstall', item]
    return res
  
  def get_removepath(self):
    res = [];
    for item in self.removepath:
      res += ['--remove-path', item]
    return res
    
def check_pythonPath():
  path = base.get_env('PATH')
  if (path.find(sys.exec_prefix) == -1):
    base.set_env('PATH', sys.exec_prefix + os.pathsep + path)

def check_npmPath():
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
  base.print_info('Check installed Node.js')
  
  nodejs_version = base.run_command('node -v')['stdout']
  if (nodejs_version == ''):
    print('Node.js not found')
    dependence.append_install('Node.js')
    return dependence
  
  nodejs_cur_version = int(nodejs_version.split('.')[0][1:])
  print('Installed Node.js version: ' + str(nodejs_cur_version))
  nodejs_min_version = 8
  nodejs_max_version = 10
  if (nodejs_min_version > nodejs_cur_version or nodejs_cur_version > nodejs_max_version):
    print('Installed Node.js version must be 8.x to 10.x')
    dependence.append_uninstall('Node.js')
    dependence.append_install('Node.js')
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

def check_erlang():
  dependence = CDependencies()
  base.print_info('Check installed Erlang')
  erlangHome = os.getenv("ERLANG_HOME")
  
  if (erlangHome is not None):
    erlangBitness = base.run_command('"' + erlangHome + '\\bin\\erl" -eval "erlang:display(erlang:system_info(wordsize)), halt()." -noshell')['stdout']
    if (erlangBitness == '8'):
      print("Installed Erlang is valid")
      return dependence
  
  print('Need Erlang with bitness x64')
  
  dependence.append_removepath(os.environ['AppData'] + '\\RabbitMQ\\db')
  dependence.append_uninstall('Erlang')
  dependence.append_uninstall('RabbitMQ')
  dependence.append_install('Erlang')
  dependence.append_install('RabbitMQ')
  
  return dependence

def check_rabbitmq():
  dependence = CDependencies()
  base.print_info('Check installed RabbitMQ')
  result = base.run_command('sc query RabbitMQ')['stdout']
  
  if (result.find('RabbitMQ') != -1):
    print('Installed RabbitMQ is valid')
    return dependence
  
  print('RabbitMQ not found')
  dependence.append_removepath(os.environ['AppData'] + '\\RabbitMQ\\db')
  dependence.append_uninstall('Erlang')
  dependence.append_uninstall('RabbitMQ')
  dependence.append_install('Erlang')
  dependence.append_install('RabbitMQ')
  
  return dependence

def find_redis(base_path):
  return base.find_file(os.path.join(base_path, 'Redis'), 'redis-cli.exe')

def check_redis():
  dependence = CDependencies()
  base.print_info('Check Redis server')
  
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
  if (redis_cli == None):
    print('Redis not found in default folder')
    dependence.append_uninstall('Redis on Windows')
    dependence.append_install('RedisServer')
    return dependence
      
  result = base.run_command('"' + redis_cli + '"' + ' info server')['stdout']
  if (result == ''):
    print('Redis client is invalid')
    dependence.append_uninstall('Redis on Windows')
    dependence.append_install('RedisServer')
    return dependence
     
  info = result.split('tcp_port:')[1]
  tcp_port = info.split('\r', 1)[0]
  config_port = install_params['Redis'].split('PORT=', 1)[1]
  config_port = config_port.split(' ', 1)[0]
  if (tcp_port != config_port):
    print('Invalid Redis port, need reinstall')
    dependence.append_uninstall('Redis on Windows')
    dependence.append_install('RedisServer')
    return dependence
    
  print('Installed Redis is valid')
  return dependence
  
def check_vc_components():
  base.print_info('Check Visual C++ components')
  result = True
  if (len(get_programUninstalls('Microsoft Visual C++ 2015-2019 Redistributable (x64)')) == 0):
    print('Microsoft Visual C++ 2015-2019 Redistributable (x64) not found')
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

def get_mysql_path_to_bin(mysqlPath = ''):
  if (mysqlPath == ''):
    mysqlPath = os.environ['PROGRAMW6432'] + '\\MySQL\\MySQL Server 8.0\\'
  return '"'+ mysqlPath + 'bin\\mysql"'
def get_mysqlLoginSrting(mysqlPath = ''):
  return get_mysql_path_to_bin(mysqlPath) + ' -u ' + install_params['MySQLServer']['user'] + ' -p' +  install_params['MySQLServer']['pass']
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
  arrInfo = get_mysqlServersInfo()
  
  for info in arrInfo:
    if (base.is_dir(info['Location']) == False):
      continue
    
    mysqlLoginSrt = get_mysqlLoginSrting(info['Location'])
    mysql_full_name = 'MySQL Server ' + info['Version'] + ' '
    
    connectionResult = base.run_command(mysqlLoginSrt + ' -e "SHOW GLOBAL VARIABLES LIKE ' + r"'PORT';" + '"')['stdout']
    if (connectionResult.find('port') != -1 and connectionResult.find(install_params['MySQLServer']['port']) != -1):
      print(mysql_full_name + 'configuration is valid')
      dependence.mysqlPath = info['Location']
      return dependence
    print(mysql_full_name + 'configuration is not valid')
      
  print('Valid MySQL Server not found')
  
  dependence.append_uninstall('MySQL Installer')
  dependence.append_uninstall('MySQL Server')
  dependence.append_install('MySQLInstaller')
  dependence.append_install('MySQLServer')
  
  dependence.append_removepath(os.environ['ProgramData'] + '\\MySQL\\')
  
  return dependence
def check_MySQLConfig(mysqlPath = ''):
  result = True
  mysqlLoginSrt = get_mysqlLoginSrting(mysqlPath)
  
  if (base.run_command(mysqlLoginSrt + ' -e "SHOW DATABASES;"')['stdout'].find('onlyoffice') == -1):
    print('Database onlyoffice not found')
    creatdb_path = base.get_script_dir() + "/../../server/schema/mysql/createdb.sql"
    result = execMySQLScript(mysqlPath, creatdb_path) and result
  if (base.run_command(mysqlLoginSrt + ' -e "SELECT plugin from mysql.user where User=' + "'" + install_params['MySQLServer']['user'] + "';")['stdout'].find('mysql_native_password') == -1):
    print('Password encryption is not valid')
    result = set_MySQLEncrypt(mysqlPath, 'mysql_native_password') and result
  
  return result
def execMySQLScript(mysqlPath, scriptPath):
  print('Execution ' + scriptPath)
  mysqlLoginSrt = get_mysqlLoginSrting(mysqlPath)
  
  code = subprocess.call(mysqlLoginSrt + ' < "' + scriptPath + '"', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
  if (code != 0):
    print('Execution failed!')
    return False
  print('Execution completed')
  return True
def set_MySQLEncrypt(mysqlPath, sEncrypt):
  print('Setting MySQL password encrypting...')
  mysqlLoginSrt = get_mysqlLoginSrting(mysqlPath)
  
  code = subprocess.call(mysqlLoginSrt + ' -e "' + "ALTER USER '" + install_params['MySQLServer']['user'] + "'@'localhost' IDENTIFIED WITH " + sEncrypt + " BY '" + install_params['MySQLServer']['pass'] + "';" + '"', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
  if (code != 0):
    print('Setting password encryption failed!')
    return False
  
  print('Setting password encryption completed')
  return True

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
  
  unInfo = get_programUninstalls(sName)
  for info in unInfo:
    if (base.is_file(info) == False):
      info = info.replace('/I', '/x').replace('/i', '/x') + ' /qn'
    else:
      info = '"' + info + '" /S'
    
    print("Uninstalling " + sName + "...")
    print(info)
    if (os.system(info) != 0):
      print("Uninstalling was failed!")
      return False
      
  return True

def installProgram(sName):
  base.print_info("Installing " + sName + "...")
  if (sName in install_special):
    code = install_special[sName]()
  else:
    if (sName not in downloads_list):
      print("Url for install not found!")
      return False
      
    download_url = downloads_list[sName]
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
  
  if (code != 0):
    print("Installing was failed!")
    return False
  
  return True
  
def install_gruntcli():
  check_npmPath()
  return os.system('npm install -g grunt-cli')

def install_mysqlserver():
  return os.system('"' + os.environ['ProgramFiles(x86)'] + '\\MySQL\\MySQL Installer for Windows\\MySQLInstallerConsole" community install server;' + install_params['MySQLServer']['version'] + ';x64:*:type=config;openfirewall=true;generallog=true;binlog=true;serverid=' + install_params['MySQLServer']['port'] + ';enable_tcpip=true;port=' + install_params['MySQLServer']['port'] + ';rootpasswd=' + install_params['MySQLServer']['pass'] + ' -silent')

def install_redis():
  base.print_info("Installing Redis...")
  pid = base.run_command('netstat -ano | findstr ' + install_params['Redis'].split(' ')[0].split('=')[1])['stdout'].split(' ')[-1]
  if (pid != ''):
    os.system('taskkill /F /PID ' + pid)
  os.system('sc delete Redis')
  
  return installProgram('Redis')
  
downloads_list = {
  'Git': 'https://github.com/git-for-windows/git/releases/download/v2.29.0.windows.1/Git-2.29.0-64-bit.exe',
  'Node.js': 'https://nodejs.org/dist/latest-v10.x/node-v10.22.1-x64.msi',
  'Java': 'https://javadl.oracle.com/webapps/download/AutoDL?BundleId=242990_a4634525489241b9a9e1aa73d9e118e6',
  'RabbitMQ': 'https://github.com/rabbitmq/rabbitmq-server/releases/download/v3.8.9/rabbitmq-server-3.8.9.exe',
  'Erlang': 'http://erlang.org/download/otp_win64_23.1.exe',
  'VC2019x64': 'https://aka.ms/vs/16/release/vc_redist.x64.exe',
  'MySQLInstaller': 'https://dev.mysql.com/get/Downloads/MySQLInstaller/mysql-installer-web-community-8.0.21.0.msi',
  'BuildTools': 'https://download.visualstudio.microsoft.com/download/pr/11503713/e64d79b40219aea618ce2fe10ebd5f0d/vs_BuildTools.exe',
  'Redis': 'https://github.com/tporadowski/redis/releases/download/v5.0.9/Redis-x64-5.0.9.msi'
}
install_special = {
  'GruntCli': install_gruntcli,
  'MySQLServer': install_mysqlserver,
  'RedisServer' : install_redis 
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
  'Redis': 'PORT=6379 ADD_FIREWALL_RULE=1'
}
