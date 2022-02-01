#!/usr/bin/env python

import package_desktop
import package_server
import package_builder

def make(product):
  if product == 'desktop': package_desktop.make()
  if product == 'server':  package_server.make()
  if product == 'builder': package_builder.make()
  else: exit(1)
  return
