# Before starting, make sure that:
# 1. MVS 2022 is installed and the necessary individual components are in its installer
# �	Windows Universal C Runtime
# �	.NET Framework 4.x SDK (.NET Framework 5.x SDK and later are currently not supported. These don't register their information to registry, don't have csc.exe and they use dotnet command with csc.dll instead for compiling.)
# �	C++ 20xx Redistributable MSMs (only required to build MSI installer)
# �	C++ Clang Compiler for Windows (x.x.x)
# 2. Java JDK >= 17
# 3. Antivirus is turned off
# 4. There is enough free space on the disk (50GB Libre Office, 50Gb cygwin64)

# after completion, the files will appear:
# {LO_BUILD_PATH}/sources/libo-core/instdir/program/soffice.exe
# {LO_BUILD_PATH}/sources/libo-core/LibreOffice.sln
# debugging can be done via MVS 2022
# https://wiki.documentfoundation.org/Development/IDE#Microsoft_Visual_Studio
# or via attatch to the soffice.bin process
# https://wiki.documentfoundation.org/Development/How_to_debug#Debugging_with_gdb

import sys

sys.path.append('../../scripts')
import threading

import os
import subprocess
import shutil
import argparse
import base

CYGWIN_DOWNLOAD_URL = 'https://cygwin.com/setup-x86_64.exe'
CYGWIN_TEMP_PATH = './tmp'
CYGWIN_SETUP_FILENAME = 'setup-x86_64.exe'
CYGWIN_SETUP_PARAMS = [
    "-P", "autoconf",
    "-P", "automake",
    "-P", "bison",
    "-P", "cabextract",
    "-P", "doxygen",
    "-P", "flex",
    "-P", "gawk=5.2.2-1",
    "-P", "gcc-g++",
    "-P", "gettext-devel",
    "-P", "git",
    "-P", "gnupg",
    "-P", "gperf",
    "-P", "make",
    "-P", "mintty",
    "-P", "nasm",
    "-P", "openssh",
    "-P", "openssl",
    "-P", "patch",
    "-P", "perl",
    "-P", "python",
    "-P", "python3",
    "-P", "pkg-config",
    "-P", "rsync",
    "-P", "unzip",
    "-P", "vim",
    "-P", "wget",
    "-P", "zip",
    "-P", "perl-Archive-Zip",
    "-P", "perl-Font-TTF",
    "-P", "perl-IO-String",
    "--no-admin",
    "--quiet-mode"
]
CYGWIN_BAT_PATH = 'C:/cygwin64/Cygwin.bat'
LO_BUILD_PATH = os.path.normpath(os.path.join(os.getcwd(), '../../../LO'))

CONFIGURE_PARAMS = [f'--with-external-tar="{LO_BUILD_PATH}/sources/lo-externalsrc"',
                    f'--with-junit="{LO_BUILD_PATH}/sources/junit-4.10.jar"',
                    f'--with-ant-home="{LO_BUILD_PATH}/sources/apache-ant-1.9.5"',
                    "--enable-pch",
                    "--disable-ccache",
                    "--with-visual-studio=2022",
                    "--enable-dbgutil",
                    '--enable-symbols="all"']


def create_folder_safe(folder_path):
    if not os.path.exists(folder_path):
        try:
            os.mkdir(folder_path)
            print(f"Folder '{folder_path}' created successfully.")
        except Exception as e:
            print(f"Error creating folder: {e}")
    else:
        print(f"Folder '{folder_path}' already exists.")


class CygwinRunner:
    @staticmethod
    def process_commands(commands: list[str]):
        proc = subprocess.Popen(
            [CYGWIN_BAT_PATH], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE
        )

        def read_stdout():
            for line in iter(proc.stdout.readline, ''):
                sys.stdout.write(line)
            proc.stdout.close()

        def read_stderr():
            for line in iter(proc.stderr.readline, ''):
                sys.stderr.write(line)
            proc.stderr.close()

        stdout_thread = threading.Thread(target=read_stdout)
        stderr_thread = threading.Thread(target=read_stderr)

        stdout_thread.start()
        stderr_thread.start()

        for command in commands:
            proc.stdin.write(command + '\n')
            proc.stdin.flush()

        stdout_thread.join()
        stderr_thread.join()

        proc.stdin.close()

        proc.wait()

    @staticmethod
    def install_gnu_make():
        base.print_info("install_gnu_make")
        commands = ['mkdir -p /opt/lo/bin',
                    'cd /opt/lo/bin',
                    'wget https://dev-www.libreoffice.org/bin/cygwin/make-4.2.1-msvc.exe',
                    'cp make-4.2.1-msvc.exe make',
                    'chmod +x make',
                    'exit']
        CygwinRunner.process_commands(commands)

    @staticmethod
    def install_ant_and_junit():
        base.print_info("install_ant_and_junit")
        commands = [f'mkdir -p {LO_BUILD_PATH}/sources',
                    f'cd {LO_BUILD_PATH}/sources',
                    'wget https://archive.apache.org/dist/ant/binaries/apache-ant-1.9.5-bin.tar.bz2',
                    'tar -xjvf apache-ant-1.9.5-bin.tar.bz2',
                    'wget http://downloads.sourceforge.net/project/junit/junit/4.10/junit-4.10.jar',
                    'exit']
        CygwinRunner.process_commands(commands)

    @staticmethod
    def clone_lo():
        base.print_info("clone_lo")
        commands = [f'cd {LO_BUILD_PATH}/sources',
                    'git clone https://gerrit.libreoffice.org/core libo-core',
                    'exit']
        CygwinRunner.process_commands(commands)

    @staticmethod
    def build_autogen():
        base.print_info("build_autogen")
        commands = [f'cd {LO_BUILD_PATH}/sources/libo-core',
                    f"./autogen.sh {' '.join(map(str, CONFIGURE_PARAMS))}",
                    'exit']
        CygwinRunner.process_commands(commands)

    @staticmethod
    def run_make_build():
        base.print_info("run_make")
        commands = [f'cd {LO_BUILD_PATH}/sources/libo-core',
                    f'/opt/lo/bin/make gb_COLOR=1',
                    "exit"]
        CygwinRunner.process_commands(commands)

    @staticmethod
    def build_vs_integration():
        base.print_info("run_make")
        commands = [f'cd {LO_BUILD_PATH}/sources/libo-core',
                    f'/opt/lo/bin/make gb_COLOR=1 vs-ide-integration',
                    "exit"]
        CygwinRunner.process_commands(commands)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="options")
    parser.add_argument("--lo_build_path", dest="build_path", default=f'../../../LO')
    parser.add_argument("--disable_sln", dest="disable_sln", action=argparse.BooleanOptionalAction)
    args = parser.parse_args()

    LO_BUILD_PATH = args.build_path
    DISABLE_SLN = args.disable_sln
    create_folder_safe(f'{LO_BUILD_PATH}/sources/lo-externalsrc')
    create_folder_safe(CYGWIN_TEMP_PATH)
    os.chdir(CYGWIN_TEMP_PATH)
    base.download(CYGWIN_DOWNLOAD_URL, CYGWIN_SETUP_FILENAME)
    subprocess.run([CYGWIN_SETUP_FILENAME] + CYGWIN_SETUP_PARAMS)
    os.chdir('..')
    shutil.rmtree(CYGWIN_TEMP_PATH)
    CygwinRunner.install_gnu_make()
    CygwinRunner.install_ant_and_junit()
    CygwinRunner.clone_lo()
    CygwinRunner.build_autogen()
    CygwinRunner.run_make_build()
    if not DISABLE_SLN:
        CygwinRunner.build_vs_integration()
