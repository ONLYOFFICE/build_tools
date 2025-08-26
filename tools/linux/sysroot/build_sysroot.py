#!/usr/bin/env python

import sys
sys.path.append('../../../scripts')
import base
import os
import shutil
import fix_symlinks

def bash_chroot(command, sysroot):
    base.cmd2('sudo -S chroot', [sysroot, '/bin/bash -c', '\"' + command + ' \"'])


def download_sysroot():
    curr_dir = base.get_script_dir(__file__)
    tmp_sysroot_ubuntu_dir = curr_dir + '/sysroot_ubuntu_1604'

    if os.path.isdir(tmp_sysroot_ubuntu_dir):
       shutil.rmtree(tmp_sysroot_ubuntu_dir)

    # debootstrap for downloading sysroot
    base.cmd2('sudo -S apt-get', ['install', 'debootstrap'])

    archive_ubuntu_url = 'http://archive.ubuntu.com/ubuntu/'
    base.cmd2('sudo -S debootstrap', ['--arch=amd64', 'xenial', tmp_sysroot_ubuntu_dir, archive_ubuntu_url])

    # setup a new sources
    base.cmd2('sudo -S cp', [curr_dir + '/sources.list', tmp_sysroot_ubuntu_dir + '/etc/apt/sources.list'])

    bash_chroot('apt update -y', tmp_sysroot_ubuntu_dir)
    bash_chroot('apt upgrade -y', tmp_sysroot_ubuntu_dir)
    bash_chroot('apt install -y build-essential curl libpthread-stubs0-dev zlib1g-dev', tmp_sysroot_ubuntu_dir)

    # # downloading arm toolchain
    arm_toolchain_url = 'https://releases.linaro.org/components/toolchain/binaries/5.4-2017.05/aarch64-linux-gnu/'
    arm_toolchain_tar_filename = 'gcc-linaro-5.4.1-2017.05-x86_64_aarch64-linux-gnu.tar.xz'
    arm_toolchain_output_dir = 'gcc-linaro-5.4.1-2017.05-x86_64_aarch64-linux-gnu'
    base.cmd2('wget', [arm_toolchain_url + arm_toolchain_tar_filename])
    base.cmd2('tar', ['-xf', arm_toolchain_tar_filename])
    base.cmd2('sudo -S rsync', ['-avh', '--progress', curr_dir + '/' + arm_toolchain_output_dir + '/', tmp_sysroot_ubuntu_dir + '/usr/'])
    shutil.rmtree(arm_toolchain_output_dir)
    os.remove(arm_toolchain_tar_filename)

    base.cmd2('sudo -S chmod', ['-R', 'o+rwx', tmp_sysroot_ubuntu_dir])

    # fix symlinks
    fix_symlinks.fix_symlinks(tmp_sysroot_ubuntu_dir)

    return

if __name__ == '__main__':
    download_sysroot()
