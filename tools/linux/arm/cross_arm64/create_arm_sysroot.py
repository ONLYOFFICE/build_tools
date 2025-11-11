#!/usr/bin/env python

import sys
import os

sys.path.append('../../../../scripts')
sys.path.append('../../sysroot')

import base # type: ignore
import fix_symlinks # type: ignore

def make():
    arm_sysroot_dir = os.path.abspath("./arm_sysroot")
    if not base.is_dir(arm_sysroot_dir):
        os.makedirs(arm_sysroot_dir)
    
    curr_dir = os.path.abspath(os.path.curdir)
    os.chdir(arm_sysroot_dir)
    
    sysroot_ubuntu_arm64v8_dir = os.path.abspath("./sysroot-ubuntu20.04-arm64v8")
    if not base.is_dir(sysroot_ubuntu_arm64v8_dir):
        os.makedirs(sysroot_ubuntu_arm64v8_dir)
        
    img_name = "image-ubuntu20.04-arm64v8:v1"
    container_name = "sysroot-ubuntu20.04-arm64v8"
    
    base.cmd("docker run --rm --privileged multiarch/qemu-user-static:register --reset")
    base.cmd("docker buildx install")
    base.cmd("docker buildx build --platform linux/arm64 --tag " + img_name + " .")   
    
    try:
        base.cmd("docker run -d --platform=linux/arm64 --name=" + container_name + " " + img_name)
        base.cmd("docker cp " + container_name + ":/usr " + sysroot_ubuntu_arm64v8_dir + "/usr")
        base.cmd("docker cp " + container_name + ":/lib " + sysroot_ubuntu_arm64v8_dir + "/lib")
        base.cmd("docker cp " + container_name + ":/bin " + sysroot_ubuntu_arm64v8_dir + "/bin")
        base.cmd("docker cp " + container_name + ":/etc " + sysroot_ubuntu_arm64v8_dir + "/etc")
        base.cmd("docker cp " + container_name + ":/var " + sysroot_ubuntu_arm64v8_dir + "/var")
        base.cmd("docker cp " + container_name + ":/sbin " + sysroot_ubuntu_arm64v8_dir + "/sbin")
    finally:
        base.cmd("docker stop " + container_name)
        base.cmd("docker rm " + container_name)
        
    os.chdir(curr_dir)
    
    fix_symlinks.fix_symlinks(sysroot_ubuntu_arm64v8_dir)
    
if __name__ == "__main__":
    make()