#!/usr/bin/env python3

import packages_desktop
import packages_server
import packages_builder

def make(product, platform, targets):
  if ("desktop" == product):
    packages_desktop.make(platform, targets)
  if ("server" == product):
    packages_server.make(platform, targets)
  if ("builder" == product):
    packages_builder.make(platform, targets)
  else:
    exit(1)
  return
