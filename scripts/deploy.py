#!/usr/bin/env python

import config
import base
import deploy_desktop
import deploy_builder
import deploy_server
import deploy_core
import deploy_mobile
import deploy_osign

def make():
  if config.check_option("module", "desktop"):
    deploy_desktop.make()
  if config.check_option("module", "builder"):
    deploy_builder.make()
  if config.check_option("module", "server"):
    deploy_server.make()
  if config.check_option("module", "core"):
    deploy_core.make()
  if config.check_option("module", "mobile"):
    deploy_mobile.make()
  if config.check_option("module", "osign"):
    deploy_osign.make()
  if base.is_use_create_artifacts_qemu_any_platform():
    base.create_artifacts_qemu_any_platform()
  return
