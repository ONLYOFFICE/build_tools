#!/usr/bin/env python

import sys
sys.path.append('modules')
sys.path.append('..')

import config
import base

import boost
import cef
import icu
import openssl
import curl
import ixwebsocket
import v8
import html2

def make():
  boost.make()
  cef.make()
  icu.make()
  openssl.make()
  curl.make()
  ixwebsocket.make()
  v8.make()
  html2.make()
  return
