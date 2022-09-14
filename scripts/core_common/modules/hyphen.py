#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import os

def make():
    print("[fetch]: hyphen")
    new_dir = base.get_script_dir() + "/../../core/Common/3dParty/hyphen"
    old_dir = os.getcwd()
    os.chdir(new_dir)

    if not base.is_dir("hyphen"):
        base.cmd("git", ["clone", "https://github.com/hunspell/hyphen"])


    os.chdir(old_dir)
    return

