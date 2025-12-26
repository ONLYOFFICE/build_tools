sudo apt-get install git curl wget p7zip-full

sudo apt-get install git-lfs
# for old system (ubuntu 16)
#curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
#sudo apt-get install git-lfs

# save login
git config --global credential.helper store

# clone build_tools
git clone https://git.onlyoffice.com/ONLYOFFICE/build_tools.git

# deps =========================================

cd ./build_tools/tools/linux

# python 3.10
./python.sh

# qt
#./python3/bin/python3 ./qt_binary_fetch.py amd64
#./python3/bin/python3 ./qt_binary_fetch.py arm64
./python3/bin/python3 ./qt_binary_fetch.py all

# deps
./python3/bin/python3 ./deps.py

# cmake 3.30
sudo ./cmake.sh

cd ../../

# ==============================================

# sysroots (IF NEEDED) =========================

cd ./build_tools/tools/linux/sysroot
#./python3/bin/python3 ./fetch.py amd64
#./python3/bin/python3 ./fetch.py arm64
./../python3/bin/python3 ./fetch.py all
cd ../../../

# ==============================================


# configure ====================================

./tools/linux/python3/bin/python3 ./configure.py --clean "0" --update-light "1" --update "1" --branch "hotfix/v9.2.1" --module "desktop" --qt-dir "$(pwd)/tools/linux/qt_build/Qt-5.9.9"

# with sysroot: sysroot "1"

# ==============================================

# cross build linux_arm64
sudo apt install qemu-user qemu-user-static binfmt-support
sudo update-binfmts --enable qemu-aarch64

# 1) without sysroot
#sudo apt install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu
#sudo dpkg --add-architecture arm64
#sudo apt update
#... install all dev packages ...

# 2) official supported: with sysroot
./tools/linux/python3/bin/python3 ./configure.py sysroot "1" #...
