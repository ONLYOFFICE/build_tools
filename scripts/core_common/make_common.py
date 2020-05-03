#!/usr/bin/env python

import sys
sys.path.append('modules')
sys.path.append('..')

import config
import base

import platform

import boost
import cef
import icu
import openssl
import v8

def make():
  boost.make()
  if "ppc64" not in platform.machine():
    cef.make()
  icu.make()
  openssl.make()
  v8.make()
  return
