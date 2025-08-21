#!/usr/bin/env python

import sys
import os
sys.path.append('../../../../scripts')

import base

def make():
    arm_url = 'https://releases.linaro.org/components/toolchain/binaries/5.4-2017.05/aarch64-linux-gnu/'
    
    arm_toolchain_tar_filename = 'gcc-linaro-5.4.1-2017.05-x86_64_aarch64-linux-gnu.tar.xz'
    arm_toolchain_dirname = 'gcc-linaro-5.4.1-2017.05-x86_64_aarch64-linux-gnu'
    
    arm_sysroot_tar_filename = 'sysroot-glibc-linaro-2.21-2017.05-aarch64-linux-gnu.tar.xz'
    arm_sysroot_dirname = 'sysroot-glibc-linaro-2.21-2017.05-aarch64-linux-gnu'  
    
    if not base.is_file(arm_toolchain_tar_filename):
        base.cmd2('wget', [arm_url + arm_toolchain_tar_filename])
    
    if not base.is_dir(arm_toolchain_dirname):
        base.cmd2('tar', ['-xf', arm_toolchain_tar_filename])
        
    if not base.is_file(arm_sysroot_tar_filename):
        base.cmd2('wget', [arm_url + arm_sysroot_tar_filename])
    
    if not base.is_dir(arm_sysroot_dirname):
        base.cmd2('tar', ['-xf', arm_sysroot_tar_filename])

if __name__ == "__main__":
	make()