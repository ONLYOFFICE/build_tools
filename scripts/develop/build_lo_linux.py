# This script was successfully executed on Ubuntu 22.04.5 LTS

# Before starting, make sure that:
# 1. Python >= 3.9
# 2. The current working folder with the script and its path do not contain spaces and use Latin characters.
# 3. Antivirus is turned off
# 4. There is enough free space on the disk (50GB Libre Office and during the unpacking of packages, it's recommended that you allocate at least 80 gigabytes of free space)
# 5. The current working folder with the script and its path do not contain spaces and use Latin characters.

# If the error "You must put some 'source' URIs in your sources.list" occurs, you need to run the command:
    # software-properties-gtk 
# in the terminal, and then under the "Ubuntu Software" tab, click "Source code" if it's not turned on and submit

# after completion, the file will appear:
# current_folder_with_script/libreoffice_build/instdir/soffice
# debugging can be done via MVS 2022
# https://wiki.documentfoundation.org/Development/IDE#Microsoft_Visual_Studio
# or via VS Code with c/c++ tools
# https://wiki.documentfoundation.org/Development/IDE#Visual_Studio_Code_(VSCode)
# or via Qt Creator
# https://wiki.documentfoundation.org/Development/IDE#Qt_Creator
# or via attatch to the soffice.bin process
# https://wiki.documentfoundation.org/Development/How_to_debug#Debugging_with_gdb

import subprocess
import sys
import os

CONFIGURE_PARAMS = [
        "--enable-dbgutil",
        "--without-doxygen",
        "--enable-pch",
        "--disable-ccache",
        # "--with-visual-studio=2022",
        '--enable-symbols="all"'
    ]

SUDO_DEPENDENCIES = [
        "git", "build-essential", "zip", "ccache", "junit4", "libkrb5-dev", "nasm", "graphviz", "python3", 
        "python3-dev", "python3-setuptools", "qtbase5-dev", "libkf5coreaddons-dev", "libkf5i18n-dev", 
        "libkf5config-dev", "libkf5windowsystem-dev", "libkf5kio-dev", "libqt5x11extras5-dev", "autoconf", 
        "libcups2-dev", "libfontconfig1-dev", "gperf", "openjdk-17-jdk", "doxygen", "libxslt1-dev", 
        "xsltproc", "libxml2-utils", "libxrandr-dev", "libx11-dev", "bison", "flex", "libgtk-3-dev", 
        "libgstreamer-plugins-base1.0-dev", "libgstreamer1.0-dev", "ant", "ant-optional", "libnss3-dev", 
        "libavahi-client-dev", "libxt-dev"
    ]

DIR_NAME = "libreoffice"
OFFICE_PATH = "instdir/program/soffice"

class bcolors:
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    RESET = '\033[0m'

def run_command(command, exit_on_error=True):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"{bcolors.FAIL}Error executing command: {command}{bcolors.RESET}")
        if exit_on_error:
            sys.exit(1)

def install_dependencies():
    print("Updating package list...")
    run_command("sudo apt update")
    
    print("Adding PPA for GCC/G++ update...")
    run_command("sudo add-apt-repository -y ppa:ubuntu-toolchain-r/test")
    run_command("sudo apt update")
    
    print("Installing dependencies for LibreOffice...")
    run_command("sudo apt-get build-dep -y libreoffice")
    run_command(f"sudo apt-get install {' '.join(map(str, SUDO_DEPENDENCIES))}")

    print("Updating GCC/G++ to v12...")
    run_command("sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-12 60 --slave /usr/bin/g++ g++ /usr/bin/g++-12", exit_on_error=False)
    
    print(bcolors.OKGREEN + "All dependencies successfully installed!" + bcolors.RESET)

def build_libreoffice():
    print("Cloning LibreOffice repository...")
    run_command(f"git clone https://git.libreoffice.org/core {DIR_NAME}", exit_on_error=False)
    
    print("Changing to build directory...")
    os.chdir(f"./{DIR_NAME}")

    print("Start configurator autogen.sh...")
    run_command(f"./autogen.sh {' '.join(map(str, CONFIGURE_PARAMS))}")
    
    print(bcolors.OKCYAN + "Starting libreoffice build, this may take up to 24 hours and takes up about 20 GB of drive space. You will also most likely need at least 8 GBs of RAM, otherwise the machine might fall into swap and appear to freeze up..." + bcolors.RESET)
    run_command("make")
    
    print(bcolors.OKGREEN + "LibreOffice build completed!" + bcolors.RESET)

    # print(bcolors.OKCYAN + "Running LibreOffice..." + bcolors.RESET)
    # run_command(OFFICE_PATH, exit_on_error=False)

    
if __name__ == "__main__":
    install_dependencies()
    build_libreoffice()
