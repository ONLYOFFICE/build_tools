#!/usr/bin/env python3

import packages_desktop
# import packages_server
# import packages_builder

def make(product, package_list):
  if ("desktop" == product):
    packages_desktop.make(package_list.split())
  # if ("server" == product):
  #   packages_server.make(package_list.split())
  # if ("builder" == product):
  #   packages_builder.make(package_list.split())
  return
