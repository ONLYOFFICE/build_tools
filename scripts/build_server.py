#!/usr/bin/env python

import config
import base
import platform


def make():
  product_version = base.get_env('PRODUCT_VERSION')
  if(not product_version):
    product_version = "0.0.0"
    base.set_env('PRODUCT_VERSION', product_version)

  build_number = base.get_env('BUILD_NUMBER')
  if(not build_number):
    build_number = "0"
    base.set_env('BUILD_NUMBER', build_number)

  publisher_name = base.get_env('PUBLISHER_NAME')
  if(not publisher_name):
    publisher_name = "Ascensio System SIA"
    base.set_env('PUBLISHER_NAME', publisher_name)

  publisher_url = base.get_env('PUBLISHER_URL')
  if(not publisher_url):
    publisher_url = "https://www.onlyoffice.com/"
    base.set_env('PUBLISHER_URL', publisher_url)

  base.set_env("PRODUCT_VERSION", product_version)
  base.set_env("BUILD_NUMBER", build_number)
  base.set_env("PUBLISHER_NAME", publisher_name)
  base.set_env("PUBLISHER_URL", publisher_url)

  branding_dir = base.get_env('BRANDING_DIR')
  if(not branding_dir):
    branding_dir = 'branding'

  plt = platform.platform()
  if(plt.find('Linux') >= 0):
    target_platform = 'linux'
    exec_ext = ''
  else:
    target_platform = 'win'
    exec_ext = '.exe'

  arch = platform.architecture()[0]
  if(arch.find('64bit') >= 0):
    target_architecture = '64'
  else:
    target_architecture = '32'

  target = target_platform + "_" + target_architecture
  output = '../build_tools/out/' + target + '/onlyoffice/documentserver/server'
  grunt_out_file = 'Gruntfile.js.out'


  base.set_cwd("../server");

  base.cmd("npm", ["install"])
  base.cmd("grunt", ["--no-color", "-v"])
  base.create_dir(output)
  base.copy_dir('build/server', output)

  f = open(grunt_out_file, 'w')
  f.write('Done')
  f.close()

  #dictionaries
  spellchecker_dictionaries = output + '/SpellChecker/dictionaries'
  spellchecker_dictionaries_files = '../dictionaries'
  base.create_dir(spellchecker_dictionaries)
  base.copy_dir(spellchecker_dictionaries_files, spellchecker_dictionaries)

  #tools
  tools = output + '/tools'
  tools_file1 = '../core/build/bin/' + target + '/allfontsgen' + exec_ext
  tools_file2 = '../core/build/bin/' + target + '/allthemesgen' + exec_ext
  base.create_dir(tools)
  base.copy_file(tools_file1, tools)
  base.copy_file(tools_file2, tools)

  #schema
  schema_files = 'schema'
  schema = output + '/schema'
  base.create_dir(schema)
  base.copy_dir(schema_files, schema)

  #core-fonts
  core_fonts_files = '../core-fonts'
  core_fonts = output + '/../core-fonts'
  base.create_dir(core_fonts)
  base.copy_dir(core_fonts_files, core_fonts)

  #license
  license_file1 = 'LICENSE.txt'
  license_file2 = '3rd-Party.txt'
  license_dir = 'license'
  license = output + '/license'
  base.copy_file(license_file1, output)
  base.copy_file(license_file2, output)
  base.copy_dir(license_dir, license)

  #branding
  welcome_files = branding_dir + '/welcome'
  welcome = output + '/welcome'
  base.create_dir(welcome)
  base.copy_dir(welcome_files, welcome)

  info_files = branding_dir + '/info'
  info = output + '/info'
  base.create_dir(info)
  base.copy_dir(info_files, info)

  custom_public_key = branding_dir + '/licenseKey.pem'

  if(base.is_exist(custom_public_key)):
    base.copy_file(custom_public_key, output + '/Common/sources')

  base.cmd("sed", ["s|\(const buildVersion = \).*|const buildVersion = '" + product_version + "';|", "-i", output + "/Common/sources/commondefines.js"])
  base.cmd("sed", ["s|\(const buildNumber = \).*|const buildNumber = " + build_number + ";|", "-i", output + "/Common/sources/commondefines.js"])
  base.cmd("sed", ["s|\(const buildDate = \).*|const buildDate = '$(date +%F)';|", "-i", output + "/Common/sources/license.js"])

