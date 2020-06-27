#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import os
import build

def make(src_dir, modules):
  old_cur = os.getcwd()

  base.cmd("./bootstrap.sh", ["--with-libraries=" + ",".join(modiles)])
  base.cmd("./b2", ["headers"])
  base.cmd("./b2", ["--clean"])
  base.cmd("b2.exe", ["--prefix=./../build/android", "link=static", "install"])

  for module in modules:
    module_dir = src_dir + "/libs/" + module
    os.chdir(module_dir)
    pro_file_content = []
    pro_file_content.append("QT -= core gui")
    pro_file_content.append("TARGET = boost_" + module)
    pro_file_content.append("TEMPLATE = lib")
    pro_file_content.append("CONFIG += staticlib")
    pro_file_content.append("")
    pro_file_content.append("include($$PWD/../../../../../base.pri)")
    pro_file_content.append("")
    pro_file_content.append("MAKEFILE=$$PWD/makefiles/build.makefile_$$CORE_BUILDS_PLATFORM_PREFIX")
    pro_file_content.append("core_debug:MAKEFILE=$$join(MAKEFILE, MAKEFILE, \"\", \"_debug_\")")
    pro_file_content.append("build_xp:MAKEFILE=$$join(MAKEFILE, MAKEFILE, \"\", \"_xp\")")
    pro_file_content.append("OO_BRANDING_SUFFIX = $$(OO_BRANDING)")
    pro_file_content.append("!isEmpty(OO_BRANDING_SUFFIX):MAKEFILE=$$join(MAKEFILE, MAKEFILE, \"\", \"$$OO_BRANDING_SUFFIX\")")
    pro_file_content.append("")
    pro_file_content.append("BOOST_SOURCES=$$PWD/../..")
    pro_file_content.append("INCLUDEPATH=$$BOOST_SOURCES")
    pro_file_content.append("INCLUDEPATH=$$PWD/include")
    pro_file_content.append("")
    pro_file_content.append("SOURCES += $$files($$PWD/src/*.cpp, true)")
    pro_file_content.append("")
    pro_file_content.append("DESTDIR = $$BOOST_SOURCES/../build/android/lib/$$CORE_BUILDS_PLATFORM_PREFIX")
    base.save_as_script(module_dir + "/" + module + ".pro", pro_file_content)
    build.make_pro_file(module_dir, module_dir + "/" + module + ".pro")
  
  os.chdir(old_cur)
  return
