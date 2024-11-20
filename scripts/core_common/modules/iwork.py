#!/usr/bin/env python

import sys
sys.path.append('../..')
import config
import base
import os
import subprocess

def make(use_gperf = True):
    base_dir = base.get_script_dir() + "/../../core/Common/3dParty/apple"

    cmd_args = ["fetch.py"]

    if True == use_gperf:
        cmd_args.append("--gperf")

    base.cmd_in_dir(base_dir, "python", cmd_args)
    return

if __name__ == '__main__':
    # manual compile
    make(False)