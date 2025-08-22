#!/usr/bin/env python

import sys
import os
sys.path.append('../../../../scripts')
sys.path.append('../../sysroot')

import base
import fix_symlinks

def make():
    arm_sysroot_dir = os.path.abspath("./arm_sysroot")
    if not base.is_dir(arm_sysroot_dir):
        os.makedirs(arm_sysroot_dir)
    
    curr_dir = os.path.abspath(os.path.curdir)
    os.chdir(arm_sysroot_dir)
    
    sysroot_ubuntu16_04_arm64v8_dir = os.path.abspath("./sysroot-ubuntu16.04-arm64v8")
    if not base.is_dir(sysroot_ubuntu16_04_arm64v8_dir):
        os.makedirs(sysroot_ubuntu16_04_arm64v8_dir)
    
    base.cmd("docker run --rm --privileged multiarch/qemu-user-static:register --reset")
    base.cmd("docker buildx install")
    base.cmd("docker buildx build --platform linux/arm64 --tag image-ubuntu16.04-arm64v8:v1 .")   
    
    try:
        base.cmd("docker run -d --platform=linux/arm64 --name=sysroot-ubuntu16.04-arm64v8 image-ubuntu16.04-arm64v8:v1")
        base.cmd("docker cp sysroot-ubuntu16.04-arm64v8:/usr " + sysroot_ubuntu16_04_arm64v8_dir + "/usr")
        base.cmd("docker cp sysroot-ubuntu16.04-arm64v8:/lib " + sysroot_ubuntu16_04_arm64v8_dir + "/lib")
        base.cmd("docker cp sysroot-ubuntu16.04-arm64v8:/bin " + sysroot_ubuntu16_04_arm64v8_dir + "/bin")
        base.cmd("docker cp sysroot-ubuntu16.04-arm64v8:/etc " + sysroot_ubuntu16_04_arm64v8_dir + "/etc")
        base.cmd("docker cp sysroot-ubuntu16.04-arm64v8:/var " + sysroot_ubuntu16_04_arm64v8_dir + "/var")
        base.cmd("docker cp sysroot-ubuntu16.04-arm64v8:/sbin " + sysroot_ubuntu16_04_arm64v8_dir + "/sbin")
    finally:
        base.cmd("docker stop sysroot-ubuntu16.04-arm64v8")
        base.cmd("docker rm sysroot-ubuntu16.04-arm64v8")
        
    os.chdir(curr_dir)
    
    fix_symlinks.fix_symlinks(sysroot_ubuntu16_04_arm64v8_dir)
    
    #rename libpcre.so.3.0 -> libpcre.so.3
    
if __name__ == "__main__":
    make()