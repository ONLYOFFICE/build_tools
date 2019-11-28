#!/usr/bin/env python

import sys
sys.path.append('modules')
sys.path.append('../')

import config
import base

import boost
import cef
import icu
import openssl
import v8

def make():
  boost.make()
  cef.make()
  icu.make()
  openssl.make()
  v8.make()
  return
