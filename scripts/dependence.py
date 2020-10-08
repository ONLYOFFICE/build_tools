import sys
import os
import base

if (sys.version_info[0] >= 3):
  import winreg
else:
  import _winreg as winreg

class CDependencies:
  def __init__(self):
    self.progsToInstall = []
    self.progsToUninstall = []
    self.pathsToRemove = []
    self.pathToValidMySQLServer = ''
  
  def append(self, oCdependencies):
    self.progsToInstall += oCdependencies.progsToInstall
    self.progsToUninstall += oCdependencies.progsToUninstall
    self.pathsToRemove += oCdependencies.pathsToRemove
    self.pathToValidMySQLServer = oCdependencies.pathToValidMySQLServer
    self.progsToInstall = list(set(self.progsToInstall))
    self.progsToUninstall = list(set(self.progsToUninstall))
    
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
    dependence.progsToInstall.append('Node.js')
    return dependence
  
  nodejs_cur_version = int(nodejs_version.split('.')[0][1:])
  print('Installed Node.js version: ' + str(nodejs_cur_version))
  nodejs_min_version = 8
  nodejs_max_version = 10
  if (nodejs_min_version > nodejs_cur_version or nodejs_cur_version > nodejs_max_version):
    print('Installed Node.js version must be 8.x to 10.x')
    dependence.progsToUninstall.append('Node.js')
    dependence.progsToInstall.append('Node.js')
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
  
  dependence.progsToInstall.append('Java')
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
  
  dependence.progsToUninstall.append('Erlang')
  dependence.progsToUninstall.append('RabbitMQ')
  dependence.progsToInstall.append('Erlang')
  dependence.progsToInstall.append('RabbitMQ')
  
  return dependence

def check_rabbitmq():
  dependence = CDependencies()
  base.print_info('Check installed RabbitMQ')
  result = base.run_command('sc query RabbitMQ')['stdout']
  
  if (result.find('RabbitMQ') != -1):
    print('Installed RabbitMQ is valid')
    return dependence
  
  print('RabbitMQ not found')
  dependence.progsToUninstall.append('Erlang')
  dependence.progsToUninstall.append('RabbitMQ')
  dependence.progsToInstall.append('Erlang')
  dependence.progsToInstall.append('RabbitMQ')
  
  return dependence

def check_gruntcli():
  dependence = CDependencies()
  
  base.print_info('Check installed Grunt-Cli')
  result = base.run_command('npm list -g --depth=0')['stdout']
  
  if (result.find('grunt-cli') == -1):
    print('Grunt-Cli not found')
    dependence.progsToInstall.append('GruntCli')
    return dependence
  
  print('Installed Grunt-Cli is valid')
  return dependence

def check_buildTools():
  dependence = CDependencies()
  
  base.print_info('Check installed Build Tools')
  result = base.run_command('vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property DisplayName')['stdout']
  if (result == ''):
    print('Build Tools not found')
    dependence.progsToInstall.append('BuildTools')
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
  dependence.progsToInstall.append('MySQLInstaller')
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
  print("Uninstalling " + sName + "...")
  
  unInfo = get_programUninstalls(sName)
  for info in unInfo:
    if (base.is_file(info) == False):
      info = info.replace('/I', '/x').replace('/i', '/x')
    else:
      info = '"' + info + '" /S'
      
    print(info)  
    if (os.system(info) != 0):
      print("Uninstalling was failed!")
      return False
      
  return True
