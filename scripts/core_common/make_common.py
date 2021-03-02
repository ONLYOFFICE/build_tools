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
import v8
import html2
import hunspell

def make():
  boost.make()
  cef.make()
  icu.make()
  openssl.make()
  v8.make()
  html2.make()
  hunspell.make(False)
  return
