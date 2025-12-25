wget https://github.com/Kitware/CMake/releases/download/v3.30.0/cmake-3.30.0-linux-x86_64.tar.gz
tar -xzf cmake-3.30.0-linux-x86_64.tar.gz -C /opt
ln -s /opt/cmake-3.30.0-linux-x86_64/bin/cmake /usr/local/bin/cmake
ln -s /opt/cmake-3.30.0-linux-x86_64/bin/ctest /usr/local/bin/ctest
rm cmake-3.30.0-linux-x86_64.tar.gz
