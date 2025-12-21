#!/bin/bash

wget https://github.com/ONLYOFFICE-data/build_tools_data/raw/refs/heads/master/python/python3.tar.gz
wget https://github.com/ONLYOFFICE-data/build_tools_data/raw/refs/heads/master/python/extract.sh

chmod +x ./extract.sh
./extract.sh

rm ./extract.sh
rm ./python3.tar.gz


