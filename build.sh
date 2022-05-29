#!/bin/bash

docker build --tag onlyoffice-part1 -f Dockerfile-arm64 . 
docker build --tag onlyoffice-part2 -f Dockerfile-arm64-part2 .
