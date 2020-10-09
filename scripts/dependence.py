import sys
import os
import base

if (sys.version_info[0] >= 3):
  import winreg
else:
  import _winreg as winreg

downloads_list = {
  'Node.js': 'https://nodejs.org/dist/latest-v10.x/node-v10.22.1-x64.msi',
  'Java': 'https://javadl.oracle.com/webapps/download/AutoDL?BundleId=242990_a4634525489241b9a9e1aa73d9e118e6',
  'RabbitMQ': 'https://github.com/rabbitmq/rabbitmq-server/releases/download/v3.8.8/rabbitmq-server-3.8.8.exe',
  'Erlang': 'http://erlang.org/download/otp_win64_23.0.exe',
  'MySQLInstaller': 'https://dev.mysql.com/get/Downloads/MySQLInstaller/mysql-installer-web-community-8.0.21.0.msi',
  'BuildTools': 'https://download.visualstudio.microsoft.com/download/pr/11503713/e64d79b40219aea618ce2fe10ebd5f0d/vs_BuildTools.exe'
}

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
  dependence.append_uninstall('Erlang')
  dependence.append_uninstall('RabbitMQ')
  dependence.append_install('Erlang')
  dependence.append_install('RabbitMQ')
  
  return dependence

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

def check_mysqlInstaller():
  dependence = CDependencies()
  aReg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
  aKey= winreg.OpenKey(aReg, "SOFTWARE\\", 0, winreg.KEY_READ | winreg.KEY_WOW64_32KEY)
  
  try:
    asubkey = winreg.OpenKey(aKey, 'MySQL')
    count_subkey = winreg.QueryInfoKey(asubkey)[0]
    
    for i in range(count_subkey):
      MySQLsubkey_name = winreg.EnumKey(asubkey, i)
      if (MySQLsubkey_name.find('MySQL Installer') != - 1):
        return dependence
  except:
    pass
  dependence.append_install('MySQLInstaller')
  return dependence

def get_programUninstallsByFlag(sName, flag):
  info = []
  aReg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
  aKey= winreg.OpenKey(aReg, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall", 0, winreg.KEY_READ | flag)
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
  download_url = downloads_list[sName]
  if (download_url is None):
    print("Url for install not found!")
    return False
  file_name = "install."
  is_msi = download_url.endswith('msi')
  if is_msi:
    file_name += "msi"
  else:
    file_name += "exe"
  base.download(download_url, file_name)
  
  base.print_info("Install " + sName + "...")
  if is_msi:
    install_command = "msiexec.exe /i " + file_name + " /qn"
  else:
    install_command = file_name + " /S"
  
  print(install_command)
  code = os.system(install_command)
  base.delete_file(file_name)
  
  if (code != 0):
    print("Installing was failed!")
    return False
  
  return True

def install_module(path):
  base.print_info('Install: ' + path)
  base.cmd_in_dir(path, 'npm', ['install'])
