#!/usr/bin/env python

import config
import base
import deploy_desktop
import deploy_builder
import deploy_server
import develop.deploy_server as develop_deploy_server
import deploy_core
import deploy_mobile

def make():
  if config.check_option("module", "desktop"):
    deploy_desktop.make()
  if config.check_option("module", "builder"):
    deploy_builder.make()
  if config.check_option("module", "server"):
    deploy_server.make()
  if config.check_option("module", "develop"):
    develop_deploy_server.make()
  if config.check_option("module", "core"):
    deploy_core.make()
  if config.check_option("module", "mobile"):
    deploy_mobile.make()
  return
