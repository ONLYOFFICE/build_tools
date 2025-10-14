#!/usr/bin/env python

import sys
import os
sys.path.append('../../../../scripts')

import base

def make():
    arm_toolchain_url = 'https://releases.linaro.org/components/toolchain/binaries/5.4-2017.05/aarch64-linux-gnu/'
    arm_toolchain_tar_filename = 'gcc-linaro-5.4.1-2017.05-x86_64_aarch64-linux-gnu.tar.xz'
    base.cmd2('wget', [arm_toolchain_url + arm_toolchain_tar_filename])
    base.cmd2('tar', ['-xf', arm_toolchain_tar_filename])

if __name__ == "__main__":
	make()