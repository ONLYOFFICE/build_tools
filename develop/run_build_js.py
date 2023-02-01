#!/usr/bin/env python3

import sys
sys.path.append(sys.argv[1] + '/build_tools/scripts')
sys.path.append(sys.argv[1] + '/build_tools/scripts/develop')
import build_js
import run_server
import config
import base

git_dir = sys.argv[1];

base.cmd_in_dir(git_dir + '/build_tools/', 'python3', ['configure.py', '--develop', '1'])
config.parse()

if base.is_exist(git_dir + "/server/FileConverter/bin/fonts.log"):
  base.print_info('remove font cache to regenerate fonts in external sdkjs volume')
  base.delete_file(git_dir + "/server/FileConverter/bin/fonts.log");

# external server volume
if base.is_exist(sys.argv[1] + '/server/DocService/package.json'):
  base.print_info('replace supervisor cfg to run docservice and converter from source')
  base.replaceInFileRE("/etc/supervisor/conf.d/ds-docservice.conf", "command=.*", "command=node " + git_dir + "/server/DocService/sources/server.js")
  base.replaceInFileRE("/app/ds/setup/config/supervisor/ds/ds-docservice.conf", "command=.*", "command=node " + git_dir + "/server/DocService/sources/server.js")
  base.replaceInFileRE("/etc/supervisor/conf.d/ds-converter.conf", "command=.*", "command=node " + git_dir + "/server/FileConverter/sources/convertermaster.js")
  base.replaceInFileRE("/app/ds/setup/config/supervisor/ds/ds-converter.conf", "command=.*", "command=node " + git_dir + "/server/FileConverter/sources/convertermaster.js")
  base.print_info('run_server.run_docker_server')
  run_server.run_docker_server();
else:
  #Fix theme generation for external sdkjs volume
  if base.is_exist(git_dir + "/server/FileConverter/bin/DoctRenderer.config"):
    base.print_info('replace DoctRenderer.config for external sdkjs volume')
    base.generate_doctrenderer_config(git_dir + "/server/FileConverter/bin/DoctRenderer.config", "../../../sdkjs/deploy/", "server", "../../../web-apps/vendor/")

  base.print_info('replace supervisor cfg to run docservice and converter from pkg')
  base.replaceInFileRE("/etc/supervisor/conf.d/ds-docservice.conf", "command=node .*", "command=/var/www/onlyoffice/documentserver/server/DocService/docservice")
  base.replaceInFileRE("/app/ds/setup/config/supervisor/ds/ds-docservice.conf", "command=node .*", "command=/var/www/onlyoffice/documentserver/server/DocService/docservice")
  base.replaceInFileRE("/etc/supervisor/conf.d/ds-converter.conf", "command=node .*", "command=/var/www/onlyoffice/documentserver/server/FileConverter/converter")
  base.replaceInFileRE("/app/ds/setup/config/supervisor/ds/ds-converter.conf", "command=node .*", "command=/var/www/onlyoffice/documentserver/server/FileConverter/converter")
  base.print_info('build_js_develop: ' + git_dir)
  build_js.build_js_develop(git_dir)
  