#!/usr/bin/env python

import packages_desktop
# import packages_server
# import packages_builder

def make(product, package_list):
  if -1 != product.find("desktop"):
    packages_desktop.make(package_list.split())
  # if -1 != product.find("server"):
  #   packages_server.make(package_list.split())
  # if -1 != product.find("builder"):
  #   packages_builder.make(package_list.split())
  return
