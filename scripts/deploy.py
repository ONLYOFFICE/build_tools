import config
import base

def make_desktop():
  return

def make_builder():
  return

def make():
  if config.check_option("module", "desktop"):
    make_desktop()
  if config.check_option("module", "builder"):
    make_builder()
  return