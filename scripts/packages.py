#!/usr/bin/env python

import config
import base
import packages_desktop
# import packages_server
# import packages_builder

def make():
  if config.check_option("module", "desktop"):
    packages_desktop.make()
  # if config.check_option("module", "server"):
  #   packages_server.make()
  # if config.check_option("module", "builder"):
  #   packages_builder.make()
  return
